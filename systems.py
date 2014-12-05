__author__ = 'nico'

import json
from math import sqrt

class Coordinate:
    def __init__(self,vector):
        if (isinstance(vector, dict)):
            v = vector
            vector = (v["x"],v["y"],v["z"])
        assert (len(vector) == 3)
        self.x, self.y, self.z = vector

    def distance(self,other):
        dsum = 0.0
        dsum += pow(abs(self.x - other.x), 2)
        dsum += pow(abs(self.y - other.y), 2)
        dsum += pow(abs(self.z - other.z), 2)
        return sqrt(dsum)

class EliteSystems:
    def __init__(self, filename="systems.json"):
        with open(filename,"rt") as f:
            data = f.read()

        jdata = json.loads(data)
        self.coordinates = {}
        for x in jdata:
            self.coordinates[x["name"]]=(x["x"],x["y"],x["z"])

    def neighbors(self, system, max_distance):
        c_sys = Coordinate(self.coordinates[system])
        result = dict()
        for n,x in self.coordinates.items():
            #print x,
            if n == system : continue
            if c_sys.distance(Coordinate(x)) < max_distance:
                result[n]=x
                #print x
        return result

    def neighbor_ranks(self, system, target, max_distance, ignore_systems):
        matches = []
        for n in self.neighbors(system,max_distance).items():
            if n in ignore_systems:
                continue
            matches.append((n, Coordinate(n[1]).distance(Coordinate(self.coordinates[target]))))
        matches.sort(key=lambda x:x[1])
        return matches

    def route(self, a_start, a_target, max_distance):
        start = self.guess_system_name(a_start)
        if not start in self.coordinates.keys():
            print "System unknown:", a_start
            return ["System unknown -> "+a_start,str(max_distance),target]

        target = self.guess_system_name(a_target)
        if not target in self.coordinates.keys() :
            print "System unknown:", a_target
            return [start, str(max_distance),"System unknown -> "+a_target]

        current = start
        steps = [start]
        failures = 0
        bad_steps = []

        lowest_dist=9999
        closest_system=start

        while not current == target:
            n =self.neighbor_ranks(current,target,max_distance, bad_steps)
            OK = lambda x: x not in bad_steps and x not in steps
            eligible = [node for node in n if OK(node[0][0])]
            n = eligible
            if len(n) < 1:
                print "FAIL at %s" % current
                if failures < 5:
                    failures += 1
                    print "No candidates, retracing a step"
                    print "route so far: ", steps
                    print "Bad steps:", bad_steps
                    bad_steps.append(current)
                    del steps[-1]
                    current = steps[-1]
                else:
                    steps.append("INCOMPLETE :(")
                    break
            if len(n)== 0:
                print "Giving up :("
                steps.append("INCOMPLETE :(")
                break
            closest = n[0]
            #print closest
            print current, " --> ",
            current = closest[0][0]
            print current," remaining:",closest[1],"LY"

            if closest[1] < lowest_dist:
                lowest_dist = closest[1]
                closest_system = current

            if current in steps:
                if failures < 5:
                    failures += 1
                    print "retracing a step"
                    print "Bad steps:", bad_steps
                    bad_steps.append(current)
                    del steps[-1]
                    del steps[-1]
                    current = steps[-1]
                else:
                    print "FAIL, incomplete"
                    steps.append("INCOMPLETE :(")
                    break
            steps.append(current)

        print "Closest point:" , closest_system, "at ", lowest_dist , "LY"
        if not closest_system == target:
            steps.append("Closest system: %s" % closest_system)

        if len(steps) == 1:
            return []

        return steps

    def guess_system_name(self,name, guess_partial=False):
        s = None
        for k in self.coordinates.keys():
            if k.lower() == name.lower():
                s = k
                break

        if not s and guess_partial:
            for k in self.coordinates.keys():
                if name.lower()in k.lower() :
                    s = k
                    break

        return s

    def distance_between(self, start, destination):
        s = t = None
        s = self.guess_system_name(start)
        t = self.guess_system_name(destination)

        if not s or not t:
            print "Couldn't find %s or %s" % (start, destination)
            return None

        s = Coordinate(self.coordinates[s])
        t = Coordinate(self.coordinates[t])

        return s.distance(t)

def run():
    print EliteSystems().route("Sol","Bingo",14.0)

if __name__ == "__main__":
    run()