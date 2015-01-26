__author__ = 'w0nk0'

__version__ = "0.3"

import elitesystems as es
from random import choice, random

from PySide.QtGui import *
from PySide.QtCore import *
import os

from styles import default_style

import sys
from time import sleep

from donate import write_html


class Writer(QObject):
    writer = Signal(object)

    def __init__(self, parent, stream):
        super(Writer, self).__init__(parent)
        try:
            assert isinstance(stream, file)
            self._stdout = stream
        except:
            print "No valid stream, won't also print"
            self._stdout = None
            # sys.stdout = self

    def __getattr__(self, item):
        # self._stdout.write("Getattr " + str(item))
        # print "getattr!"
        return getattr(self._stdout, item)

    def x__getattribute__(self, item):
        # if not item == self._stdout:
        try:
            self._stdout.write("Getattribute " + str(item))
        except:
            pass

    def write(self, txt):
        # print "Emitting!",txt
        self.writer.emit(txt)  # .replace("\n"," / ")
        try:
            self._stdout.write(str(txt))
        except:
            pass


class MyWindow(QDialog):
    def __init__(self, app=None):
        super(MyWindow, self).__init__()
        self.app = app
        self.event_callback = None

        self.setWindowTitle("W0nk0's Elite Trade Route Finder")
        self.setMinimumWidth(400)
        self.setMinimumHeight(600)

        layout = QVBoxLayout()

        # json file
        w = self.ed_json = QLineEdit("tgcsystems.json")
        lbl = QLabel("Json File")
        lbl.setBuddy(w)
        layout.addWidget(lbl)
        layout.addWidget(w)

        self.cb_caching = w = QCheckBox("Route caching")
        self.cb_caching.setChecked(True)
        layout.addWidget(w)

        # ants_number
        w = self.ed_ants = QLineEdit("5000")
        lbl = QLabel("Number of virtual ants")
        lbl.setBuddy(w)
        layout.addWidget(lbl)
        layout.addWidget(w)

        # Systems
        w = self.ed_systems = QLineEdit("Orrere,Phiagre,Rusani,Liaedin,Coelrind,Flech,Potriti,Sol,Arinna,Hyperion")
        lbl = QLabel("Comma-separated list of systems")
        lbl.setBuddy(w)
        layout.addWidget(lbl)
        layout.addWidget(w)

        # jump_length
        w = self.ed_jump = QLineEdit("20.0")
        lbl = QLabel("Maximum jump capability of your ship")
        lbl.setBuddy(w)
        layout.addWidget(lbl)
        layout.addWidget(w)


        # save_file
        w = self.ed_save_file = QLineEdit("elite-rare-route.txt")
        lbl = QLabel("Name to save found route under")
        lbl.setBuddy(w)
        layout.addWidget(lbl)
        layout.addWidget(w)

        # Start
        w = self.btn_start = QPushButton("Start")
        # lbl = QLabel("Name to save found route under")
        #lbl.setBuddy(w)
        #layout.addWidget(lbl)
        layout.addWidget(w)

        # output
        w = self.output = QTextEdit()
        lbl = QLabel("Output")
        lbl.setBuddy(w)
        layout.addWidget(lbl)
        layout.addWidget(w)

        self.btn_donate = None
        self.btn_reverse = None

        self.setLayout(layout)
        self.setup()
        self.show()

    def setup(self):
        self.btn_start.clicked.connect(lambda: self.go())
        self.writer = Writer(self, sys.stdout)
        sys.stdout = self.writer
        self.writer.writer.connect(lambda x: self.message(x, False))

    def message(self, txt, highlight=True):
        o = self.output
        if not highlight:
            txt = txt.replace("\n", " <br> ")
            # if "\n" in txt:
            #    self.output.append(" ")
            self.output.setTextColor(QColor("grey"))
            txt = "<font color = 'grey'>" + txt + "</font>"
            self.output.moveCursor(QTextCursor.End)
            self.output.insertHtml(txt)
            self.output.moveCursor(QTextCursor.End)
        else:
            self.output.setTextColor(QColor("orange"))
            self.output.append(txt)
            # txt = "<p><font color = 'orange'>"+ txt + "<br></font></p>"

        self.app.processEvents()
        o.verticalScrollBar().setValue(o.verticalScrollBar().maximum())

    def total_route_distance(self, route_items):
        total = 0.0
        prev = route_items[0]
        route_items.append(prev)
        for item in route_items[1:]:
            total += self.router.distance(prev, item)
            prev = item
        return total

    def calculate_route(self, systems_text, json, ants, jump):
        # return ["Leesti","Sol","Liaedin"]

        systems = [self.syslist.system_from_name(n) for n in systems_text]
        #self.message("Systems: "+str(systems))
        systems = [s for s in systems if not (s == None)]

        cb = self.event_callback

        route = test3(systems, self.syslist, number=ants, ant_curiosity=0.5, scent_decay=0.948, callback=cb)
        self.router.save_cache()

        return route

    def save_route(self, route):
        save_as = self.ed_save_file.text()
        self.message("Saving as " + str(save_as))
        try:
            with open(save_as, "wt") as f:
                for item in route:
                    f.write(item + "\n")
                self.message("OK!")
                return True
        except Exception, err:
            self.message("Failed :(")
            self.message("Error: " + str(err))

    def go(self):
        print "go"
        self.message("Starting")
        json = ants = jump = None
        try:
            json = self.ed_json.text()
            json_ok = os.path.exists(json)
            self.syslist = syslist = es.EliteSystemsList(json, caching=self.cb_caching.isChecked())
            syslist.verbose = False

            ants = int(self.ed_ants.text())
            jump = float(self.ed_jump.text())

            system_text = [n.strip() for n in self.ed_systems.text().split(",")]
            self.message("Systems: " + str(system_text), False)

        except Exception, err:
            self.message("One of the values you entered doesn't seem right, aborting\nError:" + str(err))
            return None

        global eliterouter
        eliterouter = self.router = Router(syslist, jump)

        global JUMP_DEFAULT
        JUMP_DEFAULT = jump

        self.message("\nLength of initial route calculating..")
        sleep(0.1)
        self.message("Initial route is %.1f LY long!\n" % self.total_route_distance(system_text))

        result = [s.name for s in self.calculate_route(system_text, json, ants, jump)]
        self.found_route = result[:-1]

        self.message("Optimized route:\n----------------\n" + "\n".join(result))

        if not self.btn_donate:
            self.btn_donate = btn_donate = QPushButton("Buy the author a drink! ;)")
            self.layout().addWidget(btn_donate)
            btn_donate.clicked.connect(lambda: self.donate())

        if not self.btn_reverse:
            self.btn_reverse = btn = QPushButton("Reverse the route")
            self.layout().addWidget(btn)
            btn.clicked.connect(lambda: self.reverse_route())

        self.message("\nLength of found route calculating..")
        sleep(0.1)
        self.message("Optimized route is %.1f LY long!" % self.total_route_distance(result))

        if self.save_route(result[:-1]):
            # self.message("\n".join(result))
            os.startfile(self.ed_save_file.text())


    @staticmethod
    def donate():
        write_html("donate.html")
        QDesktopServices().openUrl("donate.html")
        QTimer().singleShot(30000, lambda: os.unlink("donate.html"))

    def reverse_route(self):
        if not self.found_route:
            return None
        self.found_route = self.found_route[::-1]
        if self.save_route(self.found_route):
            os.startfile(self.ed_save_file.text())


def simple_distance(sys1, sys2):
    try:
        assert isinstance(sys1, es.EliteSystem)
        assert isinstance(sys2, es.EliteSystem)
    except:
        print locals()
        raise
    return sys1.distance_to(sys2)


def test():
    for idx, s1 in enumerate(systems):
        for s2 in systems[idx:]:
            if s2 == s1: continue
            print "From %s to %s: %f" % (s1.name, s2.name, distance(s1, s2))


class RandomWeightedSelector:
    def __init__(self, population, weights):
        assert isinstance(population, list)
        try:
            assert isinstance(weights, list)
        except:
            print "!! weights needs to be list, got: ", weights
        self.p = population
        self.w = weights

    def select1(self):
        p = zip(self.p, self.w)
        w = self.w
        # eliminate candidates randomly until 1 left
        # for each elimination set a random cutoff weight, only c's under cutoff can be eliminated
        while len(p) > 1:
            mx = max(w)
            r = random() * mx
            # select candidates with weight under r cutoff
            candidates = [c for c in p if p[1] <= r]
            if len(candidates):
                elim = choice(candidates)
            else:
                elim = choice(p)
            p.remove(elim)

        return p[0]

    def select(self):
        p = zip(self.p, self.w)
        w = self.w
        p.sort(key=lambda x: 100 + x[1] * random())

        return p[-1][0]


class Ant:
    def __init__(self, systems):
        self.systems = systems
        self.scent = {}
        self.route_length = -1

    def find_route(self):
        visited = []
        left = self.systems[:]
        length = 0
        nxt = choice(left)
        visited.append(nxt)
        left.remove(nxt)
        while len(left):
            previous = nxt
            nxt = choice(left)
            length += distance(nxt, previous)
            visited.append(nxt)
            left.remove(nxt)
        length += distance(nxt, visited[0])
        pheromones = 100000 / length
        self.route_length = length
        for idx in range(len(visited)):
            if idx == 0: continue
            self.scent[(visited[idx - 1], visited[idx])] = pheromones

        self.visited = visited
        return self.scent

    def scent_between(self, sys1, sys2):
        from random import random

        return self.scent.get((sys1, sys2), random()) + self.scent.get((sys2, sys1), random())


class SmartAnt:
    def __init__(self, systems, scent_input, curiosity=0.65):
        assert isinstance(scent_input, dict)
        self.curiosity = curiosity
        self.systems = systems
        self.scents = scent_input
        self.own_scent = {}
        self.route_length = -1
        self.route = []

    def __repr__(self):
        return "Ant: %.1f LY" % self.route_length

    def find_route(self):
        visited = []
        left = self.systems[:]
        length = 0
        next_system = choice(left)
        visited.append(next_system)
        left.remove(next_system)
        while len(left):
            previous = next_system
            weights = self.target_weights(previous, left)
            # print "WEIGHTS --> ", zip([n.name for n in left],weights)
            next_system = RandomWeightedSelector(left, weights).select()
            length += distance(next_system, previous)
            visited.append(next_system)
            left.remove(next_system)
        length += distance(next_system, visited[0])
        pheromones = 100000 / (10 + length)
        self.route_length = length
        for idx in range(len(visited)):
            if idx == 0: continue
            self.own_scent[(visited[idx - 1], visited[idx])] = pheromones

        self.visited = visited
        self.route = visited[:]
        self.route.append(visited[0])
        return self.own_scent

    def target_weights(self, from_sys, to_list):
        """
        :param from_sys: EliteSystem to search for targets from
        :param to_list: list of eligible destination systems
        :return: dict of system:weight
        """
        try:
            assert isinstance(from_sys, es.EliteSystem)
            for i in to_list:
                assert isinstance(i, es.EliteSystem)
        except:
            from pprint import pprint

            pprint(locals())
            pprint(to_list)
            raise
        weights = {}
        for target in to_list:
            keys = (from_sys, target)
            scent_weight = self.scents.get(keys, self.scents.get(keys, 0.0))
            try:
                dist = distance(from_sys, target)
            except AttributeError, err:
                print "Couldn't calc distance from {} to {}".format(from_sys, target)
                dist = 999.99
            # print dist, from_sys, target
            dist_weight = -(1 + random()) * 10 * dist
            rand = random()
            weights[target.name] = dist_weight * random() * self.curiosity + scent_weight * random() * (
                1 - self.curiosity)
            # if random()>self.curiosity:
            # weights[target.name] = scent_weight

        result = []
        for i in to_list:
            result.append(weights[i.name])

        return result

    def own_scent_between(self, sys1, sys2):
        """
        :param sys1: system 1
        :param sys2: system 2
        :return: own scent betwee sys1 and sys2
        """
        return self.own_scent.get((sys1, sys2), 0.0) + self.own_scent.get((sys2, sys1), 0.0)


class Scents:
    def __init__(self):
        self.s = {}

    def __getitem__(self, item):
        return self.s.get(item)

    def update(self, other_scents):
        for i in other_scents.keys():
            self.s[(i[0], i[1])] = self.s.get((i[0], i[1]), 0.0) + other_scents.get(i, 0.0)
            self.s[(i[1], i[0])] = self.s.get((i[1], i[0]), 0.0) + other_scents.get(i, 0.0)

    def evaporate(self, factor):
        """factor <1 """
        for i in self.s.keys():
            self.s[i] = self.s[i] * factor

    def from_to(self, origin, destination):
        keys = (origin, destination)
        keys2 = (destination, origin)
        return self.s.get(keys, self.s.get(keys2, 0.0))


def test2():
    num_ants = 50
    ants = []
    scents = Scents()
    for i in range(num_ants):
        ants.append(Ant(systems))
        scents.update(ants[-1].find_route())
        scents.evaporate(0.95)

    for idx, s1 in enumerate(systems):
        for s2 in systems:
            if s2 == s1:
                continue
            print "Scent From %s to %s: %f" % (s1.name, s2.name, scents.s.get((s1, s2), 0))


def test1():
    a = Ant(systems)
    print "Route:\n", a.find_route()
    print "\n\nVisited:", [x.name for x in a.visited], "Length:", a.route_length


def route_length(visited):
    total = 0.0
    route = visited[:]
    route.append(visited[0])
    cur = route[0]
    for sys in route[1:]:
        total += distance(cur, sys)
        cur = sys
    return total


def make_route_from_scents(scents, systems, syslist=None):
    current = systems[0]
    left = systems[1:]
    visited = []
    while len(left):
        visited.append(current.name)
        # make list of target,scent tuples
        # from pprint import pprint
        # pprint ("Left: ")
        # pprint(map(lambda x:x.name, left))
        dists = [(target, scents.from_to(current, target)) for target in left]
        # print("dists")
        # pprint(dists)
        dists.sort(key=lambda x: x[1])
        target = dists[-1][0]
        left.remove(target)
        current = target
    visited.append(visited[0])
    total = route_length([syslist.system_from_name(n) for n in visited])
    # total += distance(current, systems[0])
    return total, visited


class Router:
    def __init__(self, systemlist, jump):
        assert isinstance(systemlist, es.EliteSystemsList)
        self.jump = jump
        self.sl = systemlist
        self.sl.economic_routing = False
        self.cache = {}
        self.load_cache()
        self.hits = 0
        self.misses = 0

    def load_cache(self):
        from cPickle import load

        try:
            self.cache = load(open("ACScache-%.1f.cache" % self.jump))
            print "ACS Route cache: %d loaded" % len(self.cache)
        except Exception, err:
            print err
            pass

    def save_cache(self):
        from cPickle import dump

        try:
            dump(self.cache, open("ACScache-%.1f.cache" % self.jump, "w"))

            # print 'w:{0:d}'.format(len(self.cache)),
        except Exception, err:
            print err
            pass

    def distance(self, start, end):
        if start == end:
            return 0.0
        if start > end:
            x = end
            end = start
            start = x
        cached = self.cache.get((start, end), None)
        if cached:
            self.hits += 1
            # print "h",
            return cached
        self.misses += 1
        print "routing ", start, "->", end, ".",  # len(self.cache),
        route = self.sl.route(start, end, self.jump)
        result = self.sl.route_length(route)

        self.cache[(start, end)] = result
        # self.cache[(end,start)] = result
        # print "->",len(self.cache),
        if random() < 0.05:
            self.save_cache()
        return result


def distance(esys1, esys2, router=None):
    # print "From %s to %s" % (esys1.name,esys2.name),
    if not router: router = eliterouter
    dist = router.distance(esys1.name, esys2.name)
    # print dist
    return dist


def test3(system_list, syslist, number=500, ant_curiosity=0.5, scent_decay=0.96, callback=None):
    from random import choice

    num_ants = number
    ants = []
    scents = Scents()
    for i in range(num_ants):
        if callback: callback(i)
        new_ant = SmartAnt(system_list, scents.s, curiosity=random())  # ant_curiosity*0.5+random()*0.5
        route = new_ant.find_route()
        if callback: callback(i)
        scents.update(new_ant.own_scent)
        ants.append(new_ant)
        # reinforce best ants path
        if len(ants) > 10:
            ants.sort(key=lambda x: x.route_length)
            # reinforce random (from top quarter) ant's scent
            scents.update(choice(ants[:int(len(ants) / 4)]).own_scent)
            scents.update(ants[0].own_scent)
            scents.evaporate(scent_decay)

        if i % 250 == 0: print "\nBest route after %d: %.1f LY" % (i, ants[0].route_length),
        # if i % 250 == 0: print "Avg: %.0f" % (sum([x.route_length for x in ants]) / len(ants)),
        #if i % 250 == 0: print "Worst: ", ants[-1:]

    total, visited = make_route_from_scents(scents, system_list, syslist)

    print "Visited", visited
    print "Total", total

    print "\nRandom\n"
    sysnames = lambda x: [z.name for z in x]
    visited.sort(key=lambda x: random())
    print "Visited", visited
    print "Total", route_length([syslist.system_from_name(n) for n in visited])

    print "\nBest Ant\n"
    visited = ants[0].route
    print "Visited", map(lambda x: x.name, visited)
    print "Total", route_length([n for n in visited])

    print "Final detailed route:"
    sleep(0.2)
    total_route = []
    cur = visited[0]
    for sys in visited[1:]:
        leg = syslist.route(cur.name, sys.name, JUMP_DEFAULT)
        total_route.extend(leg[:-1])
        cur = sys
    total_route.append(leg[-1])
    print "\n".join(total_route)
    print "TOTAL ROUTE\n\n %d steps, %.1f LY\n" % (len(total_route), total)
    # print "\nVisited systems:\n----------------"
    #print "\n".join(sysnames(visited[:]))
    return visited
    #print "Cache hits/misses: ", eliterouter.hits, "/", eliterouter.misses


def setup():
    syslist = es.EliteSystemsList("tgcsystems.json", caching=True)
    syslist.verbose = False
    print "Total: %s systems in syslist", len(syslist.coordinates)

    names = "Orrere,Phiagre,Rusani,Liaedin,Coelrind,Flech,Potriti,Sol,Arinna,Hyperion,Siren,Delphin,HIP 1013,Vertumnus,LHS 3333".split(
        ",")

    hardcoded = """Orrere
    Phiagre
    Quechua
    Rajukru
    Rapa Bao
    Rusani
    Sanuma
    Tanmark
    Tarach Tor
    Thrutis
    Tiolce
    Toxandji
    Uszaa
    Utgaroar
    Uzumoku
    V1090 Herculis
    Vanayequi
    Vidavanta
    Volkhab
    Wheemete
    Witchhaul
    Wolf 1301
    Wulpa
    Wuthielo Ku
    Xihe
    Yaso Kondi
    Zaonce
    Zeessze"""


def old_run():
    from sys import argv

    try:
        names = [x.strip() for x in open(argv[1], "rt").readlines()]
    except:
        systemlist = raw_input("Enter a list of systems, separated by comma (e.g. Leesti,Sanuma,Jaroua,Tiolce): ")
        systemlist = [x.strip() for x in systemlist.split(",")]
        systemlist = "\n".join(systemlist)

    if len(systemlist) < 2:
        systemlist = hardcoded

    names = set(systemlist.split("\n"))
    systems = [syslist.system_from_name(n) for n in names]

    systems = [s for s in systems if not (s == None)]

    print "Systems used:"
    for sys in systems: print sys

    ants = "0" + raw_input("Enter a number of virtual ants to look for your route (e.g. 5000): ")
    num_ants = int(ants)
    if not (num_ants): num_ants = 5000

    jump = "0" + raw_input("Enter your jump capability in LY (like 20.5): ")
    jump = float(jump)

    JUMP_DEFAULT = 20.0
    jump_ly = jump or JUMP_DEFAULT

    eliterouter = Router(syslist, jump_ly)

    print "Using %.2f jump distance." % jump_ly
    # print "If you change the jump distance, delete the ACScache.cache file in this directory that will be created"
    #print "That file stores the routing info which is specific for the jump range"


    # NUMBER -> number of ants
    # jump distance -> JUMP_DEFAULT von weiter oben
    # es wird ein cache der jump distances erstellt und benutzt

    route = test3(systems, number=num_ants, ant_curiosity=0.5, scent_decay=0.948)

    save_as = raw_input("Save the route steps under which name ( default: 'elite-rare-route.txt'): ")
    save_as = save_as or "elite-rare-route.txt"

    with open(save_as, "wt") as f:
        for item in route:
            f.write(item.name + "\n")


def run():
    app = QApplication([])
    app.setStyleSheet(default_style)
    win = MyWindow(app)
    win.event_callback = lambda x: app.processEvents()
    try:
        sys.stdout = win.writer
    except:
        pass

    sys.exit(app.exec_())


if __name__ == "__main__":
    run()

# os.startfile(save_as)

eliterouter.save_cache()
