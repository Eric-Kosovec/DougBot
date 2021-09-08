import json
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
        return json_object

    @staticmethod
    def increasecurrenthealth(json_object, amount):
        maxhealth = json_object['maxhealth']
        currenthealth = json_object['currenthealth']
        if maxhealth < (currenthealth + amount):
            json_object['currenthealth'] = maxhealth
        else:
            json_object['currenthealth'] = currenthealth + amount

        return json_object

    @staticmethod
    def decreasecurrenthealth(json_object, amount):
        currenthealth = json_object['currenthealth']
        if 0 > (currenthealth - amount):
            json_object['currenthealth'] = 0
        else:
            json_object['currenthealth'] = currenthealth - amount

        return json_object

    @staticmethod
    def feed(json_object, amount):
        currentamount = json_object['food']
        if 100 < (currentamount + amount):
            json_object['food'] = 100
        else:
            json_object['food'] = currentamount + amount

        return json_object

    @staticmethod
    def starve(json_object, amount):
        currentamount = json_object['food']
        if 0 > (currentamount - amount):
            json_object['food'] = 0
        else:
            json_object['food'] = currentamount - amount

        return json_object

    @staticmethod
    def water(json_object, amount):
        currentamount = json_object['water']
        if 100 < (currentamount + amount):
            json_object['water'] = 100
        else:
            json_object['water'] = currentamount + amount

        return json_object

    @staticmethod
    def dehydrate(json_object, amount):
        currentamount = json_object['water']
        if 0 > (currentamount - amount):
            json_object['water'] = 0
        else:
            json_object['water'] = currentamount - amount

        return json_object

    @staticmethod
    def clean(json_object, amount):
        currentamount = json_object['cleanliness']
        if 100 < (currentamount + amount):
            json_object['cleanliness'] = 100
        else:
            json_object['cleanliness'] = currentamount + amount

        return json_object

    @staticmethod
    def dirty(json_object, amount):
        currentamount = json_object['cleanliness']
        if 0 > (currentamount - amount):
            json_object['cleanliness'] = 0
        else:
            json_object['cleanliness'] = currentamount - amount

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
        json_object['deathdate'] = datetime.datetime.now().strftime('%d/%m/%y %H:%M:%S')

        return json_object

    @staticmethod
    def checkpet(json_object):
        currentdate = datetime.datetime.now()
        lastdate = datetime.datetime.strptime(json_object['lastchecked'], '%d/%m/%y %H:%M:%S')
        delta = currentdate - lastdate
        dayspassed = delta.days
        if dayspassed > 0:
            food = json_object['food']
            water = json_object['water']
            cleanliness = json_object['cleanliness']

            if food == 0:
                json_object = PetHandler.decreasecurrenthealth(json_object, 10 * dayspassed)
            if water == 0:
                json_object = PetHandler.decreasecurrenthealth(json_object, 10 * dayspassed)
            if cleanliness == 0:
                json_object = PetHandler.decreasecurrenthealth(json_object, 10 * dayspassed)
        print(json_object)
        return json_object

    @staticmethod
    def newpet(name):

        json_object = {
            'name': name,
            'lastchecked': datetime.datetime.now().strftime('%d/%m/%y %H:%M:%S'),
            'type': 'SadBoy',
            'level': 1,
            'birthdate': datetime.datetime.now().strftime('%d/%m/%y %H:%M:%S'),
            'deathdate': '',
            'deathreason': '',
            'maxhealth': 100,
            'currenthealth': 50,
            'attack': 1,
            'defence': 1,
            'food': 50,
            'water': 50,
            'cleanliness': 50
        }

        PetHandler.savedata(json_object)

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
