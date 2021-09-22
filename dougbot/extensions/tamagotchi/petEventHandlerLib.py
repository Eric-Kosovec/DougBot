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
            rand = random.randint(0, len(walkevents['goodevents']) - 1)
            eventtext = walkevents['goodevents'][rand]['message']
            type = 'good'
            foodamount = random.randint(0, 5)
            wateramount = random.randint(0, 5)
            cleanlinessamount = random.randint(0, 5)
            happinessamount = random.randint(0, 5)
        if eventtype == 1:
            rand = random.randint(0, len(walkevents['badevents']) - 1)
            eventtext = walkevents['badevents'][rand]['message']
            type = 'bad'
            foodamount = -random.randint(0, 5)
            wateramount = -random.randint(0, 5)
            cleanlinessamount = -random.randint(0, 5)
            happinessamount = -random.randint(0, 5)
        if eventtype == 2:
            rand = random.randint(0, len(walkevents['neutralevents']) - 1)
            eventtext = walkevents['neutralevents'][rand]['message']
            type = 'neutral'
            foodamount = 0
            wateramount = 0
            cleanlinessamount = 0
            happinessamount = 0

        msg = 'You take ' + name + ' for a walk and ' + name + ' '
        eventtext.replace("+name+", name)
        combinedmsg = msg + eventtext

        evnt = PetEvent(combinedmsg, type, 0, foodamount, wateramount, cleanlinessamount, happinessamount)

        return evnt

    @staticmethod
    def getwalkevents():
        package_dir = os.path.dirname(os.path.abspath(__file__))
        thefile = os.path.join(package_dir, 'walkEvents.txt')
        with open(thefile) as json_file:
            json_object = json.load(json_file)
            json_file.close()

        return json_object
