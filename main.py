#-------------------------------------------------------------------------------
# Name:        main
# Purpose:     RPG game to learn classes and data handling
#
# Author:      Hacène Dramchini
#
# Created:     26/10/2020
# Copyright:   (c) Hacène Dramchini 2020
# Licence:     Free to use and distribute
#-------------------------------------------------------------------------------

import sys
import json
#from JSON_writer import Create
from gameinfo import GameInfo, Create
from architecture_class import Room, Furniture
from character import Enemy, Friend

def main():
    def previous():
        try:
            open('befriender_settings.json', 'r')
            continuegame = True
        except:
            continuegame = False
        return continuegame

    Befriender = GameInfo()

    if previous() == True:
        inp = input('You have a saved game. Do you want to continue it? (y/n) > ')
        if inp == 'y':
            current_room_name = GameInfo.continuepreviousgame()
        else:
            current_room_name = GameInfo.newgame()
    else:
        current_room_name = GameInfo.newgame()

    GameInfo.getgamedata(GameInfo.filelist, current_room_name)
    GameInfo.set_default_room()

    if GameInfo.continued == 0:
        GameInfo.readrules(Befriender)
        GameInfo.definelevel()
    else:
        print('************************************************')
        print('*                Welcome back!                 *')
        print('************************************************')


    optionlist = list()

    """
    start the new room and its inhabitant
    """
    if GameInfo.continued == 0:
        GameInfo.current_room = GameInfo.defaultroom()
    else:
        GameInfo.current_room.describe()

    while GameInfo.lives > 0:
        GameInfo.banner()
        """
        checks if there is a character in the room
        for all cases, defines command options and the explore status of the room
        """
        stg = GameInfo.current_room.get_ch_det()
        inh_profile = stg[0]
        inhabitant = GameInfo.current_room.get_character()
        if inhabitant is not None:
            """
            checks the type of character
            """
            wtd = GameInfo.whatchoice(inhabitant, Room.current_room, GameInfo.myitems)
            command = wtd[0]
            optionlist = wtd[1]
        else:
            GameInfo.current_room.explored = 1
            if GameInfo.current_room.get_search() == 1:
                print('You already cleared and searched this room')
                optionlist = ['m']
                command = 'm'
            else:
                command = input(">  What do you want to do?\n\tMove (m)?\n\texplore (x)? > ")
                optionlist = ['m', 'x'] + GameInfo.generaloptionslist

        if command not in optionlist:
            """
            this section checks that the command is valid
            """
            print('\nSorry, no such command!')
            continue
        elif command == str.lower('m'):
            """
            this section deals with moving from room to room
            """
            #display possible moves
            moveoption = GameInfo.current_room.can_move(GameInfo.House_dict)
            GameInfo.changeroom(moveoption)
            continue

        elif command == str.lower('x'): #exploring sequence
            """
            this section defines searching for objects in the furniture (not already searched)
            """
            GameInfo.explore(Befriender, GameInfo.myitems)


        elif command == str.lower('t'): #talking sequence
            """
            this section defines the talk exchange with a friend and receiving a gift
            """
            GameInfo.speechsequence(Befriender, inhabitant, inh_profile, GameInfo.myitems)

        elif command == str.lower('f'): #fighting sequence
            """
            this section defines fighting with an enemy
            """
            if len(GameInfo.myitems) !=0:
                lives = GameInfo.lives
                myfight = GameInfo.rumble(Befriender, GameInfo.myitems, inhabitant, inh_profile[0], inh_profile[1])
                GameInfo.health = myfight[2]
                if lives > myfight[3]:
                    GameInfo.defaultroom()
                    GameInfo.lives = myfight[3]
                continue
            else:
                print('You cannot fight, your inventory is empty!')
                continue

        else:
            GameInfo.mainmenu(Befriender,command)
    print('not working')
    sys.exit(0)

if __name__ == '__main__':
    main()
    sys.exit()