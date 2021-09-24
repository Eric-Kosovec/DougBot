import json
import os
import random

from dougbot.extensions.tamagotchi.petEvent import *


class PetEventHandler:

    @staticmethod
    def walkevent(name):
        eventtype = random.randint(0, 2)
        walkevents = PetEventHandler.getwalkevents()
        if eventtype == 0:
            etype = 'good'
        if eventtype == 1:
            etype = 'bad'
        if eventtype == 2:
            etype = 'neutral'

        rand = random.randint(0, len(walkevents['goodevents']) - 1)
        typename = etype + 'events'
        eventtext = walkevents[typename][rand]['message']
        healthamount = walkevents[typename][rand]['health']
        foodamount = walkevents[typename][rand]['food']
        wateramount = walkevents[typename][rand]['water']
        cleanlinessamount = walkevents[typename][rand]['cleanliness']
        happinessamount = walkevents[typename][rand]['happiness']

        msg = 'You take ' + name + ' for a walk and ' + name + ' '
        eventtext = eventtext.replace('+name+', name)
        combinedmsg = msg + eventtext

        evnt = PetEvent(combinedmsg, etype, 0, foodamount, wateramount, cleanlinessamount, happinessamount)

        return evnt

    @staticmethod
    def getwalkevents():
        package_dir = os.path.dirname(os.path.abspath(__file__))
        thefile = os.path.join(package_dir, 'walkEvents.txt')
        with open(thefile) as json_file:
            json_object = json.load(json_file)
            json_file.close()

        return json_object
