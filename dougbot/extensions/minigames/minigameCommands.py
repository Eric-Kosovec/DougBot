import asyncio
import json
import math
import os
import random

from discord import Embed
from discord.ext import commands, tasks

from dougbot.core.bot import DougBot


class MinigameCommands(commands.Cog):

    def __init__(self, bot: DougBot):  # Doing the 'bot: DougBot' allows the IDE to see the methods within the bot and be able to list them, for ease of use.
        self.bot = bot

    ##########################RACING##############################################################################################################################
    listofracers = []
    joininground = False
    raceongoing = False

    # TODO:record wins / average round length
    # TODO:detailed win stats
    # TODO:when win react with emoji winning placement
    @commands.command()
    async def startrace(self, ctx):
        botlist = ['Shot Hottie', 'Anonymous', '( ͡° ͜ʖ ͡°)', 'TryhardTimmy', 'Doug', 'Cool Whip', 'Thunder Bunt', 'Lowercase Guy', '✧GͥOͣDͫ✧', '𝐅𝐎𝐑𝐓𝐍𝐈𝐓𝐄 GOD', '¯\_(ツ)_/¯']

        if not MinigameCommands.raceongoing:
            joinroundtimer = 15
            MinigameCommands.listofracers = []

            message = await ctx.send('The Depression races are starting! in ' + str(joinroundtimer) + 's Type !joinrace to enter!')
            # start the join race background
            joinracetask = MinigameCommands.joinracetask.start(joinroundtimer, message, ctx)
            await joinracetask
            await asyncio.sleep(2)

            # start the race
            MinigameCommands.raceongoing = True

            # adding bots if not enough players
            if len(MinigameCommands.listofracers) < 4:
                for x in range(4 - len(MinigameCommands.listofracers)):
                    rand = random.randint(0, len(botlist) - 1)
                    botname = botlist[rand]
                    if botname not in MinigameCommands.listofracers:
                        MinigameCommands.listofracers.append(botname)

            await MinigameCommands.race(MinigameCommands.listofracers, message)
            await asyncio.sleep(2)
            await ctx.message.delete()
        else:
            await ctx.message.add_reaction('<:sipsScared:819393684549533716>')
            await asyncio.sleep(2)
            await ctx.message.delete()

    @staticmethod
    async def race(listofracers, message):
        tracklength = 10
        movespeedstat = 0
        movechancestat = 0
        embed = Embed(color=0x228B22)
        raceremojilist = []
        racerpositionlist = []
        winner = ['none', 0]
        roundtimer = 0
        overtimeround = 20
        specialtraitslist = []

        # initalboardsetup
        for x, racer in enumerate(listofracers):
            # assign random emoji to racer
            selectedemojiobject = MinigameCommands.randomemoji(raceremojilist, movechancestat, movespeedstat, specialtraitslist)
            raceremojilist.append(selectedemojiobject[0])

            # update the overal move/chance stats
            movechancestat = selectedemojiobject[1]
            movespeedstat = selectedemojiobject[2]

            # update special traits list
            specialtraitslist = selectedemojiobject[3]

            # apply special traits
            if 'protection' in specialtraitslist:
                movechancestat = 0
                movespeedstat = 0

            # set racer position at starting line
            racerpositionlist.append(1)

            msgcontentline = MinigameCommands.calnumberbehind(racerpositionlist[x], tracklength) + raceremojilist[x]['emoji'] + MinigameCommands.calnumberahead(racerpositionlist[x], tracklength)

            # if it is a bot we just pass the string, if not the user object
            if type(racer) is str:
                embed.add_field(name=racer, value=msgcontentline, inline=False)
            else:
                embed.add_field(name=racer.name, value=msgcontentline, inline=False)

        await message.edit(content='Go! Go! Go!\n Round: ' + str(roundtimer) + '\nMovespeed stat: ' + str(movespeedstat) + '\nMovechance stat: ' + str(movechancestat), embed=embed)

        # racing
        while MinigameCommands.raceongoing:

            roundtimer += 1

            if roundtimer > overtimeround:
                movechancestat += 1
                movespeedstat += 1

            await message.edit(content='Round: ' + str(roundtimer) + '\nMovespeed stat: ' + str(movespeedstat) + '\nMovechance stat: ' + str(movechancestat), embed=embed)

            # reset embed
            embed = Embed(color=0x228B22)

            for x, racer in enumerate(listofracers):
                moveroll = random.uniform(0, 10)
                movechance = raceremojilist[x]['movechance'] + movechancestat
                # movechance adjustment
                if movechance < 0:
                    movechance = .1
                if moveroll <= movechance:
                    movement = random.uniform(raceremojilist[x]['minmove'], raceremojilist[x]['maxmove'] + movespeedstat)
                    # movement adjustment
                    if movement < 0:
                        movement = 0
                else:
                    movement = 0
                racerpositionlist[x] = racerpositionlist[x] + movement
                # check for race win
                if racerpositionlist[x] >= 10:
                    MinigameCommands.raceongoing = False
                    winner = racer
                    emoji = raceremojilist[x]
                msgcontentline = MinigameCommands.calnumberbehind(racerpositionlist[x], tracklength) + raceremojilist[x]['emoji'] + MinigameCommands.calnumberahead(racerpositionlist[x], tracklength)
                if type(racer) is str:
                    embed.add_field(name=racer, value=msgcontentline, inline=False)
                else:
                    embed.add_field(name=racer.name, value=msgcontentline, inline=False)

            await message.edit(embed=embed)
            await asyncio.sleep(2)

        if type(winner) is str:
            await message.edit(content='Winner: ' + winner + '\n ' + emoji['emoji'] + ': ' + emoji['quote'] + '\n \u200b', embed=None)
        else:
            await message.edit(content='Winner: ' + winner.mention + '\n ' + emoji['emoji'] + ': ' + emoji['quote'] + '\n \u200b', embed=None)
        MinigameCommands.recordstats(emoji, raceremojilist)

    @staticmethod
    @tasks.loop(seconds=1, count=1)
    async def joinracetask(joinroundtimer, message, ctx):
        MinigameCommands.joininground = True
        MinigameCommands.raceongoing = True
        await message.add_reaction('<:smug32:255496009361129483>')

        while joinroundtimer != 0:
            joinroundtimer -= 1
            await message.edit(content=('The Depression races are starting! in ' + str(joinroundtimer) + 's Click <:smug32:255496009361129483> to enter!'))
            if joinroundtimer == 0:
                await message.edit(content='Let the Sadness begin. Setting up race...')
                # need to fetch message again to get reaction list
                updatedmessage = await ctx.fetch_message(message.id)
                for reaction in updatedmessage.reactions:
                    if reaction.emoji.name == 'smug32':
                        async for user in reaction.users():
                            if user not in MinigameCommands.listofracers and user.bot is False:
                                MinigameCommands.listofracers.append(user)
                await asyncio.sleep(2)
            else:
                await asyncio.sleep(1)
        MinigameCommands.joininground = False
        await message.clear_reactions()

    @staticmethod
    def addspaces(numberofspaces):
        spacestring = ''

        for x in range(numberofspaces):
            spacestring = spacestring + ' '

        return spacestring

    @staticmethod
    def randomemoji(alreadyselected, movechancestat, movespeedstat, specialtraits):
        package_dir = os.path.dirname(os.path.abspath(__file__))
        thefile = os.path.join(package_dir, 'emojiracers.txt')

        with open(thefile) as json_file:
            json_object = json.load(json_file)
            json_file.close()

        selectuniqueemoji = True
        while selectuniqueemoji:
            selectedemoji = random.randint(0, len(json_object['emojilist']) - 1)
            selectedemojiobject = json_object['emojilist'][selectedemoji]
            if selectedemojiobject not in alreadyselected:
                selectuniqueemoji = False
                movechancestat = movechancestat + selectedemojiobject['allincreasemovechance'] + selectedemojiobject['alldecreasemovechance']
                movespeedstat = movespeedstat + selectedemojiobject['allincreasemaxmove'] + selectedemojiobject['alldecreasemaxmove']
                if selectedemojiobject['emoji'] == '<:protection:401942229943320586>':
                    specialtraits.append('protection')

        return [selectedemojiobject, movechancestat, movespeedstat, specialtraits]

    @staticmethod
    def calnumberbehind(number, tracklength):
        listofnumbers = [':one:', ':two:', ':three:', ':four:', ':five:', ':six:', ':seven:', ':eight:', ':nine:', ':checkered_flag:']
        numberbehind = math.floor(number)
        trackstring = ''

        if numberbehind > tracklength:
            numberbehind = tracklength

        for x in range(0, numberbehind - 1):
            trackstring = trackstring + listofnumbers[x]
        return trackstring

    @staticmethod
    def calnumberahead(number, tracklength):
        listofnumbers = [':one:', ':two:', ':three:', ':four:', ':five:', ':six:', ':seven:', ':eight:', ':nine:', ':checkered_flag:']
        numberahead = tracklength - math.floor(number)
        trackstring = ''

        if numberahead > tracklength:
            numberahead = tracklength

        start = tracklength - numberahead
        for x in range(start, tracklength):
            trackstring = trackstring + listofnumbers[x]
        return trackstring

    @staticmethod
    def recordstats(winnerobject, listofraceremojis):
        package_dir = os.path.dirname(os.path.abspath(__file__))
        thefile = os.path.join(package_dir, 'emojiracers.txt')

        with open(thefile) as json_file:
            json_object = json.load(json_file)
            json_file.close()

        emojilist = json_object['emojilist']

        # add wins
        for x, emoji in enumerate(emojilist):
            if emoji['emoji'] == winnerobject['emoji']:
                emojilist[x]['wins'] += 1
            for raceremoji in listofraceremojis:
                if emoji['emoji'] == raceremoji['emoji']:
                    emojilist[x]['totalraces'] += 1

        json_object['emojilist'] = emojilist
        with open(thefile, 'w') as outfile:
            json.dump(json_object, outfile, indent=2)
            outfile.close()

    @commands.command()
    async def racerinfo(self, ctx):
        embed = Embed(color=0x228B22)
        package_dir = os.path.dirname(os.path.abspath(__file__))
        thefile = os.path.join(package_dir, 'emojiracers.txt')
        with open(thefile) as json_file:
            json_object = json.load(json_file)
            json_file.close()

        emojilist = json_object['emojilist']

        for emoji in emojilist:
            embed.add_field(name=emoji['emoji'], value='Won: ' + str(emoji['wins']) + '\nLoss: ' + str((emoji['totalraces'] - emoji['wins'])) + '\nWin%: ' + str(math.ceil((emoji['wins'] / emoji['totalraces']) * 100)), inline=True)
        await ctx.send(embed=embed)
    ############################################################################################################################################################

    #########################################################SLOTS##############################################################################################
    @commands.command()
    async def slots(self, ctx):
        emojilist = ['<:sipsScared:819393684549533716>', '<:passMan:256140704806338560>', '<:fireball:267121761173110784>', '<:gabeN:255489512543748097>', '<:doug:337020649753018368>', '<:ripley:532377971009257492> ', '<:alex:338163624063533056>']
        slotboard = []
        slotembed = Embed(title='SadDoug Slots', color=0xa2afb8)
        for x in range(9):
            slotboard.append(random.choice(emojilist))
        slotembed.add_field(name='\u200b', value=':stop_button:' + slotboard[0] + ':eight_pointed_black_star::eight_pointed_black_star::stop_button:\n :arrow_forward:' + slotboard[3] + ':eight_pointed_black_star::eight_pointed_black_star::arrow_backward:\n:stop_button:' + slotboard[6] + ':eight_pointed_black_star::eight_pointed_black_star::stop_button:', inline=False)
        message = await ctx.send(embed=slotembed)
        await asyncio.sleep(1)
        slotembed = Embed(title='SadDoug Slots', color=0xa2afb8)
        slotembed.add_field(name='\u200b', value=':stop_button:' + slotboard[0] + ' ' + slotboard[1] + ':eight_pointed_black_star:' + ':stop_button:\n :arrow_forward:' + slotboard[3] + ' ' + slotboard[4] + ':eight_pointed_black_star:' + ':arrow_backward:\n:stop_button:' + slotboard[6] + ' ' + slotboard[7] + ':eight_pointed_black_star:' + ':stop_button:', inline=False)
        await message.edit(embed=slotembed)
        await asyncio.sleep(1)
        slotembed = Embed(title='SadDoug Slots', color=0xa2afb8)
        slotembed.add_field(name='\u200b', value=':stop_button:' + slotboard[0] + ' ' + slotboard[1] + ' ' + slotboard[2] + ':stop_button:\n :arrow_forward:' + slotboard[3] + ' ' + slotboard[4] + ' ' + slotboard[5] + ':arrow_backward:\n:stop_button:' + slotboard[6] + ' ' + slotboard[7] + ' ' + slotboard[8] + ':stop_button:', inline=False)
        await message.edit(embed=slotembed)
        if slotboard[3] is slotboard[4] is slotboard[5]:
            await message.edit(content='Winner')
        else:
            await message.edit(content='Try again')
    ############################################################################################################################################################

def setup(bot):
    bot.add_cog(MinigameCommands(bot))
