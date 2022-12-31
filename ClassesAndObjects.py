from random import randint
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import json
from UnitLibrary import *


class Map_Graph():
    """Defines structure for a map and its constructors
    -Defines random or specific initialization
    -Made of nodes
    """

    def __init__(self) -> None:
        self.nodes = dict()
        self.edges = list()
        self.orders = list()
        self.units = list()
        self.bannars = dict()
        self.radiant_fountain = Node(self,"r_fountain",100)
        self.dire_fountain = Node(self,"d_fountain",100)
        self.dire = Node(None,None,None)
        self.radiant = Node(None,None,None)

    @property
    def edge_iter(self) -> tuple:
        for edge in self.edges:
            yield (edge.A,edge.B)

    def advance_turn(self):
        # Invade Step
        for order in self.orders:
            if order["type"].lower().strip() == "invade":
                # Check for valid order
                if order["target"] not in order["unit"].location.neighbors:
                    order["unit"].defend()
                else:
                    order["unit"].invade(order["target"])

        # Call special moves
        for unit in [x.special_flags[0] for x in self.units]:
            unit.special()
        
        # Convoy Step
        for order in self.orders:
            if order["type"].lower().strip() == "convoy":
                order["unit"].convoy(order["target"])

        # Call special moves
        for unit in [x.special_flags[1] for x in self.units]:
            unit.special()

        # Support Step
        for order in self.orders:
            if order["type"].lower().strip() == "support":
                # Check for valid order
                if order["target"] not in order["unit"].location.neighbors:
                    order["unit"].defend()
                else:
                    order["unit"].support(order["target"])

        # Call special moves
        for unit in [x.special_flags[2] for x in self.units]:
            unit.special()

        # Defend Step
        for order in self.orders:
            if order["type"].lower().strip() == "defend":
                order["unit"].defend()

        # Call special moves
        for unit in [x.special_flags[3] for x in self.units]:
            unit.special()

        # Last Call

        # Call special moves
        for unit in [x.special_flags[4] for x in self.units]:
            unit.special()

        # Resolve Combat/Retreat
        for node in self.nodes.values():
            node.resolve_combat()

        # Call special moves
        for unit in [x.special_flags[5] for x in self.units]:
            unit.special()

        # Cleanup
        # Call special moves
        for unit in [x.special_flags[6] for x in self.units]:
            unit.special()

        # Destroy units
        for node in self.nodes:
            for unit in node.occupants:
                if unit.wounds > 0 and not unit.keywords["Durable"]:
                    unit.die()
                elif unit.keywords["Durable"]:
                    unit.wound = 0

        # Revive units
        for unit in self.radiant_fountain.occupants:
            if unit.bannar:
                unit.bannar.replenish(self.radiant)
            else:
                unit.revive(self.radiant)

        for unit in self.dire_fountain.occupants:
            if unit.bannar:
                unit.bannar.replenish(self.dire)
            else:
                unit.revive(self.dire)

        for order in self.orders:
            if order["type"].lower().strip() == "plant":
                order["unit"].plant_flag()

        # Change ownership/flags of regions
        for node in self.nodes:
            if len(node.occupants) < 1:
                node.owner = node.flag

        # Advance Cycle

    def build_unit_list(self,unit_info,unit_lib):
        """Initialize units to self.units from list of dicts"""
        for unit in unit_info:
            if unit["Bannar"] == "N/A":
                if unit["Unit Type"] == "Artillary":
                    self.units.append(Artillary(
                            unit["Member Name"],
                            unit["Team"],
                            unit["Owner"],
                            self.nodes[unit["Location"]],
                            unit["Bannar"],
                            (unit["Order"],unit["Target"]),
                            [self.radiant_fountain,self.dire_fountain],
                            unit["Captain"],
                            unit["Wounds"]
                        ))
                elif unit["Unit Type"] == "Battlefield Medic":
                    self.units.append(BattlefieldMedic(
                            unit["Member Name"],
                            unit["Team"],
                            unit["Owner"],
                            self.nodes[unit["Location"]],
                            unit["Bannar"],
                            (unit["Order"],unit["Target"]),
                            [self.radiant_fountain,self.dire_fountain],
                            unit["Captain"],
                            unit["Wounds"]
                        ))
                elif unit["Unit Type"] == "Assassin":
                    self.units.append(Assassin(
                            unit["Member Name"],
                            unit["Team"],
                            unit["Owner"],
                            self.nodes[unit["Location"]],
                            unit["Bannar"],
                            (unit["Order"],unit["Target"]),
                            [self.radiant_fountain,self.dire_fountain],
                            unit["Captain"],
                            unit["Wounds"]
                        ))
                elif unit["Unit Type"] == "Warrior":
                    self.units.append(Warrior(
                            unit["Member Name"],
                            unit["Team"],
                            unit["Owner"],
                            self.nodes[unit["Location"]],
                            unit["Bannar"],
                            (unit["Order"],unit["Target"]),
                            [self.radiant_fountain,self.dire_fountain],
                            unit["Captain"],
                            unit["Wounds"]
                        ))
                elif unit["Unit Type"]["name"] == "Mage":
                    self.units.append(Mage(
                            unit["Member Name"],
                            unit["Team"],
                            unit["Owner"],
                            self.nodes[unit["Location"]],
                            unit["Bannar"],
                            (unit["Order"],unit["Target"]),
                            [self.radiant_fountain,self.dire_fountain],
                            unit["Captain"],
                            unit["Wounds"]
                        ))
                elif unit["Unit Type"] == "Necromancer":
                    self.units.append(Necromancer(
                            unit["Member Name"],
                            unit["Team"],
                            unit["Owner"],
                            self.nodes[unit["Location"]],
                            unit["Bannar"],
                            (unit["Order"],unit["Target"]),
                            [self.radiant_fountain,self.dire_fountain],
                            unit["Captain"],
                            unit["Wounds"]
                        ))
            else:
                if unit["Bannar"] not in self.bannars:
                    # Create bannar
                    self.bannars[unit["Bannar"]] = Bannar(unit_lib[unit["Unit Type"]]["Members"])
        
                if unit["Unit Type"] == "Scouts":
                    self.bannars[unit["Bannar"]].add(Scouts(
                        unit["Member Name"],
                        unit["Team"],
                        unit["Owner"],
                        self.nodes[unit["Location"]],
                        self.bannars[unit["Bannar"]],
                        (unit["Order"],unit["Target"]),
                        [self.radiant_fountain,self.dire_fountain],
                        unit["Captain"],
                        unit["Wounds"]
                    ))
                elif unit["Unit Type"] == "Infantry Squad":
                    self.bannars[unit["Bannar"]].add(InfantrySquad(
                        unit["Member Name"],
                        unit["Team"],
                        unit["Owner"],
                        self.nodes[unit["Location"]],
                        self.bannars[unit["Bannar"]],
                        (unit["Order"],unit["Target"]),
                        [self.radiant_fountain,self.dire_fountain],
                        unit["Captain"],
                        unit["Wounds"]
                    ))
                elif unit["Unit Type"] == "Archer Squad":
                    self.bannars[unit["Bannar"]].add(ArcherSquad(
                        unit["Member Name"],
                        unit["Team"],
                        unit["Owner"],
                        self.nodes[unit["Location"]],
                        self.bannars[unit["Bannar"]],
                        (unit["Order"],unit["Target"]),
                        [self.radiant_fountain,self.dire_fountain],
                        unit["Captain"],
                        unit["Wounds"]
                    ))
                elif unit["Unit Type"] == "Barbarrian Squad":
                    self.bannars[unit["Bannar"]].add(BarbarrianSquad(
                        unit["Member Name"],
                        unit["Team"],
                        unit["Owner"],
                        self.nodes[unit["Location"]],
                        self.bannars[unit["Bannar"]],
                        (unit["Order"],unit["Target"]),
                        [self.radiant_fountain,self.dire_fountain],
                        unit["Captain"],
                        unit["Wounds"]
                    ))
                elif unit["Unit Type"] == "Calvary":
                    self.bannars[unit["Bannar"]].add(Calvary(
                        unit["Member Name"],
                        unit["Team"],
                        unit["Owner"],
                        self.nodes[unit["Location"]],
                        self.bannars[unit["Bannar"]],
                        (unit["Order"],unit["Target"]),
                        [self.radiant_fountain,self.dire_fountain],
                        unit["Captain"],
                        unit["Wounds"]
                    ))
                elif unit["Unit Type"] == "Heavy Infantry":
                    self.bannars[unit["Bannar"]].add(HeavyInfantry(
                        unit["Member Name"],
                        unit["Team"],
                        unit["Owner"],
                        self.nodes[unit["Location"]],
                        self.bannars[unit["Bannar"]],
                        (unit["Order"],unit["Target"]),
                        [self.radiant_fountain,self.dire_fountain],
                        unit["Captain"],
                        unit["Wounds"]
                    ))


        for bannar in self.bannars.values():
            for member in bannar.members:
                self.units.append(member)

        for unit in self.units:
            unit.location.arrive(unit)

    def initialize_board(self,target_map):
        with open(target_map,"r") as target:
            for edge in json.load(target):
                # Add missing nodes to list
                if edge[0] not in self.nodes:
                    self.nodes[edge[0]] = Node(self,str(edge[0]),randint(5,10))
                if edge[1] not in self.nodes:
                    self.nodes[edge[1]] = Node(self,str(edge[1]),randint(5,10))
                
                # Build Edges
                if len(edge) > 2:
                    self.edges.append(Edge(edge[0],edge[1],edge[2]))
                else:
                    self.edges.append(Edge(edge[0],edge[1]))

    def display_board(self):
        for node in self.nodes:
            if self.nodes[node].owner > 0:
                print("\033[92m" + "{0:}".format(self.nodes[node]) + '\033[0m',end="")
            elif self.nodes[node].owner < 0:
                print("\033[91m" + "{0:}".format(self.nodes[node]) + '\033[0m',end="")
            else:
                print("{0:}".format(self.nodes[node]),end="")
            print()

    def visualize_board(self):
        # figure(figsize=(50,50))
        G = nx.Graph(self.edge_iter)
        nx.draw_networkx(G,pos=nx.planar_layout(G))
        plt.show()




class Bannar():
    """Tracking container for multi-member units"""
    def __init__(self,num) -> None:
        self.members = list()
        self.max_members = num
        self.captain = None

    def add(self,target):
        if target.captain:
            self.captain = target
        self.members.append(target)

    @property
    def strength(self):
        return len([x for x in self.members if x.alive])

    @property
    def soundOFF(self):
        print("[",end="")
        for member in self.members:
            if member.captain:
                print("\033[92m" + '1' + '\033[0m' + ", ",end="")
            else:
                print("\033[91m" + '0' + '\033[0m' + ", ",end="")
        print("]")

    def replenish(self,target):
        if (not self.captain.alive):
            for member in self.members:
                if not member.alive:
                    member.revive(target)
        elif (self.captain.alive and 
            self.captain.location.cap + self.captain.tier < self.captain.location.max_cap and
            self.strength < self.max_members
        ):
            for member in self.members:
                if not member.alive:
                    member.revive(target=self.captain.location)
                    break

    def check_orders(self) -> bool:
        """
        Check orders of all members are the same
        """
        # Inclued all members except captain iff captain's order is defend
        _cur = [not y.captain or (y.captain and y.order[0] != "defend") for y in self.members]
        # Return true iff all orders are the same
        return all([x.order[0] == _cur[0].order[0] for x in _cur])



class Node():
    """Defines a map node.
    size: Total tier level allowed in node
    type: Special type, subclass w/special properties to be added later
    """
    def __init__(self,parent_board,name,max_cap) -> None:
        self.parent_board = parent_board
        self.name = name
        self.type = 0
        self.max_cap = max_cap
        self.cur_cap = 0
        self.power_balance = 0
        self.owner = 0 #Signed int, -1 for dire, 1 for radient
        self.hostile_invade = False
        self.guest_list = [] #Units waiting to get in, depending on results of a battle
        self.occupants = []
        self.flag = 0

    def __repr__(self) -> str:
        return f"[{self.name},{self.cur_cap}/{self.max_cap},{len(self.occupants)}]"

    def __eq__(self,other) -> bool:
        if type(other) == str:
            return self.name == other
        elif type(other) == type(self):
            return self.name == other.name
        else:
            raise ValueError(f"Bad comparison of {self.name} and {other}")

    def valid_move(self,unit)->bool:
        if (self.owner == unit.team or self.owner == 0) and self.cap + unit.tier <= self.max_cap:
            return True
        else:
            return False

    def resolve_combat(self):
        """Resolve combat for region and resolve retreats"""
        if len(self.guest_list) > 0:
            # Check highest tier for each side among invaders
            _high_radient = 0
            _high_dire = 0
            for guest in self.guest_list:
                if guest.team > 0:
                    if guest.tier > _high_radient:
                        _high_radient = guest.tier
                else:
                    if guest.tier > _high_dire:
                        _high_dire = guest.tier
            if self.power_balance > 0 and _high_radient >= _high_dire:# Radient win
                self.owner = 1
            elif self.power_balance < 0 and _high_dire >= _high_radient:# Dire win
                self.owner = -1
            else: #Tie, neutral ownership
                self.owner = 0

            # Sort guest list by tier, big bois go first
            self.guest_list.sort(key=lambda x: x.tier)

            for guest in self.guest_list:
                if guest.team == self.owner and self.valid_move(guest):
                    self.arrive(guest)
                else:
                    guest.retreat(self)
            
            # Empty the guest list now that all units have arrived or retreated
            self.guest_list.clear()

        
        # Reset the power balance to 0
        self.power_balance = 0
        # Reset invade flags
        self.hostile_invade = False

    def arrive(self,guest):
        # Add guest to occupants
        guest.location = self
        self.occupants.append(guest)
        # Reset origin to remove from limbo
        guest.origin = None
        # Update tier
        self.cur_cap += guest.tier


    @property
    def hostile(self) -> bool:
        return self.hostile_invade

    @property
    def cap(self) -> int:
        return self.cur_cap

    @property
    def neighbors(self) -> list:
        _out = []
        for edge in self.parent_board.edges:
            if edge.A == self.name:
                _out.append(self.parent_board.nodes[edge.B])
            elif edge.B == self.name:
                _out.append(self.parent_board.nodes[edge.A])
        return _out

class Edge():
    """Defines an edge between two map nodes
    """
    def __init__(self,near,far,var=0) -> None:
        self.A = near
        self.B = far
        self.type = var

    def __eq__(self, other) -> bool:
        if self.A == other.A:
            if self.B == other.B:
                return True
        if self.B == other.A:
            if self.A == other.B:
                return True
        return False

    def __repr__(self) -> str:
        return f"{self.A} -{self.type}- {self.B}"

    def __len__(self) -> int:
        return 2