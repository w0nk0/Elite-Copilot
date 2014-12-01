from os import listdir
import route
import pyttsx

CFG_speak_entire_route = False
SP_FAST = 140
SP_SLOW = 98

global speech
speech = pyttsx.init()

path = r"C:\_SSD_\Frontier\EDLaunch\Products\FORC-FDEV-D-1002\Logs"

def debug(s):
    return
    print(s)

def find_latest_log(path):
    """Returns the latest log file's path"""

class LogWatcher:
    def __init__(self,path):
        self.path = path
        self.fn = None
        self._last_visited = None
        self._new_system = False
        self.callback = None
        self.log_pattern = "netLog"

    def new_system(self):
        return self._new_system

    def last_system(self):
        return self._last_visited

    def register_callback(self,func):
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

        allfiles.sort()
        full_path = os.path.join(self.path,allfiles[-1])
        return full_path

    def _read_log(self,fn = None):
        """

        :rtype : str
        """
        log=""
        fn = fn or self._find_logfile()

        if not fn: return ""

        debug("Reading %s" % fn)
        with open(fn,"rt") as f:
            log=f.read()

        return log


    def _get_systems(self,logtxt):
        import re
        regex = re.compile(ur'System:\d+\((?P<System>.*?)\).*?Body:(?P<Body>\d+)')
        systems=[]
        bodies=[]
        for system, body in regex.findall(logtxt):
            systems.append(system)
            bodies.append(body)

        debug("Systems: "+str(systems))
        return systems

    def _check_log(self):
        log=self._read_log()
        systems=self._get_systems(log)

        if not systems:
            return

        last_system = systems[-1]
        #print "last_visited: ", self._last_visited
        #print "Now: ",last_system
        if last_system == self._last_visited:
            return

        print "New last system!"
        self._new_system = True
        self._last_visited = last_system
        self.callback(self._last_visited)

    def check(self):
        self._new_system = False
        self._check_log()


def system_speakify(txt):
    new_txt = ""
    counter = 0
    for c in txt:
        counter += 1
        new_txt += c
        if c in "0123456789" and counter % 2:
            new_txt += " "
        if c == "-":
            new_txt += "dash"

    return new_txt

def talker(txt):
    global speech

    txt = system_speakify(txt)
    speech.setProperty("rate", SP_FAST)
    speech.say("Arrived in system ")
    speech.setProperty("rate", SP_SLOW)
    speech.say(txt+"!!")
    print "In system "+txt
    speech.runAndWait()



def run():
    import time
    import route
    global speech

    my_route = "Beargk,B7-6,B7-2,B7-1,B7-4,Nithhogg,101806,Hayanzib,Vish,Grana,Aguano,B7-1".split(",")
    my_route=[]

    speech.setProperty("rate", SP_FAST)

    with open("route.txt","rt") as rf:
        my_route = rf.readlines()
        speech.say("Read route from route.txt")

    speech.say("Starting to monitor")
    speech.runAndWait()

    r = route.EliteRouter(my_route)
    w = LogWatcher(path)
    #w.register_callback(lambda x: debug("\n\n## NEW SYSTEM ## "+x))
    w.register_callback(talker)
    runs = 0
    routing = True


    while routing:
        time.sleep(10)

        w.check()

        if w.new_system():
            runs = 1
            time.sleep(10)
            sys = w.last_system()
            jump = r.next_jump(sys)
            if r.route_complete():
                routing = False

            speech.setProperty("rate", SP_FAST)
            speech.say("Next jump: ")
            speech.setProperty("rate", SP_SLOW)
            speech.say(system_speakify(jump)+"!!")
            speech.runAndWait()

            print "Route:",
            print r.route

        if not runs % 6:
            rem = r.remaining_route(2)
            if rem:
                speech.setProperty("rate", SP_FAST)
                speech.say("Next stops: ")
                speech.setProperty("rate", SP_SLOW)
                speech.say(system_speakify(rem))
                speech.runAndWait()

        if CFG_speak_entire_route and runs % 18 == 0:
            rem = r.remaining_route()
            if rem:
                speech.say("Next stops: "+system_speakify(rem))
                speech.runAndWait()

        runs += 1

    speech.setProperty("rate", SP_FAST)
    speech.say("Routing finished! Exiting!")
    speech.runAndWait()


if __name__ == "__main__":
    run()