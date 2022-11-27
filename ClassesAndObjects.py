from random import randint

class Map_Graph():
    """Defines structure for a map and its constructors
    -Defines random or specific initialization
    -Made of nodes
    """

    def __init__(self) -> None:
        self.nodes = dict()

    def initialize_random(self,node_num):
        for node in range(node_num):
            for 

class Node():
    """Defines a map node.
    size: Total tier level allowed in node
    type: Special type, subclass w/special properties to be added later
    """
    def __init__(self,cap) -> None:
        self.type
        self.edges = list()
        self.max_cap = cap
        self.cap = 0

    def add_neighbor(self,far) -> None:
        _edge = Edge(self,far)
        self.edges.append(_edge)
        far.edges.append(_edge)

    def move_unit(self,tier,direction=True) -> bool:
        """Move unit into node, return bool of result
        Will fail if:
            Added tier puts current cap above max_cap
        """
        if direction:
            if tier + self.cap > self.max_cap:
                return False
            else:
                self.cap += tier
                return True
        else:
            if self.cap - tier < 0:
                return False
            else:
                self.cap -= tier
                return True

    @property
    def cap(self) -> int:
        return self.cap

    @property
    def neighbors(self) -> list:
        _out = []
        for edge in self.edges:
            if edge.A is self:
                _out.append(edge.B)
            else:
                _out.append(edge.A)
        
        return _out

    


class Edge():
    """Defines an edge between two map nodes
    """
    def __init__(self,a,b) -> None:
        self.A = a
        self.B = b