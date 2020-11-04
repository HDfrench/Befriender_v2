from character import Enemy, Friend
class Room():
    current_room =''
    default_room = ''

    def __init__(self, refname):
        self.name = refname
        self.description = None
        self.linked_rooms = {}
        self.character = ()
        self.ch_det = list()
        self.furniture = {}
        if refname == 'Kitchen':
            self.explored = 1
        else:
            self.explored = 0
        self.searched = 0


    def set_name(self, room_name):
        self.name = room_name

    def get_name(self):
        return self.name

    def set_description(self, room_description):
        self.description = room_description

    def link_room(self, room_to_link, direction):
        """
        defines the layout (room linked to and direction
        this is a dictionary that contains a list = (target room objects, direction)
        """
        self.linked_rooms[str.lower(direction)] = room_to_link

    def set_furn(self, furn_ref, name, desc):
        """
        defines the pieces of furniture contained in the room
        this is a dictionary that contains a list = (funr_dict key, furn display name, furniture description)
        """
        self.furniture[str.lower(furn_ref)] = (name, desc)

    def set_character(self, new_character):
        """
        defines the character
        """
        self.character = new_character

    def get_character(self):
        return self.character

    def set_explored(self, val):
        self.explored = val

    def get_explored(self):
        return self.explored

    def set_searched(self, val):
        self.searched = val

    def get_searched(self):
        return self.searched

    def describe(self):
        #this function is to ensure the text is grammatically correct and correctly aligned
        def displaytext(part_1, part_2, val):
            if val == 1:
                maxstg = ' '*13
                cut = len(maxstg) - len(part_1)
                roottext = part_1 + maxstg[:cut] + "to the " + part_2
            else:
                stg = part_1[0] #<- part_1
                if stg[0] in ['a','e','i', 'o','u']:
                    root = 'an '
                elif part_1 == 'drawers':
                    root = 'some '
                else:
                    root = 'a '
                maxstg = ' '*25
                cut = len(maxstg) - (len(part_1) + len(root))
                roottext = '\t\t' + root + part_1 + maxstg[:cut] + part_2
            return roottext
        """
        this function displays all the attributes of the current room
        -- name and description
        -- architecture (links to other rooms)
        -- content
        """
        print('************************************************')
        print("You are in the", self.name,'\n************************************************')
        print('\t',self.description)
        if len(self.linked_rooms) !=0:
            print('\tYou can go:')
            for dr, rm in self.linked_rooms.items():
                if self.get_explored() == 0:
                    if rm.get_explored()==1:
                        print('\t\t', displaytext(dr, rm.name, 1))
                else:
                    print('\t\t', displaytext(dr, rm.name, 1))

        if len(self.furniture) !=0:
            print('\tIn this room, you can see:')
            for fr, desc in self.furniture.items():
                print(displaytext(desc[0], desc[1], 2))
        print('************************************************')
        if self.get_character() is not None:
            stg = self.get_ch_det()
            inh_profile = stg[0]
            stg = inh_profile[1]
            if stg[0] in ['a','e','i', 'o','u']:
                root = 'an'
            else:
                root = 'a'
            print('You can see\t', inh_profile[0], root, inh_profile[1])
            print('************************************************')


    def set_ch_det(self, ch_dic):
        self.ch_det = [(v.name, v.description) for k,v in ch_dic.items() if self.character == v]

    def get_ch_det(self):
        return self.ch_det

    def can_move(self, room_dic):
        """
        this function defines where the player can move to
        if the room contains an enemy, the player cannot
        go into unvisited rooms
        """
        print('\t********************************')
        a = 1
        moveoptions = list()
        mes = '\tYou can go:\n'
        for dr, rm in self.linked_rooms.items():
            for k, v in room_dic.items():
                if (rm.name == v.name) and (self.explored == 1 or v.explored == 1):
                    mes += '\t' + str(a) + ')\tthe ' + str.upper(dr) + ' to the ' + str.upper(v.name) + '\n'
                    moveoptions.append((a, dr, room_dic[k]))
                    a += 1
                    break
        if a>1:
            print(mes, '\t********************************')
        else:
            print('There is nowhere to go!')
        return moveoptions

    def move(self, direction, mydict):
        mv = False
        for  dr, val in self.linked_rooms.items():
            #stg_dr = str(dr[0])
            if dr == direction:
                for k,v in mydict.items():
                    if v == val:
                        mv = True
                        return self.linked_rooms[dr]
                        continue
        if mv == False:
            print('You cannot go that way!')
            return self

    def searchable(self, furn, r_name):
        """
        this function looks at what piece of furniture
        has not yet been seaarched
        """
        a = 1
        stg = str(self.name)
        nme = stg.replace(' ', '_')
        mes = 'You can look in:\n'
        Listfurn = list()
        for nm, tup in self.furniture.items():
            for k,v in furn.items():
                if v.explored == 0 and tup[0] == v.name and v.roomed ==r_name:
                    mes += '\t' + str(a) + ')\tthe ' + tup[0] + '\n'
                    Listfurn.append((a, nm,furn[nm]))
                    a += 1
        if a > 1:
            print(mes, '\t********************************')
        else:
            print('There is nothing more to find in this room!')
            self.set_explored(1)

        return Listfurn

    def search(self, furniture):
        print('You have found', furniture.hidden)
        return furniture.hidden

    #This function is to extract the current room data for saving the game
    def extractroomstructure(self, rf):
        mystg = {'Name': rf, 'Display': self.name, 'Description': self.description, "Explored": self.explored, "Searched": self.searched}
        return mystg


class Furniture():
    def __init__(self):
        self.name = None
        self.description = None
        self.hidden = list()
        self.roomed = None
        self.explored = 0

    def set_description (self, furniture_description):
        self.description = furniture_description

    def get_description (self, furniture_description):
        return self.description

    def set_name(self, furniture_name):
        self.name = furniture_name

    def get_name(self):
        return self.name

    def set_room(self, room_name):
        """
        defines the room the piece of furniture is in
        """
        self.roomed = room_name

    def get_room(self):
        return self.roomed

    def set_hidden(self, hidden_item):
        """
        defines the hidden object and its category (2 item list)
        """
        self.hidden = hidden_item

    def get_hidden(self):
        """
        gets the name of the hidden object
           first => object name
        """
        return self.hidden[0]

    def get_purpose(self):
        """
        gets the use of the hidden object
           second => object category (0, k or c)
        """
        return self.hidden[1]

    def set_explore(self, val):
        """
        defines whether the piece of furniture was explored
        """
        self.explored = val

    def get_explore(self):
        return self.explored

    def extractfurniturestructure(self, rf):
        mystg = {"Room": self.roomed, "Name": rf, "Display": self.name, "Description": self.description, "Hidden": self.hidden, "Exploration": self.explored}
        return mystg
