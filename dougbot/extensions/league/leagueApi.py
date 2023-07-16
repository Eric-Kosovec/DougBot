import json
import os
import time
import math
import re

import PIL.Image
import discord
from supabase import client
from supabase.client import Client
from dougbot import config

from dougbot.config import EXTENSION_RESOURCES_DIR
from nextcord import Embed
from nextcord.ext import commands, tasks
from dougbot.core.bot import DougBot
from riotwatcher import LolWatcher, ApiError


# golbal variables
api_key = 'RGAPI-f73d8cdb-07b2-455b-84ce-bdfb670f2d73'
watcher = LolWatcher(api_key)
my_region = 'na1'
clash_team_capitan_summoner_name = 'Dimkaz'
dimkaz_discord_mention = '<@236657245796958208>'
opgg_lookup_url = 'https://www.op.gg/summoners/na/'


def connect() -> Client:
    configs = config.get_configuration()
    return client.create_client(configs.db_url, configs.db_api_key)


class LeagueApi(commands.Cog):

    def __init__(self, bot: DougBot):
        self.bot = bot

    @commands.command()
    async def getplayer(self, ctx, summonername:str ):
        leagueprofiledir = os.path.join(EXTENSION_RESOURCES_DIR, 'leagueapi', '13.5.1', 'img', 'profileicon')
        summoner = watcher.summoner.by_name(my_region, summonername)
        summonericon = os.path.join(leagueprofiledir, str(summoner["profileIconId"]) + ".png")
        summonerRank5v5 = watcher.league.by_summoner(my_region, summoner["id"])
        print(summoner)
        print(summonerRank5v5)
        embed = Embed(title=summoner["name"], color=0x228B22, )
        file = discord.File(summonericon, filename="image.png")
        embed.set_thumbnail(url="attachment://image.png")
        embed.add_field(name='Level:', value=summoner["summonerLevel"], inline=True)
        winpercentage = math.floor((summonerRank5v5[0]["wins"] / (summonerRank5v5[0]["wins"] + summonerRank5v5[0]["losses"])) * 100)
        embed.add_field(name='Ranked Solo:', value=str(summonerRank5v5[0]["tier"]) + ' ' + str(summonerRank5v5[0]["rank"]) + ' ' + str(summonerRank5v5[0]["leaguePoints"]) + " LP" + ' ' + str(winpercentage) + '% WR',inline=True)
        await ctx.send(embed=embed, file=file)

    @commands.command()
    async def getclashteam(self, ctx, summonername:str):
        summoner = watcher.summoner.by_name(my_region, summonername)
        team = watcher.clash.by_summoner(my_region, summoner["id"])
        await ctx.send(str(team))

    @commands.command()
    async def getclashteaminfo(self, ctx, summonername:str):
        summoner = watcher.summoner.by_name(my_region, summonername)
        indvteam = watcher.clash.by_summoner(my_region, summoner["id"])
        teamid = indvteam[0]["teamId"]
        team = watcher.clash.by_team(my_region,str(teamid))

        embed = Embed(title=team["name"] + " " + team["abbreviation"], color=0x228B22, )
        teamplayerlist = team["players"]
        for player in teamplayerlist:
            summoner = watcher.summoner.by_id(my_region, player["summonerId"])
            embed.add_field(name= summoner["name"] + '-' + player["position"], value=opgg_lookup_url + str(summoner["name"]).replace(' ', '%20'), inline=True)
        await ctx.send(embed=embed)


    @staticmethod
    def daysort(clashtime):
        return clashtime[0]

    @commands.command()
    async def getnextclash(self, ctx):
        teamtier = watcher.clash.by_team(my_region, '4532047')["tier"]
        if teamtier >= 3:
            lesstime = ((teamtier - 1) * 45 * 60) + (30 * 60)
        else:
            lesstime = teamtier * 45 * 60
        nextclash = watcher.clash.tournaments(my_region)
        times = []
        for x in nextclash:
            times.append([str(x["nameKeySecondary"]), str(math.floor((x["schedule"][0]["registrationTime"] / 1000) - (86400 * 5))), str(math.floor(x["schedule"][0]["startTime"] / 1000) - lesstime), str(x["nameKey"])])
        times.sort(key=self.daysort)
        for x in times:
            if int(x[1]) > math.floor(time.time()):
                day = re.findall(r'\d+', x[0])
                if int(day[0])%2 == 0:
                    await ctx.send("The next clash starts at <t:" + x[2] + ":f>")
                else:
                    await ctx.send(dimkaz_discord_mention + " The next clash registration time is <t:" + x[1] + ":D> and the first game starts at <t:" + x[2] + ":f>")
                break

    @commands.command()
    async def getnextclashall(self, ctx):
        teamtier = watcher.clash.by_team(my_region, '4532047')["tier"]
        if teamtier >= 3:
            lesstime = ((teamtier - 1) * 45 * 60) + (30 * 60)
        else:
            lesstime = teamtier * 45 * 60
        nextclash = watcher.clash.tournaments(my_region)
        times = []
        for x in nextclash:
            times.append([str(x["nameKeySecondary"]), str(math.floor((x["schedule"][0]["registrationTime"] / 1000) - (86400 * 5))), str(math.floor(x["schedule"][0]["startTime"] / 1000) - lesstime), str(x["nameKey"])])
        times.sort(key=self.daysort)
        print(times)
        for x in times:
            day = re.findall(r'\d+', x[0])
            if int(day[0]) % 2 == 0:
                await ctx.send("starts at <t:" + x[2] + ":f>")
            else:
                await ctx.send("The next clash registration time is <t:" + x[1] + ":D> and starts at <t:" + x[2] + ":f>")

    @commands.command()
    async def getpastmatches(self, ctx, summonername:str, numberofgames:int, matchtype:str):
        summoner = watcher.summoner.by_name(my_region, summonername)
        db_client = None

        try:
            db_client = connect()
            data = db_client.table('lol_api_users').select("*").eq('puuid',summoner["puuid"]).execute()
            if len(data.data) == 0:
                db_client.table('lol_api_users').insert({'puuid':summoner["puuid"]}).execute()
            matchidlist = watcher.match.matchlist_by_puuid(my_region, summoner["puuid"], None, numberofgames, None, matchtype, None, None)
            summonerpuuid = str('(\"' + summoner['puuid'] + '\")')
            summonerdbiddata = db_client.table('lol_api_users').select('id').filter('puuid', 'in', summonerpuuid).execute()
            summonerdbid = summonerdbiddata.data[0]['id']
            for match in matchidlist:
                matchidstring = str('(\"' + match+ '\")')
                data = db_client.table('lol_api_game_data').select("match_id").filter('match_id', 'in', matchidstring).execute()
                if len(data.data) == 0:
                    matchdata = watcher.match.by_id(my_region, match)
                    db_client.table('lol_api_game_data').insert({'lol_api_user_id': summonerdbid, 'match_id': match, 'match_data': matchdata}).execute()
        except Exception:
            print("Error with finding user")
        finally:
            if db_client:
                db_client.auth.close()

    @commands.command()
    async def processpastmatches(self, ctx, summonername:str):
        summoner = watcher.summoner.by_name(my_region, summonername)
        db_client = None
        try:
            db_client = connect()
            data = db_client.table('lol_api_users').select("id").eq('puuid',summoner["puuid"]).execute()
            print(data.data)
            print(data.data[0]["id"])
            if len(data.data) == 0:
                print("User not found")
            matchlist = db_client.table('lol_api_game_data').select("match_id").eq('lol_api_user_id', int(data.data[0]['id'])).execute()

            gamecount = 0
            wincount = 0
            losscount = 0
            roledick = dict()
            sumdick = dict()
            champdick = dict()
            mythicitemdick = dict()


            for matchid in matchlist.data:
                playermatchinfo = None
                matchdata = db_client.table('lol_api_game_data').select("match_data").eq('match_id', matchid['match_id']).execute()
                participantslist = matchdata.data[0]['match_data']['info']['participants']
                for playerinfo in participantslist:
                    if playerinfo["puuid"] == summoner["puuid"]:
                        playermatchinfo = playerinfo
                        break
                gamecount+=1
                if bool(playermatchinfo['win']):
                    wincount+=1
                else:
                    losscount+=1
                if playermatchinfo['role'] in roledick.keys():
                    roledick[playermatchinfo['role']]+=1
                else:
                    roledick[playermatchinfo['role']] = 1
                if playermatchinfo['summoner1Id'] in sumdick.keys():
                    sumdick[playermatchinfo['summoner1Id']]+=1
                else:
                    sumdick[playermatchinfo['summoner1Id']] = 1
                if playermatchinfo['summoner2Id'] in sumdick.keys():
                    sumdick[playermatchinfo['summoner2Id']]+=1
                else:
                    sumdick[playermatchinfo['summoner2Id']] = 1
                if playermatchinfo['championName'] in champdick.keys():
                    if bool(playermatchinfo['win']):
                        champdick[playermatchinfo['championName']]['win'] += 1
                    else:
                        champdick[playermatchinfo['championName']]['loss'] += 1
                else:
                    if bool(playermatchinfo['win']):
                        champdick[playermatchinfo['championName']] = {'win': 1,'loss': 0}
                    else:
                        champdick[playermatchinfo['championName']] = {'win': 0,'loss': 1}
                print(matchid['match_id'])
                print(gamecount)
                print(wincount)
                print(losscount)
                print(roledick)
                print(sumdick)
                print(champdick)
                print(mythicitemdick)
            bestchamp = ''
            bestwin = 0
            bestloss = 0
            bestper = 0

            for k, v in champdick.items():
                if (int(v['win']) / (int(v['win'])+int(v['loss']))) > bestper and (int(v['win'])+int(v['loss'])) > (bestwin + bestloss):
                    bestchamp = k
                    bestwin = int(v['win'])
                    bestloss = int(v['loss'])
                    bestper = (int(v['win']) / (int(v['win'])+int(v['loss'])))
            print('Best Champ: ' + bestchamp)
            print('Win: ' + str(bestwin))
            print('Loss: ' + str(bestloss))
            print('Per: ' + str(math.floor(bestper * 100)))
            embed = Embed(title=summoner['name'], color=0x228B22, )
            embed.add_field(name="Best Champ", value=bestchamp)
            embed.add_field(name="Win%: ", value=str(math.floor(bestper * 100)))
            embed.add_field(name="Total Games: ", value=str(bestwin+bestloss))

            await ctx.send(embed=embed)


        except Exception:
            print("error processing matches")
        finally:
            if db_client:
                db_client.auth.close()

def setup(bot):
    bot.add_cog(LeagueApi(bot))