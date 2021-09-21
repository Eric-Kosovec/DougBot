from discord.ext import commands

from dougbot.core.bot import DougBot

from dougbot.extensions.tamagotchi.petHandlerLib import *
from discord import Embed


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

    def __init__(self, bot: DougBot):  # Doing the 'bot: DougBot' allows the IDE to see the methods within the bot and be able to list them, for ease of use.
        self.bot = bot

    @commands.command()
    async def checkpet(self, ctx):
        pet = PetHandler.getcurrentpet()
        if not PetHandler.isdead(pet):
            pet = PetHandler.checkpet(pet)
            if PetHandler.isdead(pet):
                pet = PetHandler.death(pet, 'Somebody didn\'t take good care of this one. Ask Papa Doug nicely and he might get you a new one.')
                PetHandler.puttorest(pet)
                await ctx.send('rip ' + pet['name'] + '. ' + pet['deathreason'])
            PetHandler.savedata(pet)
            embed = PetCommands.buildembed(pet, True, None)
            await ctx.send(embed=embed)
        else:
            await ctx.send(pet['name'] + ' is dead. ' + pet['deathreason'])

    @commands.command()
    async def feedpet(self, ctx):
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
        PetHandler.savedata(pet)
        embed = PetCommands.buildembed(pet, ableto, 'feed')
        await ctx.send(embed=embed)

    @commands.command()
    async def waterpet(self, ctx):
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
        PetHandler.savedata(pet)
        embed = PetCommands.buildembed(pet, ableto, 'water')
        await ctx.send(embed=embed)

    @commands.command()
    async def cleanpet(self, ctx):
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
        PetHandler.savedata(pet)
        embed = PetCommands.buildembed(pet, ableto, 'clean')
        await ctx.send(embed=embed)

    @commands.command()
    async def petpet(self, ctx):
        ableto = False
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
        PetHandler.savedata(pet)
        embed = PetCommands.buildembed(pet, ableto, 'pet')
        await ctx.send(embed=embed)

    @commands.command()
    async def newpet(self, ctx, name: str):
        pet = PetHandler.newpet(name)
        embed = PetCommands.buildembed(pet, True, None)
        await ctx.send(embed=embed)

    @staticmethod
    def buildembed(json_object, ableto, type):
        embed = Embed(title='<:sipsScared:819393684549533716> Name: ' + str(json_object['name']), color=0x228B22)
        embed.add_field(name='Health', value=str(json_object['currenthealth']) + '/' + str(json_object['maxhealth']), inline=True)
        embed.add_field(name='Food', value=str(json_object['food']) + '/100', inline=True)
        embed.add_field(name='Water', value=str(json_object['water']) + '/100', inline=True)
        embed.add_field(name='Cleanliness', value=str(json_object['cleanliness']) + '/100', inline=True)
        embed.add_field(name='Happiness', value=str(json_object['happiness']) + '/100', inline=True)
        if not ableto:
            ##maybe add time to this foooter
            embed.set_footer(text='Unable to ' + type + ' right now.')
        return embed


def setup(bot):
    bot.add_cog(PetCommands(bot))

