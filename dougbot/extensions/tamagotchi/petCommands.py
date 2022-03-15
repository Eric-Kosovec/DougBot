from nextcord import Embed
from nextcord import User
from nextcord.ext import commands

from dougbot.core.bot import DougBot
from dougbot.extensions.tamagotchi.petEventHandlerLib import *
from dougbot.extensions.tamagotchi.petHandlerLib import *


class PetCommands(commands.Cog):
    json_object = {
        'name': 'Doug',
        'lastchecked': '9/19/21 01:00:00',
        'type': 'bird',
        'level': 1,
        'birthdate': '9/19/21 01:00:00',
        'deathdate': '',
        'deathreason': '',
        'maxhealth': 100,
        'currenthealth': 50,
        'attack': 1,
        'defence': 1,
        'happiness': 50,
        'lastpet': '9/19/21 01:00:00',
        'food': 50,
        'lastfeed': '9/19/21 01:00:00',
        'water': 50,
        'lastwatered': '9/19/21 01:00:00',
        'cleanliness': 50,
        'lastcleaned': '9/19/21 01:00:00'
    }

    def __init__(self, bot: DougBot):
        self.bot = bot

    @commands.command()
    async def checkpet(self, ctx):
        pet = PetHandler.getcurrentpet()
        if not PetHandler.isdead(pet):
            pet = PetHandler.checkpet(pet)
            if PetHandler.isdead(pet):
                pet = PetHandler.death(pet, "Somebody didn't take good care of this one. Ask Papa Doug nicely and he might get you a new one.")
                PetHandler.puttorest(pet)
                await ctx.send('rip ' + pet['name'] + '. ' + pet['deathreason'])
            PetHandler.savedata(pet)
            embed = PetCommands.buildembed(pet, True, None)
            await ctx.send(embed=embed)
        else:
            await ctx.send(pet['name'] + ' is dead. ' + pet['deathreason'])

    @commands.command()
    async def feedpet(self, ctx):
        user = ctx.message.author
        ableto = True
        pet = PetHandler.getcurrentpet()
        currentdate = datetime.datetime.now()
        foodlastdate = datetime.datetime.strptime(pet['lastfeed'], '%m/%d/%y %H:%M:%S')
        fooddelta = currentdate - foodlastdate
        foodhourspassed = math.floor((fooddelta.days * 24) + (fooddelta.seconds / 3600))
        if foodhourspassed > 1:
            pet = PetHandler.feed(pet, 20)
        else:
            ableto = False
        pet = PetHandler.checkpet(pet)
        pet = PetHandler.favorability(pet, user.id, 1)
        PetHandler.savedata(pet)
        embed = PetCommands.buildembed(pet, ableto, 'feed')
        await ctx.send(embed=embed)

    @commands.command()
    async def waterpet(self, ctx):
        user = ctx.message.author
        ableto = True
        pet = PetHandler.getcurrentpet()
        currentdate = datetime.datetime.now()
        waterlastdate = datetime.datetime.strptime(pet['lastwatered'], '%m/%d/%y %H:%M:%S')
        waterdelta = currentdate - waterlastdate
        waterhourspassed = math.floor((waterdelta.days * 24) + (waterdelta.seconds / 3600))
        if waterhourspassed > 1:
            pet = PetHandler.water(pet, 20)
        else:
            ableto = False
        pet = PetHandler.checkpet(pet)
        pet = PetHandler.favorability(pet, user.id, 1)
        PetHandler.savedata(pet)
        embed = PetCommands.buildembed(pet, ableto, 'water')
        await ctx.send(embed=embed)

    @commands.command()
    async def cleanpet(self, ctx):
        user = ctx.message.author
        ableto = True
        pet = PetHandler.getcurrentpet()
        currentdate = datetime.datetime.now()
        cleanlastdate = datetime.datetime.strptime(pet['lastcleaned'], '%m/%d/%y %H:%M:%S')
        cleandelta = currentdate - cleanlastdate
        cleanhourspassed = math.floor((cleandelta.days * 24) + (cleandelta.seconds / 3600))
        if cleanhourspassed > 1:
            pet = PetHandler.clean(pet, 20)
        else:
            ableto = False
        pet = PetHandler.checkpet(pet)
        pet = PetHandler.favorability(pet, user.id, 1)
        PetHandler.savedata(pet)
        embed = PetCommands.buildembed(pet, ableto, 'clean')
        await ctx.send(embed=embed)

    @commands.command()
    async def petpet(self, ctx):
        user = ctx.message.author
        ableto = True
        pet = PetHandler.getcurrentpet()
        currentdate = datetime.datetime.now()
        petlastdate = datetime.datetime.strptime(pet['lastpet'], '%m/%d/%y %H:%M:%S')
        petdelta = currentdate - petlastdate
        pethourspassed = math.floor((petdelta.days * 24) + (petdelta.seconds / 3600))
        if pethourspassed > 1:
            pet = PetHandler.happy(pet, 20)
        else:
            ableto = False
        pet = PetHandler.checkpet(pet)
        pet = PetHandler.favorability(pet, user.id, 1)
        PetHandler.savedata(pet)
        embed = PetCommands.buildembed(pet, ableto, 'pet')
        await ctx.send(embed=embed)

    @commands.command()
    async def careforpet(self, ctx):
        user = ctx.message.author
        ableto = True
        type = []
        typestr = ''
        pet = PetHandler.getcurrentpet()
        currentdate = datetime.datetime.now()
        foodlastdate = datetime.datetime.strptime(pet['lastfeed'], '%m/%d/%y %H:%M:%S')
        waterlastdate = datetime.datetime.strptime(pet['lastwatered'], '%m/%d/%y %H:%M:%S')
        cleanlastdate = datetime.datetime.strptime(pet['lastcleaned'], '%m/%d/%y %H:%M:%S')
        petlastdate = datetime.datetime.strptime(pet['lastpet'], '%m/%d/%y %H:%M:%S')
        fooddelta = currentdate - foodlastdate
        waterdelta = currentdate - waterlastdate
        cleandelta = currentdate - cleanlastdate
        petdelta = currentdate - petlastdate
        foodhourspassed = math.floor((fooddelta.days * 24) + (fooddelta.seconds / 3600))
        waterhourspassed = math.floor((waterdelta.days * 24) + (waterdelta.seconds / 3600))
        cleanhourspassed = math.floor((cleandelta.days * 24) + (cleandelta.seconds / 3600))
        pethourspassed = math.floor((petdelta.days * 24) + (petdelta.seconds / 3600))
        if foodhourspassed > 1:
            pet = PetHandler.feed(pet, 20)
        else:
            ableto = False
            type.append('feed')
        if waterhourspassed > 1:
            pet = PetHandler.water(pet, 20)
        else:
            ableto = False
            type.append('water')
        if cleanhourspassed > 1:
            pet = PetHandler.clean(pet, 20)
        else:
            ableto = False
            type.append('clean')
        if pethourspassed > 1:
            pet = PetHandler.happy(pet, 20)
        else:
            ableto = False
            type.append('pet')

        for idx, val in enumerate(type):
            if len(type) == 1:
                typestr = type[idx]
                break
            if idx == (len(type) - 1) and idx != 0:
                typestr = typestr + 'or ' + type[idx]
            else:
                typestr = typestr + type[idx] + ', '
        pet = PetHandler.checkpet(pet)
        pet = PetHandler.favorability(pet, user.id, 1)
        PetHandler.savedata(pet)
        embed = PetCommands.buildembed(pet, ableto, typestr)
        await ctx.send(embed=embed)

    @commands.command()
    async def newpet(self, ctx, name: str):
        pet = PetHandler.newpet(name)
        embed = PetCommands.buildembed(pet, True, None)
        await ctx.send(embed=embed)

    @commands.command()
    async def walkpet(self, ctx):
        pet = PetHandler.getcurrentpet()
        evnt = PetEventHandler.walkevent(pet['name'])
        pet = PetHandler.feed(pet, evnt.food)
        pet = PetHandler.water(pet, evnt.water)
        pet = PetHandler.clean(pet, evnt.cleanliness)
        pet = PetHandler.happy(pet, evnt.happiness)
        pet = PetHandler.checkpet(pet)
        PetHandler.savedata(pet)
        if evnt.type == 'good':
            PetHandler.savedata(pet)
            await ctx.send('<:mushWalk:255486412403638274> ' + evnt.text)
            embed = PetCommands.buildembed(pet, True, None)
            await ctx.send(embed=embed)
        if evnt.type == 'bad':
            await ctx.send(':skull: ' + evnt.text)
            embed = PetCommands.buildembed(pet, True, None)
            await ctx.send(embed=embed)
        if evnt.type == 'neutral':
            await ctx.send(':man_shrugging: ' + evnt.text)
            embed = PetCommands.buildembed(pet, True, None)
            await ctx.send(embed=embed)

    @commands.command()
    async def checktime(self, ctx):
        pet = PetHandler.getcurrentpet()
        embed = Embed(title=':motorized_wheelchair: Name: ' + str(pet['name'] + ' :motorized_wheelchair:'), color=0x228B22)
        embed.add_field(name='Last Checked', value=str(pet['lastchecked']), inline=True)
        embed.add_field(name='Last Fed', value=str(pet['lastfeed']), inline=True)
        embed.add_field(name='Last Watered', value=str(pet['lastwatered']), inline=True)
        embed.add_field(name='Last Cleaned', value=str(pet['lastcleaned']), inline=True)
        embed.add_field(name='Last Pet', value=str(pet['lastpet']), inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    async def checkfav(self, ctx):
        try:
            pet = PetHandler.getcurrentpet()
            user = ctx.message.author
            calfav = PetHandler.getfavorability(pet, user.id)
            quote = PetHandler.getfavorablilityquote(calfav)
            await ctx.send(str(user.mention) + ', favorability is ' + str(calfav) + ' ' + str(pet['name']) + ' ' + quote)
        except KeyError as e:
            await ctx.send(str(user.mention) + ', has never interacted with' + str(pet['name']) + '.')

    @commands.command()
    async def fav(self, ctx, user: User):
        try:
            pet = PetHandler.getcurrentpet()
            user = user
            calfav = PetHandler.getfavorability(pet, user.id)
            quote = PetHandler.getfavorablilityquote(calfav)
            await ctx.send(str(user.mention) + ', favorability is ' + str(calfav) + ' ' + str(pet['name']) + ' ' + quote)
        except KeyError as e:
            await ctx.send(str(user.mention) + ', has never interacted with ' + str(pet['name']) + '.')

    @commands.command()
    async def mostfav(self, ctx):
        try:
            pet = PetHandler.getcurrentpet()
            fav = PetHandler.mostfavoriate(pet)
            user = await PetCommands.getdiscorduserinfo(ctx, fav[0])
            await ctx.send(str(user.mention) + ' is ' + str(pet['name']) + '\'s favorite person and has a favorability of ' + str(fav[1]) + '!')
        except TypeError as e:
            await ctx.send('No one has ever interacted with' + str(pet['name']) + '. Sad really...')

    @commands.command()
    async def leastfav(self, ctx):
        try:
            pet = PetHandler.getcurrentpet()
            fav = PetHandler.leastfavorite(pet)
            user = await PetCommands.getdiscorduserinfo(ctx, fav[0])
            await ctx.send(str(user.mention) + ' is ' + str(pet['name']) + '\'s least favorite person and has a favorability of ' + str(fav[1]) + '...')
        except TypeError as e:
            await ctx.send('No one has ever interacted with' + str(pet['name']) + '. Sad really...')

    @commands.command()
    async def checkinteractions(self, ctx):
        try:
            pet = PetHandler.getcurrentpet()
            user = ctx.message.author
            intercount = PetHandler.getinteractioncount(pet, user.id)
            await ctx.send(str(user.mention) + ', interacted with ' + str(pet['name']) + ' ' + str(intercount) + ' times.')
        except KeyError as e:
            await ctx.send(str(user.mention) + ', has never interacted with' + str(pet['name']) + '.')

    @commands.command()
    async def interactions(self, ctx, user: User):
        try:
            pet = PetHandler.getcurrentpet()
            user = user
            intercount = PetHandler.getinteractioncount(pet, user.id)
            await ctx.send(str(user.mention) + ', interacted with ' + str(pet['name']) + ' ' + str(intercount) + ' times.')
        except KeyError as e:
            await ctx.send(str(user.mention) + ', has never interacted with ' + str(pet['name']) + '.')

    @commands.command()
    async def mostinteractions(self, ctx):
        try:
            pet = PetHandler.getcurrentpet()
            intercount = PetHandler.mostinteractions(pet)
            user = await PetCommands.getdiscorduserinfo(ctx, intercount[0])
            await ctx.send(str(user.mention) + ' has interacted with ' + str(pet['name']) + 'the most with ' + str(intercount[1]) + ' interactions!')
        except TypeError as e:
            await ctx.send('No one has ever interacted with' + str(pet['name']) + '. Sad really...')

    @commands.command()
    async def leastinteractions(self, ctx):
        try:
            pet = PetHandler.getcurrentpet()
            intercount = PetHandler.leastinteractions(pet)
            user = await PetCommands.getdiscorduserinfo(ctx, intercount[0])
            await ctx.send(str(user.mention) + ' has interacted with ' + str(pet['name']) + 'the least with' + str(intercount[1]) + ' interactions...')
        except TypeError as e:
            await ctx.send('No one has ever interacted with' + str(pet['name']) + '. Sad really...')

    @commands.command()
    async def detailedstats(self, ctx):
        pet = PetHandler.getcurrentpet()
        embed = Embed(title='<:clownS:819397835636080640> Name: ' + str(pet['name'] + ' <:clownS:819397835636080640>'), color=0x228B22)
        embed.add_field(name='Health', value=str(pet['currenthealth']) + '/' + str(pet['maxhealth']), inline=True)
        embed.add_field(name='Food', value=str(pet['food']) + '/100', inline=True)
        embed.add_field(name='Water', value=str(pet['water']) + '/100', inline=True)
        embed.add_field(name='Cleanliness', value=str(pet['cleanliness']) + '/100', inline=True)
        embed.add_field(name='Happiness', value=str(pet['happiness']) + '/100', inline=True)

        embed.add_field(name='Birthday', value=str(pet['birthdate']), inline=True)
        embed.add_field(name='Last Checked', value=str(pet['lastchecked']), inline=True)
        embed.add_field(name='Last Fed', value=str(pet['lastfeed']), inline=True)
        embed.add_field(name='Last Watered', value=str(pet['lastwatered']), inline=True)
        embed.add_field(name='Last Cleaned', value=str(pet['lastcleaned']), inline=True)
        embed.add_field(name='Last Pet', value=str(pet['lastpet']), inline=True)

        embed.add_field(name='Type:', value=str(pet['type']), inline=True)
        embed.add_field(name='Level', value=str(pet['level']), inline=True)
        embed.add_field(name='Attack', value=str(pet['attack']), inline=True)
        embed.add_field(name='Defence', value=str(pet['defence']), inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    async def test(self, ctx):
        user = ctx.message.author
        pet = PetHandler.getcurrentpet()
        pet = PetHandler.favorability(pet, user.id, 1)
        PetHandler.savedata(pet)

    @staticmethod
    def buildembed(json_object, ableto, type):
        embed = Embed(title='<:sipsScared:819393684549533716> Name: ' + str(json_object['name']), color=0x228B22)
        embed.add_field(name='Health', value=str(json_object['currenthealth']) + '/' + str(json_object['maxhealth']), inline=True)
        embed.add_field(name='Food', value=str(json_object['food']) + '/100', inline=True)
        embed.add_field(name='Water', value=str(json_object['water']) + '/100', inline=True)
        embed.add_field(name='Cleanliness', value=str(json_object['cleanliness']) + '/100', inline=True)
        embed.add_field(name='Happiness', value=str(json_object['happiness']) + '/100', inline=True)
        if not ableto:
            embed.set_footer(text='Unable to ' + type + ' right now.')
        return embed

    @staticmethod
    async def getdiscorduserinfo(ctx, userid: int):
        if userid != -1:
            user = await ctx.guild.fetch_member(userid)
        else:
            raise TypeError
        return user

    @commands.command()
    async def getdiscorduser(self, ctx, userid: int):
        user = await ctx.guild.fetch_member(userid)
        await ctx.send("This person is " + user.display_name + ' and joined ' + user.guild.name + ' at ' + str(user.joined_at))

    @commands.command()
    async def di(self, ctx):
        user = ctx.message.author
        await ctx.send("Your user id is " + str(user.id) + '. Your name is ' + str(user.mention) + '.')


def setup(bot):
    bot.add_cog(PetCommands(bot))
