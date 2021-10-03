import json
import math
import os
import datetime


class PetHandler:

    @staticmethod
    def savedata(json_object):
        thefile = os.path.join(os.path.dirname(__file__), 'currentPetData.txt')

        json_objects = {'tama': []}
        json_objects['tama'].append(json_object)

        with open(thefile, 'w') as outfile:
            json.dump(json_objects, outfile)
            outfile.close()

    @staticmethod
    def getcurrentpet():
        package_dir = os.path.dirname(os.path.abspath(__file__))
        thefile = os.path.join(package_dir, 'currentPetData.txt')
        with open(thefile) as json_file:
            json_object = json.load(json_file)
            json_file.close()

        pet = json_object['tama'][0]
        return pet

    @staticmethod
    def currenthealth(json_object, amount):
        maxhealth = json_object['maxhealth']
        currenthealth = json_object['currenthealth']
        if amount > 0:
            if maxhealth < (currenthealth + amount):
                json_object['currenthealth'] = maxhealth
            else:
                json_object['currenthealth'] = currenthealth + amount
        if amount < 0:
            if 0 > (currenthealth + amount):
                json_object['currenthealth'] = 0
            else:
                json_object['currenthealth'] = currenthealth + amount

        return json_object

    @staticmethod
    def feed(json_object, amount):
        currentamount = json_object['food']
        if amount > 0:
            if 100 < (currentamount + amount):
                json_object['food'] = 100
            else:
                json_object['food'] = currentamount + amount
            json_object['lastfeed'] = datetime.datetime.now().strftime('%m/%d/%y %H:%M:%S')
        if amount < 0:
            if 0 > (currentamount + amount):
                json_object['food'] = 0
            else:
                json_object['food'] = currentamount + amount
        return json_object

    @staticmethod
    def water(json_object, amount):
        currentamount = json_object['water']
        if amount > 0:
            if 100 < (currentamount + amount):
                json_object['water'] = 100
            else:
                json_object['water'] = currentamount + amount
            json_object['lastwatered'] = datetime.datetime.now().strftime('%m/%d/%y %H:%M:%S')
        if amount < 0:
            if 0 > (currentamount + amount):
                json_object['water'] = 0
            else:
                json_object['water'] = currentamount + amount

        return json_object

    @staticmethod
    def clean(json_object, amount):
        currentamount = json_object['cleanliness']
        if amount > 0:
            if 100 < (currentamount + amount):
                json_object['cleanliness'] = 100
            else:
                json_object['cleanliness'] = currentamount + amount
            json_object['lastcleaned'] = datetime.datetime.now().strftime('%m/%d/%y %H:%M:%S')
        if amount < 0:
            if 0 > (currentamount + amount):
                json_object['cleanliness'] = 0
            else:
                json_object['cleanliness'] = currentamount + amount

        return json_object

    @staticmethod
    def happy(json_object, amount):
        currentamount = json_object['happiness']
        if amount > 0:
            if 100 < (currentamount + amount):
                json_object['happiness'] = 100
            else:
                json_object['happiness'] = currentamount + amount
            json_object['lastpet'] = datetime.datetime.now().strftime('%m/%d/%y %H:%M:%S')
        if amount < 0:
            if 0 > (currentamount + amount):
                json_object['happiness'] = 0
            else:
                json_object['happiness'] = currentamount + amount

        return json_object

    @staticmethod
    def isdead(json_object):
        if json_object['currenthealth'] == 0:
            return True
        else:
            return False

    @staticmethod
    def death(json_object, reason):
        json_object['deathreason'] = reason
        json_object['deathdate'] = datetime.datetime.now().strftime('%m/%d/%y %H:%M:%S')

        return json_object

    @staticmethod
    def checkpet(json_object):
        currentdate = datetime.datetime.now()
        lastdate = datetime.datetime.strptime(json_object['lastchecked'], '%m/%d/%y %H:%M:%S')
        foodlastdate = datetime.datetime.strptime(json_object['lastfeed'], '%m/%d/%y %H:%M:%S')
        waterlastdate = datetime.datetime.strptime(json_object['lastwatered'], '%m/%d/%y %H:%M:%S')
        cleanlastdate = datetime.datetime.strptime(json_object['lastcleaned'], '%m/%d/%y %H:%M:%S')

        delta = currentdate - lastdate
        fooddelta = currentdate - foodlastdate
        waterdelta = currentdate - waterlastdate
        cleandelta = currentdate - cleanlastdate
        dayspassed = delta.days

        hourspassed = math.floor((delta.days * 24) + (delta.seconds / 3600))
        foodhourspassed = math.floor((fooddelta.days * 24) + (fooddelta.seconds / 3600))
        waterhourspassed = math.floor((waterdelta.days * 24) + (waterdelta.seconds / 3600))
        cleanhourspassed = math.floor((cleandelta.days * 24) + (cleandelta.seconds / 3600))

        if foodhourspassed > 0:
            json_object = PetHandler.feed(json_object, -(hourspassed * 2))
            if json_object['food'] == 0:
                json_object = PetHandler.currenthealth(json_object, -10)
        if waterhourspassed > 0:
            json_object = PetHandler.water(json_object, -(hourspassed * 2))
            if json_object['water'] == 0:
                json_object = PetHandler.currenthealth(json_object, -10)
        if cleanhourspassed > 0:
            json_object = PetHandler.clean(json_object, -(hourspassed * 2))
            if json_object['cleanliness'] == 0:
                json_object = PetHandler.currenthealth(json_object, -10)

        if hourspassed > 0:
            if json_object['food'] > 70 and json_object['water'] > 75 and json_object['cleanliness'] > 60:
                json_object = PetHandler.currenthealth(json_object, (hourspassed * 5))
            if json_object['food'] > 90 and json_object['water'] > 95 and json_object['cleanliness'] > 90:
                json_object = PetHandler.happy(json_object, (hourspassed * 5))
            if json_object['food'] < 60 and json_object['water'] < 60 and json_object['cleanliness'] < 60:
                json_object = PetHandler.happy(json_object, -(hourspassed * 5))

        json_object['lastchecked'] = currentdate.strftime('%m/%d/%y %H:%M:%S')

        return json_object

    @staticmethod
    def newpet(name):

        json_object = {
            'name': name,
            'lastchecked': datetime.datetime.now().strftime('%m/%d/%y %H:%M:%S'),
            'type': 'bird',
            'level': 1,
            'birthdate': datetime.datetime.now().strftime('%m/%d/%y %H:%M:%S'),
            'deathdate': '',
            'deathreason': '',
            'maxhealth': 100,
            'currenthealth': 50,
            'attack': 1,
            'defence': 1,
            'happiness': 50,
            'lastpet': datetime.datetime.now().strftime('%m/%d/%y %H:%M:%S'),
            'food': 50,
            'lastfeed': datetime.datetime.now().strftime('%m/%d/%y %H:%M:%S'),
            'water': 50,
            'lastwatered': datetime.datetime.now().strftime('%m/%d/%y %H:%M:%S'),
            'cleanliness': 50,
            'lastcleaned': datetime.datetime.now().strftime('%m/%d/%y %H:%M:%S')
        }

        PetHandler.savedata(json_object)
        return json_object

    @staticmethod
    def puttorest(json_object):

        package_dir = os.path.dirname(os.path.abspath(__file__))
        thefile = os.path.join(package_dir, 'graveyard.txt')
        with open(thefile) as json_file:
            graveyard = json.load(json_file)
            json_file.close()

        graveyard['graveyard'].append(json_object)

        with open(thefile, 'w') as outfile:
            json.dump(graveyard, outfile)
            outfile.close()

    @staticmethod
    def graveyardcheck():
        package_dir = os.path.dirname(os.path.abspath(__file__))
        thefile = os.path.join(package_dir, 'graveyard.txt')
        with open(thefile) as json_file:
            graveyard = json.load(json_file)
            json_file.close()
        return graveyard
