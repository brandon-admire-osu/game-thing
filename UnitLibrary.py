class Unit():
    """Define the base Unit object.
    -Units are any player controlled game piece
    -Units can have between 1-4 members
    -Members are a subtype, and just define mini-units that share a parent unit.
    """

    def __init__(
        self,
        name,
        fountain,
        tier=0,
        mobility=0,
        team=0,
        owner_id=0,
        location=None,
        order=("defend",None),
        wounds=0,
        bannar=None,
        captain=False
        ):
        # Basic info
        self.name = name
        self.tier = int(tier)
        self.mobility = int(mobility)
        self.team = int(team) #-1 for dire, 1 for radient
        self.owner_id = owner_id
        self.keywords = { # Used to track keywords
            "Fragile":False,
            "Durable":False,
            "Tough":0,
            "Bombard":0,
            "Frail":0,
            "Powerful":0,
            "Highground":0
        }
        self.special_flags = [False,False,False,False,False,False,False] # Used to indicate special behavior at specific game step

        # Current state info
        self.wound = int(wounds) # unit destroyed if wounds == 1
        self.location = location
        self.order = order
        self.fountain = None
        if team == 1:
            self.fountain = fountain[0]
        else:
            self.fountain = fountain[1]

        # Trackers for resolving
        self.origin = None # Used for movement/invade

        # wounds tracked in negative numbers if capacity greater than 1
        if self.keywords["Tough"] > 0:
            self.wound -= self.keywords["Tough"]

        # Bannar tracking for multi member units
        self.captain = None
        if captain == "TRUE":
            self.captain = True
        else:
            self.captain = False

        self.bannar = bannar


    @property
    def alive(self) -> bool:
        return self.wounds > 0

    def __repr__(self) -> str:
        if self.team > 0:
            return "\033[92m" + str(self.tier) + '\033[0m'
        elif self.team < 0:
            return "\033[91m" + str(self.tier) + '\033[0m'

    def plant_flag(self):
        self.location.flag = self.team

    def convoy(self,path):
        mov = self.mobility
        self.origin = self.location

        # Remove from origin
        self.location.cur_cap -= self.tier
        self.location.occupants.remove(self)

        node_path = [x in path for x in self.location.parent_board.nodes]

        # Walk down path
        for step in node_path:
            # Check if valid step
            if (
                step not in self.location.neighbors or # Check that step is adjacent
                mov < 1 or # Check for sufficient movement
                not step.valid_move(self)): # Check that there is room for the unit to move in/through region
                self.defend()
                return
            else:
                # Remove from current location
                self.location.cur_cap -= self.tier
                self.location.occupants.remove(self)
                # Pay movment
                mov -= 1
                # Arrive at next step
                step.arrive(self)


    def invade(self,target):
        """Put unit on invasion force for target node."""
        # Check if target is valid
        if (target not in self.location.neighbors):
            self.defend()

        # Add power to battle calculation
        target.power_balance += (self.tier + self.keywords["Powerful"] - self.keywords["Frail"]) * self.team
        # Add self to guest list
        target.guest_list.append(self)
        # Put unit in combat limbo
        self.origin = self.location
        self.location = None
        # Remove unit from origin occupants
        try:
            self.origin.cur_cap -= self.tier
            self.origin.occupants.remove(self)
        except:
            pass

        # If owner is neutral, temporarily change ownership to invading team.
        # Future invasions this turn will now register as hostile.
        if (target.owner == 0):
            target.owner = self.team
        # Flag if invasion is hostile
        if (target.owner*-1 == self.team): #-1 inverts sign to check for presence of enemy.
            target.hostile_invade = True

    def defend(self):
        self.location.power_balance += (self.tier + 1) * self.team
        self.wound -= 1
        if self.wound < 0 - self.keywords["Tough"]:
            self.wound = 0 - self.keywords["Tough"]
        self.order = ("defend",None)

    def support(self,target):
        # Check if target is valid
        if (self.location in target.neighbors and not self.location.hostile):
            target.power_balance += self.tier + self.keywords["Bombard"]
        elif (self.location.hostile):
            self.location.power_balance += (self.tier + self.keywords["Powerful"] - self.keywords["Frail"]) * self.team
        else:
            self.defend()
    
    def die(self):
        self.location = None
        self.origin = None
        self.fountain.arrive(self)

    def revive(self,target):
        self.wound = 0 - self.keywords["Tough"]
        target.arrive(self)

    def retreat(self,target):
        """
        Move back from an illegal move
        -defeted in combat
        """
        if (self.keywords["Fragile"]):
            self.die()
            return
        # Check if origin is a valid retreat path
        elif (self.origin.valid_move(self) and self.wound < 1):
            target.arrive(self)
            self.wound += 1
            return
        # Check adjacent nodes for valid retreat path
        for neighbor in target.neighbors:
            if (neighbor.valid_move(self) and self.wound < 1):
                neighbor.arrive(self)
                self.wound += 1
                return
        # Destroy unit if no valid retreat path
        self.die()
        
    def special(self):
        """Special ability call, no functionality by default."""
        pass

class Scouts(Unit):
    """
    This unit automattically takes the Plant a Flag action as part of an Invade if the Invade was uncontested.
    2 members
    """
    def __init__(
        self,
        name,
        team,
        owner_id, 
        location, 
        bannar, 
        order,
        fountain,
        captain=False, 
        wounds=0
        ):
        super().__init__(name,fountain,1,2,team,owner_id,location,order,wounds,bannar,captain)
        self.special_flags[1] = True #Special ability activates during convoy

    def special(self):
        if self.order[0] == "invade" and not self.order[1].hostile_invade:
            self.order[1].flag = self.team

class InfantrySquad(Unit):
    """
    When taking the Defend action, this unit revives an additional member at the beginning of cleanup (before units are destroyed.).
    5 members
    """

    def __init__(
        self,
        name,
        team,
        owner_id, 
        location, 
        bannar, 
        order,
        fountain,
        captain=False, 
        wounds=0
        ):
        if captain:
            super().__init__(name,fountain,1,1,team,owner_id,location,order,wounds,bannar,captain)
            self.special_flags[6] = True #Special ability activates during cleanup

        else:
            super().__init__(name,fountain,1,1,team,owner_id,location,order,wounds,bannar,captain)

    def special(self,target):
        if self.order[0] == "defend":
            self.bannar.replenish()


class ArcherSquad(Unit):
    """
    No special abilites
    2 members
    """
    def __init__(
        self,
        name,
        team,
        owner_id, 
        location, 
        bannar, 
        order,
        fountain,
        captain=False, 
        wounds=0
        ):
        super().__init__(name,fountain,1,1,team,owner_id,location,order,wounds,bannar,captain)
        self.keywords["Bombard"] = 1

class BarbarrianSquad(Unit):
    """
    If this unit is invading with at least one other member of its unit, it gets Powerful 1.
    3 members
    """
    def __init__(
        self,
        name,
        team,
        owner_id, 
        location, 
        bannar, 
        order,
        fountain,
        captain=False, 
        wounds=0
        ):
        super().__init__(name,fountain,1,1,team,owner_id,location,order,wounds,bannar,captain)
        self.special_flags[4] = True #Special ability activates during last call

    def special(self):
        if (self.order[0] == "invade" and 
        any([x.name != self.name and x.location == self.location for x in self.bannar.members])
        ):
            self.location.power_balance += 1 * self.team

class Calvary(Unit):
    """
    No special abilites
    2 members
    """
    def __init__(
        self,
        name,
        team,
        owner_id, 
        location, 
        bannar, 
        order,
        fountain,
        captain=False, 
        wounds=0
        ):
        super().__init__(name,fountain,2,3,team,owner_id,location,order,wounds,bannar,captain)

class Artillary(Unit):
    """
    No special abilites
    1 member
    """
    def __init__(
        self,
        name,
        team,
        owner_id, 
        location, 
        bannar, 
        order,
        fountain,
        captain=False, 
        wounds=0
        ):
        super().__init__(name,fountain,2,1,team,owner_id,location,order,wounds,bannar,captain)
        self.keywords["Bombard"] = 3
        self.keywords["Fragile"] = True

class BattlefieldMedic(Unit):
    """
    Clear one wound from all units that share a region with this unit at the beginning of cleanup.
    1 member
    """
    def __init__(
        self,
        name,
        team,
        owner_id, 
        location, 
        bannar, 
        order,
        fountain,
        captain=False, 
        wounds=0
        ):
        super().__init__(name,fountain,2,1,team,owner_id,location,order,wounds,bannar,captain)
        self.keywords["Fragile"] = True
        self.keywords["Frail"] = 1
        self.special_flags[6] = True #Special ability activates during cleanup
    
    def special(self):
        for unit in self.location.occupants:
            unit.wound -= 1
            if unit.wound < 0 - unit.keywords["Tough"]:
                unit.wound = 0 - unit.keywords["Tough"]

class HeavyInfantry(Unit):
    """
    No special abilites
    2 members
    """
    def __init__(
        self,
        name,
        team,
        owner_id, 
        location, 
        bannar, 
        order,
        fountain,
        captain=False, 
        wounds=0
        ):
        super().__init__(name,fountain,2,1,team,owner_id,location,order,wounds,bannar,captain)
        self.keywords["Tough"] = 1

class Assassin(Unit):
    """
    Assasinate: When Invading, if there is a unit in the combat of a tier higher, this unit gains Powerful 2.
    1 member
    """
    def __init__(
        self,
        name,
        team,
        owner_id, 
        location, 
        bannar, 
        order,
        fountain,
        captain=False, 
        wounds=0
        ):
        super().__init__(name,fountain,2,2,team,owner_id,location,order,wounds,bannar,captain)
        self.special_flags[0] = True #Special ability activates during Invade

    def special(self):
        for unit in self.location.occupants:
            if unit.team != self.team and unit.tier > self.tier:
                self.location.power_balance += 2 * self.team

class Warrior(Unit):
    """
    No special abilites
    1 member
    """
    def __init__(
        self,
        name,
        team,
        owner_id, 
        location, 
        bannar, 
        order,
        fountain,
        captain=False, 
        wounds=0
        ):
        super().__init__(name,fountain,3,1,team,owner_id,location,order,wounds,bannar,captain)
        self.keywords["Powerful"] = 2
        self.keywords["Durable"] = True

class Necromancer(Unit):
    """
    If a unit (atomic unit, so members included) dies in an adjacent region, add a new member (if there is room) to this unit. The new member is a zombie with the following stats: Tier 0, Mobility 1, Fragile, Powerful 1.
    1 member (sorta)
    """

    def __init__(
        self,
        name,
        team,
        owner_id, 
        location, 
        bannar, 
        order,
        fountain,
        captain=False, 
        wounds=0
        ):
        super().__init__(name,fountain,3,1,team,owner_id,location,order,wounds,bannar,captain)
        self.keywords["Frail"] = 2

    def special(self):
        return super().special()

class Mage(Unit):
    """
    When taking the support action against a region that is NOT being invaded by friendly units, all units in that region take 1 wound. This unit takes 1 wound.
    1 member
    """
    def __init__(
        self,
        name,
        team,
        owner_id, 
        location, 
        bannar, 
        order,
        fountain,
        captain=False, 
        wounds=0
        ):
        super().__init__(name,fountain,3,1,team,owner_id,location,order,wounds,bannar,captain)
        self.keywords["Frail"] = 2
        self.keywords["Fragile"] = True
        self.special_flags[2] = True #Special ability activates during last call
    
    def special(self):
        if self.order[0] == "support":
            for unit in self.order[1].guest_list:
                unit.wound += 1