import gamelib
import random
import math
import warnings
from sys import maxsize
import json


"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips: 

  - You can analyze action frames by modifying on_action_frame function

  - The GameState.map object can be manually manipulated to create hypothetical 
  board states. Though, we recommended making a copy of the map to preserve 
  the actual current map state.
"""

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        seed = random.randrange(maxsize)
        random.seed(seed)
        gamelib.debug_write('Random seed: {}'.format(seed))

    def on_game_start(self, config):
        """ 
        Read in config and perform any initial setup here 
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        self.flag=1
        global FILTER, ENCRYPTOR, DESTRUCTOR, PING, EMP, SCRAMBLER
        FILTER = config["unitInformation"][0]["shorthand"]
        ENCRYPTOR = config["unitInformation"][1]["shorthand"]
        DESTRUCTOR = config["unitInformation"][2]["shorthand"]
        PING = config["unitInformation"][3]["shorthand"]
        EMP = config["unitInformation"][4]["shorthand"]
        SCRAMBLER = config["unitInformation"][5]["shorthand"]
        # This is a good place to do initial setup
        #self.build_defences(game_state)
        self.scored_on_locations = []

    
        

    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        game_state.suppress_warnings(True)  #Comment or remove this line to enable warnings.

        self.starter_strategy(game_state)

        game_state.submit_turn()


    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safely be replaced for your custom algo.
    """


    def starter_strategy(self, game_state):
        #game_state.attempt_spawn(EMP, [24, 10], 3)
        """
        For defense we will use a spread out layout and 2 Scramblers early on.
        We will place destructors near locations the opponent managed to score on.
        For offense we will use long range EMPs if they place stationary units near the enemy's front.
        If there are no stationary units to attack in the front, we will send Pings to try and score quickly.
        """
        # First, place basic defenses
        self.build_defences(game_state)
        # Now build reactive defenses based on where the enemy scored
        #self.build_reactive_defense(game_state)

        # If the turn is less than 5, stall with Scramblers and wait to see enemy's base
        
        if game_state.turn_number < 5:
            self.stall_with_scramblers(game_state, count = 1)
            ## @dev steal tower

        else:
            # defend large attack, especially a chain of PING
            large_defense = self.scramblers_defend_large_attack(game_state)

            ## @dev steal tower
            if game_state.turn_number < 10 and large_defense == False:
                True
            
            # @dev big attack
            self.long_march(game_state)

            # this is starter's choice
            """
            # Now let's analyze the enemy base to see where their defenses are concentrated.
            # If they have many units in the front we can build a line for our EMPs to attack them at long range.
            if self.detect_enemy_unit(game_state, unit_type=None, valid_x=None, valid_y=[14, 15]) > 10:             ## @dev only y = 14, 15 ?????
                self.emp_line_strategy(game_state)
            else:
                # They don't have many units in the front so lets figure out their least defended area and send Pings there.

                # Only spawn Ping's every other turn
                ## @dev I don't like this ping strategy need to check it
                # Sending more at once is better since attacks can only hit a single ping at a time
                if game_state.turn_number % 2 == 1:
                    # To simplify we will just check sending them from back left and right
                    ping_spawn_location_options = [[13, 0], [14, 0]]
                    best_location = self.least_damage_spawn_location(game_state, ping_spawn_location_options)
                    game_state.attempt_spawn(PING, best_location, 1000)

                # Lastly, if we have spare cores, let's build some Encryptors to boost our Pings' health.
                encryptor_locations = [[13, 2], [14, 2], [13, 3], [14, 3]]
                game_state.attempt_spawn(ENCRYPTOR, encryptor_locations)

            """

    def build_defences(self, game_state):
        """
        Build basic defenses using hardcoded locations.
        Remember to defend corners and avoid placing units in the front where enemy EMPs can attack them.
        """
        # Useful tool for setting up your base locations: https://www.kevinbai.design/terminal-map-maker
        # More community tools available at: https://terminal.c1games.com/rules#Download

        # Place destructors that attack enemy units
        destructor_locations = [[0, 13], [1, 12], [25, 12], [26, 12], [2, 11]]
        # attempt_spawn will try to spawn units if we have resources, and will check if a blocking unit is already there
        
        # Place filters in front of destructors to soak up damage for them
        #filter_locations = [[1, 13], [3, 13], [12, 13], [15, 13], [18, 13], [21, 13], [24, 13], [26, 13]]
        game_state.attempt_spawn(DESTRUCTOR, destructor_locations)
        #game_state.attempt_spawn(FILTER, filter_locations)
        
        
        encryptor_locations2 = [[4, 12], [5, 12], [7, 12], [8, 12], [10, 12], [11, 12], \
             [13, 12], [14, 12], [16, 12], [17, 12], [19, 12], [20, 12], [22, 12], [23, 12], [25, 12], [26, 12]]
        filter_locations2=[[1, 13], [2, 13], [4, 13], [6, 13], [9, 13], [12, 13], [15, 13], [18, 13], [21, 13],\
             [24, 13], [25, 13], [26, 13], [27, 13]]
        encryptor_locations2=sorted(encryptor_locations2, key= lambda a:a[1], reverse=True)
        filter_locations2=sorted(filter_locations2, key= lambda a:a[1], reverse=True)
        destructor_locations2=sorted(destructor_locations, key= lambda a:a[1], reverse=True)
        self.flag=1
        for i in encryptor_locations2:
            if not game_state.contains_stationary_unit(i) and game_state.turn_number<3:
                self.flag=0

        encryptor_locations3=[[3, 10], [4, 10], [5, 10], [6, 10], [10, 10], [11, 10], [16, 10], [17, 10], [18, 10],[7, 10], [8, 10], [9, 10], [12, 10], [13, 10], [14, 10], [15, 10], [19, 10], [20, 10]]
        
        if game_state.turn_number>0:
            if self.flag==0:
                game_state.attempt_spawn(ENCRYPTOR, encryptor_locations2)
            if self.flag==1:
                game_state.attempt_spawn(DESTRUCTOR, encryptor_locations2)
            game_state.attempt_spawn(FILTER, filter_locations2)
            game_state.attempt_spawn(DESTRUCTOR, destructor_locations2)
            if game_state.get_resource(game_state.CORES)>10:
                game_state.attempt_spawn(ENCRYPTOR, encryptor_locations3)    
        
        if game_state.turn_number>5:
            dlocations2=[[4, 12], [5, 12], [22, 11], [23, 11], [24, 11], [25, 11], [7, 10], [8, 10], [9, 10],\
                 [12, 10], [13, 10], [14, 10], [15, 10], [19, 10], [20, 10]]
            dlocations2=sorted(dlocations2, key= lambda a:a[1], reverse=True)
            i=0
            while game_state.get_resource(game_state.CORES)>10:
                if i==len(dlocations2):
                    break
                if game_state.contains_stationary_unit(dlocations2[i]):
                    game_state.attempt_remove(dlocations2[i])
                game_state.attempt_spawn(DESTRUCTOR, dlocations2[i] )
                i+=1
        
        if game_state.get_resource(game_state.BITS)>=12:
            elocations=[[13, 7], [14, 7], [15, 7], [13, 6], [14, 6], [15, 6]]
            game_state.attempt_spawn(ENCRYPTOR, elocations )

        
        
        
        
        

    def build_reactive_defense(self, game_state):
        """
        This function builds reactive defenses based on where the enemy scored on us from.
        We can track where the opponent scored by looking at events in action frames 
        as shown in the on_action_frame function
        """
        for location in self.scored_on_locations:
            # Build destructor one space above so that it doesn't block our own edge spawn locations
            build_location = [location[0], location[1]+1]
            game_state.attempt_spawn(DESTRUCTOR, build_location)
            filter_location=[location[0], location[1]+2]
            game_state.attempt_spawn(FILTER, filter_location)

    def stall_with_scramblers(self, game_state, count = 3):
        """
        Send out Scramblers at random locations to defend our base from enemy moving units.
        """
        # count the total scrambler, default = 3 to save BITs

        # We can spawn moving units on our edges so a list of all our edge locations
        friendly_edges = game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_LEFT) + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)
        
        # Remove locations that are blocked by our own firewalls 
        # since we can't deploy units there.
        deploy_locations = self.filter_blocked_locations(friendly_edges, game_state)
        
        # While we have remaining bits to spend lets send out scramblers randomly.
        while count > 0 and game_state.get_resource(game_state.BITS) >= game_state.type_cost(SCRAMBLER) and len(deploy_locations) > 0:
            # Choose a random deploy location.
            deploy_index = random.randint(0, len(deploy_locations) - 1)
            deploy_location = deploy_locations[deploy_index]
            
            game_state.attempt_spawn(SCRAMBLER, deploy_location)
            count -= 1
            """
            We don't have to remove the location since multiple information 
            units can occupy the same space.
            """

    
    def least_damage_spawn_location(self, game_state, location_options):
        """
        This function will help us guess which location is the safest to spawn moving units from.
        It gets the path the unit will take then checks locations on that path to 
        estimate the path's damage risk.
        """
        damages = []
        # Get the damage estimate each path will take
        for location in location_options:
            path = game_state.find_path_to_edge(location)
            damage = 0
            for path_location in path:
                # Get number of enemy destructors that can attack the final location and multiply by destructor damage
                damage += len(game_state.get_attackers(path_location, 0)) * gamelib.GameUnit(DESTRUCTOR, game_state.config).damage
            damages.append(damage)
        
        # Now just return the location that takes the least damage
        return location_options[damages.index(min(damages))]

    def detect_enemy_unit(self, game_state, unit_type=None, valid_x = None, valid_y = None):
        total_units = 0
        for location in game_state.game_map:
            if game_state.contains_stationary_unit(location):
                for unit in game_state.game_map[location]:
                    if unit.player_index == 1 and (unit_type is None or unit.unit_type == unit_type) and (valid_x is None or location[0] in valid_x) and (valid_y is None or location[1] in valid_y):
                        total_units += 1
        return total_units
        
    def filter_blocked_locations(self, locations, game_state):
        filtered = []
        for location in locations:
            if not game_state.contains_stationary_unit(location):
                filtered.append(location)
        return filtered

    def on_action_frame(self, turn_string):
        """
        This is the action frame of the game. This function could be called 
        hundreds of times per turn and could slow the algo down so avoid putting slow code here.
        Processing the action frames is complicated so we only suggest it if you have time and experience.
        Full doc on format of a game frame at: https://docs.c1games.com/json-docs.html
        """
        # Let's record at what position we get scored on
        state = json.loads(turn_string)
        events = state["events"]
        breaches = events["breach"]
        for breach in breaches:
            location = breach[0]
            unit_owner_self = True if breach[4] == 1 else False
            # When parsing the frame data directly, 
            # 1 is integer for yourself, 2 is opponent (StarterKit code uses 0, 1 as player_index instead)
            if not unit_owner_self:
                gamelib.debug_write("Got scored on at: {}".format(location))
                self.scored_on_locations.append(location)
                gamelib.debug_write("All locations: {}".format(self.scored_on_locations))

    def scramblers_defend_large_attack(self, game_state):
        """
        This method is used to predict if enemy is going to release huge attack, 
        especially with a large chain of PING
        for different turns, there is different standard to release scramblers.
        for different turns, we need different amount of scramblers
        """
        large_attack = False    # a flag to mark if there is large_attack or not

        # combine enemy's BITS and turn number to predict large attack
        if game_state.turn_number < 10:
            if game_state.get_resource(game_state.BITS, player_index = 1) >= 15:
                self.stall_with_scramblers(game_state, count = 4)
                large_attack = True
            elif game_state.get_resource(game_state.BITS, player_index = 1) >= 8:
                self.stall_with_scramblers(game_state, count = 2)
                large_attack = True

        elif game_state.turn_number < 20:
            if game_state.get_resource(game_state.BITS, player_index = 1) >= 15:
                self.stall_with_scramblers(game_state, count = 4)
                large_attack = True
            elif game_state.get_resource(game_state.BITS, player_index = 1) >= 10:
                self.stall_with_scramblers(game_state, count = 3)
                large_attack = True

        elif game_state.turn_number < 30:
            if game_state.get_resource(game_state.BITS, player_index = 1) >= 17:
                self.stall_with_scramblers(game_state, count = 5)
                large_attack = True
            if game_state.get_resource(game_state.BITS, player_index = 1) >= 10:
                self.stall_with_scramblers(game_state, count = 3)
                large_attack = True

        else:
            if game_state.get_resource(game_state.BITS, player_index = 1) >= 18:
                self.stall_with_scramblers(game_state, count = 5)
                large_attack = True
            if game_state.get_resource(game_state.BITS, player_index = 1) >= 12:
                self.stall_with_scramblers(game_state, count = 4)
                large_attack = True
        
        # even if there is no large_attack, release a small amount of scramblers is a must
        if large_attack == False:
            if game_state.turn_number < 20:
                self.stall_with_scramblers(game_state, count = 2)
            else:
                self.stall_with_scramblers(game_state, count = 2)   

        return large_attack             

    def long_march(self, game_state):
        """
        This is the big attack when we have enough armys 
        """
        spawn_location_options = [[24, 10], [23, 9], [14, 0], [13, 0]]

        if game_state.turn_number < 10:
            if game_state.get_resource(game_state.BITS) >= game_state.type_cost(EMP) * 1 + game_state.type_cost(PING) * 5:        
                best_location = self.least_damage_spawn_location(game_state, spawn_location_options)
                # attempt to locate fixed amount EMPs + as many PINGs as possible
                game_state.attempt_spawn(EMP, best_location, 1)
                game_state.attempt_spawn(PING, best_location, 1000)

        elif game_state.turn_number < 20:
            if game_state.get_resource(game_state.BITS) >= game_state.type_cost(EMP) * 2 + game_state.type_cost(PING) * 8:
                best_location = self.least_damage_spawn_location(game_state, spawn_location_options)
                # attempt to locate fixed amount EMPs + as many PINGs as possible
                game_state.attempt_spawn(EMP, best_location, 2)
                game_state.attempt_spawn(PING, best_location, 1000)

        elif game_state.turn_number < 30:
            if game_state.get_resource(game_state.BITS) >= game_state.type_cost(EMP) * 2 + game_state.type_cost(PING) * 9:
                best_location = self.least_damage_spawn_location(game_state, spawn_location_options)
                # attempt to locate fixed amount EMPs + as many PINGs as possible
                game_state.attempt_spawn(EMP, best_location, 2)
                game_state.attempt_spawn(PING, best_location, 1000)
        else:
            if game_state.get_resource(game_state.BITS) >= game_state.type_cost(EMP) * 3 + game_state.type_cost(PING) * 10:
                best_location = self.least_damage_spawn_location(game_state, spawn_location_options)
                # attempt to locate fixed amount EMPs + as many PINGs as possible
                game_state.attempt_spawn(EMP, best_location, 3)
                game_state.attempt_spawn(PING, best_location, 1000)


if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
