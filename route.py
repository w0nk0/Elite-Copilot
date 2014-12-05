_route = "".split(",")
route_systems = set(_route)


class EliteRouter:
    def __init__(self, route):
        # route = route or _route
        assert (isinstance(route, list))
        self.route = []
        for i in route:
            #if i.startswith("DONE"): continue
            i = i.lower().strip()
            i = i.replace("done", "DONE")
            if len(i) > 1:
                self.route.append(i)

    def get_route(self):
        return self.route

    def next_jump(self, current_system):
        cur = current_system.lower()

        found = -1
        for idx, sys in enumerate(self.route):
            if sys in cur:
                found = idx

        if found > -1:
            if len(self.route) > found + 1:
                next_system = self.route[found + 1]
            else:
                next_system = "You have arrived at your destination!"

            # check off visited systems
            for i in range(0, found + 1):
                if not self._is_done(self.route[i]):
                    self.route[i] = self._done(self.route[i])
        else:
            next_system = "Not found"

        return next_system

    @staticmethod
    def _done(item):
        item = "DONE: " + item
        return item

    @staticmethod
    def _undone(item):
        item = item.replace("DONE: ", "")
        item = item.replace("done: ", "")
        return item

    @staticmethod
    def _is_done(item):
        if item.startswith("DONE"):
            return True
        return False

    def remaining_route(self, next_steps_num=999):
        """
        :param next_steps_num: Number of steps to return
        :return: Returns a string with next_steps remaining stops
        :rtype: str
        """
        result = []
        # print "r:",self.route
        for i in self.route:
            if self._is_done(i):
                continue
            result.append(i)
        result = result[:next_steps_num]
        #print "rem:",result
        return result

    def route_complete(self):
        return len(self.remaining_route()) < 1

    def reverse_route(self):
        # print "r route:", self.route
        self.route.reverse()
        result = []
        for item in self.route:
            result.append(self._undone(item))
        self.route = result
        #print "r route:", self.route


def test():
    r = "A10-4,Beargk,Lave,Earth".split(",")
    e = EliteRouter(r)

    print e.next_jump("A10-4")
    print e.next_jump("A10-4")
    print e.route
    print e.next_jump("Lave")
    print e.route
    print e.next_jump("Earth")
    print e.route


if __name__ == "__main__":
    test()
