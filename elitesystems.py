__author__ = 'nico'

import json
from math import sqrt

PRE_CACHE_DIST = 28.0
DEFAULT_JUMP_LENGTH = 13.0
ECONOMIC_ROUTING = True

SYSTEMS_JSON_URL = 'https://github.com/SteveHodge/ed-systems/blob/master/systems.json?raw=true'

class Coordinate:
    def __init__(self, vector):
        if isinstance(vector, dict):
            v = vector
            vector = (v["x"], v["y"], v["z"])
        assert (len(vector) == 3)
        self.x, self.y, self.z = vector

    def __repr__(self):
        return "Coordinate(%.2f %.2f %.2f) " % (self.x, self.y, self.z)

    def distance(self, other, squared=True):
        dsum = 0.0
        dsum += pow(abs(self.x - other.x), 2)
        dsum += pow(abs(self.y - other.y), 2)
        dsum += pow(abs(self.z - other.z), 2)
        if squared:
            return sqrt(dsum)
        else:
            return dsum


class EliteSystem():
    def __init__(self, name, coordinate):
        assert (isinstance(name, basestring))
        assert (isinstance(coordinate, Coordinate))
        self.name = name
        self.coordinates = coordinate

    def __repr__(self):
        return "EliteSystem('%s', %s)" % (self.name, self.coordinates)


class EliteSystemsList:
    def __init__(self, filename="systems.json", caching=True, default_jump=0):
        with open(filename, "rt") as f:
            data = f.read()

        jdata = json.loads(data)
        self.coordinates = {}
        for x in jdata:
            self.coordinates[x["name"]] = (x["x"], x["y"], x["z"])

        self.caching = caching
        self.known_neighbors = {}  # dict of (system, range) -> list
        self.pre_cache = {}  # dict of {range :  {system: neighbors}, .. } caches
        self.pre_cache_lightyears = 0
        self.last_routing_jump_distance = default_jump or DEFAULT_JUMP_LENGTH

        self.economic_routing = ECONOMIC_ROUTING

        if self.caching:
            self.fill_pre_cache()

    def all_system_names(self):
        return self.coordinates.keys()

    def system_from_name(self, system_name):
        """returns an EliteSystem()"""
        system = self.guess_system_name(system_name)
        if not system:
            system = elitesystems.guess_system_name(system_name, guess_partial=True)
            print "Guessing you mean %s ?" % system
        if not system:
            return None

        return EliteSystem(system, Coordinate(self.coordinates[system]))

    def neighbors(self, system, max_distance):
        """
        :param system: base system
        :param max_distance: jump distance
        :return: dict of { system: coordinates }
        """
        if self.caching:
            cached = self.known_neighbors.get((system, max_distance))
            if cached:
                return cached

        distance_squared = max_distance * max_distance
        base_coordinate = Coordinate(self.coordinates[system])

        result = dict()
        potential_neighbors = self.cached_neighbors(system, max_distance) or self.coordinates

        for candidate_name, candidate_coord in potential_neighbors.items():
            # Don't include reference system in neighbor list
            if candidate_name == system:
                continue

            if base_coordinate.distance(Coordinate(candidate_coord), False) < distance_squared:  #avoiding sqrt overhead
                result[candidate_name] = candidate_coord


        if self.caching:
            self.known_neighbors[(system, max_distance)] = result
        return result

    def neighbor_ranks(self, system, target, max_distance, ignore_systems):
        matches = [] #  array of (system, distance to target) tuples
        try:
            neighbor_list = self.neighbors(system, max_distance).items()
        except Exception, err:
            print "Error!", err
            print "locals:", locals()
            return [(0,0)]
            
        for n in neighbor_list:
            if n in ignore_systems:
                continue
            target_coordinates = Coordinate(self.coordinates[target])
            dist_to_target = Coordinate(n[1]).distance(target_coordinates, False)
            matches.append((n, dist_to_target))
        matches.sort(key=lambda x: x[1])
        return matches

    def econ_neighbor_ranks(self, system, target, max_distance, ignore_systems):
        matches = [] #  array of (system, distance to target) tuples
        try:
            neighbor_list = self.neighbors(system, max_distance).items()
        except Exception, err:
            print "Error!", err
            print "locals:", locals()
            return [(0,0)]

        start_coordinates = Coordinate(self.coordinates[system])
        target_coordinates = Coordinate(self.coordinates[target])
        start_dist_to_target = start_coordinates.distance(target_coordinates, False)

        print "Max_Dist:", max_distance

        for n in neighbor_list:
            if n in ignore_systems:
                continue

            dist_to_target = Coordinate(n[1]).distance(target_coordinates, False)
            improvement = sqrt(start_dist_to_target) - sqrt(dist_to_target)
            jump = sqrt(Coordinate(n[1]).distance(start_coordinates, False))
            #efficiency = dist_to_target / (improvement/(jump+2.0))*100
            #efficiency = improvement
            waste = -( improvement - jump)
            efficiency = improvement - waste*2
            efficiency = improvement*100.0 / (jump+2)
            efficiency = -dist_to_target-jump
            # fuel_usage = pow(max(jump,max_distance*0.6),1.5)-jump
            fuel_usage = jump
            if jump > max_distance*0.70:
                fuel_usage += pow(jump-max_distance*0.70,2)
            if jump > max_distance *0.7:
                fuel_adjust = pow(jump-max(jump,max_distance*0.7),2)
                waste += fuel_adjust
            efficiency = -waste   #-fuel_usage
            efficiency = improvement-waste - fuel_usage/2
            efficiency = improvement / (fuel_usage+2) * 100
            if improvement > -1:
                print "%18s: jump %6.1f / closer: %6.1f / wasted: %6.1f / eff: %6.1f " % (n[0],jump, improvement, waste,efficiency),
                print "Fuel usage: %6.1f " % fuel_usage
            matches.append((n, dist_to_target, efficiency))

        matches.sort(key=lambda x: -x[2]) # sort by efficiency
        if matches:
            print "Top jump: ", matches[0]
        else:
            print "No matches in eco_neighbor_ranks :("
        return [(n[0],n[1]) for n in matches]

    def route(self, a_start, a_target, max_distance=-1.0, verbose=True, avoid_systems=[]):
        if max_distance < 0 and self.last_routing_jump_distance:
            max_distance = self.last_routing_jump_distance

        self.last_routing_jump_distance = max_distance
        if max_distance < 0:
            return ["Max jump distance unknown!"]

        neighbor_ranker = self.neighbor_ranks
        if self.economic_routing:
            neighbor_ranker = self.econ_neighbor_ranks
            print "Economic routing: ON"

        start = self.guess_system_name(a_start)
        if not start in self.coordinates.keys():
            print "System unknown:", a_start
            return ["System unknown -> " + a_start, str(max_distance), a_target]

        target = self.guess_system_name(a_target)
        if not target in self.coordinates.keys():
            print "System unknown:", a_target
            return [start, str(max_distance), "System unknown -> " + a_target]

        current = start
        steps = [start]
        failures = 0
        bad_steps = [self.guess_system_name(x) for x in avoid_systems]

        lowest_dist = 9999
        closest_system = start

        while not current == target:
            # find eligible neighbors and sorts them
            n = neighbor_ranker(current, target, max_distance, bad_steps)
            OK = lambda x: x not in bad_steps and x not in steps
            eligible = [node for node in n if OK(node[0][0])]
            n = eligible

            # if no systems to jump to available
            if len(n) < 1:
                print "FAIL at %s" % current
                if failures < 20:
                    failures += 1
                    print "No candidates in %s, retracing a step" % current
                    print "route so far: ", steps
                    print "Bad steps:", bad_steps
                    bad_steps.append(current)
                    try:
                        current = steps.pop()
                    except IndexError:
                        failures += 1
                        continue
                    print "retraced to %s" % current
                    continue
                else:
                    steps.append("INCOMPLETE :(")
                    steps.append(target)
                    break

            # if still no systems?
            # TODO: DISABLED
            if len(n) < 0: # DISABLED!! < 0
                print "Giving up :("
                steps.append("INCOMPLETE :(")
                steps.append(target)
                break
            closest = n[0]
            # print closest
            if verbose: print "%20s " % current + " --> ",
            current = closest[0][0]

            if verbose: print "%20s " % current + " remaining: %5.1f LY " % (sqrt(closest[1]))  # sqrt optimization

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

        if verbose: print "Closest point:", closest_system, "at ", lowest_dist, "LY"
        if not closest_system == target:
            steps.append("Closest system: %s" % closest_system)

        if len(steps) == 1:
            return []

        return steps

    def route_length(self, route_steps):
        previous = None
        distance = 0.0
        for step in route_steps:
            if previous:
                try:
                    distance += self.distance_between(step, previous)
                except:
                    print "Couldn't find distance from %s to %s" % (step, previous)
                    return -1.0
            previous = step
        return distance

    def guess_system_name(self, name, guess_partial=False):
        s = None
        for k in self.coordinates.keys():
            if k.lower() == name.lower():
                s = k
                break

        if not s and guess_partial:
            for k in self.coordinates.keys():
                if name.lower() in k.lower():
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

    @staticmethod
    def cache_filename(max_jump = 0, filename="neighbor-cache"):
        max_jump = max_jump or PRE_CACHE_DIST
        return "%s-%0.1fLY-dump.z" % (filename, max_jump)

    def fill_pre_cache(self):
        self.pre_cache_lightyears = PRE_CACHE_DIST

        print "Filling pre-cache"
        from cPickle import loads
        import zlib

        try:
            with open(self.cache_filename(self.pre_cache_lightyears), "rb") as f:
                text = f.read()
                text = zlib.decompress(text)
                self.pre_cache = loads(text)
            print "%d entries loaded into cache successfully!" % len(self.pre_cache.keys())
        except Exception, e:
            print "Failed: ", e
            self.pre_cache_lightyears = -1
            self.pre_cache = {}

        return len(self.pre_cache)

    def cached_neighbors(self, system, max_jump):
        if not self.caching:
            return None
        if self.pre_cache_lightyears <= max_jump:
            return None
        return self.pre_cache.get(system, None)

    def write_pre_cache(self, max_jump=None):
        """
        sets self.pre_cache to { system: [neighbor1, ..] } dict
        sets self.pre_cache_lightyears to the size of the inclusion bubble around each system
        :return: len of pre-cache
        """
        distance = max_jump or PRE_CACHE_DIST

        all_neighbors = {}

        remember = self.caching
        self.caching = False
        all_systems = self.coordinates.keys()
        print "Generating neighbor pre-cache for %d systems, this will take a while" % len(all_systems)
        count = 0.0
        for name in all_systems:
            count += 1
            all_neighbors[name] = self.neighbors(name, distance)
            if count % 50 == 1:
                print "%.2f %% done" % (count * 100.0 / len(all_systems))

        self.pre_cache = all_neighbors
        self.pre_cache_lightyears = PRE_CACHE_DIST

        self.caching = remember

        from pickle import dumps
        import zlib

        with open(self.cache_filename(int(distance)), "wb") as output:
            text = dumps(all_neighbors, 1)
            zipped = zlib.compress(text)
            output.write(zipped)
        print "Done!"

# TESTS
def run(sys1="Sol", sys2="Bingo"):
    print EliteSystemsList().route(sys1, sys2, 14.0)

def benchmark():
    import timeit

    e = EliteSystemsList(caching=False)
    e2 = EliteSystemsList()
    # print timeit.timeit(lambda: e.route("sol","Aiabiko",14.0,False),number=10)
    print "WIth cache:", timeit.timeit(lambda: e2.route("sol", "Aiabiko", 14.0, False), number=100)


import sys


def make_cache():
    EliteSystemsList().write_pre_cache(PRE_CACHE_DIST)


if __name__ == "__main__":
    # make_cache()
    print "Please supply FROM and TO system on the command line"
    if len(sys.argv) < 3:
        pass  #run()
    else:
        run(sys.argv[1], sys.argv[2])
    print "Benchmarking"
    benchmark()
