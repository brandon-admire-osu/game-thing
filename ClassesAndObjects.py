from random import randint
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import json

global dire_fountain
dire_fountain = []
global radiant_fountain
radiant_fountain = []

class Map_Graph():
    """Defines structure for a map and its constructors
    -Defines random or specific initialization
    -Made of nodes
    """

    def __init__(self) -> None:
        self.nodes = dict()
        self.edges = list()

    @property
    def edge_iter(self) -> tuple:
        for edge in self.edges:
            yield (edge.A,edge.B)

    def resolve_combat(self):
        for node in self.nodes.values():
            node.resolve_combat()

    # def initialize_grid(self,node_num):
    #     for x in range(node_num):
    #         for y in range(node_num):
    #             self.nodes[(x,y)] = Node(self,(x,y),randint(5,10))

    #     for x in range(node_num-1):
    #         for y in range(node_num-1):
    #             self.edges.append(Edge((x,y),(x+1,y+1)))

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

class Unit():
    """Define the base Unit object.
    -Units are any player controlled game piece
    -Units can have between 1-4 members
    -Members are a subtype, and just define mini-units that share a parent unit.
    """

    def __init__(self,tier,team,num=1):
        self.tier = tier
        self.members = []
        self.team = team #-1 for dire, 1 for radient
        self.wound = False
        self.location = Node(None,None,None) #Dummy node for new units
        self.origin = None # Used for movement/invade
        if num > 1:
            for i in range(num):
                self.members.append(Member(tier))
                return
        else:
            return

    def __repr__(self) -> str:
        if self.team > 0:
            return "\033[92m" + str(self.tier) + '\033[0m'
        elif self.team < 0:
            return "\033[91m" + str(self.tier) + '\033[0m'


    def invade(self,target):
        # Add power to battle calculation
        target.power_balance += self.tier * self.team
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
        # Flag if invasion is hostile
        if (target.owner != self.team):
            target.hostile_invade = True

    def defend(self):
        self.location.power_balance += self.tier + 1 * self.team

    def support(self,target):
        # Check if it is within 1
        # (Special cases will be class modifications)
        if (self.location in target.neighbors and not self.location.hostile):
            target.power_balance += self.tier
        elif (self.location.hostile):
            self.location.power_balance += self.tier * self.team
        else:
            self.defend()
    
    def retreat(self,target):
        """
        Move back from an illegal move
        -defeted in combat
        """
        # Check if origin is a valid retreat path
        if (self.origin.valid_move(self)):
            target.arrive(self)
            return
        # Check adjacent nodes for valid retreat path
        for neighbor in target.neighbors:
            if (neighbor.valid_move(self)):
                neighbor.arrive(self)
                return
        # Wound/destroy unit if no valid retreat path
        self.location = None
        self.origin = None
        self.wound = True
        if self.team > 0:
            radiant_fountain.append(self)
        else:
            dire_fountain.append(self)
        


class Member(Unit):
    """Individual member of a unit with more than one member
    (A squad of henchmen, a group of calvary)
    """
    pass



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

    def __repr__(self) -> str:
        return f"[{self.name},{self.cur_cap}/{self.max_cap},{len(self.occupants)}]"

    def valid_move(self,unit)->bool:
        if self.owner == unit.team and self.cap + unit.tier <= self.max_cap:
            return True
        else:
            return False

    def resolve_combat(self):
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