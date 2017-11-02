import sys
import discord
import asyncio
import logging
import random
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials

logging.basicConfig(level=logging.INFO)
client = discord.Client()

class Option:
    def __init__(self):
        self.turnview = True
        self.deathrole = True
        self.lgmaxturn = 3
        self.lgchat = True

class LoupGarou:
    def __init__(self):
        self.URL = {"Villageois":"https://pierre.chachatelier.fr/jeux-societe/images/loups-garous-villageois-large.jpg",
                "Loup-Garou":"https://pierre.chachatelier.fr/jeux-societe/images/loups-garous-loup-large.jpg",
                "Voyante":"https://pierre.chachatelier.fr/jeux-societe/images/loups-garous-voyante-large.jpg",
                "Sorcière":"http://www.jeuxetcompagnie.fr/wp-content/uploads/2011/11/sorciere3.jpg",
                "Chasseur":"http://www.cyberfab.fr/gfx/loupsgarous/carte_chasseur.jpg",
                "Cupidon":"http://www.jeuxetcompagnie.fr/wp-content/uploads/2011/11/cupidon3.jpg",
                "Petite Fille":"https://www.jeuxetcompagnie.fr/wp-content/uploads/2011/11/petite-fille.jpg"}
        self.color = {"Villageois":0xCACC2D,
                    "Loup-Garou":0xB30000,
                    "Voyante":0xDC01A2,
                    "Sorcière":0xF37D06,
                    "Chasseur":0x328910,
                    "Cupidon":0x17DFD0,
                    "Petite Fille":0x2A24DB}
        self.amoureux = []
        self.jour = "1"
        self.poison = ""
        self.witch_heal = True
        self.witch_poison = True
        
        
class Player:
	def __init__(self,objet,leter,role,lettre):
		self.object = objet
		self.name = objet.name
		self.id = leter
		self.leter = lettre
		self.role = role
		
lg = LoupGarou()
option = Option()

# @client.event
#async def on_message_edit(b,after):
#    print(after.content)
    
@client.event
async def on_message(message):
    if message.content == "/test rlan":
        randomrole = random.choice(["Villageois","Loup-Garou","Voyante","Sorcière","Chasseur","Cupidon"])
        i = message.author
        em = discord.Embed(title="Vous êtes : " +randomrole,description=random.choice(lg.text["announce_"+randomrole]),colour=lg.color[randomrole])
        await client.send_message(client.get_channel("302448382788501505"), embed=em.set_author(name=i.name, icon_url=i.avatar_url).set_thumbnail(url=lg.URL[randomrole]))
    if message.content == "/test lgvote":
        lg.mj,lg.canal = message.author,message.channel
        await playerlist()
        setnbrl()
        lg.msg = await client.send_message(lg.canal,embed=discord.Embed(title="Chargement"))
        await roledistrib()
        while 1:
            await loupgarou()
            await endnight()
         
    if message.content.startswith("/helpmj") and message.channel != lg.mj and message.author != client.user:
        await client.send_message(lg.mj, message.content)
        while 1:
            reply = await client.wait_for_message(author=lg.mj)
            if reply.content.startswith("/mjreply"):
                await client.send_message(message.author, lg.mj.name +" vous a répondu :\n\n" +reply.content.split(" ")[-(len(reply.content.split(" "))-1):])


    if message.content == "/start":
        lg.mj,lg.canal = message.author,message.channel
        await playerlist()
        await option_main()
        await roledistrib()
        #début de game
        if verif("Cupidon"): await cupidon()
        while 1:
            lg.msg = await client.send_message(lg.canal,embed=discord.Embed(title="Nouveau Tour"))
            if verif("Voyante"): await voyante()
            await loupgarou()
            if verif("Sorcière"): await sorciere()
            await endnight()
            await village()
            await endnight()


            
            
def verif(role):
    return role in [x.role for x in lg.player]

async def cupidon():
    role = "Cupidon"
    await client.edit_message(lg.msg, embed=discord.Embed(title="Au tour de Cupidon", description=random.choice(lg.text["turn_" +role])).set_author(name="Nuit " +lg.jour, icon_url=lg.URL[role]))
    for x in lg.player:
        if x.role == "Cupidon":
            lg.cupidon = x
    mp = await client.send_message(lg.cupidon.object, embed=discord.Embed(title="A vous de jouer"))
    pltxt = "__Liste des joueurs__ :"
    for x in lg.player:
        await client.add_reaction(mp, x.id)
        pltxt +="\n" +x.leter +" : " +x.name
    while 1:
        await client.edit_message(mp, embed=discord.Embed(title="A vous de jouer", description=random.choice(lg.text["urturn_" +role])+"\n" +pltxt +"\n\n" +", ".join([x.name for x in lg.amoureux])).set_footer(text="Utilisez les réactions pour choisir les amoureux"))
        reac = await client.wait_for_reaction(message=mp,user=lg.cupidon.object)
        for x in lg.player:
            if x.id == reac.reaction.emoji:
                lg.amoureux.append(x)
        if len(lg.amoureux) == 2:
            break
    await client.send_message(lg.amoureux[0].object, embed=discord.Embed(title="Vous êtes amoureux avec " +lg.amoureux[1].name, description=random.choice(lg.text["announce_amoureux"]),colour=0xF51CD2))
    await client.send_message(lg.amoureux[1].object, embed=discord.Embed(title="Vous êtes amoureux avec " +lg.amoureux[0].name, description=random.choice(lg.text["announce_amoureux"]),colour=0xF51CD2))
    await client.edit_message(mp, embed=discord.Embed(title="Cupidon se rendort", description=lg.amoureux[0].name +" et " +lg.amoureux[1].name +" sont maintenant amoureux"))

async def voyante():
    f = True
    role = "Voyante"
    await client.edit_message(lg.msg, embed=discord.Embed(title="Au tour de la Voyante", description=random.choice(lg.text["turn_" +role])).set_author(name="Nuit " +lg.jour, icon_url=lg.URL[role]))
    for x in lg.player:
        if x.role == "Voyante":
            lg.voyante = x
    mp = await client.send_message(lg.voyante.object, embed=discord.Embed(title="A vous de jouer"))
    pltxt = "__Liste des joueurs__ :"
    for x in lg.player:
        if x.role != "Voyante":
            await client.add_reaction(mp, x.id)
            pltxt +="\n" +x.leter +" : " +x.name
    while f:
        await client.edit_message(mp, embed=discord.Embed(title="A vous de jouer", description=random.choice(lg.text["urturn_" +role]) +"\n" +pltxt).set_footer(text="Utilisez les réactions pour choisir qui espionner"))
        reac = await client.wait_for_reaction(message=mp,user=lg.voyante.object)
        for x in lg.player:
            if reac.reaction.emoji == x.id:
                await client.edit_message(mp, embed=discord.Embed(title= x.name +" est : " +x.role,description=random.choice(lg.text["voyante_" +x.role])).set_thumbnail(url=lg.URL[x.role]).set_footer(text="La Voyante se rendort"))
                f = False
                
async def petitefille():
    print()

async def loupgarou():
    tour = 1 #Nombre tour de tour
    lglist = [] #Liste des loups-garous
    msglist = [] #Liste du message des loups-garous
    vote = {}
    choice = [] #Joueurs pouvant être voté
    m = 0 # nombre de char dans le nom le plus long chez les Loups
    f = 1 #fin de tour
    role = "Loup-Garou"
    await client.edit_message(lg.msg, embed=discord.Embed(title="Au tour des Loups-Garous", description=random.choice(lg.text["turn_" +role])).set_author(name="Nuit " +lg.jour, icon_url=lg.URL[role]))

    for x in lg.player:
        if x.role == "Loup-Garou":
            lglist.append(x)
            if len(x.name) > m : m = len(x.name)
        else:
            choice.append(x) #création de la liste par défaut
            
    while f: #Boucle Tour des Loups-Garous       
        for x in lglist:
            vote[x] = "None"
            x.lgmsg = await client.send_message(x.object, embed=discord.Embed(title="Veuillez patientez",description=random.choice(lg.text["urturn_" +role])))
        print(vote)
        pltxt = "__Liste des joueurs__ :"
        for x in choice:
            print(x.name)
            pltxt += "\n" +x.leter +" : " +x.name
        for y in lglist:
            for x in choice:
                await client.add_reaction(y.lgmsg, x.id) #Ajout des réactions à chaque message des loups-garoux
        while 1: #Boucle d'un tour de Vote
            vtxt = "\n```diff"
            for x,y in vote.items():
                if y == "None":
                    vtxt += "\n- " +x.name +" "*(m-len(x.name)) +" > "
                else:
                    vtxt += "\n+ " +x.name +" "*(m-len(x.name)) +" > " +y.name +" (" +y.leter +")"
            for x in lglist:
                await client.edit_message(x.lgmsg, embed=discord.Embed(title="A vous de Jouer",description= vtxt +"```\n" +pltxt))
            reac = await client.wait_for_reaction()
            if reac.user in [x.object for x in lglist] and reac.reaction.emoji in [x.id for x in lg.player]:
                for x in lg.player:
                    if reac.reaction.emoji == x.id :
                        for y in lglist:
                            if y.object == reac.user:
                                vote[y] = x
            if "None" not in vote.values():
                choice = calculvote(vote)
                break
        #Fin d'un tour
        vtxt = "\n```diff"
        for x,y in vote.items():
            if y == "None":
                vtxt += "\n- " +x.name +" "*(m-len(x.name)) +" > "
            else:
                vtxt += "\n+ " +x.name +" "*(m-len(x.name)) +" > " +y.name +" (" +y.leter +")"
        for x in lglist:
            await client.edit_message(x.lgmsg, embed=discord.Embed(title="A vous de Jouer",description= vtxt +"```\n" +pltxt ))
        if len(choice) == 1:
            lg.victime = choice[0]
            f = 0
            for x in lglist:
                await client.edit_message(x.lgmsg, embed=discord.Embed(title="Les Loups-Garous se rendorment",description= "Victime : " +lg.victime.name))
        else:
            if tour <= option.lgmaxturn: #par défaut == 3
                tour += 1
                for x in lglist:
                    await client.edit_message(x.lgmsg, embed=discord.Embed(title="Fin du Tour",desctiption="Les votes ont finis à égalité entres plusieurs Joueurs"))
            if tour < option.lgmaxturn:
                lg.victime = random.choice(choice)
                for x in lglist:
                    await client.edit_message(x.lgmsg, embed=discord.Embed(title="Fin du Tour",desctiption=random.choice(lg.text["Loup-Garou_timeout"]).format(lg.victime.name)))

async def sorciere():
    if not lg.witch_heal and not lg.witch_poison : return
    role = "Sorcière"
    await client.edit_message(lg.msg, embed=discord.Embed(title="Au tour de la Sorcière", description=random.choice(lg.text["turn_" +role])).set_author(name="Nuit " +lg.jour, icon_url=lg.URL[role]))
    for x in lg.player:
        if x.role == "Sorcière":
            lg.sorciere = x
    mp = await client.send_message(lg.sorciere.object, embed=discord.Embed(title="A vous de jouer"))
    if lg.witch_heal: await client.add_reaction(mp, "♥")
    if lg.witch_poison: await client.add_reaction(mp, '\U0001f480')
    await client.add_reaction(mp, '✅')
    f = True
    while f:
        await client.edit_message(mp, embed=discord.Embed(title="A vous de jouer", description=random.choice(lg.text["urturn_" +role])).set_footer(text="Utilisez les réactions pour choisir quelle potion utiliser"))
        reac = await client.wait_for_reaction(message=mp,user=lg.sorciere.object)
        if reac.reaction.emoji == "♥":
            lg.victime = ""
            lg.witch_heal = False
            f = False
        if reac.reaction.emoji == "\U0001f480":
            await sorciere_poison(mp)
            lg.witch_poison = False
            f = False
        if reac.reaction.emoji == "✅":
            f = False
    await client.edit_message(mp, embed=discord.Embed(title="La sorcière se rendort"))
  
async def sorciere_poison(mp):
    await client.remove_reaction(mp, "♥", client.user)
    await client.remove_reaction(mp, "\U0001f480", client.user)
    await client.remove_reaction(mp, "✅", client.user)
    txt = "__Liste des joueurs__ :\n```\n"
    for x in lg.player:
        if x != lg.sorciere:
            txt += "\n" +x.leter +" : " +x.name
            await client.add_reaction(mp, x.id)
    await client.edit_message(mp, embed=discord.Embed(title="A vous de jouer", description=txt +"```").set_footer(text="Utilisez les réactions pour choisir qui empoisonner"))
    f = True
    while f:
        reac = await client.wait_for_reaction(message=mp,user=lg.sorciere.object)
        for x in lg.player:
            if x.id == reac.reaction.emoji: 
                await kill(x,"Sorcière")
                f = False

async def chasseur():
    role = "Chasseur"
    await client.edit_message(lg.msg, embed=discord.Embed(title="AU tour du Chasseur", description=random.choice(lg.text["turn_Chasseur"])).set_author(name="Jour " +lg.jour, icon_url=lg.URL[role]))
    for x in lg.death:
        if x.role == "Chasseur":
            lg.chasseur = x
    mp = await client.send_message(lg.chasseur.object, embed=discord.Embed(title="A vous de jouer"))
    txt = "__Liste des joueurs__ :\n```\n"
    for x in lg.player:
        if x != lg.chasseur:
            txt += "\n" +x.leter +" : " +x.name
            await client.add_reaction(mp, x.id)
    await client.edit_message(mp, embed=discord.Embed(title="A vous de jouer", description=txt +"```").set_footer(text="Utilisez les réactions pour choisir qui empoisonner"))
    f = True
    while f:
        reac = await client.wait_for_reaction(message=mp,user=lg.chasseur.object)
        for x in lg.player:
            if x.id == reac.reaction.emoji: 
                await kill(x,"Chasseur")
                await client.edit_message(mp, embed=discord.Embed(title="Le chasseur se rendort"))
                f = False

async def village():
    vote = {}
    choice = [] #Joueurs pouvant être voté
    m = 0 # nombre de char dans le nom le plus long
    tour = 1
    role = "Villageois"
    await client.edit_message(lg.msg, embed=discord.Embed(title="Le Village se réveille", description=random.choice(lg.text["urturn_village"])).set_author(name="Jour " +lg.jour, icon_url=lg.URL[role]))
    for x in lg.player:
        choice.append(x)
        if len(x.name) > m : m = len(x.name)
    f = True
    while f:
        for x in lg.player:
            vote[x] = "None"
        pltxt = "__Liste des joueurs__ :"
        for x in choice:
            pltxt +="\n" +x.leter +" : " +x.name
            await client.add_reaction(lg.msg, x.id)
        k = True
        while k:
            vtxt = "\n```diff"
            for x,y in vote.items():
                if y == "None":
                    vtxt += "\n- " +x.name +" "*(m-len(x.name)) +" > "
                else:
                    vtxt += "\n+ " +x.name +" "*(m-len(x.name)) +" > " +y.name +" (" +y.leter +")"
            await client.edit_message(lg.msg, embed=discord.Embed(title="Le Village se réveille",description=random.choice(lg.text["urturn_village"]) +"\n" +vtxt +"```\n" +pltxt))
            reac = await client.wait_for_reaction()
            if reac.user in [x.object for x in lg.player] and reac.reaction.emoji in [x.id for x in lg.player]:
                 for x in lg.player:
                    if reac.reaction.emoji == x.id :
                        for y in lg.player:
                            if y.object == reac.user:
                                vote[y] = x
            if "None" not in vote.values():
                choice = calculvote(vote)
                k =  False
        #Fin du tour
        await client.clear_reactions(lg.msg)
        vtxt = "\n```diff"
        for x,y in vote.items():
            if y == "None":
                vtxt += "\n- " +x.name +" "*(m-len(x.name)) +" > "
            else:
                vtxt += "\n+ " +x.name +" "*(m-len(x.name)) +" > " +y.name +" (" +y.leter +")"
        await client.edit_message(lg.msg, embed=discord.Embed(title="Le Village se réveille",description=random.choice(lg.text["urturn_village"]) +"\n" +vtxt +"```\n" +pltxt))
        if len(choice) == 1:
            await kill(choice[0],"Villageois")
            f = 0
        else:
            if tour <= option.lgmaxturn: #par défaut == 3
                tour += 1
                await client.edit_message(lg.msg, embed=discord.Embed(title="Fin du Tour",desctiption="Les votes ont finis à égalité entres plusieurs Joueurs"))
            if tour < option.lgmaxturn:
                await client.edit_message(lg.msg, embed=discord.Embed(title="Fin du Vote",desctiption=random.choice(lg.text["Villageois_timeout"])))
    
def calculvote(vote):
    l = [] #liste des votés
    m = 0 #vote max
    print(vote.values())
    for y in lg.player:
        print(y.name)
        x = list(vote.values()).count(y) # x = nombre de voix pour la personne
        print(x)
        print(m)
        if x > m:
            m = x
            l = []
            l.append(y)
        elif x == m:
            l.append(y)
    return l

async def endnight():
    if lg.victime:
        await kill(lg.victime,"Loup-Garou")
        lg.victime = ""
     #Vérification des conditions de victoire
    if len(lg.amoureux) == len(lg.player) : await victory("Amoureux")
    if [x.role for x in lg.player].count("Loup-Garou") == len(lg.player) : await victory("Loup-Garou")
    if [x.role for x in lg.player].count("Loup-Garou") == 0 : await victory("Villageois")
    
    
async def kill(x,reason):
    lg.player.remove(x)
    lg.death.append(x)
    em = discord.Embed(title= x.name +" est mort !",description=random.choice(lg.text["death_" +reason]).format(x.name),colour=lg.color[reason]).set_author(name=x.name, icon_url=x.object.avatar_url)
    if option.deathrole:
        em.set_thumbnail(url=lg.URL[x.role])
    await client.edit_message(lg.msg, embed=em)
    lg.msg = await client.send_message(lg.canal, embed=discord.Embed(title="."))
    if x in lg.amoureux:
        lg.amoureux.remove(x)
        am = lg.amoureux[0]
        lg.amoureux = []
        await kill(am,"Cupidon")
    if x.role == "Chasseur": await chasseur()
    
    
async def roledistrib():
    liste = ["\U0001f1e6","\U0001f1e7","\U0001f1e8","\U0001f1e9","\U0001f1ea","\U0001f1eb","\U0001f1ec","\U0001f1ed","\U0001f1ee","\U0001f1ef","\U0001f1f0","\U0001f1f1","\U0001f1f2","\U0001f1f3","\U0001f1f4","\U0001f1f5","\U0001f1f6","\U0001f1f7","\U0001f1f8","\U0001f1f9"]
    leterlist = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T']
    lg.player = []
    lg.death = []
    rolelist = []
    x = 0
    await client.edit_message(lg.msg, embed=discord.Embed(title="Répartition des rôles", description="Chargement"))
    print(option.nbrl)
    for r,n in option.nbrl.items():
        while n > 0:
            rolelist.append(r)
            n = n-1
    for i in lg.playerlist:
        randomrole = random.choice(rolelist)
        em = discord.Embed(title="Vous êtes : " +randomrole,description=random.choice(lg.text["announce_"+randomrole]),colour=lg.color[randomrole])
        await client.send_message(i, embed=em.set_author(name=i.name, icon_url=i.avatar_url).set_thumbnail(url=lg.URL[randomrole]))
        lg.player.append(Player(i,liste[x],randomrole,leterlist[x]))
        rolelist.remove(randomrole)
        x = x + 1
        await client.edit_message(lg.msg, embed=discord.Embed(title="Répartition des rôles", description=str(x) +"/" +str(len(lg.playerlist)) +"\nAjout de : " +i.name ))
    pltxt = "__Liste des joueurs__ :\n"
    for x in lg.player:
        pltxt += "\n" +x.leter +" : " +x.name
    await client.edit_message(lg.msg, embed=discord.Embed(title="Répartition des rôles", description=pltxt))

def setnbrl():
    option.nbrl = {"Voyante":1,"Sorcière":1,"Chasseur":1,"Cupidon":1,"Petite Fille":0}
    if len(lg.playerlist) < 12: option.nbrl["Loup-Garou"] = 2
    elif len(lg.playerlist) > 17: option.nbrl["Loup-Garou"] = 4
    else: option.nbrl["Loup-Garou"] = 3
    option.nbrl["Villageois"] = len(lg.playerlist)- (option.nbrl["Loup-Garou"] + option.nbrl["Voyante"] + option.nbrl["Sorcière"] + option.nbrl["Chasseur"] + option.nbrl["Cupidon"])

async def option_main():
    setnbrl()
    option.foot = lg.mj.name +", Veuillez utilisez les reactions pour modifier les options"
    lg.msg = await client.send_message(lg.canal,embed=discord.Embed(title="Chargement"))
    while 1:
        await client.edit_message(lg.msg, embed=discord.Embed(title="Option:",description="A - Configuration nombre de rôle >\nB - Affichage/Visibilité >\nC - Configuration rôles spéciaux >\nD - Configuration petite fille (avancé) >").set_footer(text=option.foot))
        await addreac(lg.msg,4)
        await client.add_reaction(lg.msg, "✅")
        reac = await client.wait_for_reaction(message=lg.msg,user=lg.mj)
        if reac.reaction.emoji == "\U0001f1e6":
            await client.clear_reactions(lg.msg) 
            await option_a()
        if reac.user != client.user and reac.reaction.emoji == "\U0001f1e7":
            await client.clear_reactions(lg.msg) 
            await option_b()
        if reac.user != client.user and reac.reaction.emoji == "\U0001f1e8":
            await client.clear_reactions(lg.msg) 
            await option_c()
        if reac.user != client.user and reac.reaction.emoji == "✅" and option.nbrl["Villageois"] >= 0 and option.nbrl["Loup-Garou"] > 0:
            await client.clear_reactions(lg.msg)
            break
        
async def option_a():
    liste = ["\U0001f43a","\U0001f441","\U0001f383","\U0001f52b","\U0001f498","\U0001f467","✅"]
    mem = True
    while 1:
        option.nbrl["Villageois"] = len(lg.playerlist) - (option.nbrl["Loup-Garou"] + option.nbrl["Voyante"] + option.nbrl["Sorcière"] + option.nbrl["Chasseur"] + option.nbrl["Cupidon"] + option.nbrl["Petite Fille"])
        text = "```diff"
        for r,n in option.nbrl.items():
            text = text +"\n" +colorline(n) +" " +r +" "*(12-len(r)) +": " +str(n)
        if option.nbrl["Villageois"] < 0:
            text = text + "\n\n- ERREUR : VEUILLEZ RETIRER DES PERSONNAGES OU DES LOUPS-GAROUS" 
        await client.edit_message(lg.msg, embed=discord.Embed(title="Répartition des rôles", description="nombre de Joueurs : " +str(len(lg.playerlist)) +"\n" +text +"```"))
        if mem == True:
            mem = False
            for e in liste:
                await client.add_reaction(lg.msg, e)
        reac = await client.wait_for_reaction(message=lg.msg,user=lg.mj)
        if reac.user != client.user and reac.reaction.emoji == "\U0001f43a":
            await client.remove_reaction(lg.msg,"\U0001f43a",reac.user)
            temp = await client.send_message(lg.canal, lg.mj.mention +", Veuillez rentrer le nombre de Loups-Garous désiré dans le chat")
            nb = await client.wait_for_message(author=lg.mj)
            option.nbrl["Loup-Garou"] = int(nb.content)
            await client.delete_message(temp)
            await client.delete_message(nb)
        if reac.user != client.user and reac.reaction.emoji == "\U0001f441":
            option.nbrl["Voyante"] = int(not option.nbrl["Voyante"])
            await client.remove_reaction(lg.msg,"\U0001f441",reac.user)
        if reac.user != client.user and reac.reaction.emoji == "\U0001f383":
            option.nbrl["Sorcière"] = int(not option.nbrl["Sorcière"])
            await client.remove_reaction(lg.msg,"\U0001f383",reac.user)
        if reac.user != client.user and reac.reaction.emoji == "\U0001f52b":
            option.nbrl["Chasseur"] = int(not option.nbrl["Chasseur"])
            await client.remove_reaction(lg.msg,"\U0001f52b",reac.user)
        if reac.user != client.user and reac.reaction.emoji == "\U0001f498":
            option.nbrl["Cupidon"] = int(not option.nbrl["Cupidon"])
            await client.remove_reaction(lg.msg,"\U0001f498",reac.user)
        if reac.user != client.user and reac.reaction.emoji == "\U0001f467":
            option.nbrl["Petite Fille"] = int(not option.nbrl["Petite Fille"])
            await client.remove_reaction(lg.msg,"\U0001f467",reac.user)
        if reac.user != client.user and reac.reaction.emoji == "✅" and option.nbrl["Villageois"] >= 0 and option.nbrl["Loup-Garou"] > 0:
            await client.clear_reactions(lg.msg)
            break
        
async def option_b():
    while 1:
        if option.turnview:
            a = "+ A : Le tour en cours est affiché"
        else:
            a = "- A : Le tour en cours est caché"
        if option.deathrole:
            b = "+ B : Les Rôles sont révélés à la mort"
        else:
            b = "- B : Les Rôles sont caché à la mort"
        await client.edit_message(lg.msg, embed=discord.Embed(title="Affichage/Visibilité",description="```diff\n" +a +"\n" +b +"```"))
        await addreac(lg.msg,2)
        await client.add_reaction(lg.msg, "✅")
        reac = await client.wait_for_reaction(message=lg.msg,user=lg.mj)
        if reac.user != client.user and reac.reaction.emoji == "\U0001f1e6":
            option.turnview = not option.turnview
            await client.remove_reaction(lg.msg,reac.reaction.emoji,reac.user)
        if reac.user != client.user and reac.reaction.emoji == "\U0001f1e7":
            option.deathrole = not option.deathrole
            await client.remove_reaction(lg.msg,reac.reaction.emoji,reac.user)
        if reac.user != client.user and reac.reaction.emoji == "✅":
            await client.clear_reactions(lg.msg)
            break

async def option_c(): #configuration role spéciaux
    while 1:
        if option.lgchat:
            a = "+ C : Les loups-garous peuvent communiquer pendant leur tour"
        else:
            a = "- C : Les loups-garous ne peuvent pas communiquer pendant leur tour"
        await client.edit_message(lg.msg, embed=discord.Embed(title="Configuration des rôles spéciaux",description="```diff\n" +colorline(lg.witch_heal) +" A : La sorcière a " +str(int(lg.witch_heal)) +" potion de Santé\n" 
                                                              +colorline(lg.witch_poison) + " B : La sorcière a " +str(int(lg.witch_poison)) +" potion de poison\n"
                                                              +a +"\n"
                                                              +"+ D : Les loups-Garous ont " +str(option.lgmaxturn) +" pour se décider" 
                                                              +"```"))
        await addreac(lg.msg,4)
        await client.add_reaction(lg.msg, "✅")
        reac = await client.wait_for_reaction(message=lg.msg,user=lg.mj)
        if reac.user != client.user and reac.reaction.emoji == "\U0001f1e6":
            lg.witch_heal = not lg.witch_heal
            await client.remove_reaction(lg.msg,reac.reaction.emoji,reac.user)
        if reac.user != client.user and reac.reaction.emoji == "\U0001f1e7":
            lg.witch_poison = not lg.witch_poison
            await client.remove_reaction(lg.msg,reac.reaction.emoji,reac.user)
        if reac.user != client.user and reac.reaction.emoji == "\U0001f1e8":
            option.lgchat = not option.lgchat
            await client.remove_reaction(lg.msg,reac.reaction.emoji,reac.user)
        if reac.user != client.user and reac.reaction.emoji == "✅":
            await client.clear_reactions(lg.msg)
            break

async def playerlist():
    lg.playerlist = [lg.mj]
    msg = await client.send_message(lg.canal, embed=discord.Embed(title="Liste des joueurs:",description="- " +"\n- ".join([x.name for x in lg.playerlist])).set_footer(text="Utilisez les réactions pour rejoindre la partie"))
    await client.add_reaction(msg, "❌")
    await client.add_reaction(msg, "✅")
    while 1:
        reac = await client.wait_for_reaction(message=msg)
        if reac.user != client.user and reac.reaction.emoji == "✅" and reac.user not in lg.playerlist and len(lg.playerlist) < 20:
            lg.playerlist.append(reac.user)
            await client.edit_message(msg, embed=discord.Embed(title="Liste des joueurs:",description="- " +"\n- ".join([x.name for x in lg.playerlist])).set_footer(text="Utilisez les réactions pour rejoindre la partie"))
        elif reac.user != client.user and reac.reaction.emoji == "❌":
            try:
                lg.playerlist.remove(reac.user)
                await client.edit_message(msg, embed=discord.Embed(title="Liste des joueurs:",description="- " +"\n- ".join([x.name for x in lg.playerlist])).set_footer(text="Utilisez les réactions pour rejoindre la partie"))
                await client.remove_reaction(msg,"✅",reac.user)
                await client.remove_reaction(msg,"❌",reac.user)
            except:
                await client.remove_reaction(msg,"❌",reac.user)
                print("player not in list")
        elif reac.user != client.user and reac.user == lg.mj and reac.reaction.emoji == "▶":
            await client.clear_reactions(msg)
            await client.edit_message(msg, embed=discord.Embed(title="Liste des joueurs:",description="- " +"\n- ".join([x.name for x in lg.playerlist])).set_footer(text="La liste des joueurs a été validé (par " +reac.user.name +")"))
            break
        if len(lg.playerlist) > 5 and "▶" not in [x.emoji for x in msg.reactions]:
            await client.add_reaction(msg, "▶")

async def victory(role):
    if role == "Amoureux":
        winner = ""
        for player in lg.amoureux:
            winner += "\n" + player.object.mention +" : " +player.role
        looser = ""
        for player in lg.death:
            looser += "\n" + player.object.mention +" : " +player.role
        await client.send_message(lg.canal, embed=discord.Embed(title="Les amoureux ont gagnés",description="__GG à__:\n" +winner +"\n-----------------" +deathwinner +"\n__Mention \"l'important c'est de participer\" à__:\n" +looser,color=0x17DFD0)
                                  .set_footer(text="Le Bot va s'arreter automatiquement. GG <3"))
    if role == "Loup-Garou":
        winner = ""
        for player in lg.player:
            if player.role == "Loup-Garou":
                winner += "\n" + player.object.mention +" : " +player.role
        deathwinner = ""
        for player in lg.death:
            if player.role == "Loup-Garou":
                deathwinner += "\n" + player.object.mention +" : " +player.role
        looser = ""
        for player in lg.death:
            if player.role != "Loup-Garou":
                looser += "\n" + player.object.mention +" : " +player.role
        await client.send_message(lg.canal, embed=discord.Embed(title="Les Loups-garous ont gagnés",description="__GG à__:\n" +winner +"\n-----------------" +deathwinner +"\n__Mention \"l'important c'est de participer\" à__:\n" +looser,color=0xB30000)
                                  .set_footer(text="Le Bot va s'arreter automatiquement. GG <3"))
    if role == "Villageois":
        winner = ""
        for player in lg.player:
            if player.role != "Loup-Garou":
                winner += "\n" + player.object.mention +" : " +player.role
        deathwinner = ""
        for player in lg.death:
            if player.role != "Loup-Garou":
                deathwinner += "\n" + player.object.mention +" : " +player.role
        looser = ""
        for player in lg.death:
            if player.role == "Loup-Garou":
                looser += "\n" + player.object.mention +" : " +player.role
        await client.send_message(lg.canal, embed=discord.Embed(title="Les Villageois ont gagnés",description="__GG à__:\n" +winner +"\n-----------------" +deathwinner +"\n__Mention \"l'important c'est de participer\" à__:\n" +looser,color=0xCACC2D)
                                  .set_footer(text="Le Bot va s'arreter automatiquement. GG <3"))
    client.logout()
    raise "Fin de la Partie"

def get_announce_spread():
    gc = gspread.authorize(ServiceAccountCredentials.from_json_keyfile_name("Boblebot-bf62eff2e7f4.json",["https://spreadsheets.google.com/feeds"]))
    wb = gc.open_by_key('1-JJZmP9SPJbzsRHXvBPbFTIDejwN2goqtHPv-Vdqtcg').get_worksheet(0)
    a = wb.get_all_values()
    del a[0]
    dico = {}
    for liste in a:
        while 1:
            if '' in liste:
                liste.remove('')
            else:
                break
        dico[liste[0]] = liste[-(len(liste)-1):]
    return dico

lg.text = get_announce_spread()
    
async def addreac(msg,nb):
    liste = ["\U0001f1e6","\U0001f1e7","\U0001f1e8","\U0001f1e9","\U0001f1ea","\U0001f1eb","\U0001f1ec","\U0001f1ed","\U0001f1ee","\U0001f1ef","\U0001f1f0","\U0001f1f1","\U0001f1f2","\U0001f1f3","\U0001f1f4","\U0001f1f5","\U0001f1f6","\U0001f1f7","\U0001f1f8","\U0001f1f9"][:nb]
    for e in liste:
        await client.add_reaction(msg, e)

def colorline(nb):
    if nb <= 0:
        return "-"
    if bool(nb) == True:
        return "+"

def rp(): #only for debbug
    return client.get_server("302447376679960576")

client.run(sys.argv[1],sys.argv[2])
