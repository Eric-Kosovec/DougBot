from dougbot.extensions.tamagotchi.petHandlerLib import *


class PetCommands:
    json_object = {
        'name': 'Doug',
        'lastchecked': '01/09/21 01:56:54',
        'type': 'bird',
        'level': 1,
        'birthdate': '01/09/21 01:56:54',
        'deathdate': '',
        'deathreason': 'Did not live past 1',
        'maxhealth': 100,
        'currenthealth': 1,
        'attack': 1,
        'defence': 1,
        'food': 0,
        'water': 0,
        'cleanliness': 0
    }

    PetHandler.newpet("stage1")
    pet = PetHandler.getcurrentpet()
    p = pet['tama'][0]
    print(p)
    #p['name'] = 'DeadDoug'

    p = PetHandler.decreasecurrenthealth(p, 3)
    print(p)
    print(PetHandler.isdead(p))
    p = PetHandler.death(p, "just too dead")
    print(p)
    print(PetHandler.checkpet(p))
    PetHandler.puttorest(p)
    PetHandler.newpet('TheRealDoug')
    graveyard = PetHandler.graveyardcheck()
    graves = graveyard['graveyard']
    for d in graves:
        print(d['name'])