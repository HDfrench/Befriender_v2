class Character():

    def __init__(self, char_name, char_description, char_speech):
        """
        Create a character
        """
        self.name = char_name
        self.description = char_description
        self.conversation = char_speech

    def describe(self):
        """
         Describe this character
        """
        print( '\t\t', str.upper(self.name),"is here!\t", self.description )

    # Set what this character will say when talked to
    def set_conversation(self, conversation):
        self.conversation = conversation

    def talk(self):
        """
         Talk to this character
        """
        if self.conversation is not None:
            print("[" + self.name + " says]:", self.conversation,"\n")
        else:
            print(self.name + " doesn't want to talk to you")

    def fight(self, combat_item):
        """
         Fight with this character
        """
        print(self.name + " doesn't want to fight with you")
        return True

class Enemy(Character):
    converts = 0

    def __init__(self, char_name, char_description, char_speech, char_tools):
        super().__init__(char_name, char_description, char_speech)
        self.isscaredof = char_tools[0]
        self.iskilledby = char_tools[1]
        self.isconvertedby = char_tools[2]
        self.concedes = 0
        self.killed = 0
        self.befriended = 0

    #those next 3 functions are read only in the game so only get_
    def get_killedby(self):
        """
        what kills the enemy
        """
        return self.iskilledby

    def get_scaredof(self):
        """
        what scares it off
        """
        return self.isscaredof

    def get_convertswith(self):
        """
        what makes it a friend
        """
        return self.isconvertedby

    #those 3 functions are setting the character status post battle
    def set_killed(self,val):
        self.killed = val
    def get_killed(self):
        return self.killed

    def set_befriended(self, val):
        self.befriended = val
    def get_befriended(self):
        return self.befriended

    def set_concede(self, val):
        self.concedes = val
    def get_concede(self):
        return self.concedes

    def fight(self, combat_item, health, lives):
        """
        this function analyses the fight
        based on the item used
        """
        item = combat_item[0]
        isgift = combat_item[1]
        if item == self.iskilledby:
            print("\nYou kill ", self.name, " with the", item, '.\n', self.name, 'falls to the ground motionless.\n')
            self.set_killed(1)
            return (True, health, lives)
        elif item == self.isconvertedby:
            print('\nYour thoughtful gift changed', self.name, 'into a friend')
            self.set_befriended(1)
            Enemy.converts +=1
            return (True, health, lives)
        elif item == self.isscaredof:
            print('\n' + self.name, 'is terrified and cowers in a corner of the room.\n')
            self.set_concede(1)
            return (True, health, lives)
        else:
            # if the weapon used is not for this character
            #look at the category (c => convert, g => scared of, k => kill)
            if isgift == 'c':
                print('\n' + self.name, 'refuses your gift and attacks you!\n')
            elif isgift == 'g':
                print('\n' + self.name, 'is not afraid of the', item,'.\nYou receive a blow that throws you on the floor!\n')
            else:
                print('\nYour weapon has no effect on', self.name, 'who assaults you!\n')
            #reduce health and if health = 0 then reduce life
            health -= 3
            if health == 0:
                lives -= 1
                if lives != 0:
                    health = 9
                    print(self.name,"crushes you, puny adventurer.\nYou lose a life!\nlives remaining:", lives)

                else:
                    print('\t\tGAME OVER\t\t\nYou lie in a pool of your own blood, your skull smashed in.\n')
                    exit('Thank you for playing')

            return (False, health, lives)

class Friend(Character):
    def __init__(self, char_name, char_description, char_speech, char_gift):
        super().__init__(char_name, char_description, char_speech)
        self.given = 0
        self.gift = char_gift
        self.present = self.gift[0]

    def set_gift(self, present, target):
        self.gift = (present, target)
        self.set_present()

    def get_gift(self):
        """
        function to get the gift added to the player's item list
        """
        return self.gift

    def set_given(self, val):
        """
        function to define whether the gift has already been given
        """
        self.given = val

    def get_given(self):
        return self.given

    def talk(self):
        """
        defines the 3 part speech of the character
        """
        friendspeech = self.conversation
        return friendspeech
