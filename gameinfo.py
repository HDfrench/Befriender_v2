#-------------------------------------------------------------------------------
# Name:        architecture_class
# Purpose:     class to control The Befriender RPG game
#
# Author:      Hacène Dramchini
#
# Created:     26/10/2020
# Copyright:   (c) Hacène Dramchini 2020
# Licence:     Free to use and distribute
#-------------------------------------------------------------------------------
import sys
import json
import os

from architecture_class import Room, Furniture
from character import Enemy, Friend

class GameInfo():
    author = 'Hacène Dramchini'
    generaloptionslist = ['k', 'o', 'r', 'q', '@']
    continued = 0
    mode = 0
    lives = 3
    health = 9
    default_room  = ''
    current_room = ''
    #defines the list of files to read game data from
    filelist = ('room_details.json', 'house_layout.json', 'furn_data.json', 'character_data.json')
    #Dictionaries:
    #   for the rooms in the house
    House_dict = dict()
    #   for each item of furniture
    Furn_dict = dict()
    #   for Friends
    Fr_dict = dict()
    #   for Enemies
    En_dict = dict()
    #   for all characters
    Ch_dict = dict()
    potentialfriends = 0
    myitems = list()

    def __Init__(self, game_title):
        self.title = game_title

    @classmethod
    def newgame(cls):
        current_room_name = "kitchen"
        while True:
            inp = input("Select your play mode: 1) basic or 2) extended > ")
            if inp in ['1', '2']:
                Create.house_data(int(inp))
                break
        return current_room_name



    @classmethod
    def continuepreviousgame(cls):
        with open('befriender_settings.json', 'r') as fhand:
            data = json.load(fhand)
            for k in data:
                for x in k:
                    if x == "Mode":
                        GameInfo.mode = int(k[x])
                    elif x == "Lives":
                        GameInfo.lives = int(k[x])
                    elif x == "Health":
                        GameInfo.health = int(k[x])
                    elif x == "Potential":
                        GameInfo.potentialfriends = int(k[x])
                    elif x == "Converts":
                        Enemy.converts = int(k[x])
                    elif x == "CurrentRoom":
                        current_room_name = k[x]
                    elif x == "Inventory":
                        GameInfo.myitems = k[x]
                    else:
                        print('Not catered for!')
            GameInfo.continued = 1
        return current_room_name

    @classmethod
    def getgamedata(cls, filelist, current_room_name):
        """
        this section gets the layout of the room,
        the furniture with hidden object in each room
        the characters in each room
        """
        def buildhouse(stg, stg_name, stg_desc, expl, srch):
            """
            function to create room objects and assign details
            """
            n_stg = stg
            stg = Room(stg_name)
            #stg.name = str.lower(stg_name)
            stg.description = stg_desc
            stg.explored = expl
            stg.searched = srch
            cls.House_dict[str(n_stg)] = stg

            if stg.name == 'Kitchen':
                GameInfo.set_default_room()
            if n_stg == current_room_name:
                    GameInfo.current_room = cls.House_dict[str(n_stg)]
            return stg, cls.House_dict

        def furnishhouse(r_name, stg, stg_name, stg_desc, stg_hidden, stg_explore):
            """
            function to create furniture objects and assign details
            """
            n_stg = stg
            stg = Furniture()
            stg.name = stg_name
            stg.description = stg_desc
            """
            the hidden_item will pass a 2 item list to the hidden property of the furniture
            all items follow the same list pattern
            """
            stg.set_hidden(stg_hidden)
            stg.explored = int(stg_explore)
            stg.set_room(r_name)
            cls.Furn_dict[str(n_stg)] = stg
            """
            #assign furniture to room
            """
            myroom = cls.House_dict[r_name]
            myroom.set_furn(n_stg, stg_name, stg_desc)
            return stg, cls.Furn_dict, cls.House_dict

        def charsetting(s_name, c_type, room_asgn, c_cat, c_speech, SubmitTo, KilledBy, ConvertWith, st_shy, st_killed, st_friend):
            """
            function to create character objects and assign details
            """
            n_stg = s_name
            if c_type == 'Friend':
                """
                the (SubmitTo, KilledBy) will pass a 2 item list to the friend
                all items follow the same list pattern
                """
                stg = Friend(s_name, c_cat, c_speech, (SubmitTo, KilledBy))
                if st_shy == 1:
                    stg.given = 1
                cls.Fr_dict[str(n_stg)] = stg
                cls.Ch_dict[str(n_stg)] = stg
            else:
                stg = Enemy(s_name, c_cat, c_speech, (SubmitTo, KilledBy, ConvertWith))
                stg.concedes = int(st_shy)
                stg.killed = int(st_killed)
                stg.befriended = int(st_friend)
                GameInfo.potentialfriends += 1
                cls.En_dict[str(n_stg)] = stg
                cls.Ch_dict[str(n_stg)] = stg
            for rm, r_obj in cls.House_dict.items():
                """
                assign character to room
                """
                if room_asgn == rm:
                    r_obj.set_character(stg)
                    r_obj.set_ch_det(cls.Ch_dict)

            return stg, cls.Fr_dict, cls.En_dict, cls.Ch_dict, cls.House_dict
        """
        this section reads the layout of the house and links the rooms.
        The file "house_layout.json" has the following structure:
          col 1:  room name (origin) ==> key value from house_dict (no space!)
          col 2:  direction
          col 3:  room name (target) ==> key value from house_dict (no space!)
        """
        fhand = open(filelist[0])
        data = json.load(fhand)
        for item in data:
            buildhouse(item['Name'], item['Display'], item['Description'], int(item['Explored']), int(item['Searched']))
        fhand.close
        """
        this section reads the layout of the house and links the rooms.

        The file "house_layout.json" has the following structure:
          col 1:  room name (origin) ==> key value from house_dict (no space!)
          col 2:  direction
          col 3:  room name (target) ==> key value from house_dict (no space!)

        """
        fhand = open(filelist[1])
        data = json.load(fhand)
        for item in data:
            crr = GameInfo.House_dict[item['Room']]
            tgr = GameInfo.House_dict[item['LinkTo']]
            crr.link_room(tgr, item['Direction'])
        fhand.close
        """
        this section defines the furniture in each room
        The file "furn_data.json" has the following structure:
          col 1:  room name ==> key value in House_dict (no space!)
          col 2:  furniture name ==> key value in Furn_dict (no space!)
          col 3:  furniture display name
          col 4:  furniture description
          col 5:  hidden object
          col 6:  0 = not relevant
                  k = will kill a character
                  c = will convert an enemy into a friend
        """
        fhand = open(filelist[2])
        data = json.load(fhand)
        for itm in data:
            furnishhouse(itm['Room'], itm['Name'], itm['Display'], itm['Description'], itm['Hidden'], int(itm['Exploration']))
        fhand.close
        """
        this section defines all the characters in the game
        The file "character_data.json" has the following structure:
          First lists all Enemies
          Second lists all Friends
          col 1:  character name ==> key value in Char_dict, En_Dict or Fr_Dict (no space!)
          col 2:  character type ==> Friend or Enemy
          col 3:  room to be found in ==> key value in House_dict (no space!)
          col 4:  character description
          col 5 to 7:   character speech
                        Enemy or Friend (to cater for potential Enemy conversion into Friend)
                    col 5: greetings
                    col 6: hint as to the use for the gift to be received
                    col 7: line to bestow the character gift to the player
          col 8 to 10:  | separated content
                  Enemy:  col 8: what frightens it
                          col 9: what kills it
                          col 10: what converts it into a friend
                  Friend: col 8: gift name
                          col 9: category (always "g")
                          col 10: Enemy concerned (target name)
          col 11 to 13: | separated content
                  Enemy:  col 11: concede status (0 or 1)
                          col 12: killed status (0 or 1)
                          col 13: converted status (0 or 1)
                  Friend: col 11: 0 (False/n.a)
                          col 12: 0 (False/n.a)
                          col 13: 0 (False/n.a)
        """
        #fhand = open(filelist[3])
        #data = json.load(fhand)
        data = json.load(open(filelist[3]))
        for itm in data:
            charsetting(itm['Name'], itm['Type'], itm['Room'], itm['Description'], itm['Conversation'], itm['Submit_to'], itm['Kill_by'], itm['Convert_with'], itm['St_concede'], itm['St_killed'], itm['St_converted'])
        fhand.close

    def readrules(self):
        """
        This is the game introduction section
        """
        self.readfile('befriender_rules.json')
        a = 1
        b = 1
        self.banner()
        while a == 1:
            print('> or play (p)')
            optionlist = ['p'] + self.generaloptionslist
            inp = input('  > ')
            if len(inp)>0:
                if str.lower(inp[0]) not in optionlist:
                    self.banner()
                    continue
                elif str.lower(inp[0]) in self.generaloptionslist:
                    self.mainmenu(str.lower(inp[0]))
                    self.banner()
                    continue
                else:
                    self.banner()
                    break
            else:
                self.banner()
                continue

    @classmethod
    def definelevel(cls):
        """
        this is the main playing section
        """
        print('************************************************')
        print('*              Choose your level               *')
        print('************************************************')
        print('* 1) Easy,  2) Medium,  3) hard,  4) insane    *')
        print('************************************************')
        while True:
            inp = input('> ')
            if len(inp) !=0:
                if str.lower(inp[0]) not in ['1','2','3','4']:
                   continue
                elif inp == '4':
                    cls.lives = 1
                    cls.health = 3
                    break
                else:
                    tval = int(inp) - 1
                    cls.lives = 3 - tval
                    cls.health = 9
                    break
            else:
                continue
        print('************************************************')
        print("*                 Let's begin!                 *")
        print('************************************************')

    @staticmethod
    def banner():
        """
        function to display always the general options
        """
        print('************************************************')
        print('* map (k) - options (o) - rules (r) - quit (q) *')
        print('************************************************')

    @classmethod
    def completedgame(cls):
        """
        this function is for the end of the game once all enemies have been vanquished or converted
        """
        print('************************************************')
        print('  CONGRATULATIONS - YOU WIN - no more enemies  *')
        print('************************************************')
        if Enemy.converts !=0:
            enm = ('    x','  O/ ',' /|  ',' / \ ')
            inb = ('     ','     ',' ==> ','     ')
            frd = ('     ',' \O/ ','  |  ',' / \ ')
            if Enemy.converts == 1:
                myend = ('enemy', 'a friend')
            else:
                myend = ('enemies', 'friends')
            print('\tYou converted', Enemy.converts, myend[0], 'into', myend[1])
            x = 1
            while x < len(enm)+1:
                print(enm[x-1] * 3, inb[x-1], frd[x-1] * 3)
                x +=1
            if Enemy.converts == GameInfo.potentialfriends:
                print('\nPerfect game!\nYou managed to convert all your enemies into friends!\nVery well done!!!!')
                print('\nYou now live in a house full of friends!')
            else:
                print('\nWell done converting some of your enemies into friends!\n')
                print('A pity you had to kill some!\n')
                print('Still, the house is now enemy free!\nWell done!')
        else:
            print('\nYou killed all your enemies!\nNext time try to change them into friends!')
        exit('Thank you for playing')

    @classmethod
    def credit(cls):
        print('Thank you for playing!')
        print('Created by', cls.author)

    def readfile(self, jsonfile):
        """
        function to read the various json files
        """
        with open(jsonfile, 'r') as fhand:
            data2 = json.load(fhand)
            for k in data2:
                print(k['Line'])
        fhand.close

    def mainmenu(self, inp):
        """
        #this function is to deal with player keying a main menu options
        the option '@' is a secret cheat to see the list of enemies and what affects them and how
        """
        if inp == 'k':
            self.readfile('befriender_map.json')
        elif inp == 'r':
            self.readfile('befriender_rules.json')
        elif inp == 'o':
            self.readfile('befriender_options.json')
        elif inp == '@':
            self.readfile('befriender_enemies.json')
        elif inp == 'q':
            saving = input('Do you want to save your progress? (y/n) > ')
            if saving.lower() == 'y':
                Create.savedata()
                print('Game saved!')
            else:
                if os.path.exists('befriender_settings.json'):
                    os.remove('befriender_settings.json')
                    print('file deleted!')
            GameInfo.credit()
            exit('Thank you for playing')
        else:
            print('something is wrong!')

    def chat(self, lp):
        """
        this function deals with the conversation with a character
        """
        refstg = " "*20
        play_intro = '[You]:'
        spacing = len(refstg) - len(play_intro)
        textintro = play_intro + refstg[:spacing]
        if lp == 0:
            print(textintro, 'Please to meet you!')
        elif lp==1:
            print(textintro, 'What is special about you?')
        else:
            print(textintro, 'It is so nice for you.')

    @staticmethod
    def whatchoice(inhabitant, current_room, myitems):
        """
        This function defines the options available to the player
        """
        if isinstance(inhabitant,Enemy)==True:
            GameInfo.current_room.set_explored(0)
            if inhabitant.get_concede() == 1:
                optionlist = ['m', 'x'] + GameInfo.generaloptionslist
                mystg = input(">  What do you want to do?\n\tMove (m)?\n\tExplore (x)? > ")
            else:
                if len(myitems) != 0:
                    optionlist = ['m', 'f'] + GameInfo.generaloptionslist
                    mystg = input(">  What do you want to do?\n\tMove (m)?\n\tFight (f)? > ")
                else:
                    optionlist = ['m'] + GameInfo.generaloptionslist
                    mystg = input(">  You can only Move (m)! > ")
        else:
            GameInfo.current_room.explored = 1
            if GameInfo.current_room.get_searched() == 0:
                optionlist = ['m', 'x', 't'] + GameInfo.generaloptionslist
                mystg = input(">  What do you want to do?\n\tMove (m)?\n\texplore (x)?\n\ttalk (t)? > ")
            else:
                optionlist = ['m', 't'] + GameInfo.generaloptionslist
                mystg = input(">  What do you want to do?\n\tMove (m)?\n\ttalk (t)? > ")
        return mystg, optionlist, myitems


    @classmethod
    def set_default_room(cls):
        for k, v in cls.House_dict.items():
            if k =='kitchen':
                cls.default_room = cls.House_dict[k]
                continue

    @classmethod
    def defaultroom(cls):
        """
        this function reset the game to the original default room
        where the game starts and where the player respawn after losing a life
        """
        cls.current_room = cls.default_room
        inhabitant = cls.current_room.get_character()
        inh_profile = cls.current_room.get_ch_det()
        cls.current_room.describe()
        return cls.current_room

    @classmethod
    def changeroom(cls, moveoption):
        """
        this function deals with moving between rooms
        """
        optl = str([x[0] for x in moveoption])
        a = 0
        b = 1
        while a == 0:
            mymove = input(' > your choice: ')
            if mymove not in optl:
                print('Not an option!')
                continue
            else:
                if mymove in optl:
                    myref = int(mymove) - 1
                    mytup = moveoption[myref]
                    GameInfo.current_room = GameInfo.current_room.move(mytup[1], GameInfo.House_dict)
                    inhabitant = GameInfo.current_room.get_character()
                    inh_profile = GameInfo.current_room.get_ch_det()
                    GameInfo.current_room.describe()
                    if isinstance(inhabitant,Enemy)==True:
                        inhabitant.set_concede(0)
                    print("\n")
                    a == 1
                    break
                elif mymove in GameInfo.generaloptionslist:
                    GameInfo.mainmenu(mymove)
                else:
                    continue

    def speechsequence(self, inhabitant, inh_profile, myitems):
        """
        this function deals with the talk sequence of the game
        """
        myspeech = inhabitant.talk()
        refstg = " "*20
        inh_intro = '[' + inh_profile[0] + ' says]:'
        spacing = len(refstg) - len(inh_intro)
        textintro = inh_intro + refstg[:spacing]
        print(textintro, 'I am', inh_profile[0] + ', a', inh_profile[1] +'.')
        lp = 0
        while lp<3:
            inp = input('(press return) >')
            GameInfo.chat(self, lp)
            if lp<2:
                print(textintro, myspeech[lp],'\n')
            lp +=1
        inp = input('>')
        if inhabitant.get_given() == 0:
            print('[' + inh_profile[0], 'says]:\t', myspeech[2],'\n')
            gft = str(inhabitant.present)
            if gft in ['cheese','fairy dust', 'mouthwash', 'air freshener']:
                msg = 'some'
            elif gft == 'emerald':
                msg == 'an'
            else:
                msg = 'a'
            print('\n', inhabitant.name, 'gives you', msg, inhabitant.present, '\n')
            myitems.append(inhabitant.gift)
            inhabitant.set_given(1)

    def explore(self, myitems):
        """
        this function deals with searching the room
        """
        a = 0
        while a == 0:
            for k,v in GameInfo.House_dict.items():
                if v.name == GameInfo.current_room.name:
                    r_name = k
                    continue
            Cansearchin = GameInfo.current_room.searchable(GameInfo.Furn_dict, r_name)
            """
            defines the furniture in the room that has not yet been searched
            """
            if len(Cansearchin) != 0:
                res_list = str([x[0] for x in Cansearchin])
                mysearch = input('> Select a number or x to stop searching > ')
                if mysearch == 'x':
                    a = 1
                    break
                elif mysearch in res_list:
                    try:
                        myref = int(mysearch) - 1
                        mytup = Cansearchin[myref]
                        myfurn = GameInfo.Furn_dict[mytup[1]]
                        print('\n\tIn the', myfurn.get_name(), 'you found ==> ', myfurn.get_hidden(),'\n')
                        if myfurn.get_hidden() != str.lower('nothing'):
                            myitems.append((myfurn.get_hidden(),myfurn.get_purpose()))
                            myfurn.set_hidden('nothing')
                        myfurn.set_explore(1)
                    except:
                        continue
                elif mysearch in GameInfo.generaloptionslist:
                    GameInfo.mainmenu(self, mysearch)
                else:
                    print('This is not an option!')

            else:
                GameInfo.current_room.set_searched(1)
                print('You already searched/found everything in this room!')
                a = 1
                break
        return myitems

    def rumble(self, myitems, inhabitant, name, profile):
        """
        this function deals with the fight sequence of the game
        """
        fightfinished = False
        while fightfinished == False:
            print('************* FIGHT - FIGHT - FIGHT ************')
            print('*           YOU\tvs.\t', str.upper(name), 'the', profile)
            print('************************************************')
            numlist = list()
            rk = 1
            print('You can use:')
            usedweapon = [itm[0] for itm in myitems]
            for usedweapon in myitems:
                print('\t-', rk, ')\t', usedweapon[0])
                numlist.append(str(rk))
                rk +=1
            print('\tor simply give up the fight (g)!')
            fightinput = input('> what do you want to use? > ')
            if fightinput not in numlist:
                if fightinput != str.lower('g'):
                    print('This is not an option!\n')
                else:
                    print('Wise choise!\n')
                    break
            else:
                myref = int(fightinput) - 1
                weapon = myitems[myref]
                fightresult = inhabitant.fight(weapon, GameInfo.health, GameInfo.lives)
                GameInfo.health = fightresult[1]
                if fightresult[0] == True:
                    if inhabitant.get_befriended() == 1:
                        myitems.pop(myref)
                        converted = Friend(inhabitant.name, inhabitant.description, inhabitant.conversation, ("",""))
                        converted.set_given(1)
                        converted.explored = 1
                        GameInfo.Fr_dict[str(inhabitant.name)] = converted
                        GameInfo.En_dict.pop(inhabitant.name)
                        inhabitant = converted
                        GameInfo.current_room.set_character(inhabitant)
                        print('Well done for converting', inhabitant.name, 'into a friend\n')
                    else:
                        if inhabitant.get_killed() == 1:
                            GameInfo.En_dict.pop(inhabitant.name)
                            inhabitant = None
                            GameInfo.current_room.set_character(None)

                    if len(GameInfo.En_dict) == 0:
                        GameInfo.completedgame()
                    fightfinished = True
                else:
                    if fightresult[2] == 0:
                        exit('Thank you for playing')
                    elif fightresult[2]!= GameInfo.lives:
                        print('You cannot fight anymore!')
                        GameInfo.lives = fightresult[2]
                        fightfinished = True
        return myitems, inhabitant, GameInfo.health, GameInfo.lives

    @classmethod
    def extractcharacter(cls):
        mystg = []
        myroom = ''
        for k, v in cls.En_dict.items():
            for x, y in cls.House_dict.items():
                if y.character == cls.En_dict[k]:
                    myroom = x
                    continue
            mystg.append({"Name": v.name, "Type": "Enemy", "Room": myroom, "Description": v.description, "Conversation": v.conversation, "Submit_to": v.isscaredof, "Kill_by": v.iskilledby, "Convert_with": v.isconvertedby, "St_concede": str(v.concedes), "St_killed": str(v.killed), "St_converted": str(v.befriended)})
        for k, v in cls.Fr_dict.items():
            for x, y in cls.House_dict.items():
                if y.character == cls.Fr_dict[k]:
                    myroom = x
                    continue
            mystg.append({"Name": v.name, "Type": "Friend", "Room": myroom, "Description": v.description, "Conversation": v.conversation, "Submit_to": v.present, "Kill_by": v.gift[1], "Convert_with": "0", "St_concede": '0', "St_killed": "0", "St_converted": "0"})
        return mystg

class Create():
    def __init__(self):
        self.name = None

    @classmethod
    #'''
    #This function creates the json files required for the game
    #val can be:
    #    1) basic
    #    2) extended
    #    3) basic - continue
    #    4) extended - continue
    #'''
    def house_data(cls, val):
        def commontext():
            def rules():
                g_rules =[{"Line": " "},
                    {"Line": "        Welcome to The Befriender"},
                    {"Line": " "},
                    {"Line": " In this game, you will explore a house, trying to make as many friends as possible."},
                    {"Line": " In each room, you will meet characters, that can be friendly or hostile."},
                    {"Line": " "},
                    {"Line": " Friends can give you secret objects to convert hostiles into friends, but they will not tell you which object when, although you have to pay attention to what they say!"},
                    {"Line": " "},
                    {"Line": " When meeting hostiles, you must fight them. For each fight, you will pick an item from your inventory that will convert, subdue or kill your opponent, or do nothing!"},
                    {"Line": " If you convert your opponent into a friend, the fight is over, you have won and you can explore the room."},
                    {"Line": " If you subdue your opponent, you can search the room, but next time you will visit this room, your enemy will be there ready to fight!"},
                    {"Line": " If you kill your enemy, you will never meet this character again in the game."},
                    {"Line": " "},
                    {"Line": " When you use a gift, it is taken out of your inventory and you won't be able to find or acquire it again!"},
                    {"Line": " If you use the wrong item in a fight, you will lose a third of your health. "},
                    {"Line": " Be careful, you only have 3 lives!"},
                    {"Line": " So, you can always run away and go back to a room you already explored. :-)"},
                    {"Line": " "},
                    {"Line": " You cannot go into an unexplored room unless you have defeated or subdued any hostile in your current room."},
                    {"Line": " "},
                    {"Line": " Rooms also contain furniture that you can explore and maybe find weapons to use against hostiles."},
                    {"Line": " "},
                    {"Line": " Good luck!"},
                    {"Line": " "}]
                return g_rules
            def options():
                g_options = [{"Line": ""},
                    {"Line": "You will play with the keyboard pressing only "},
                    {"Line": "\t\t1 key + return"},
                    {"Line": ""},
                    {"Line": "In each room, you will be given up a few options"},
                    {"Line": "\t\t\t\tand sub options:"},
                    {"Line": "\tMove (m) ==> go to another room"},
                    {"Line": "\t\t** optional (not with hostile!)"},
                    {"Line": "\t\t   if there is an enemy in the room"},
                    {"Line": "\t\t   you can only access already visited"},
                    {"Line": "\t\t   rooms."},
                    {"Line": "\t\tn, s, w, e ==> direction"},
                    {"Line": ""},
                    {"Line": "\tExplore (x) ==> search the furniture"},
                    {"Line": "\t\t** displays a numbered list of"},
                    {"Line": "\t\t   furniture"},
                    {"Line": "\t\t1, 2, etc."},
                    {"Line": "\t\tx to stop searching"},
                    {"Line": ""},
                    {"Line": "\tTalk (t) ==> speak with a friend"},
                    {"Line": "\t\t**required to obtain objects to "},
                    {"Line": "\t\tconvert hostiles"},
                    {"Line": ""},
                    {"Line": "\tFight (f) ==> fight an enemy"},
                    {"Line": "\t\t** displays a numbered list of"},
                    {"Line": "\t\t   items in your inventory"},
                    {"Line": "\t\t1, 2, etc."},
                    {"Line": "\t\tg to give up fighting"},
                    {"Line": ""},
                    {"Line": "\tKey (k) ==> will show a map of the house"},
                    {"Line": "\tOptions (o) ==> will show this file"},
                    {"Line": "\tRules (r) ==> will show the rules of the game"},
                    {"Line": ""},
                    {"Line": "\tQuit (q) ==> to quit the game"},
                    {"Line": ""}]
                return g_options
            return rules(), options()
        def basic_environment():
            def basic_layout():
                blayout_data =[{"Room": "kitchen", "Direction": "west", "LinkTo": "pantry"},
                    {"Room": "kitchen", "Direction": "south", "LinkTo": "dining_hall"},
                    {"Room": "dining_hall", "Direction": "north", "LinkTo": "kitchen"},
                    {"Room": "dining_hall", "Direction": "west", "LinkTo": "ballroom"},
                    {"Room": "dining_hall", "Direction": "east", "LinkTo": "hallway"},
                    {"Room": "ballroom", "Direction": "east", "LinkTo": "dining_hall"},
                    {"Room": "hallway", "Direction": "west", "LinkTo": "dining_hall"},
                    {"Room": "hallway", "Direction": "south", "LinkTo": "bathroom"},
                    {"Room": "hallway", "Direction": "east", "LinkTo": "corridor"},
                    {"Room": "corridor", "Direction": "west", "LinkTo": "hallway"},
                    {"Room": "corridor", "Direction": "north", "LinkTo": "den"},
                    {"Room": "corridor", "Direction": "south", "LinkTo": "bedroom"},
                    {"Room": "corridor", "Direction": "east", "LinkTo": "library"},
                    {"Room": "library", "Direction": "west", "LinkTo": "corridor"},
                    {"Room": "library", "Direction": "south", "LinkTo": "office"},
                    {"Room": "office", "Direction": "north", "LinkTo": "library"},
                    {"Room": "bedroom", "Direction": "north","LinkTo": "corridor"},
                    {"Room": "bedroom", "Direction": "south", "LinkTo": "cabinet"},
                    {"Room": "cabinet", "Direction": "north", "LinkTo": "bedroom"},
                    {"Room": "den", "Direction": "south", "LinkTo": "corridor"},
                    {"Room": "bathroom", "Direction": "north", "LinkTo": "hallway"},
                    {"Room": "pantry", "Direction": "east", "LinkTo": "kitchen"}]
                return blayout_data
            def basic_enemies():
                benemies_data =[{"Line": "_______________________________________________________________________"},
                    {"Line": "| Enemy     |   Submit          |   Convert       |   Kill             |"},
                    {"Line": "|___________|___________________|_________________|____________________|"},
                    {"Line": "| clown     |   whip            |   cheese        |   feather          |"},
                    {"Line": "| monster   |   remote control  |   key           |   matches          |"},
                    {"Line": "| scarecrow |     pitch fork    |   hat           |   magnifying glass |"},
                    {"Line": "| vampire   |   sun lamp        |   mouthwash     |   garlic           |"},
                    {"Line": "| witch     |   fairy dust      |   wooden spoon  |   incantation      |"},
                    {"Line": "| zombie    |   air freshener   |   billiard ball |   knife            |"},
                    {"Line": "|___________|___________________|_________________|____________________|"}]
                return benemies_data
            def basic_map():
                bmap_data = [{"Line": " "},
                    {"Line": " \t\t\tThe house"},
                    {"Line": " "},
                    {"Line": " *************************************************************************"},
                    {"Line": " *             *                   *        *                *           *"},
                    {"Line": " *             |                   *        * Entertainement *    L      *"},
                    {"Line": " *   Pantry    |     Kitchen       *   H    *     Room       *    I      *"},
                    {"Line": " *             *                   *   A    *                *    B      *"},
                    {"Line": " *             *                   *   L    *                *    R      *"},
                    {"Line": " *             *                   *   L    *                *    A      *"},
                    {"Line": " ************************___********   W    *******___********    R      *"},
                    {"Line": " *                *                *   A    |   Corridor     |    Y      *"},
                    {"Line": " *                *                *   Y    |                |           *"},
                    {"Line": " *                *                |        *******___********           *"},
                    {"Line": " *                *                |        *                *           *"},
                    {"Line": " *                *                *        *                *           *"},
                    {"Line": " *    Ballroom    |  Dining room   *        *    Bedroom     *****___*****"},
                    {"Line": " *                |                *        *                *           *"},
                    {"Line": " *                *                ****__****                *           *"},
                    {"Line": " *                *                *        *                *           *"},
                    {"Line": " *                *                *        ******___*********  Office   *"},
                    {"Line": " *                *                *  Bath- *                *           *"},
                    {"Line": " *                *                *  room  *    Walk in     *           *"},
                    {"Line": " *                *                *        *    Cabinet     *           *"},
                    {"Line": " *                *                *        *                *           *"},
                    {"Line": " *************************************************************************"},
                    {"Line": " "},
                    {"Line": " Key:  * wall          North"},
                    {"Line": "       | door            ^"},
                    {"Line": "                         |"},
                    {"Line": "                 West <-- --> East"},
                    {"Line": "                         |"},
                    {"Line": "                         v"},
                    {"Line": "                       South"},
                    {"Line": ""}]
                return bmap_data
            return basic_layout(), basic_enemies(), basic_map()
        def extended_environment():
            def extended_layout():
                elayout_data =[{"Room": "kitchen", "Direction": "west", "LinkTo": "pantry"},
                    {"Room": "kitchen", "Direction": "south", "LinkTo": "dining_hall"},
                    {"Room": "dining_hall", "Direction": "north", "LinkTo": "kitchen"},
                    {"Room": "dining_hall", "Direction": "west", "LinkTo": "ballroom"},
                    {"Room": "dining_hall", "Direction": "north-east", "LinkTo": "hallway"},
                    {"Room": "dining_hall", "Direction": "south-east", "LinkTo": "vestibule"},
                    {"Room": "ballroom", "Direction": "east", "LinkTo": "dining_hall"},
                    {"Room": "vestibule", "Direction": "east", "LinkTo": "dining_hall"},
                    {"Room": "vestibule", "Direction": "west", "LinkTo": "livingroom"},
                    {"Room": "hallway", "Direction": "west", "LinkTo": "dining_hall"},
                    {"Room": "hallway", "Direction": "south", "LinkTo": "stairwell"},
                    {"Room": "hallway", "Direction": "east", "LinkTo": "corridor"},
                    {"Room": "corridor", "Direction": "west", "LinkTo": "hallway"},
                    {"Room": "corridor", "Direction": "north", "LinkTo": "den"},
                    {"Room": "corridor", "Direction": "south", "LinkTo": "livingroom"},
                    {"Room": "corridor", "Direction": "east", "LinkTo": "library"},
                    {"Room": "library", "Direction": "west", "LinkTo": "corridor"},
                    {"Room": "library", "Direction": "south", "LinkTo": "office"},
                    {"Room": "office", "Direction": "north", "LinkTo": "library"},
                    {"Room": "office", "Direction": "west", "LinkTo": "livingroom"},
                    {"Room": "livingroom", "Direction": "west", "LinkTo": "vestibule"},
                    {"Room": "livingroom", "Direction": "north", "LinkTo": "corridor"},
                    {"Room": "livingroom", "Direction": "east", "LinkTo": "office"},
                    {"Room": "den", "Direction": "south", "LinkTo": "corridor"},
                    {"Room": "pantry", "Direction": "east", "LinkTo": "kitchen"},
                    {"Room": "stairwell", "Direction": "down", "LinkTo": "hallway"},
                    {"Room": "stairwell", "Direction": "up", "LinkTo": "landing"},
                    {"Room": "landing", "Direction": "north-west", "LinkTo": "bathroom"},
                    {"Room": "landing", "Direction": "north-east", "LinkTo": "children"},
                    {"Room": "landing", "Direction": "south-west", "LinkTo": "master"},
                    {"Room": "landing", "Direction": "south-east", "LinkTo": "guestroom"},
                    {"Room": "landing", "Direction": "south", "LinkTo": "stairwell"},
                    {"Room": "bathroom", "Direction": "east", "LinkTo": "landing"},
                    {"Room": "children", "Direction": "west", "LinkTo": "landing"},
                    {"Room": "guestroom", "Direction": "north-west", "LinkTo": "landing"},
                    {"Room": "guestroom", "Direction": "south-east", "LinkTo": "ensuite"},
                    {"Room": "guestroom", "Direction": "south-east", "LinkTo": "laundry"},
                    {"Room": "guestroom", "Direction": "south", "LinkTo": "powderroom"},
                    {"Room": "powderroom", "Direction": "north", "LinkTo": "guestroom"},
                    {"Room": "ensuite", "Direction": "north", "LinkTo": "guestroom"},
                    {"Room": "laundry", "Direction": "east", "LinkTo": "guestroom"},
                    {"Room": "laundry", "Direction": "west", "LinkTo": "master"},
                    {"Room": "master", "Direction": "north", "LinkTo": "nursery"},
                    {"Room": "master", "Direction": "north-east", "LinkTo": "toilet"},
                    {"Room": "master", "Direction": "south-east", "LinkTo": "shower"},
                    {"Room": "master", "Direction": "south", "LinkTo": "boudoir"},
                    {"Room": "master", "Direction": "north-east", "LinkTo": "landing"},
                    {"Room": "master", "Direction": "south-east", "LinkTo": "laundry"},
                    {"Room": "shower", "Direction": "east", "LinkTo": "master"},
                    {"Room": "toilet", "Direction": "east", "LinkTo": "master"},
                    {"Room": "nursery", "Direction": "south", "LinkTo": "master"},
                    {"Room": "boudoir", "Direction": "north", "LinkTo": "master"}]
                return elayout_data
            def extended_enemies():
                eenemies_data =[{"Line": "_______________________________________________________________________"},
                    {"Line": "| Enemy     |   Submit          |   Convert       |   Kill             |"},
                    {"Line": "|___________|___________________|_________________|____________________|"},
                    {"Line": "| clown     |   whip            |   cheese        |   feather          |"},
                    {"Line": "| ghoul     |   trumpet         |   dreamcatcher  |   stake            |"},
                    {"Line": "| goblin    |   leather belt    |   emerald       |   dagger           |"},
                    {"Line": "| imp       |   salt            |   steak         |   water            |"},
                    {"Line": "| monster   |   remote control  |   key           |   matches          |"},
                    {"Line": "| orc       |   lighter         |   human skull   |   ax               |"},
                    {"Line": "| scarecrow |     pitch fork    |   hat           |   magnifying glass |"},
                    {"Line": "| troll     |   cattle prod     |   shiny ring    |   mirror           |"},
                    {"Line": "| vampire   |   sun lamp        |   mouthwash     |   garlic           |"},
                    {"Line": "| werewolf  |   perfume         |   chew toy      |   silver spoon     |"},
                    {"Line": "| witch     |   fairy dust      |   wooden spoon  |   incantation      |"},
                    {"Line": "| zombie    |   air freshener   |   billiard ball |   knife            |"},
                    {"Line": "|___________|___________________|_________________|____________________|"}]
                return eenemies_data
            def extended_map():
                emap_data = [{"Line": ""},
                    {"Line": "\t\t\tThe house"},
                    {"Line": ""},
                    {"Line": " Ground floor"},
                    {"Line": " *************************************************************************"},
                    {"Line": " *             *                   *        *                *           *"},
                    {"Line": " *             |                   *        * Entertainement *    L      *"},
                    {"Line": " *   Pantry    |     Kitchen       *   H    *     Room       *    I      *"},
                    {"Line": " *             *                   *   A    *                *    B      *"},
                    {"Line": " *             *                   *   L    *                *    R      *"},
                    {"Line": " *             *                   *   L    *                *    A      *"},
                    {"Line": " ************************___********   W    *******___********    R      *"},
                    {"Line": " *                *                |   A    |   Corridor     |    Y      *"},
                    {"Line": " *                *                |   Y    |                |           *"},
                    {"Line": " *                *                ***___**********___********           *"},
                    {"Line": " *                *                *        *                *           *"},
                    {"Line": " *                *                * stairs *                *           *"},
                    {"Line": " *    Ballroom    |  Dining room   *        *                *****___*****"},
                    {"Line": " *                |                **********                *           *"},
                    {"Line": " *                *                *        *    Living-     *           *"},
                    {"Line": " *                *                *        *     room       *           *"},
                    {"Line": " *                *                | Vesti- |                |  Office   *"},
                    {"Line": " *                *                |  bule  |                |           *"},
                    {"Line": " *                *                *        *                *           *"},
                    {"Line": " *                *                *        *                *           *"},
                    {"Line": " *                *                *        *                *           *"},
                    {"Line": " *************************************************************************"},
                    {"Line": ""},
                    {"Line": ""},
                    {"Line": " First floor"},
                    {"Line": " *************************************************************************"},
                    {"Line": " *                    *            *        *                            *"},
                    {"Line": " *                    *            *   L    *                            *"},
                    {"Line": " *       Nursery      *  Bathroom  |   A    *          Children          *"},
                    {"Line": " *                    *            |   N    |            Room            *"},
                    {"Line": " *                    *            *   D    |                            *"},
                    {"Line": " *                    *            *   I    *                            *"},
                    {"Line": " *****************___***************   N    ******************************"},
                    {"Line": " *           *                     |   G    |                            *"},
                    {"Line": " *    W.C.   |                     |        |                            *"},
                    {"Line": " *           |                     ***___****                            *"},
                    {"Line": " *           *                     *        *         Guest              *"},
                    {"Line": " *************   Master Bedroom    * stairs *        Bedroom             *"},
                    {"Line": " *           |                     *        *                            *"},
                    {"Line": " *           |                     **********                            *"},
                    {"Line": " *           *                     |   L    |                            *"},
                    {"Line": " *  Shower   *                     |   A    |                            *"},
                    {"Line": " *   room    *                     *   U    ******___*************___*****"},
                    {"Line": " *           ******************___**   N    *                *           *"},
                    {"Line": " *           *                     *   D    *    Powder      *           *"},
                    {"Line": " *           *       Boudoir       *   R    *     room       * En-suite  *"},
                    {"Line": " *           *                     *   Y    *                *           *"},
                    {"Line": " *************************************************************************"},
                    {"Line": ""},
                    {"Line": " Key:  * wall          North"},
                    {"Line": "       | door            ^"},
                    {"Line": "                         |"},
                    {"Line": "                 West <-- --> East"},
                    {"Line": "                         |"},
                    {"Line": "                         v"},
                    {"Line": "                       South"},
                    {"Line": ""}]
                return emap_data
            return extended_layout(), extended_enemies(), extended_map()
        def basic_game():
            def basic_house():
                bhouse_data = [{'Name': 'kitchen', 'Display': 'Kitchen', 'Description':"A room full of light and mouth-watering scents.", "Explored": 1, "Searched": 0},
                    {'Name': 'ballroom', 'Display': 'Ballroom', 'Description':"A large and wide empty room with a splendid flooring and magnificent chandeliers.", "Explored": 0, "Searched": 0},
                    {'Name': 'dining_hall', 'Display': 'Dining hall', 'Description':"A rather large room, with a grandiose dining table able to sit 8 peoples, surrounded by furniture covered walls displaying magnificent tableware.", "Explored": 0, "Searched": 0},
                    {'Name': 'pantry', 'Display': 'Pantry', 'Description':"A small dark room with shelves.", "Explored": 0, "Searched": 0},
                    {'Name': 'hallway', 'Display': 'Hallway', 'Description':"The centre of the house, the intersection between the east and west wings.", "Explored": 0, "Searched": 0},
                    {'Name': 'bathroom', 'Display': 'Bathroom', 'Description':"A lovely warm and cosy washing area.", "Explored": 0, "Searched": 0},
                    {'Name': 'corridor', 'Display': 'Corridor', 'Description':"A long and narrow passage leading to the east wing of the house.", "Explored": 0, "Searched": 0},
                    {'Name': 'office', 'Display': 'Office', 'Description':"A room organised around a large glass desk, with a beautiful chair and many filling cabinets.", "Explored": 0, "Searched": 0},
                    {'Name': 'bedroom', 'Display': 'Bedroom', 'Description':"The only bedroom in the house, fitted with a large king size bed and some wardrobe.", "Explored": 0, "Searched": 0},
                    {'Name': 'cabinet', 'Display': 'Walk-in cabinet', 'Description':"A magnificent and well-organised walk-in cabinet displaying well pressed expensive garnments and shoes.", "Explored": 0, "Searched": 0},
                    {'Name': 'den', 'Display': 'Entertainment room', 'Description':"A very large room with a pool table, an entertainment center, an oval coffee table and a great five seater leather sofa.", "Explored": 0, "Searched": 0},
                    {'Name': 'library', 'Display': 'Library', 'Description':"A cosy room filled with bookshelves and a reading area.", "Explored": 0, "Searched": 0}]
                return bhouse_data
            def basic_furniture():
                bfurn_data = [{"Room": "kitchen", "Name": "kitchen_table", "Display": "kitchen table", "Description": "A small round table with 3 chairs", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "kitchen", "Name": "kitchen_sink", "Display": "kitchen sink", "Description": "A standard kitchen sink", "Hidden": ("knife", "k"), "Exploration": 0},
                    {"Room": "kitchen", "Name": "kitchen_oven", "Display": "oven", "Description": "A beautiful fan oven", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "kitchen", "Name": "kichen_draw", "Display": "drawers", "Description": "A set of drawers", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "kitchen", "Name": "kitchen_fridge", "Display": "fridge", "Description": "A double-door fridge", "Hidden": ("cheese", "c"), "Exploration": 0},
                    {"Room": "kitchen", "Name": "kitchen_dishwasher", "Display": "dishwasher", "Description": "A dishwasher with its door ajar", "Hidden": ("wooden spoon", "c"), "Exploration": 0},
                    {"Room": "dining_hall", "Name": "dining_table", "Display": "dining table", "Description": "A long oval wooden well-polished table with 8 chairs", "Hidden": ("a box of matches", "k"), "Exploration": 0},
                    {"Room": "dining_hall", "Name": "dining_draw_1", "Display": "commode", "Description": "A tall 8 drawers wooden commode", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "dining_hall", "Name": "dining_draw_2", "Display": "set of drawers", "Description": "A medium size set of 4 drawers", "Hidden": ("garlic", "k"), "Exploration": 0},
                    {"Room": "ballroom", "Name": "ballroom_armchair", "Display": "armchair", "Description": "A comfortable, impressive and luxurious leather armchair", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "ballroom", "Name": "ballroom_sofa", "Display": "reclining sofa", "Description": "A three-sitter reclining sofa covered in a lovely purple velvet", "Hidden": ("hat", "c"), "Exploration": 0},
                    {"Room": "pantry", "Name": "shelf_1", "Display": "shelf", "Description": "a shelf full of small boxes", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "hallway", "Name": "hallway_table", "Display": "gueridon", "Description": "A small table with a vase and some flowers", "Hidden": ("key", "c"), "Exploration": 0},
                    {"Room": "bathroom", "Name": "bathroom_sink", "Display": "sink", "Description": "An enamel wash bassin", "Hidden": ("mouthwash", "c"), "Exploration": 0},
                    {"Room": "bathroom", "Name": "bathroom_cupboard", "Display": "bathroom cabinet", "Description": "A small cabinet containing toiletries", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "bathroom", "Name": "bathroom_cupboard_2", "Display": "undersink cupboard", "Description": "A cupboard under the sink containing household cleaning products", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "office", "Name": "office_desk", "Display": "desk", "Description": "A large oak desk with some drawers", "Hidden": ("incantation", "k"), "Exploration": 0},
                    {"Room": "office", "Name": "office_chair", "Display": "chair", "Description": "A large leather chair", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "office", "Name": "office_shelf", "Display": "bookshelf", "Description": "A tall and wide shelf full of files", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "bedroom", "Name": "bedroom_bed", "Display": "bed", "Description": "A king size bed with lovely linen", "Hidden": ("feather", "k"), "Exploration": 0},
                    {"Room": "bedroom", "Name": "bedroom_nightstand", "Display": "nightstand", "Description": "A small and nice pine table", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "bedroom", "Name": "bedroom_wardrobe", "Display": "wardrobe", "Description": "A massive pine wardrobe", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "cabinet", "Name": "cabinet_left", "Display": "hangers", "Description": "A huge and long rack, full of clothes on hangers", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "cabinet", "Name": "cabinet_right", "Display": "drawers", "Description": "A set of drawers, full of folded garnments", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "den", "Name": "den_table", "Display": "coffee table", "Description": "A long coffee table", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "den", "Name": "den_pool", "Display": "pool table", "Description": "A standard pool table", "Hidden": ("billiard ball", "c"), "Exploration": 0},
                    {"Room": "den", "Name": "den_enter", "Display": "entertainment centre", "Description": "A massive and complete entertainment centre", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "den", "Name": "den_sofa", "Display": "sofa", "Description": "A large and comfortable velvet sofa", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "library", "Name": "lib_reclining", "Display": "reclining armchair", "Description": "A lovely reclining armchair, ideal for reading", "Hidden": ("magnifying glass", "k"), "Exploration": 0},
                    {"Room": "library", "Name": "lib_bookshelf_1", "Display": "tall bookshelf", "Description": "A long bookshelf covering the entire wall, packed with innumerable books", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "library", "Name": "lib_bookshelf_2", "Display": "short bookshelf", "Description": "A smaller bookshelf near the reclining chair", "Hidden": ("nothing", "0"), "Exploration": 0}]
                return bfurn_data
            def basic_characters():
                bchar_data = [{"Name": "Dave", "Type": "Enemy", "Room": "pantry", "Description": "zombie", "Conversation": ("Argh, brains...", "Ooh smelly cheese!", "Blades are bad!"), "Submit_to": "airfreshener", "Kill_by": "knife", "Convert_with": "billiard ball", "St_concede": 0, "St_killed": 0, "St_converted": 0},
                    {"Name": "Drac", "Type": "Enemy", "Room": "office", "Description": "vampire", "Conversation": ("Blood! Blood! Blood!", "I don't like suntanning!", "Not a fan of French cuisine either!"), "Submit_to": "sun lamp", "Kill_by": "garlic", "Convert_with": "mouthwash", "St_concede": 0, "St_killed": 0, "St_converted": 0},
                    {"Name": "Henzel", "Type": "Enemy", "Room": "bathroom", "Description": "witch", "Conversation": ("By the eyes of newt...", "I am allergic to fairy dust", "A spell can be a nasty thing."), "Submit_to": "fairy dust", "Kill_by": "incantation", "Convert_with": "wooden spoon", "St_concede": 0, "St_killed": 0, "St_converted": 0},
                    {"Name": "Ricky", "Type": "Enemy", "Room": "dining_hall", "Description": "clown", "Conversation": ("Come here, let me tickle you!", "I am all for laughing and being wild", "My favorite cheese is probably the laughing cow"), "Submit_to": "whip", "Kill_by": "feather", "Convert_with": "cheese", "St_concede": 0, "St_killed": 0, "St_converted": 0},
                    {"Name": "Franky", "Type": "Enemy", "Room": "corridor", "Description": "monster", "Conversation": ("Kill! Smash! Destroy!", "Fire bad, very bad!", "Sometimes, I cross my wires!"), "Submit_to": "remote control", "Kill_by": "matches", "Convert_with": "key", "St_concede": 0, "St_killed": 0, "St_converted": 0},
                    {"Name": "Scary", "Type": "Enemy", "Room": "cabinet", "Description": "scarecrow", "Conversation": ("Come and rest on my hay, he he he!", "You know you can make fire using a magnifying glass?", "Nobody saw my hat :-("), "Submit_to": "pitchfork", "Kill_by": "magnifying glass", "Convert_with": "hat", "St_concede": 0, "St_killed": 0, "St_converted": 0},
                    {"Name": "Greg", "Type": "Friend", "Room": "den", "Description": "angel", "Conversation": ("May peace be upon you :)", "I am not afraid of zombies.", "Let me give you some air freshener."), "Submit_to": "air freshener", "Kill_by": "g", "Convert_with": "Dave", "St_concede": 0, "St_killed": 0, "St_converted": 0},
                    {"Name": "Liz", "Type": "Friend", "Room": "library", "Description": "librarian", "Conversation": ("How lovely to see you.", "Vampirism is such an ugly disease.", "Here is a sun lamp to help you."), "Submit_to": "sun lamp", "Kill_by": "g", "Convert_with": "Drac", "St_concede": 0, "St_killed": 0, "St_converted": 0},
                    {"Name": "Heather", "Type": "Friend", "Room": "ballroom", "Description": "fairy", "Conversation": ("Beautiful and happy day to you", "Magic is wonderful", "Here is some fairy dust to help you win against magic!"), "Submit_to": "fairy dust", "Kill_by": "g", "Convert_with": "Henzel", "St_concede": 0, "St_killed": 0, "St_converted": 0},
                    {"Name": "Cathy", "Type": "Friend", "Room": "kitchen", "Description": "lion tamer", "Conversation": ("Hiya. Hope you are doing great!", "Bozos are really not funny :-(", "I gift you this whip to get things cracking!"), "Submit_to": "whip", "Kill_by": "g", "Convert_with": "Ricky", "St_concede": 0, "St_killed": 0, "St_converted": 0},
                    {"Name": "Ruppert", "Type": "Friend", "Room": "hallway", "Description": "scientist", "Conversation": ("Hello, how do you do?", "Nothing cannot be solved with the help of science", "I think this remote control will help you if you ever get into trouble."), "Submit_to": "remote control", "Kill_by": "g", "Convert_with": "Franky", "St_concede": 0, "St_killed": 0, "St_converted": 0},
                    {"Name": "Mike", "Type": "Friend", "Room": "bedroom", "Description": "farmer", "Conversation": ("All right? what's up?", "Load of things to do on the farm! never any rest", "You can never get by without a pitchfork!"), "Submit_to": "pitchfork", "Kill_by": "g", "Convert_with": "Scary", "St_concede": 0, "St_killed": 0, "St_converted": 0}]
                return bchar_data
            return basic_house(), basic_furniture(), basic_characters()
        def extended_game():
            def extended_house():
                ehouse_data = [{"Name": "ballroom", "Display": "Dining room", "Description": "A large and wide empty room with a splendid flooring and magnificent chandeliers.", "Explored": 0, "Searched": 0},
                    {"Name": "vestibule", "Display": "Vestibule", "Description": "A small rooom, a vestibule leading from the dining hall to the living room, fitted with side wardrobes and hangers.", "Explored": 0, "Searched": 0},
                    {"Name": "corridor", "Display": "Corridor", "Description": "A long and narrow passage leading to the east wing of the house.", "Explored": 0, "Searched": 0},
                    {"Name": "den", "Display": "Entertainment room", "Description": "A very large room with a pool table, an entertainment center, an oval coffee table and a great five seater leather sofa.", "Explored": 0, "Searched": 0},
                    {"Name": "dining_hall", "Display": "Dining hall", "Description": "A rather large room, with a grandiose dining table able to sit 8 peoples, surrounded by furniture covered walls displaying magnificent tableware.", "Explored": 0, "Searched": 0},
                    {"Name": "stairwell", "Display": "Bottom stairwell", "Description": "A stairwell between the ground floor and top floor.", "Explored": 0, "Searched": 0},
                    {"Name": "hallway", "Display": "Hallway", "Description": "The centre of the house, the intersection between the east and west wings and upstairs.", "Explored": 0, "Searched": 0},
                    {"Name": "kitchen", "Display": "Kitchen", "Description": "A room full of light and mouth-watering scents.", "Explored": 1, "Searched": 0},
                    {"Name": "library", "Display": "Library", "Description": "A cosy room filled with bookshelves and a reading area.", "Explored": 0, "Searched": 0},
                    {"Name": "livingroom", "Display": "Living-room", "Description": "A cosy room fitted with chairs and a sofa, a nice tea table to enjoy tea or coffee after meals.", "Explored": 0, "Searched": 0},
                    {"Name": "office", "Display": "Office", "Description": "A room organised around a large glass desk, with a beautiful chair and many filling cabinets.", "Explored": 0, "Searched": 0},
                    {"Name": "pantry", "Display": "Pantry", "Description": "A small dark room with shelves.", "Explored": 0, "Searched": 0},
                    {"Name": "bathroom", "Display": "Bathroom", "Description": "The main bathroom of the house with a couple of cabinets.", "Explored": 0, "Searched": 0},
                    {"Name": "boudoir", "Display": "Boudoir", "Description": "A room reserved for the lady of the house.", "Explored": 0, "Searched": 0},
                    {"Name": "laundry", "Display": "Laundry room", "Description": "A room whiA magnificent and well-organised walk-in cabinet displaying well pressed expensive garnments and shoes.", "Explored": 0, "Searched": 0},
                    {"Name": "children", "Display": "Children bedroom", "Description": "The children's bedroom, fitted with a double-decker bed, a wardrobe and some toy chests.", "Explored": 0, "Searched": 0},
                    {"Name": "ensuite", "Display": "Private bathroom", "Description": "A bathroom reserved for guests.", "Explored": 0, "Searched": 0},
                    {"Name": "guestroom", "Display": "Guest bedroom", "Description": "A large bedroom set aside for welcoming house guests.", "Explored": 0, "Searched": 0},
                    {"Name": "landing", "Display": "Landing", "Description": "This is the centre of the top floor.", "Explored": 0, "Searched": 0},
                    {"Name": "master", "Display": "Master bedroom", "Description": "A large bedroom, fitted with a large king size bed and some wardrobes, reserved for the master of the house.", "Explored": 0, "Searched": 0},
                    {"Name": "nursery", "Display": "Nursery", "Description": "A smaller bedroom, converted into a nursery with a cradle, a rocking chair and amazingly decorated walls.", "Explored": 0, "Searched": 0},
                    {"Name": "powderroom", "Display": "Powder-room", "Description": "A room reserved for lady guests.", "Explored": 0, "Searched": 0},
                    {"Name": "shower", "Display": "Shower", "Description": "The largest bathroom in the house.", "Explored": 0, "Searched": 0},
                    {"Name": "toilet", "Display": "Toilet", "Description": "A small privy room for the master bedroom.", "Explored": 0, "Searched": 0}]
                return ehouse_data
            def extended_furniture():
                efurn_data=[{"Room": "ballroom", "Name": "ballroom_armchair", "Display": "armchair", "Description": "A comfortable, impressive and luxurious leather armchair", "Hidden": ("perfume", "c"), "Exploration": 0},
                    {"Room": "ballroom", "Name": "ballroom_sofa", "Display": "reclining sofa", "Description": "A three-sitter reclining sofa covered in a lovely purple velvet", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "vestibule", "Name": "coat_hanger", "Display": "coat rack", "Description": "A long hanging rack for coats and garnments, along the north wall", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "vestibule", "Name": "bulk_cupboard", "Display": "bulk storage cupboard", "Description": "A complex set of drawers and cupboards set along the south wall", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "den", "Name": "den_pool", "Display": "pool table", "Description": "A standard pool table", "Hidden": ("cattle prod", "c"), "Exploration": 0},
                    {"Room": "den", "Name": "den_enter", "Display": "entertainment centre", "Description": "A massive and complete entertainment centre", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "den", "Name": "den_sofa", "Display": "sofa", "Description": "A large and comfortable velvet sofa", "Hidden": ("sun lamp", "c"), "Exploration": 0},
                    {"Room": "dining_hall", "Name": "dining_table", "Display": "dining table", "Description": "A long oval wooden well-polished table with 8 chairs", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "dining_hall", "Name": "dining_draw_1", "Display": "commode", "Description": "A tall 8 drawers wooden commode", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "dining_hall", "Name": "dining_draw_2", "Display": "set of drawers", "Description": "A medium size set of 4 drawers", "Hidden": ("air freshener", "c"), "Exploration": 0},
                    {"Room": "stairwell", "Name": "wooden_chest", "Display": "wooden chest", "Description": "A small wooden chest", "Hidden": ("silver spoon", "k"), "Exploration": 0},
                    {"Room": "hallway", "Name": "hallway_table", "Display": "gueridon", "Description": "A small table with a vase and some flowers", "Hidden": ("whip", "c"), "Exploration": 0},
                    {"Room": "kitchen", "Name": "kitchen_table", "Display": "kitchen table", "Description": "A small round table with 3 chairs", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "kitchen", "Name": "kitchen_sink", "Display": "kitchen sink", "Description": "A standard kitchen sink", "Hidden": ("ax", "k"), "Exploration": 0},
                    {"Room": "kitchen", "Name": "kitchen_oven", "Display": "oven", "Description": "A beautiful fan oven", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "kitchen", "Name": "kichen_draw", "Display": "drawers", "Description": "A set of drawers", "Hidden": ("garlic", "k"), "Exploration": 0},
                    {"Room": "kitchen", "Name": "kitchen_fridge", "Display": "fridge", "Description": "A double-door fridge", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "kitchen", "Name": "kitchen_dishwasher", "Display": "dishwasher", "Description": "A dishwasher with its door ajar", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "library", "Name": "lib_reclining", "Display": "reclining armchair", "Description": "A lovely reclining armchair, ideal for reading", "Hidden": ("remote control", "c"), "Exploration": 0},
                    {"Room": "library", "Name": "lib_bookshelf_1", "Display": "tall bookshelf", "Description": "A long bookshelf covering the entire wall, packed with innumerable books", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "library", "Name": "lib_bookshelf_2", "Display": "short bookshelf", "Description": "A smaller bookshelf near the reclining chair", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "livingroom", "Name": "liv_table", "Display": "coffee table", "Description": "An oval glass coffee table", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "livingroom", "Name": "liv_set", "Display": "side table", "Description": "A side table between the two armchairs", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "livingroom", "Name": "liv_arm_1", "Display": "left armchair", "Description": "A comfortable armchair with a tall back, part of a set", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "livingroom", "Name": "liv_arm_2", "Display": "right armchair", "Description": "A comfortable armchair with a tall back, part of a set", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "livingroom", "Name": "liv_commode", "Display": "commode", "Description": "A wooden commode to store tea cups and board games", "Hidden": ("leather belt", "c"), "Exploration": 0},
                    {"Room": "office", "Name": "office_desk", "Display": "desk", "Description": "A large oak desk with some drawers", "Hidden": ("matches", "k"), "Exploration": 0},
                    {"Room": "office", "Name": "office_chair", "Display": "chair", "Description": "A large leather chair", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "office", "Name": "office_shelf", "Display": "bookshelf", "Description": "A tall and wide shelf full of files", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "pantry", "Name": "shelf_1", "Display": "shelf", "Description": "a shelf full of small boxes", "Hidden": ("pitch fork", "c"), "Exploration": 0},
                    {"Room": "bathroom", "Name": "bathroom_sink", "Display": "sink", "Description": "An enamel wash bassin", "Hidden": ("trumpet", "c"), "Exploration": 0},
                    {"Room": "bathroom", "Name": "bathroom_cupboard", "Display": "bathroom cabinet", "Description": "A small cabinet containing toiletries", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "bathroom", "Name": "bathroom_cupboard_2", "Display": "undersink cupboard", "Description": "A cupboard under the sink containing household cleaning products", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "boudoir", "Name": "boudoir_chair", "Display": "chair", "Description": "A stylish forged iron chair with a red velvet sit", "Hidden": ("dagger", "k"), "Exploration": 0},
                    {"Room": "boudoir", "Name": "boudoir_table", "Display": "desk", "Description": "A make-up desk with a mirror surrounded by lights and some drawers", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "boudoir", "Name": "boudoir_chest", "Display": "chest", "Description": "A small chest looking like a small barrel", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "laundry", "Name": "laundry_washer", "Display": "washing machine", "Description": "A standard american style washing machine", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "laundry", "Name": "laundry_drier", "Display": "drier", "Description": "A standard american style drier", "Hidden": ("incantation", "k"), "Exploration": 0},
                    {"Room": "laundry", "Name": "landry_hampster", "Display": "hampster", "Description": "A large bamboo hampster", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "laundry", "Name": "laundry_cupboard", "Display": "cupboard", "Description": "An ordinary looking  cupboard", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "laundry", "Name": "laundry_iron", "Display": "ironing board", "Description": "A large ironing board to press iron", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "children", "Name": "children_twin", "Display": "twin bed", "Description": "A double decker bed", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "children", "Name": "children_chair_1", "Display": "chair", "Description": "A small computer chair", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "children", "Name": "children_desk_1", "Display": "desk", "Description": "A small computer desk", "Hidden": ("magnifying glass", "k"), "Exploration": 0},
                    {"Room": "children", "Name": "children_chair_2", "Display": "ergonomic chair", "Description": "A children size ergonomic chair", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "children", "Name": "children_desk_2", "Display": "table", "Description": "A school rectangular table", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "children", "Name": "children_wardorbe", "Display": "wardrobe", "Description": "A brightly coloured 6 feet long wardrobe", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "children", "Name": "children_chest", "Display": "chest", "Description": "A large toy chest with an open lid", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "ensuite", "Name": "ensuite_sink", "Display": "sink", "Description": "A designer pink marble sink", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "ensuite", "Name": "ensuite_shower", "Display": "shower", "Description": "A multijet shower", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "ensuite", "Name": "ensuite_bidet", "Display": "bidet", "Description": "A designer bidet, also in pink marble", "Hidden": ("salt", "c"), "Exploration": 0},
                    {"Room": "ensuite", "Name": "ensuite_pharmacy", "Display": "pharmacy cabinet", "Description": "A vintage pharmacy cabinet mounted above the sink", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "ensuite", "Name": "ensuite_toilet", "Display": "W.C.", "Description": "A designer toilet... in pink marble", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "guestroom", "Name": "guest_queen", "Display": "queen bed", "Description": "A beautifully crafted wooden quenn bed, covered with Egyptian cotton sheets and fluffy pillows", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "guestroom", "Name": "guest_nightstand_1", "Display": "nightstand", "Description": "An ivory top nightstand, part of a set", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "guestroom", "Name": "guest_nightstand_2", "Display": "nightstand", "Description": "An ivory top nightstand, the other part of the set", "Hidden": ("water", "k"), "Exploration": 0},
                    {"Room": "guestroom", "Name": "guest_wardrobe", "Display": "oak wardrobe", "Description": "An full oak wardrobe, magnificiently engraved", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "guestroom", "Name": "guest_desk", "Display": "desk", "Description": "A walnut polished writing table", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "guestroom", "Name": "guest_chair", "Display": "chair", "Description": "A cushioned chair", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "guestroom", "Name": "guest_armchair", "Display": "armchair", "Description": "A delicately embroided 18th century armchair", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "landing", "Name": "landing_gueridon", "Display": "gueridon table", "Description": "A sophisticated small table", "Hidden": ("fairy dust", "c"), "Exploration": 0},
                    {"Room": "master", "Name": "master_king", "Display": "king bed", "Description": "An impressive king size bed, with white Egyptian cotton linen and covers", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "master", "Name": "master_desk", "Display": "table", "Description": "A small but stylish writing table", "Hidden": ("mirror", "k"), "Exploration": 0},
                    {"Room": "master", "Name": "master_chair", "Display": "chair", "Description": "A minimalist wooden chair", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "master", "Name": "master_wardrobe", "Display": "wardrobe", "Description": "An impressive wardrobe almost hidding the southern wall", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "master", "Name": "master_stand", "Display": "nightstand", "Description": "A small and discreet nightstand", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "master", "Name": "master_drawer", "Display": "drawer", "Description": "A small squarish drawer, en lieu of a nightstand", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "nursery", "Name": "nursery_craddle", "Display": "craddle", "Description": "A simple wooden cradle", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "nursery", "Name": "nursery_horse", "Display": "rocking horse", "Description": "A toy rocking horse", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "nursery", "Name": "nursery_rocking", "Display": "rocking chair", "Description": "A lovingly hand-crafted wooden rocking chair", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "nursery", "Name": "nursery_drawer", "Display": "drawer", "Description": "A set of drawers", "Hidden": ("lighter", "c"), "Exploration": 0},
                    {"Room": "nursery", "Name": "nursery_table", "Display": "changing table", "Description": "A standard changing table", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "powderroom", "Name": "powder_chair", "Display": "stool", "Description": "A small but comfortable wooden stool", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "powderroom", "Name": "powder_table", "Display": "desk", "Description": "A make-up desk with a mirror surrounded by lights and some drawers", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "powderroom", "Name": "powder_chest", "Display": "chest", "Description": "A small chest looking like a dice", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "powderroom", "Name": "powder_hanger", "Display": "coat hanger", "Description": "A small rack to hang coats and clothes", "Hidden": ("knife", "k"), "Exploration": 0},
                    {"Room": "shower", "Name": "shower_sink", "Display": "sink", "Description": "A well designed enamel sink", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "shower", "Name": "shower_bath", "Display": "bath tube", "Description": "A large oval easy access bath tube", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "shower", "Name": "shower_cabinet", "Display": "cabinet", "Description": "A practical pharmacy and cosmetics cabinet", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "shower", "Name": "shower_hamper", "Display": "hamper", "Description": "A bamboo hamper", "Hidden": ("feather", "k"), "Exploration": 0},
                    {"Room": "shower", "Name": "shower_rack", "Display": "towel rack", "Description": "A self-heating towel rack", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "shower", "Name": "shower_cupboard", "Display": "cupboard", "Description": "A long and tall cupboard for toiletries", "Hidden": ("nothing", "0"), "Exploration": 0},
                    {"Room": "toilet", "Name": "toilet_cupboard", "Display": "cupboard", "Description": "A small cupboard for cleaning and hygienic products", "Hidden": ("stake", "k"), "Exploration": 0}]
                return efurn_data
            def extended_characters():
                echar_data = [{"Name": "Ricky", "Type": "Enemy", "Room": "master", "Description": "clown", "Conversation": ("Come here, let me tickle you!", "I am all for laughing and being wild", "My favorite cheese is probably the laughing cow"), "Submit_to": "whip", "Kill_by": "feather", "Convert_with": "cheese", "St_concede": 0, "St_killed": 0, "St_converted": 0},
                    {"Name": "Franky", "Type": "Enemy", "Room": "corridor", "Description": "monster", "Conversation": ("Kill! Smash! Destroy!", "Fire bad, very bad!", "Sometimes, I cross my wires!"), "Submit_to": "remote control", "Kill_by": "matches", "Convert_with": "key", "St_concede": 0, "St_killed": 0, "St_converted": 0},
                    {"Name": "Scary", "Type": "Enemy", "Room": "guestroom", "Description": "scarecrow", "Conversation": ("Come and rest on my hay, he he he!", "You know you can make fire using a magnifying glass?", "Nobody saw my hat :-("), "Submit_to": "pitch fork", "Kill_by": "magnifying glass", "Convert_with": "hat", "St_concede": 0, "St_killed": 0, "St_converted": 0},
                    {"Name": "Drac", "Type": "Enemy", "Room": "office", "Description": "vampire", "Conversation": ("Blood! Blood! Blood!", "I don't like suntanning!", "Not a fan of French cuisine either!"), "Submit_to": "sun lamp", "Kill_by": "garlic", "Convert_with": "mouthwash", "St_concede": 0, "St_killed": 0, "St_converted": 0},
                    {"Name": "Henzel", "Type": "Enemy", "Room": "livingroom", "Description": "witch", "Conversation": ("By the eyes of newt...", "I am allergic to fairy dust", "A spell can be a nasty thing."), "Submit_to": "fairy dust", "Kill_by": "incantation", "Convert_with": "wooden spoon", "St_concede": 0, "St_killed": 0, "St_converted": 0},
                    {"Name": "Dave", "Type": "Enemy", "Room": "toilet", "Description": "zombie", "Conversation": ("Argh, brains...", "Ooh smelly cheese!", "Blades are bad!"), "Submit_to": "air freshener", "Kill_by": "knife", "Convert_with": "billiard ball", "St_concede": 0, "St_killed": 0, "St_converted": 0},
                    {"Name": "Impy", "Type": "Enemy", "Room": "stairwell", "Description": "imp", "Conversation": ("Hi! Hi! He! He! Ha! Ha!", "When they sent me from hell, they did not tell me the world was so beautiful.", "There is nothing better than a big juicy steak!"), "Submit_to": "salt", "Kill_by": "water", "Convert_with": "steak", "St_concede": 0, "St_killed": 0, "St_converted": 0},
                    {"Name": "Haidan", "Type": "Enemy", "Room": "pantry", "Description": "ghoul", "Conversation": ("Come to me and give me your soul!", "I need people souls because I am so lonely.", "Without this dream catcher, I would not be able to sleep nightmare free."), "Submit_to": "trumpet", "Kill_by": "stake", "Convert_with": "dreamcatcher", "St_concede": 0, "St_killed": 0, "St_converted": 0},
                    {"Name": "Shawn", "Type": "Enemy", "Room": "ensuite", "Description": "werewolf", "Conversation": ("a-oooooo!!!", "I am glad full moon is only three days every months.", "I love chew toys, they are hours of fun!"), "Submit_to": "perfume", "Kill_by": "silver spoon", "Convert_with": "chew toy", "St_concede": 0, "St_killed": 0, "St_converted": 0},
                    {"Name": "Riskit", "Type": "Enemy", "Room": "boudoir", "Description": "goblin", "Conversation": ("Braeunk vhos trolkh", "Living underground is terrible. I wish I could always be around people.", "Emeralds are the most powerful gem one can have."), "Submit_to": "leather belt", "Kill_by": "dagger", "Convert_with": "emerald", "St_concede": 0, "St_killed": 0, "St_converted": 0},
                    {"Name": "Gnarlug", "Type": "Enemy", "Room": "bathroom", "Description": "orc", "Conversation": ("Anukh!", "The other orcs make fun of me because I am scared of fire.", "My brethens are going to be so proud of me for bringing back a human skull!"), "Submit_to": "lighter", "Kill_by": "ax", "Convert_with": "human skull", "St_concede": 0, "St_killed": 0, "St_converted": 0},
                    {"Name": "Haijen", "Type": "Enemy", "Room": "dining_hall", "Description": "troll", "Conversation": ("Ooh! Fresh meat", "I am afraid of thunder and lightning", "For us trolls, shiny things are a display of status and power."), "Submit_to": "cattle prod", "Kill_by": "mirror", "Convert_with": "shiny ring", "St_concede": 0, "St_killed": 0, "St_converted": 0},
                    {"Name": "Cathy", "Type": "Friend", "Room": "laundry", "Description": "lion tamer", "Conversation": ("Hiya. Hope you are doing great!", "Bozos are really not funny :-(", "I gift you this whip to get things cracking!"), "Submit_to": "cheese", "Kill_by": "g", "Convert_with": "Ricky", "St_concede": 0, "St_killed": 0, "St_converted": 0},
                    {"Name": "Rupert", "Type": "Friend", "Room": "powderroom", "Description": "scientist", "Conversation": ("Hello, how do you do?", "Nothing cannot be solved with the help of science", "I think this remote control will help you if you ever get into trouble."), "Submit_to": "key", "Kill_by": "g", "Convert_with": "Franky", "St_concede": 0, "St_killed": 0, "St_converted": 0},
                    {"Name": "Mike", "Type": "Friend", "Room": "landing", "Description": "farmer", "Conversation": ("All right? what's up?", "Load of things to do on the farm! never any rest", "You can never get by without a pitchfork!"), "Submit_to": "hat", "Kill_by": "g", "Convert_with": "Scary", "St_concede": 0, "St_killed": 0, "St_converted": 0},
                    {"Name": "Liz", "Type": "Friend", "Room": "nursery", "Description": "librarian", "Conversation": ("How lovely to see you.", "Vampirism is such an ugly disease.", "Here is a sun lamp to help you."), "Submit_to": "mouthwash", "Kill_by": "g", "Convert_with": "Drac", "St_concede": 0, "St_killed": 0, "St_converted": 0},
                    {"Name": "Heather", "Type": "Friend", "Room": "children", "Description": "fairy", "Conversation": ("Beautiful and happy day to you", "Magic is wonderful", "Here is some fairy dust to help you win against magic!"), "Submit_to": "wooden spoon", "Kill_by": "g", "Convert_with": "Henzel", "St_concede": 0, "St_killed": 0, "St_converted": 0},
                    {"Name": "Muriel", "Type": "Friend", "Room": "hallway", "Description": "angel", "Conversation": ("May peace be upon you :)", "I am not afraid of zombies.", "Let me give you some air freshener."), "Submit_to": "billiard ball", "Kill_by": "g", "Convert_with": "Dave", "St_concede": 0, "St_killed": 0, "St_converted": 0},
                    {"Name": "Ariel", "Type": "Friend", "Room": "ballroom", "Description": "sprite", "Conversation": ("Joyous day, great meeting you!", "I am a natural vegetarian and I really don't like or trust carnivores!", "Still, here is a steak to help you in your quest."), "Submit_to": "steak", "Kill_by": "g", "Convert_with": "Impy", "St_concede": 0, "St_killed": 0, "St_converted": 0},
                    {"Name": "Whisper", "Type": "Friend", "Room": "den", "Description": "will-o-wisp", "Conversation": ("Light, light, joy. Happy meeting!", "Music is good for the soul, it makes you stronger.", "I love art and craft. This dreamcatcher is so lovely. It looks perfect for you."), "Submit_to": "dreamcatcher", "Kill_by": "g", "Convert_with": "Haidan", "St_concede": 0, "St_killed": 0, "St_converted": 0},
                    {"Name": "Wolfslain", "Type": "Friend", "Room": "shower", "Description": "griffin", "Conversation": ("Hark! Friendly greetings.", "You know, not all monsters are bad. You just need to know how to meet them at the right time!", "I know it is currently fashionable to have pets. Here is something for yours ;-)"), "Submit_to": "chew toy", "Kill_by": "g", "Convert_with": "Shawn", "St_concede": 0, "St_killed": 0, "St_converted": 0},
                    {"Name": "Sihnion", "Type": "Friend", "Room": "vestibule", "Description": "elf", "Conversation": ("S Suilad my friend. ", "Us, people of the light are always fighting against those who dwell in darkness.", "Let me bestow upon you this emerald."), "Submit_to": "emerald", "Kill_by": "g", "Convert_with": "Riskit", "St_concede": 0, "St_killed": 0, "St_converted": 0},
                    {"Name": "Samgel", "Type": "Friend", "Room": "library", "Description": "hobbit", "Conversation": ("Good morrow to you! Always nice to meet a kindred spirit.", "You have to be careful in your travel, particularly when meeting orcs!", "I know it does not look like much, but this skull is the skull of the last person who went on your quest!"), "Submit_to": "human skull", "Kill_by": "g", "Convert_with": "Gnarlug", "St_concede": 0, "St_killed": 0, "St_converted": 0},
                    {"Name": "Eric", "Type": "Friend", "Room": "kitchen", "Description": "dwarf", "Conversation": ("Gamut manun young hero. How are you faring?", "Never trust anything that lurks in the shadows under bridges!", "Take this shiny ring. it willalways defeat greed."), "Submit_to": "shiny ring", "Kill_by": "g", "Convert_with": "Haijen", "St_concede": 0, "St_killed": 0, "St_converted": 0}]
                return echar_data
            return extended_house(), extended_furniture(), extended_characters()
        #read common section for all types of games
        # rules and options
        myrules, myoptions = commontext()
        #write all json files
        #common section [rules and options]
        cls.writefiles('befriender_rules.json', myrules)
        cls.writefiles('befriender_options.json', myoptions)

        #for new game, read
        #basic data or extended data (player's choice)
        if GameInfo.continued == 0:
            if val == 1:
                house, furniture, characters = basic_game()
            else:
                house, furniture, characters = extended_game()
        #write game specific data [basic or extended]
        #(only new game)
            cls.writefiles('room_details.json', house)
            cls.writefiles('furn_data.json', furniture)
            cls.writefiles('character_data.json', characters)
        #read basic or extended common data
        #(either new game or continue)
        if val == 1:
            layout, enemies, carte = basic_environment()
        else:
            layout, enemies, carte = extended_environment()
        #write generic data based on user mode selection [normal or extended]
        cls.writefiles('befriender_enemies.json', enemies)
        cls.writefiles('befriender_map.json', carte)
        cls.writefiles('house_layout.json', layout)
        cls.writefiles('room_details.json', house)
        cls.writefiles('furn_data.json', furniture)
        cls.writefiles('character_data.json', characters)

    @classmethod
    def writefiles(cls, filename, data):
        with open(filename, 'w') as fhand:
            json.dump(data, fhand)

    @classmethod
    def savedata(cls):
        #get existing room data
        room_data = []
        for k, v in GameInfo.House_dict.items():
            room_data.append(Room.extractroomstructure(v, k))
            if GameInfo.House_dict[k] == GameInfo.current_room:
                cur_room = k
        #get existing furniture data
        furniture_data = []
        for k, v in GameInfo.Furn_dict.items():
            furniture_data.append(Furniture.extractfurniturestructure(v, k))
        #get existing character data
        character_data = []
        for k, v in GameInfo.Ch_dict.items():
            character_data = GameInfo.extractcharacter()
        #get the current game settings
        game_setting = [{"Mode": GameInfo.mode},
            {"Lives": GameInfo.lives},
            {"Health": GameInfo.health},
            {"Potential": GameInfo.potentialfriends},
            {"Converts": str(Enemy.converts)},
            {"CurrentRoom": cur_room},
            {"Inventory": GameInfo.myitems}]
        #write all current data to json files
        cls.writefiles('befriender_settings.json', game_setting)
        cls.writefiles('room_details.json', room_data)
        cls.writefiles('furn_data.json', furniture_data)
        cls.writefiles('character_data.json', character_data)


