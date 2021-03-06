from os import listdir
import route
import pyttsx
from os.path import exists

CFG_speak_entire_route = False

DEBUG_FLAG = False

path = r"C:\_SSD_\Frontier\EDLaunch\Products\FORC-FDEV-D-1002\Logs"


def debug(s):
    if not DEBUG_FLAG:
        return
    print(s)


class LogWatcher:
    def __init__(self, log_path):
        self.path = log_path
        self.fn = None
        self._last_visited = None
        self._new_system = False
        self.callback = None
        self.log_pattern = "netLog"
        self.logfile = ""
        self.fake_mode = True

    def is_logging_active(self):
        config_path = self.path+"/../"
        config_file = config_path + "AppConfig.xml"
        print config_file,
        #ok = exists(config_file)
        ok = False
        with open(config_file,"rt") as f:
            txt=f.read()
            ok = 'VerboseLogging="1"' in txt
        print ": ", ok
        return ok

    def new_system(self):
        return self._new_system

    def last_system(self):
        result = self._last_visited or self._get_systems(self._read_log())[-1]
        # print "Watcher->last_system:",result
        return result

    def register_callback(self, func):
        """Func needs to accept one parameter, string, the system name"""
        self.callback = func

    def _find_logfile(self):
        import os.path

        allfiles = []
        for entry in listdir(self.path):
            if entry.startswith(self.log_pattern):
                allfiles.append(entry)
        if not len(allfiles):
            return ""

        with_path = lambda x: os.path.join(self.path, x)
        allfiles.sort(key=lambda x: os.path.getmtime(with_path(x)))
        full_path = with_path(allfiles[-1])
        return full_path

    def _read_log(self, fn=None):
        """

        :rtype : str
        """
        fn = fn or self._find_logfile()

        if not fn:
            print "No log file!"
            return ""

        self._logfile = fn
        debug("Reading %s" % fn)
        with open(fn, "rt") as f:
            log = f.read()

        return log

    def _get_systems(self,logtxt):
        if self.fake_mode and not "Body:" in logtxt:
            return [self._last_visited]

        import re

        regex = re.compile(ur'System:\d+\((?P<System>.*?)\).*?Body:(?P<Body>\d+)')
        systems = []
        bodies = []
        for system, body in regex.findall(logtxt):
            systems.append(system)
            bodies.append(body)

        debug("Systems: " + str(systems))
        return systems

    def fake_system(self, system_name):
        self._last_visited = system_name
        self._new_system = system_name
        self.fake_mode = True

    def _check_log(self):
        log = self._read_log()
        systems = self._get_systems(log)

        if not systems:
            return

        last_system = systems[-1]
        # print "%d systems found in file %s: last_visited: %s" %(len(systems),self._logfile, self._last_visited)
        debug("Last system found in ..%s: %s" % (self._logfile[-14:], last_system))
        if last_system == self._last_visited:
            return

        print "New last system!"
        self._new_system = True
        self._last_visited = last_system
        self.callback(self._last_visited)

    def check(self):
        self._new_system = False
        self._check_log()


        # OLD STUFF from pre-GUI

        # def system_speakify(txt):
        # new_txt = ""
        # counter = 0
        # for c in txt:
        # counter += 1
        #         new_txt += c
        #         if c in "0123456789" and counter % 2:
        #             new_txt += " "
        #         if c == "-":
        #             new_txt += "dash"
        #
        #     return new_txt
        #
        # def talker(txt):
        #     global speech
        #
        #     txt = system_speakify(txt)
        #     speech.setProperty("rate", SP_FAST)
        #     speech.say("Arrived in system ")
        #     speech.setProperty("rate", SP_SLOW)
        #     speech.say(txt+"!!")
        #     print "In system "+txt
        #     speech.runAndWait()
        #
        #
        #
        # def run():
        #     import time
        #     import route
        #     global speech
        #
        #     my_route = "Beargk,B7-6,B7-2,B7-1,B7-4,Nithhogg,101806,Hayanzib,Vish,Grana,Aguano,B7-1".split(",")
        #     my_route=[]
        #
        #     speech.setProperty("rate", SP_FAST)
        #
        #     with open("route.txt","rt") as rf:
        #         my_route = rf.readlines()
        #         speech.say("Read route from route.txt")
        #
        #     speech.say("Starting to monitor")
        #     speech.runAndWait()
        #
        #     r = route.EliteRouter(my_route)
        #     w = LogWatcher(path)
        #     #w.register_callback(lambda x: debug("\n\n## NEW SYSTEM ## "+x))
        #     w.register_callback(talker)
        #     runs = 0
        #     routing = True
        #
        #
        #     while routing:
        #         time.sleep(10)
        #
        #         w.check()
        #
        #         if w.new_system():
        #             runs = 1
        #             time.sleep(10)
        #             sys = w.last_system()
        #             jump = r.next_jump(sys)
        #             if r.route_complete():
        #                 routing = False
        #
        #             speech.setProperty("rate", SP_FAST)
        #             speech.say("Next jump: ")
        #             speech.setProperty("rate", SP_SLOW)
        #             speech.say(system_speakify(jump)+"!!")
        #             speech.runAndWait()
        #
        #             print "Route:",
        #             print r.route
        #
        #         if not runs % 6:
        #             rem = r.remaining_route(2)
        #             if rem:
        #                 speech.setProperty("rate", SP_FAST)
        #                 speech.say("Next stops: ")
        #                 speech.setProperty("rate", SP_SLOW)
        #                 speech.say(system_speakify(rem))
        #                 speech.runAndWait()
        #
        #         if CFG_speak_entire_route and runs % 18 == 0:
        #             rem = r.remaining_route()
        #             if rem:
        #                 speech.say("Next stops: "+system_speakify(rem))
        #                 speech.runAndWait()
        #
        #         runs += 1
        #
        #     speech.setProperty("rate", SP_FAST)
        #     speech.say("Routing finished! Exiting!")
        #     speech.runAndWait()
        #
        #
        # if __name__ == "__main__":
        #     run()