__author__ = 'w0nk0'

from csv import DictReader

INFO_FILE = "elite-raregoods.csv"
ROUTE_FILE = "elite-rare-route.txt"


class RareGoodsInfos:
    def __init__(self, fn=INFO_FILE):
        self.fn = fn
        self.data = {}
        try:
            self.read()
        except IOError:
            print "ERROR: rare goods file '%s' found!" % fn
        print "{0:3d} rare goods systems in database".format(len(self.data))

    def read(self):
        with open(self.fn, "rt") as f:
            r = DictReader(f)

            for row in r:
                sys = row["SYSTEM"].upper()
                station = row["STATION"]
                good = row["ITEM"]
                self.data[sys] = row

    def announcement(self, system):
        txt = ""
        data = self.data.get(system.upper(), None)
        if not data:
            print u"No rare goods in {0:s}".format(system)
            return ""
        assert isinstance(data, dict)
        txt = " - Famous for its %s , " % data["ITEM"]
        txt += " sold at starport %s!" % data["STATION"]

        return txt


class RareGoodsRoute:
    def __init__(self, filename=ROUTE_FILE):
        self.fn = filename
        self.always_load = False
        self.data = []
        self.load()

    def load(self):
        self.data = []
        try:
            self.data = [x.strip() for x in open(self.fn, "rt").readlines()]
        except:
            print "Couldn't load rare goods route from %s" % self.fn
        return self.data

    def save(self):
        try:
            open(self.fn, "wt").writelines("\n".join(self.data))
        except:
            print "Couldn't save rare goods route to %s" % self.fn

    def pop(self):
        if self.always_load:
            self.data = self.load()
        if not len(self.data):
            return None
        item = self.data.pop(0)
        self.save()
        return item

    def __getattr__(self, item):
        return getattr(self.data, item)


def announcement(system):
    database = RareGoodsInfos()
    return database.announcement(system)


if __name__ == "__main__":
    print announcement("Leesti")
    print announcement("Orrere")
    print announcement("Sol")
