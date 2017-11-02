#Bob le bot 2.0
import sys
import discord
import asyncio
import logging
import requests
import aiohttp
import json
import random
import time
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from collections import OrderedDict
client = discord.Client()
logging.basicConfig(level=logging.INFO)
allmemberlist = client.get_all_members()
id_pres = "247342025274425346"
id_flf = "136349076353581056"
id_rp = "302447376679960576"
gc = gspread.authorize(ServiceAccountCredentials.from_json_keyfile_name("../Boblebot-bf62eff2e7f4.json",["https://spreadsheets.google.com/feeds"]))

class Mem:
    def __init__(self):
        self.msg = None
        self.sumid = {}
        
class Option:
    def __init__(self):
        self.block_taverne = False
        self.logs_delete = True
        self.logs_edit = False
        self.logs_join = True
        self.logs_leave = True
        self.logs_ban = True
        self.logs_role = True
        self.logs_role = True
        self.logs_name = True
        self.logs_avatar = True
        self.pres_update = True
        self.auto_jr = True
        self.modulo_update = "5"
        self.rgapi = sys.argv[3]

option = Option()
mem = Mem()

@client.event
async def on_ready():
    print("Connecté à :" +client.user.name +" (" +client.user.id +")")
    
    
@client.event
async def on_message(message):
    if len(message.content.split(" ")) > 1 : arg = " ".join(message.content.split(" ")[-(len(message.content.split(" "))-1):])
    else: arg = ""
    cmd = message.content.split(" ")[0]
    if cmd.startswith("/"): mem.msg = message
    if cmd.startswith("/") and message.channel.id == "136349076353581056" and message.author.id != "218830582250078209" and option.block_taverne: await error(message, "taverne")
    if cmd.startswith("/avatar"): await cmd_avatar(message,arg)
    if cmd.startswith("/discord"): await cmd_discord(message,arg) 
    if cmd.startswith("/roll"): await cmd_roll(message,arg)
    if cmd.startswith("/ping") : await cmd_ping(message)
    if cmd.startswith("//summ"): await rapi_summ(message,arg)
    if cmd.startswith("/ranked"): await rapi_ranked(message,arg)
    if cmd.startswith("/kikimeter"): await rapi_kikimeter(messsage,arg)
    if cmd.startswith("/masteries"): await rapi_masteries(message,arg)
    if cmd.startswith("/game"): await rapi_game(message,arg)
    if cmd.startswith("/match"): await rapi_game(message,arg)
    if cmd.startswith("/premade"): await rapi_premade(message,arg)
    if cmd.startswith("/afkmeter"): await rapi_afkmeter(message,arg)
    if cmd.startswith("/rpmanoir"): await rpmanoir(message,arg) # X
    if member_in_whitelist(message.author):
        if cmd.startswith("/option"): await mod_option(message,arg)
        if cmd.startswith("/admindiscord"): await mod_discord(message,arg)
        if cmd.startswith("/kill"): await mod_kill(message)
    if message.author.id == "218830582250078209":
        if cmd.startswith("//dl"): await client.send_file(message.channel, arg) 
        if cmd.startswith("//python"): await cmd_python(arg)


@client.event
async def on_member_join(member):
    joindate,date = UTC(str(member.joined_at)),UTC(str(member.created_at))
    if member.server.id == id_flf and option.logs_join: await sendlogs(discord.Embed(title="a rejoint le serveur",description="le " + joindate + "\n\nID: " + member.id + "\ncompte crée le " + date,colour=0xFFFFFF).set_author(name=member.name, icon_url=member.avatar_url),"flfn")
    if member.server.id == id_rp and option.logs_join: await sendlogs(discord.Embed(title="a rejoint le serveur",description="le " + joindate + "\n\nID: " + member.id + "\ncompte crée le " + date,colour=0xFFFFFF).set_author(name=member.name, icon_url=member.avatar_url),"rpn")
    if member.server.id == id_rp and option.auto_jr: await autojunior(member) 

@client.event
async def on_member_remove(member):
    if member.server.id == id_flf and option.logs_leave: await sendlogs(discord.Embed(title="a quitté le serveur", colour=0x000000).set_author(name=member.name, icon_url=member.avatar_url),"flfw")
    if member.server.id == id_rp and option.logs_leave: await sendlogs(discord.Embed(title="a quitté le serveur", colour=0x000000).set_author(name=member.name, icon_url=member.avatar_url),"rpw")
    if member.server.id == id_flf and option.pres_update: await gdoc_leave(member)
    
@client.event
async def on_member_ban(member):
     if member.server.id == id_flf and option.logs_ban: await sendlogs(discord.Embed(title="a été bannis !",colour=0x500000).set_author(name=member.name, icon_url=member.avatar_url),"flfw")
     if member.server.id == id_rp and option.logs_ban: await sendlogs(discord.Embed(title="a été bannis !",colour=0x500000).set_author(name=member.name, icon_url=member.avatar_url),"rpw")
     
@client.event
async def on_member_unban(server, user):
     if server.id == id_flf and option.logs_ban: await sendlogs(discord.Embed(title="a été débannis !",colour=0x00CCFF).set_author(name=user.name, icon_url=user.avatar_url),"flfw")
     if server.id == id_flf and option.logs_ban: await sendlogs(discord.Embed(title="a été débannis !",colour=0x00CCFF).set_author(name=user.name, icon_url=user.avatar_url),"rpw")

@client.event
async def on_message_delete(message):
    if message.server.id == id_flf and option.logs_delete and message.channel.name != "logs_flf":
        await sendlogs(discord.Embed(title="message suprimé dans : " + message.channel.name, description=message.content,colour=message.author.color).set_author(name=message.author.name, icon_url=message.author.avatar_url).set_footer(text="message du " + UTC(str(message.timestamp))),"flfn")
    if message.server.id == id_rp and option.logs_delete and message.channel.name not in ["loup_garou","laboratoire","logs","logs_a_rythme"]: 
        await sendlogs(discord.Embed(title="message suprimé dans : " + message.channel.name, description=message.content,colour=message.author.color).set_author(name=message.author.name, icon_url=message.author.avatar_url).set_footer(text="message du " + UTC(str(message.timestamp))),"rpn")

@client.event
async def on_message_edit(before,after):
    if after.server.id == id_flf and option.logs_edit and after.channel.name != "logs_flf" and before.content != after.content:
        await sendlogs(discord.Embed(title="message édité dans : " + before.channel.name,description=before.content + "\n\nremplacé par :\n\n" + after.content,colour=after.author.color),"flfw")
    if after.server.id == id_rp and option.logs_edit and after.channel.name != "logs_a_rythme" and before.content != after.content:
        await sendlogs(discord.Embed(title="message édité dans : " + before.channel.name,description=before.content + "\n\nremplacé par :\n\n" + after.content,colour=after.author.color),"rpw")
    if not before.pinned and after.pinned and after.channel.id == id_pres and option.pres_update: await gdoc_add(after)

@client.event
async def on_member_update(before, after):
    if after.server.id == id_flf and before.name != after.name and option.logs_name:
        await sendlogs(discord.Embed(title="Changement de nom :",description="**" + before.name + "** s'est rename en : **" + after.name + "**",colour=after.color).set_author(name=before.name, icon_url=before.avatar_url),"flfw")
    if after.server.id == id_flf and before.avatar_url != after.avatar_url and option.logs_avatar:
        await sendlogs(discord.Embed(title="Changement d'avatar :",description=after.avatar_url,colour=after.color).set_author(name=before.name, icon_url=after.avatar_url),"flfw")
    if (after.server.id == id_flf or after.server.id == id_rp) and before.roles != after.roles and option.logs_role: await logsrole(before,after) 
    if after.server.id == id_flf and before.name != after.name and option.pres_update: await gdoc_name(before,after)
    if after.id == "218830582250078209" and before.game != "League of Legends" and after.game == "League of Legends": await rapi_game(client.get_channel("151759870700421121"),"iElden")
    
#########################################################################################################

async def cmd_avatar(message,arg):
    if arg == "" : member = message.author
    else:
        try: member = message.server.get_member_named(arg)
        except: await error(message,"Keyerror")
    try: await client.send_message(message.channel, member.avatar_url)
    except: await error(message, "404")
    
async def cmd_discord(message,arg):
    try: member = forum().get_member_named(arg)
    except: member = message.author
    if "Gentil Admin" in [x.name for x in member.roles]: role = "Administrateur"
    elif "Modération" in [x.name for x in member.roles]: role = "Modérateur"
    elif "Senior" in [x.name for x in member.roles]: role = "Senior"
    elif "Junior" in [x.name for x in member.roles]: role = "Junior"
    else: role = "Inconnu"
    try:
        with open("anniv.json", encoding="ISO-8859-1") as json_file:
            member = forum().get_member_named(name)
            tag = str(member)
            annivJSON = json.load(json_file)
            anniv = str(annivJSON[tag])
            ifanniv = "\nAnniversaire: "
    except:
        anniv = ""
        ifanniv = ""
    em = discord.Embed(title="Info Client:",description="Rank: " + role + ifanniv + anniv + "\n" + arg + " a rejoint le serveur le " + UTC(str(member.joined_at)) + "\n----------------\n" + "```Récupération de la présentation ...```",colour=member.color).set_author(name=member.name, icon_url=member.avatar_url)
    msg = await client.send_message(message.channel, embed=em)
    try:
        sh = gc.open_by_key('1xd7inzne8BS4JxwzSerQmos5O88Q97ZXbaZgNtTYjwg')
        wb = sh.get_worksheet(0)
        ligne = str(wb.find(member.name + "#" + member.discriminator).row)
        pres = wb.acell('D' + ligne).value
    except:
        pres = ""
    em = discord.Embed(title="Info Client:",description="Rank: " + role + ifanniv + anniv + "\n" + arg + " a rejoint le serveur le " + UTC(str(member.joined_at)) + "\n----------------\n" +pres,colour=member.color).set_author(name=member.name, icon_url=member.avatar_url)
    await client.edit_message(msg, embed=em)

async def cmd_roll(message,arg):
    if message.content.startswith("/roll help"):
        em = discord.Embed(title="Help /roll",description="Syntaxe de la commande : /roll (nb)**d**(face)**+**(bonus)\nExemple : /roll 2d100+20 \n\nnb = nombre de dés a lancé\nface = nombre de face du dé\nbonus = bonus de point")
        await client.send_message(message.channel, embed=em)
        return
    if message.content.find("d") > 0 and message.content.find("+") > 0:  # /r xdy+z
        cmd = message.content.split(" ")[1]
        nb = int(cmd.split("d")[0])
        cmd = cmd.split("d")[1]
        face = int(cmd.split("+")[0])
        bonus = int(cmd.split("+")[1])
    if message.content.find("d") < 0 and message.content.find("+") > 0:  # /r y+z
        cmd = message.content.split(" ")[1]
        nb = 1
        face = int(cmd.split("+")[0])
        bonus = int(cmd.split("+")[1])
    if message.content.find("d") > 0 and message.content.find("+") < 0:  # /r xdy
        cmd = message.content.split(" ")[1]
        nb = int(cmd.split("d")[0])
        face = int(cmd.split("d")[1])
        bonus = 0
    if message.content.find("d") < 0 and message.content.find("+") < 0:  # /r or /r y
        nb = 1
        bonus = 0
        try:
            face = message.content.split(" ")[1]
        except:
            face = 100
    if nb < 1 or face < 1:
        em = discord.Embed(title="Erreur Syntax !",
                           description="Syntaxe de la commande : /roll (nb)**d**(face)**+**(bonus)\nExemple : /roll 2d100+20 \n\nnb = nombre de dés a lancé\nface = nombre de face du dé\nbonus = bonus de point")
        await client.send_message(message.channel, embed=em)
        try:
            await client.delete_message(message)
        except:
            await error(message, "403")
        return end
    total = 0
    x = nb
    textroll = ""
    while x > 0:
        resul = random.randint(1, face)
        textroll = textroll + " - " + str(resul)
        total = total + resul
        x = x - 1
    if bonus != 0:
        bonustext = " avec un bonus de " + str(bonus)
        total = total + bonus
    else:
        bonustext = ""
    try:
        color = message.author.color
    except:
        color = 0xFFFFFF
    em = discord.Embed(title="Lancé de dés",
                       description=message.author.name + " a lancé " + str(nb) + " dé " + str(face) + str(bonustext) + " et a obtenu :\n\n" + str(textroll) + "\nTOTAL : **" + str(total) + "**",
                       colour=color)
    await client.send_message(message.channel, embed=em)
    try:
        await client.delete_message(message)
    except:
        await error(message, "403")

async def cmd_ping(message):
    tsmsg = round((message.timestamp - datetime.datetime(1970,1,1)).total_seconds())
    tsac = round(time.time() *1000)
    print(tsmsg)
    
    await client.send_message(message.channel, str(tsac - tsmsg))


async def request(url,noerror=False):
    while 1:
        if "?" in url : response = requests.get(url +"&api_key=" + option.rgapi)
        else: response = requests.get(url +"?api_key=" + option.rgapi)
        try:
            if "status" in response.json() and not noerror:
                print(url)
                if response.json()["status"]["status_code"] == 429:
                    t = int(response.headers["Retry-After"])
                    msg = await client.send_message(mem.msg.channel, "```diff\n- [Erreur 429]\n> Trop de requête API. \n> Prochain essai dans {} seconde(s)```".format(str(t)))
                    time.sleep(t)
                    await client.delete_message(msg)
                else:
                    await error(mem.msg,"rgapi",rgapi=response.json())
            else: return response.json()
        except: return response.json()
        
async def aiorequest(url,noerror=False):
    while 1:
        if "?" in url : url = url +"&api_key=" + option.rgapi
        else: url = url +"?api_key=" + option.rgapi
        async with aiohttp.get(url) as response:
            js = await response.json()
            try:
                if "status" in js and not noerror:
                    print(url)
                    if response.json()["status"]["status_code"] == 429:
                        t = int(response.headers["Retry-After"])
                        msg = await client.send_message(mem.msg.channel, "```diff\n- [Erreur 429]\n> Trop de requête API. \n> Prochain essai dans {} seconde(s)```".format(str(t)))
                        await asyncio.sleep(t)
                        await client.delete_message(msg)
                    else:
                        await error(mem.msg,"rgapi",rgapi=js)
                else: return js
            except: return js

async def getsumm(message,arg):
    name = arg.lower().replace(" ","")
    url = "https://euw1.api.riotgames.com/lol/summoner/v3/summoners/by-name/" + name + "?api_key=" + option.rgapi
    response = await request(url)
    if "status" in response:
        await error(message,"rgapi",rgapi=response["status"])
    try:
        name = response['name']
        sum = str(response['id'])
        acc = str(response['accountId'])
        icon = "http://ddragon.canisback.com/latest/img/profileicon/" +str(response['profileIconId']) +".png"
    except KeyError:
        await error(message, "Keyerror")
    return name,sum,acc,icon

async def rapi_summ(message,arg):
    name,sum,acc,icon = await getsumm(message,arg)
    await client.send_message(message.channel, embed=discord.Embed(title="Info Summoner : ", description="sum : "+sum +"\nacc : " +acc, colour=0xDDDDDD))

async def rapi_ranked(message,arg):
    name,sum,acc,icon = await getsumm(message,arg)
    url = "https://euw1.api.riotgames.com/lol/league/v3/positions/by-summoner/" +sum +"?api_key=" + option.rgapi
    response = await request(url)
    solo_league,solo_div,solo_point,solo_win,solo_losse = "UNRANKED","","0",0,0
    flex_league,flex_div,flex_point,flex_win,flex_losse = "UNRANKED","","0",0,0
    for dic in response:
        if dic["queueType"] == "RANKED_SOLO_5x5":
            solo_league = dic["tier"]
            solo_div = dic["rank"]
            solo_point = str(dic["leaguePoints"])
            solo_win = dic["wins"]
            solo_losse = dic["losses"]
        if dic["queueType"] == "RANKED_FLEX_SR":
            flex_league = dic["tier"]
            flex_div = dic["rank"]
            flex_point = str(dic["leaguePoints"])
            flex_win = dic["wins"]
            flex_losse = dic["losses"]
    win = solo_win + flex_win
    losse = solo_losse + flex_losse
    try: color = message.server.get_member_named(name).color
    except: color = 0xDDDDDD
    await client.send_message(message.channel, embed=discord.Embed(title="Info Summoner : ",description="Solo Queue : " +solo_league +" " +solo_div +" avec " +solo_point +" LP\n"
                              +"Flex Queue : " +flex_league +" " +flex_div +" avec " +flex_point +" LP\n"
                              +"\nWin Rate : " +str(round((win /(win + losse))*100)) +"% (" +str(win) +"/" +str(losse) +")",colour=color).set_author(name=arg, icon_url=icon))

async def rapi_masteries(message,arg):
    if arg.find("#") > 0:
        nb = int(arg.split("#")[1])
        arg = arg.split(" #")[0]
    else: nb = 5
    name,sum,acc,icon = await getsumm(message,arg)
    url = "https://euw1.api.riotgames.com/lol/champion-mastery/v3/champion-masteries/by-summoner/" + sum
    response = await request(url)
    x = 0
    txt,champ,level,point,token,progress = "",{},{},{},{},{}
    while x < nb:
        try: champ[x] = await champion(str(response[x]["championId"]))
        except: champ[x] = str(response[x]["championId"])
        level[x] = str(response[x]['championLevel'])
        pt = response[x]['championPoints']
        point[x] = str((pt // 1000)) + " " + str(pt % 1000).zfill(3)
        token[x] = response[x]['tokensEarned']
        progress[x] = getprogressbar(level[x], pt, token[x])
        x += 1
    m = 0
    for l in champ.values():
        if len(l) > m: m = len(l)
    x = 0
    while x < nb:
        txt += "\n" +str(x+1) +" - **" +champ[x] +"**" +" "*(m - len(champ[x])) +" > Level : **" +level[x] +"** Points : **" +point[x] +"**" +progress[x]
        x += 1
    try: color = message.server.get_member_named(name).color
    except: color = 0xDDDDDD
    response = await request("https://euw1.api.riotgames.com/lol/champion-mastery/v3/scores/by-summoner/" + sum)
    await client.send_message(message.channel,embed=discord.Embed(title="Info Masteries :",description="Points totaux : **" +str(response) +"**\n" +txt,colour=color).set_author(name=name, icon_url=icon))

class Summoner:
    def __init__(self,name,champion,rank,masteries):
        self.name = name
        self.champion = champion
        self.rank = rank
        self.masteries = masteries

async def rapi_game(message,arg):
    if arg == "" : arg = message.author.name
    msg = await client.send_message(message.channel, embed=discord.Embed(title="Veuillez Patienter"))
    name,sum,acc,icon = await getsumm(msg,arg)
    game = await request("https://euw1.api.riotgames.com/lol/spectator/v3/active-games/by-summoner/" +sum)
    blue,red,m,n = [],[],0,0
    h = {"BRONZE":"Bronze","SILVER":"Silver","GOLD":"Gold","PLATINUM":"Platine","DIAMOND":"Diamant","MASTER":"Master","CHALLENGER":"Chall"}
    for player in game["participants"]:
        a = player["summonerName"]
        try :
            b = await champion(str(player["championId"]))
        except: b = "inconnu"
        if len(a) + len(b) >= 22 : a = "[...]"
        getrank = await request("https://euw1.api.riotgames.com/lol/league/v3/positions/by-summoner/" +str(player["summonerId"]))
        c = "unranked"
        for x in getrank:
            if x["queueType"] == "RANKED_SOLO_5x5": c = "{} {}".format(h[x["tier"]],x["rank"])
        try:
            getcm =  await request("https://euw1.api.riotgames.com/lol/champion-mastery/v3/champion-masteries/by-summoner/{}/by-champion/{}".format(str(player["summonerId"]),str(player["championId"])),noerror=True)
            point = " "*(3-len(str(getcm["championPoints"] // 1000)))+str((getcm["championPoints"] // 1000)) + "." + str(getcm["championPoints"] % 1000//100) +"k"
            d = "Level {} ({})".format(str(getcm["championLevel"]),point)
        except: d = "Level 0"
        if player["teamId"] == 100 : blue.append(Summoner(a,b,c,d))
        if player["teamId"] == 200 : red.append(Summoner(a,b,c,d))
        if len(a) + len(b) > m : m = len(a) + len(b)
        if len(c) > n : n = len(c)
    try: color = message.server.get_member_named(name).color
    except: color = 0xDDDDDD
    with open("queueid.json", encoding="ISO-8859-1") as json_file:
        jsonfile = json.load(json_file)
        queuetype = jsonfile[str(game["gameQueueConfigId"])]
    em = discord.Embed(title="Info Game",description=queuetype,colour=color)
    em.add_field(name="Blue Team", value="```lisp\n" +("\n".join([x.name +"(" +x.champion +") "+" "*(m-len(x.name)-len(x.champion)) +"> " +x.rank +" "*(n-len(x.rank)+1) +x.masteries for x in blue]) + "```"))
    em.add_field(name="Red Team", value="```lisp\n" +("\n".join([x.name +"(" +x.champion +") "+" "*(m-len(x.name)-len(x.champion)) +"> " +x.rank +" "*(n-len(x.rank)+1) +x.masteries for x in red]) + "```"))
    await client.edit_message(msg, embed=em.set_author(name=name, icon_url=icon))

async def update_premade(analysed,msg,dico,color):
    d,c = {},{}
    for x,y in dico.items():
        if y >= 5 and y <= 10:
            try: d[mem.sumid[x]] = y
            except:
                response = await request("https://euw1.api.riotgames.com/lol/summoner/v3/summoners/" +x)
                name = response["name"]
                mem.sumid[x] = name
                d[name] = y
        elif y > 10:
            try: c[mem.sumid[x]] = y
            except:
                response = await request("https://euw1.api.riotgames.com/lol/summoner/v3/summoners/" +x)
                name = response["name"]
                mem.sumid[x] = name
                c[name] = y
    dic = OrderedDict(sorted(d.items(), key=lambda t: t[0]))
    cic = OrderedDict(sorted(c.items(), key=lambda t: t[0]))
    em = discord.Embed(title="Game analysées : " +str(analysed),colour=color)
    em.add_field(name="Bests Bro",value=".\n"+"\n".join([x +" : " +str(y) for x,y in cic.items()]))
    em.add_field(name="Petits Bro",value=".\n"+"\n".join([x +" : " +str(y) for x,y in dic.items()]))
    await client.edit_message(msg,embed=em)

async def rapi_premade(message,arg):
    if arg == "" : arg = message.author.name
    msg = await client.send_message(message.channel, embed=discord.Embed(title="Veuillez Patienter"))
    name,sum,acc,icon = await getsumm(msg,arg)
    try: color = message.server.get_member_named(name).color
    except: color = 0xDDDDDD
    index,analysed,end,mate = "0",0,True,{}
    while end:
        histo = await request("https://euw1.api.riotgames.com/lol/match/v3/matchlists/by-account/{}?beginIndex={}&season=9".format(acc,index))
        for history in histo["matches"]:
            match = await request("https://euw1.api.riotgames.com/lol/match/v3/matches/" +str(history["gameId"]))
            for player in match[ "participantIdentities"]:
                try :
                    summ = str(player["player"]["summonerId"])
                    if summ != sum:
                        try: mate[summ] += 1
                        except: mate[summ] = 1
                except: print("Erreur : rapi_premade")
            analysed += 1
            if analysed % int(option.modulo_update) == 0: await update_premade(analysed,msg,mate,color)
        if len(histo["matches"]) > 0: index = str(histo["endIndex"])
        else: end = False
    await update_premade(analysed,msg,mate,color)

async def rapi_afkmeter(message,arg):
    count = {}
    name,sum,acc,icon = await getsumm(message,arg)
    response = await request("https://euw1.api.riotgames.com/lol/match/v3/matchlists/by-account/" +acc +"?season=9")
    try: color = message.server.get_member_named(name).color
    except: color = 0xDDDDDD
    msg = await client.send_message(message.channel, embed=discord.Embed(title="Afk Meter",colour=color).set_author(name=name, icon_url=icon))
    analysed = 0
    for histo in response["matches"]:
        matchid = str(histo["gameId"])
        response = await request("https://euw1.api.riotgames.com/lol/match/v3/matches/" +matchid)
        for participant in response["participantIdentities"]:
            if str(participant["player"]["accountId"]) == acc : id = str(participant["participantId"])
        response = await request("https://euw1.api.riotgames.com/lol/match/v3/timelines/by-match/" +matchid)
        oldpos,afk = "None",0
        for frame in response["frames"]:
            try : j = frame["participantFrames"][id]["position"]
            except : j = {"x":"None","y":"None"}
            pos = str(j["x"])+","+str(j["y"])
            if pos == oldpos :
                afk += 1
                if afk >= 2:
                    try: count[matchid] += 1
                    except: count[matchid] = 2
            else: afk = 0
            oldpos = pos
        analysed += 1
        if analysed % int(option.modulo_update) == 0:
            txt,nb,mt = "",0,0
            for x,y in count.items():
                txt += "\ngame n°" +x +" : **" +str(y) +"** minute(s)"
                nb += 1
                mt += y
            em = discord.Embed(title="Afk Meter :",description="Sur les " +str(analysed) +" dernières parties\n" +name +" a AFK **" +str(nb) +"** games pour un total de **" +str(mt) +"** minutes\n\n" +txt,colour=color)
            await client.edit_message(msg, embed=em.set_author(name=name, icon_url=icon))
    txt,nb,mt = "",0,0
    for x,y in count.items():
        txt += "\ngame n°" +x +" : **" +str(y) +"** minute(s)"
        nb += 1
        mt += y
    em = discord.Embed(title="Afk Méteur :",description="Sur les " +str(analysed) +" dernières parties\n" +name +" a AFK **" +str(nb) +"** games pour un total de **" +str(mt) +"** minutes\n\n" +txt,colour=color)
    await client.edit_message(msg, embed=em.set_author(name=name, icon_url=icon))
    
async def rapi_kikimeter(message,arg):
    await error(message,"kikimeter")
    if arg == "" : arg = message.author.name
    msg = await client.send_message(message.channel, embed=discord.Embed(title="Veuillez Patienter"))
    name,sum,acc,icon = await getsumm(msg,arg)
    try: color = message.server.get_member_named(arg).color
    except: color = 0xDDDDDD
    
async def mod_option(message,arg):
    if arg == "":
        text = "```diff\nOPTION DU BOT :\n"
        for x,y in option.__dict__.items():
            text += "\n" +colorline(y) +" " +x +" : " +str(y)
        await client.send_message(message.channel, text +"```")
    else:
        cmd,val = arg.split(" ")[0],arg.split(" ")[1]
        if str(val).lower() == "false": val = False
        if str(val).lower() == "true": val = True
        option.__dict__[cmd] = val
        await client.send_message(message.channel, "```diff\n" +colorline(val) +" " +message.author.name +" a modifier l'option : " +cmd +"```")
            
            
def colorline(x):
    if str(x).lower() == "true" : return "+"
    elif str(x).lower() == "false" : return "-"
    else: return ">"
            
async def mod_discord(message,arg):
    try: name = member = forum().get_member_named(arg)
    except: await ERROR(message, "Keyerror")
    joinedat = UTC(str(member.joined_at))
    createat = UTC(str(member.created_at))
    em = discord.Embed(title="Info Client:",description="Serveur rejoint le: " + joinedat + "\nCompte crée le: " + str(createat) + "\nPseudo: " + str(member.name) + "\nNickname: " + str(member.nick) + "\nID: " + str(member.id), colour=member.color)
    await client.send_message(message.channel, embed=em.set_author(name=member.name + "#" + member.discriminator, icon_url=member.avatar_url))

async def mod_kill(message):
    print("Le Bot a été kill par " + message.author.name)
    await client.send_message(message.channel, "```Le Bot a été kill par " + message.author.name + "```")
    await client.logout()

async def logsrole(before,after):
    if after.server.id == id_flf and before.roles != after.roles and option.logs_role:
        beforetext = ""
        aftertext = ""
        if len(before.roles) > len(after.roles):  # role suprimé
            for role in before.roles:
                if role.name != "@everyone" and role not in after.roles:
                    desc = after.name + " s'est fait retiré le rôle : **" + role.name + "**"
        if len(before.roles) < len(after.roles):  # role ajouté
            for role in after.roles:
                if role.name != "@everyone" and role not in before.roles:
                    desc = after.name + " s'est fait ajouté le rôle : **" + role.name + "**"
        roletext = ""
        for role in after.roles:
            if role.name != "@everyone":
                roletext = roletext + " ; **" + role.name + "**"
        em = discord.Embed(title="Changement de Rôle",description=desc + "\n\n__Il possède maintenant ces roles__ :\n" + roletext,colour=after.color)
        em.set_author(name=after.name, icon_url=after.avatar_url)
        await sendlogs(em, "flfw")
    elif after.server.id == id_rp and before.roles != after.roles and option.logs_role:
        beforetext = ""
        aftertext = ""
        if len(before.roles) > len(after.roles):  # role suprimé
            for role in before.roles:
                if role.name != "@everyone" and role not in after.roles:
                    desc = after.name + " s'est fait retiré le rôle : **" + role.name + "**"
        if len(before.roles) < len(after.roles):  # role ajouté
            for role in after.roles:
                if role.name != "@everyone" and role not in before.roles:
                    desc = after.name + " s'est fait ajouté le rôle : **" + role.name + "**"
        roletext = ""
        for role in after.roles:
            if role.name != "@everyone":
                roletext = roletext + " ; **" + role.name + "**"
        em = discord.Embed(title="Changement de Rôle",description=desc + "\n\n__Il possède maintenant ces roles__ :\n" + roletext,colour=after.color)
        em.set_author(name=after.name, icon_url=after.avatar_url)
        await sendlogs(em, "rpw")

async def gdoc_add(after):
    utc = str(after.timestamp).split(" ")[0]
    date =utc.split("-")[2] +"/" +utc.split("-")[1] +"/" +utc.split("-")[0]
    wb = gc.open_by_key('1xd7inzne8BS4JxwzSerQmos5O88Q97ZXbaZgNtTYjwg').get_worksheet(0)
    name = after.author.name +"#" +after.author.discriminator
    if name in wb.col_values(1):
        await error(after,"presfound")
    if "Senior" in [x.name for x in after.auhor.roles] or "Modération" in [x.name for x in after.auhor.roles] or "Gentil Admin" in [x.name for x in after.auhor.roles]:
        msgconf = await client.send_message(after.channel, "```diff\n- [Question]\n\n+ Voulez vous ajouter la présentation ?\n+ Le message épinglé viens d'un Senior/Modo/Admin, une confirmation est nécessaire\n> ✅ Ajouter la présentation\n> ❌ Ne pas ajouter la présentation```")
        await client.add_reaction(msgconf, "✅")
        await client.add_reaction(msgconf, "❌")
        f = 1
        while f:
            reac = await client.wait_for_reaction(message=msgconf)
            if reac.user != client.user and reac.reaction.emoji == "✅":
                await client.delete_message(msgconf)
                f = 0
            if reac.user != client.user and reac.reaction.emoji == "❌":
                await client.delete_message(msgconf)
                raise noconf
    ligne = str(wb.col_values(1).index("")+1)
    wb.update_acell("A"+ligne,name)
    wb.update_acell("B"+ligne,date)
    wb.update_acell("C"+ligne,"Junior")
    wb.update_acell("D"+ligne,after.content)
    
async def gdoc_leave(member):
    wb = gc.open_by_key('1xd7inzne8BS4JxwzSerQmos5O88Q97ZXbaZgNtTYjwg').get_worksheet(0)
    try:
        ligne = str(wb.find(member.name +"#" +member.discriminator).row)
        wb.update_acell("C"+ligne,"leave")
    except gspread.exceptions.CellNotFound:
        print("membre non trouvé")
        
async def gdoc_name(before,after):
    if before.name != after.name and after.server.id == id_flf:
        wb = gc.open_by_key('1xd7inzne8BS4JxwzSerQmos5O88Q97ZXbaZgNtTYjwg').get_worksheet(0)
        try:
            ligne = str(wb.find(before.name +"#" +before.discriminator).row)
            wb.update_acell("A"+ligne,after.name +"#" +after.discriminator)
        except gspread.exceptions.CellNotFound:
            print("membre non trouvé")

async def autojunior(member):
    name = member.name
    flfmember = forum().get_member_named(name)
    for role in flfmember.roles:
        role = str(role)
        if role == "Senior":
            addrole = discord.utils.get(server.role_hierarchy, name="Voyageur")
            await client.add_roles(member, addrole)
            await client.send_message(client.get_channel("318435538589712395"),member.mention + " est Senior sur le discord du Forum, le rôle ''Voyageur'' lui a donc été attribué")
        if role == "Modération":
            addrole = discord.utils.get(server.role_hierarchy, name="Voyageur")
            await client.add_roles(member, addrole)
            await client.send_message(client.get_channel("318435538589712395"),member.mention + " est Modo sur le discord du Forum, le rôle ''Voyageur'' lui a donc été attribué")
        if role == "Gentil Admin":
            addrole = discord.utils.get(server.role_hierarchy, name="Voyageur")
            await client.add_roles(member, addrole)
            await client.send_message(client.get_channel("318435538589712395"),member.mention + " est Admin sur le discord du Forum, le rôle ''Voyageur'' lui a donc été attribué")
        if role == "Junior":
            addrole = discord.utils.get(server.role_hierarchy, name="Voyageur")
            await client.add_roles(member, addrole)
            await client.send_message(client.get_channel("318435538589712395"),member.mention + " est Junior sur le discord du Forum, le rôle ''Voyageur'' lui a donc été attribué")

async def sendlogs(em, mode):
    if mode == "flfw":
        msg = await client.send_message(client.get_channel("318428479463096322"), embed=em)
        em.set_footer(text="le: " + UTC(msg.timestamp))
        await client.delete_message(msg)
        await client.send_message(client.get_channel("318428479463096322"), embed=em)
    if mode == "flfn":
        await client.send_message(client.get_channel("318428479463096322"), embed=em)
    if mode == "rpw":
        msg = await client.send_message(client.get_channel("318435538589712395"), embed=em)
        em.set_footer(text="le: " + UTC(msg.timestamp))
        await client.delete_message(msg)
        await client.send_message(client.get_channel("318435538589712395"), embed=em)
    if mode == "rpn":
        await client.send_message(client.get_channel("318435538589712395"), embed=em)   
#########################################################################################################    
async def error(message,error,rgapi={}):
    if error == "rgapi":
        text = "Erreur lors de la requête API\n> Erreur " +str(rgapi["status"]["status_code"]) +"\n> " +rgapi["status"]["message"]
    elif error == "403":
        text = "Accès Refusé\n> discord.errors.Forbidden: FORBIDDEN (status code: 403): Missing permissions"
    elif error == "niwl":
        text = "Seuls les modérateurs , admins et moi-mêmes peuvent utiliser cette commande\n> raise niwl"
    elif error == "Keyerror":
        text = "Pseudo incorect\n> KeyError"
    elif error == "400":
        text = "Une erreur c'est produite\n> Erreur 400"
    elif error == "taverne":
        text = "Commande bloquer dans la taverne\n> raise taverne"
    elif error == "404":
        text = "Non trouvé\n> Erreur 404"
    elif error == "kikimeter":
        text = "Riot a cassé le kikimeter, il reviendra peut être plus tard"
    elif error == "presfound":
        text = str(message.author) +" s'est déjà présenté !\n> la présentation n'a pas été ajouté au GDoc"
    else:
        text = "Le mauvais dévelloppeur de ce bot a oublié de mettre un message à cette erreur"
    msg = await client.send_message(message.channel, "```diff\n- [Erreur]\n> " + text + "```")
    await client.add_reaction(msg, "❌")
    while True:
        reac = await client.wait_for_reaction("❌", message=msg)
        if reac.user != client.user:
            await client.delete_message(msg)
            raise error  
            
def getprogressbar(level, point, token):
    dicobase = {"1": 1, "2": 1800, "3": 6000, "4": 12600}
    dicomax = {"1": 1800, "2": 6000, "3": 12600, "4": 21600}
    if level == "1" or level == "2" or level == "3" or level == "4":
        pointactu = int(point) - dicobase[level]
        pointmax = dicomax[level] - dicobase[level]
        progress = int(round(pointactu / pointmax * 10))
        progressbar = "█" * (progress // 2) + "▒" * (progress % 2) + "░" * ((10 - progress) // 2)
        progressbar = " "* 5 + "*progress:* " + progressbar
        return progressbar
    if level == "5":
        dicotoken = {0: "○ ○", 1: "√ ○", 2: "√ √"}
        progressbar = dicotoken[token]
        progressbar = " "* 5 + "*progress:* " + progressbar
        return progressbar
    if level == "6":
        dicotoken = {0: "○ ○ ○", 1: "√ ○ ○", 2: "√ √ ○", 3: "√ √ √"}
        progressbar = dicotoken[token]
        progressbar = " "* 5 + "*progress:* " + progressbar
        return progressbar
    if level == "7":
        progressbar = ""
        return progressbar

def UTC(utc):
    utc = str(utc)
    annee = utc.split("-")[0]
    mois = utc.split("-")[1]
    utc = utc.split("-")[2]
    jour = utc.split(" ")[0]
    utc = utc.split(" ")[1]
    heure = utc.split(":")[0]
    heure = int(heure) + 2
    if heure == 24:
        heure = 0
        jour = int(jour) + 1
    elif heure == 25:
        heure = 1
        jour = int(jour) + 1
    minute = utc.split(":")[1]
    utc = utc.split(":")[2]
    seconde = utc.split(".")[0]
    dicomois = {"01": "Janvier", "02": "Février", "03": "Mars", "04": "Avril", "05": "Mai", "06": "Juin",
                "07": "Juillet", "08": "Août", "09": "Septembre", "10": "Octobre", "11": "Novembre", "12": "Décembre"}
    mois = dicomois[mois]
    date = str(jour) + " " + mois + " " + annee + " à " + str(heure) + ":" + minute + ":" + seconde
    return (date)

async def champion(id):
    json = await request("http://ddragon.canisback.com/latest/data/en_GB/champion.json")
    for x in json["data"].values():
        if x["key"] == str(id): return x["id"]

def member_in_whitelist(member):
    try:
        return "Modération" in [x.name for x in member.roles] or member.id == "218830582250078209" or member.id == "165422322893848576"
    except:
        return False
            
def forum():
    return client.get_server("136349076353581056")
def rp():
    return client.get_server("302447376679960576")

client.run(sys.argv[1],sys.argv[2])
