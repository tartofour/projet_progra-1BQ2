# -*- coding: utf-8 -*-

# TODO:
#
#   - Règles du jeu
#   - Change keybind

import random
import datetime

class Menu:

    separation_template = ("------------------------------------------------")

    def __init__(self, score_file="data.txt", game=None):
        self._score_file = score_file
        self._game = game

    def start_menu(self):
        launched_menu = 1

        while launched_menu:
            self.display_menu()
            try :
                user_input = input("Votre choix : ")
                assert user_input.lower() in ["1","2","q"]

            except AssertionError:
                print("Commande inconnue !")
                print(self.separation_template)

            if user_input == "1":
                self.setup_game()
                self._game.play()

            elif user_input == "2":
                self.display_scores()

            elif user_input.lower() == "q":
                print(self.separation_template)
                print("################## AU REVOIR ! #################")
                print(self.separation_template)
                launched_menu = 0

    def choose_difficulty(self):
        while 1:
            try:
                print(self.separation_template)
                difficulty = input("Choisissez un niveau de difficulté (1-2-3) : ")
                assert difficulty in ["1","2","3"]
                return int(difficulty)

            except AssertionError:
                print("Commande inconnue !")

    def create_player(self):
        while 1:
            try:
                print(self.separation_template)
                player_name = input("Entrez votre nom : ")
                assert len(player_name) >= 5 and len(player_name) <= 12
                player = Player(player_name)
                return player

            except AssertionError:
                print("Votre nom doit être composé de 5 à 12 caractères.")

    def setup_game(self):
        difficulty = self.choose_difficulty()
        player = self.create_player()
        game = Game(player, difficulty)
        game.create_enclosure_wall()
        player.position = game.random_legal_position
        self._game = game

    def display_menu(self):
        print(self.separation_template)
        print("##################### MENU #####################")
        print(self.separation_template)
        print("1. Lancer une partie")
        print("2. Afficher le tableau des scores")
        print("Q. Quitter le programme")
        print(self.separation_template)

    def display_scores(self):
        players_scores = {}

        try:
            with open(self._score_file, "r") as file:
                print(self.separation_template)
                print("############## TABLEAU DES SCORES ##############")
                print(self.separation_template)

                for line in file :
                    if line != "\n":
                        elements = line.rstrip('\n').split(":")
                        player_name = elements[0]
                        score = int(elements[1])

                        if player_name not in players_scores:
                            players_scores[player_name] = score
                        elif score > players_scores[player_name]:
                            players_scores[player_name] = score

                #Triage du dictionnaire (descendant) en fonction du score de chaque joueur
                sorted_players_scores  = dict(sorted(players_scores.items(), key=lambda x: x[1], reverse=True))

                # Affiche chaque ligne du classement
                print("Voici le classement des joueurs : \n")
                for i, player_score in enumerate(sorted_players_scores, 1):
                    print(i,"-", player_score, ":", sorted_players_scores[player_score])

        except FileNotFoundError:
            print("Aucun fichier de sauvegarde trouvé.")

class Game:
    def __init__(self, player, difficulty=1, game_state=1, items=None, zombies=None, walls=None):

        self._player = player
        self._difficulty = difficulty
        self._items = items or []
        self._zombies = zombies or []
        self._game_state = game_state

    def __str__(self):
        return "Partie de niveau " + str(self._difficulty) + ". Jouée par " + \
                self._player.name + "."

### getters & setters
    @property
    def player(self):
        return self._player

    @property
    def difficulty(self):
        return self._difficulty
    @difficulty.setter
    def difficulty(self, new_difficulty):
        self._difficulty = new_difficulty

    @property
    def items(self):
        return self._items
    @items.setter
    def items(self, new_items):
        self._items = new_items

    @property
    def zombies(self):
        return self._zombies
    @zombies.setter
    def zombies(self, new_zombies):
        self._zombies = new_zombies

    @property
    def game_state(self):
        return self._game_state
    @game_state.setter
    def game_state(self, new_game_state):
        self._game_state = new_game_state

    @property
    def walls(self):
        return self._walls
    @walls.setter
    def walls(self, new_walls):
        self._walls = new_walls

    @property # À enlever
    def starting_time(self):
        return _starting_time

##### methods #####
    @property
    def board_size(self):
        #return 24 // self._difficulty
        return 24

    @property
    def zombies_position(self):
        zombies_position = []
        hunters_position = []
        for zombie in self._zombies:
            if type(zombie) == Zombie:
                zombies_position.append(zombie._position)
            elif type(zombie) == Hunter:
                hunters_position.append(zombie._position)
        return {"zombies" : zombies_position, \
                "hunters" : hunters_position}

    @property
    def items_position(self):
        teleporters_positions = []
        candies_position = []
        traps_position = []
        walls_position = []

        for item in self._items:
            if type(item) == Teleporter:
                teleporters_positions.append(item.position)
                teleporters_positions.append(item.destination)
            elif type(item) == Candy:
                candies_position.append(item.position)
            elif type(item) == Trap:
                traps_position.append(item.position)
            elif type(item) == Wall:
                walls_position.append(item.position)

        return {"teleporters" : teleporters_positions, \
                "candies" : candies_position, \
                "traps" : traps_position, \
                "walls" : walls_position}

    @property
    def free_positions(self):
        free_positions = []
        for line in range(self.board_size):
            for col in range(self.board_size):
                free_positions.append((line,col))

        for item_type in self.items_position:
            for item_position in self.items_position[item_type]:
                if item_position in free_positions:
                    free_positions.remove(item_position)

        for zombie_type in self.zombies_position:
            for zombie_position in self.zombies_position[zombie_type]:
                if zombie_position in free_positions:
                    free_positions.remove(zombie_position)

        return free_positions

    @property
    def random_legal_position(self):
        return random.choice(self.free_positions)

    # Dessine le plateau
    def draw(self):
        for line in range(self.board_size):
            for col in range(self.board_size):
                if (line,col) == self.player.position :
                    print(Player.symbol,end=" ")
                elif (line,col) in self.zombies_position["hunters"]:
                    print(Hunter.symbol,end=" ")
                elif (line,col) in self.zombies_position["zombies"]:
                    print(Zombie.symbol,end=" ")
                elif (line,col) in self.items_position["walls"]:
                    print(Wall.symbol,end=" ")
                elif (line,col) in self.items_position["candies"]:
                    print(Candy.symbol,end=" ")
                elif (line,col) in self.items_position["teleporters"]:
                    print(Teleporter.symbol,end=" ")
                elif (line,col) in self.items_position["traps"]:
                    print(Trap.symbol,end=" ")
                else :
                    print(".",end=" ")
            print()
        print(Menu.separation_template)

    # Fait apparaitre un item
    def pop_items(self):
        if random.randint(1, self._difficulty*3) == 3 :
            new_teleporter_positions = self.random_legal_position, self.random_legal_position
            new_teleporter = Teleporter(new_teleporter_positions[0], new_teleporter_positions[1])
            self._items.append(new_teleporter)

        if random.randint(self._difficulty, 3) == 3 :
            new_trap_position = self.random_legal_position
            new_trap = Trap(new_trap_position)
            self._items.append(new_trap)

        if random.randint(self._difficulty, 3) == 3 :
            new_candy_position = self.random_legal_position
            new_candy = Candy(new_candy_position)
            self._items.append(new_candy)

    def pop_zombies(self):
        if random.randint(self._difficulty, 3) == 3 :
            new_zombie_position = self.random_legal_position
            new_zombie = Zombie(new_zombie_position)
            self._zombies.append(new_zombie)

        if random.randint(self._difficulty*2, 12) == 12 :
            new_hunter_position = self.random_legal_position
            new_hunter = Hunter(new_hunter_position)
            self._zombies.append(new_hunter)

    def create_enclosure_wall(self):
        for line in range(self.board_size):
                self.pop_wall((line, 0))
                self.pop_wall((line, self.board_size-1))
        for col in range(0,self.board_size):
                    self.pop_wall((0, col))
                    self.pop_wall((self.board_size-1, col))

    def pop_wall(self, position):
        if position in self.free_positions:
            new_wall = Wall(position)
            self._items.append(new_wall)

    # Regarde s'il y a un ou plusieurs items sur la position du joueur
    def check_items(self):
        for item in self._items:
            if type(item) == Teleporter and ((item.position == self._player.position) or\
            (item.destination == self._player.position)): # beurk
                item.teleport_player(self._player)
            if item.position == self._player.position :
                if type(item) == Candy:
                    item.score_increment(self._player)
                    self._items.remove(item)
                if type(item) == Trap:
                    item.inflict_damage(self._player)
                    self._items.remove(item)

    # regarde s'il y a un zombie sur la position du joueur
    def check_zombies(self):
        for zombie in self._zombies:
            if zombie._position == self.player.position :
                zombie.inflict_damage(self._player)
                self._zombies.remove(zombie)

    def is_position_walled(self, position):
        return position in self.items_position["walls"]

    # Joue un tour complet
    def play_turn(self):

        self.display_player_hud()
        self.draw()

        # Action du joueur
        old_position = self._player.position
        self._player.move(self)
        if self.is_position_walled(self._player.position):
            self._player.position = old_position

        # Déplacement des zombies
        for enemy in self._zombies:
            if type(enemy) == Hunter:
                enemy.move_towards_player(self._player)
            else:
                old_enemy_position = enemy.position
                free_positions = self.free_positions
                enemy.move()

                if enemy.position not in free_positions:
                    enemy.position = old_enemy_position

        # Check des collisions
        self.check_zombies()
        self.check_items()

        # Pop items et zombies
        self.pop_items()
        self.pop_zombies()

    def pause_menu(self):
        print(Menu.separation_template)
        print("##################### PAUSE #####################")
        print(Menu.separation_template)

        while 1:
            try:
                user_input = input("Appuyez sur \"p\" pour continuer : ")
                assert user_input == "p"
                print(Menu.separation_template)
                return 0

            except AssertionError:
                print("Commande inconnue !")
                print(Menu.separation_template)


    def display_help(self):
        print("------------------------------------------------")
        print("Bienvenue dans le menu aide !\n")
        print("Vous trouverez ici les commandes permettant d'intéragir avec le jeu. Vous trouverez également une légende des différents objets et zombies.\n")


        print("ASSIGNATION DES TOUCHES :")

        for command in Player.keyboard_keys:
            if Player.keyboard_keys[command] == (-1, 0):
                print(" -", command, ": Haut")
            elif Player.keyboard_keys[command] == (1, 0):
                print(" -", command, ": Bas")
            elif Player.keyboard_keys[command] == (0, -1):
                print(" -", command, ": Gauche")
            elif Player.keyboard_keys[command] == (0, 1):
                print(" -", command, ": Droite")
            elif Player.keyboard_keys[command] == "help":
                print(" -", command, ": Help")
            elif Player.keyboard_keys[command] == "pause":
                print(" -", command, ": Pause")
        print()
        print("REPRÉSENTATION DES ZOMBIES :")
        print(" -", Zombie.symbol, ": Zombies")
        print(" -", Hunter.symbol, ": Chasseurs volants")
        print()
        print("REPRÉSENTATION DES OBJETS")
        print(" -", Teleporter.symbol, ": Téléporteurs")
        print(" -", Trap.symbol, ": Pièges")
        print(" -", Candy.symbol, ": Bonbons")
        print(" -", Wall.symbol, ": Murs")
        print()
        print("ASTUCE")
        print(" - Si vous êtes poursuivit par des chasseurs volants, entrez dans un téléporteur !")

        self._player.pause_game(self)

    # Joue une partie complète
    def play(self):
        print(Menu.separation_template)
        print("############# DÉBUT DE LA PARTIE ###############")
        print(Menu.separation_template)
        print(self)

        end = self.end_time(1,0)
        now = datetime.datetime.today()

        while now < end :
            if self._game_state == 0:
                start_pause_date = datetime.datetime.today()
                self.pause_menu()
                end_pause_date = datetime.datetime.today()
                delta_pause = end_pause_date - start_pause_date
                end += delta_pause
                self._player.resume_game(self)

            else:
                self.play_turn()

            now = datetime.datetime.today()

        print("################ PARTIE TERMINÉE ###############")
        print(Menu.separation_template)

        # Enregistrement ou non du score du joueur
        if self._player.score > 0 :
            print("Félicitation {}, votre score est de : {}".format(self.player.name,self.player.score))
            self.save_score()
        else:
            print("Votre score est de {}. Réessayez ;-)".format(self.player.score))


    def save_score(self):
        with open("data.txt", "a") as scores:
            scores.write(self._player.name + ":" + str(self._player.score) + "\n")

    def display_player_hud(self):
        print(Menu.separation_template)
        print(self._player)
        print(Menu.separation_template)

    @staticmethod
    # retourne le moment où le jeu est censé être fini
    def end_time(delta_minute, delta_second):
        delta = datetime.timedelta(minutes=delta_minute, seconds=delta_second)
        end = datetime.datetime.today() + delta
        return end

class Player:

    keyboard_keys = {'z':(-1,0),\
                     's':(1,0),\
                     'q':(0,-1),\
                     'd':(0,1),\
                     'p':"pause",\
                     'h':"help"}

    symbol = "P"

    def __init__(self, name, position=(0,0), score=0):
        self._name = name
        self._position = position
        self._score = score

    def __str__(self):
        position_line, position_col = self._position
        return "Position de " + self._name + ": (Ligne : " + str(position_line) + \
                ", " + "Colone : " + str(position_col) + ")\n" + "Score : " + \
                str(self._score)


### getters & setters
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, new_name):
        self._name = new_name

    @property
    def position(self):
        return self._position
    @position.setter
    def position(self, new_position):
        self._position = new_position

    @property
    def score(self):
        return self._score
    @score.setter
    def score(self, new_score):
        self._score = new_score

#methods
    def move(self, game) :
        try:
            key = input("Déplacez-vous (\"h\" pour afficher l'aide) : ")
            assert key in Player.keyboard_keys.keys()

        except AssertionError:
            print("Commande inconnue !")
            print(Menu.separation_template)

        else: # ???
            pause_binding = list(Player.keyboard_keys.keys())[list(Player.keyboard_keys.values()).index("pause")] # beurk
            help_binding = list(Player.keyboard_keys.keys())[list(Player.keyboard_keys.values()).index("help")]

            if key == pause_binding:
                self.pause_game(game)
            elif key == help_binding:
                self.pause_game(game)  # ?????
                game.display_help()
            else:
                move = Player.keyboard_keys[key]
                self._position = (self._position[0] + move[0], self._position[1] + move[1])

    #def change_keybing(self):

    def pause_game(self, game):
        game.game_state = 0

    def resume_game(self, game):
        game.game_state = 1


class Item :
    symbol = "I"

    def __init__(self, position):
        self._position = position

    @property
    def position(self):
        return self._position
    @position.setter
    def position(self, new_position):
        self._position = new_position

class Teleporter(Item):
    symbol = "O"

    def __init__(self, position, destination):
        super().__init__(position)
        self._destination = destination

    @property
    def destination(self):
        return self._destination
    @destination.setter
    def destination(self, new_destination):
        self._destination = new_destination
        print(Menu.separation_template)

    def teleport_player(self, player):
        if player.position == self._position:
            player.position = self._destination
        elif player.position == self._destination:
            player.position = self._position

class Trap(Item):
    symbol="X"

    def __init__(self, position, damage=5):
        super().__init__(position)
        self._damage = damage

    @property
    def damage(self):
        return self._damage
    @damage.setter
    def damage(self, new_damage):
        self._damage = new_damage

    def inflict_damage(self, player):
        player.score -= self._damage

class Candy(Item):
    symbol="*"

    def __init__(self, position, value=5):
        super().__init__(position)
        self._value = value

    @property
    def value(self):
        return self._value
    @value.setter
    def value(self, new_value):
        self._value = new_value

    def score_increment(self, player):
        player.score += self._value


class Wall(Item):
    symbol="#"

    def __init__(self, position):
        super().__init__(position)


class Zombie:
    symbol="Z"
    move_set = {"up" : (-1,0),\
                "down" : (0,-1),\
                "left" : (1,0),\
                "right" : (0,1)}

    def __init__(self, position, damage=10) :
        self._position = position
        self._damage = damage

    @property
    def damage(self):
        return self._damage

    @property
    def position(self):
        return self._position
    @position.setter
    def position(self, new_position):
        self._position = new_position

#methods
    def move(self):
        zombie_line, zombie_col = self._position
        zombie_move = Zombie.move_set[random.choice(list(Zombie.move_set.keys()))]
        self._position = (zombie_line + zombie_move[0], zombie_col + zombie_move[1])

    def inflict_damage(self, player):
        player.score -= self._damage


class Hunter(Zombie):
    symbol="H"

    def __init__(self, position, damage=15):
        super().__init__(position, damage)

        self._damage = damage

    def move_towards_player(self, player):
        hunter_line, hunter_col = self._position
        player_line, player_col = player.position

        # Mouvement de ligne
        if hunter_line > player_line:
            hunter_line -= 1
        elif hunter_line < player_line:
            hunter_line += 1

        # Mouvement de colone
        elif hunter_col > player_col:
            hunter_col -= 1
        elif hunter_col < player_col:
            hunter_col += 1

        self._position = hunter_line, hunter_col

if __name__ == "__main__" :
    m =  Menu()
    m.start_menu()
