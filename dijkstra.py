__author__ = 'nico'

from  elitesystems import EliteSystemsList, Coordinate

class RouteNode(object):
    def __init__(self):
        self.past_cost = 0
        self.remaining_cost = 0
        self.total_cost = 0

    def __repr__(self):
        return "RouteNode(f=%.1f g=%.1f h=%.1f)" % (self.f,self.g,self.h)

    @property
    def f(self):
        #return self.total_cost
        return self.g + self.h

    @f.setter
    def f(self,value):
        self.total_cost = value

    @property
    def g(self):
        return self.past_cost

    @g.setter
    def g(self,value):
        self.past_cost = value

    @property
    def h(self):
        return self.remaining_cost

    @h.setter
    def h(self,value):
        self.remaining_cost = value


class EliteRouteNode(RouteNode):
    def __init__(self, name, coordinate, destination_coordinate):
        super(EliteRouteNode,self).__init__()
        self.name = name
        assert(isinstance(coordinate,Coordinate))
        assert(isinstance(destination_coordinate,Coordinate))
        self.coordinate = coordinate
        self.destination = destination_coordinate
        self.set_remaining_cost()
        #self.set_past_cost()
        #self.set_total_cost()

    def __repr__(self):
        return "EliteRouteNode('%s', %s)" % (self.name, super(EliteRouteNode,self).__repr__())

    def distance_to(self,other):
        return self.coordinate.distance(other.coordinate,False)

    def set_remaining_cost(self):
        self.remaining_cost = self.coordinate.distance(self.destination,squared=False)

    #def set_past_cost(self):
    #    self.past_cost= self.coordinate.distance(self.destination,squared=False)

    def set_total_cost(self):
        self.total_cost= self.remaining_cost + self.past_cost

    def __gt__(self,other):
        return self.f > other.f

    def __lt__(self, other):
        return self.f < other.f


def NodeFromName(system_name, systems_data):
    assert (isinstance(systems_data,EliteSystemsList))
    return systems_data.system_from_name(system_name)

def do_route(start_node,destination_node,jump_range, systems_data):
    assert(isinstance(start_node,EliteRouteNode))
    assert(isinstance(destination_node,EliteRouteNode))
    assert(isinstance(systems_data,EliteSystemsList))

    start_node.f = 0
    open_list = [start_node]
    closed_list = []

    while(len(open_list)):
        open_list.sort()
        q = open_list.pop()
        print "q =",q

        neighbors = systems_data.neighbors(q.name,jump_range)
        successors = []
        for name, coordinate in neighbors.items():
            successors.append(EliteRouteNode(name,coordinate,destination_node.coordinate))

        print "Q succ:"
        pprint( successors)

        for successor in successors:
            assert (isinstance(successor,EliteRouteNode))
            if successor.name == destination_node.name:
                return "DONE, what do return?!"
            successor.g = q.g + successor.distance_to(q)
            successor.h = successor.distance_to(destination_node)

def test_routing(sys_list=None):
    system_data = sys_list or elitesystems.EliteSystemsList()

    start = NodeFromName("Sol", system_data)
    destination = NodeFromName("Aiabiko", system_data)

    do_route(start,destination,jump_range=14.0)

systems = EliteSystemsList()
sys1=systems.system_from_name("Sol")
sys2=systems.system_from_name("Aiabiko")
sys3=systems.system_from_name("Bingo")
target = sys2

node1 = EliteRouteNode(sys1.name, sys1.coordinates,target.coordinates)
node2 = EliteRouteNode(sys2.name, sys2.coordinates,target.coordinates)
node3 = EliteRouteNode(sys3.name, sys3.coordinates,target.coordinates)

node_list = [node1, node2, node3]

from pprint import pprint

print "list: "
pprint(node_list)
node_list.sort() #key=lambda x: x.f
print "sorted by distance to %s: " % (target)
pprint(node_list)

print node_list.pop()

do_route(node1,node2,14.0,systems)




