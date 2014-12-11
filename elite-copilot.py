__author__ = 'nico'
APPNAME = 'Elite-Copilot'
APPVERSION = '0.18'

CHECK_TIME = 10000
REPEAT_NEXT_JUMPS_TIME = 45000
NEXT_JUMP_WAIT_TIME = 9000
UPCOMING_JUMPS_NO = 2
UPCOMING_ANNOUNCE_BLOCK_TIME = 80

NATOSPELL = 'True'
HYPHENSPELL = 'False'
ROUTE_CACHING = "True"

_HELP = ("\n"
         "HELP\n"
         "****\n"
         "To get going, you need to find any of your installation of E:D's netLog files, which are in your Launcher->Products->FORC..->Logs folder! You only need to do this once.\n"
         "Enter a route in the top window. When you're done, click 'Set Route'. If you edit the route later, remember to also 'Set Route' it so it's being used!\n"
         "Routes will be saved on program exit and be reloaded next time it's started.\n"
         "\n"
         "Route items should be *partial* (or full if you're less lazy than me (: ) names of systems you want to go through.\n"
         "\n"
         "You should include the starting and ending system ideally. The router will give announce your next jump when you are in a new system. It will mark visited systems as DONE.\n"
         "\n"
         "If it doesn't work for you, you can try the \"..-console.exe\" version which will show debug output in a console window.\n"
)

inactive_help = """The 'Reload Route' button will put the waypoints back into the editor that the router currently
uses for routing, so you can change and 'Set Route' them again.
"""

import os
from time import time

from PySide.QtGui import *
from PySide.QtCore import *

from route import EliteRouter
from watchlog import LogWatcher
from talk import EliteTalker
from donate import write_html
from elitesystems import EliteSystemsList


class CopilotWidget(QWidget):
    def __init__(self, parent=None):
        super(CopilotWidget, self).__init__(parent)

        self.Router = None
        self.Watcher = None
        self.routing = False
        self.log_path = None
        self.watch_log_timer = None
        self.next_jumps_time = time()
        self.no_reroute_systems = []

        self.nato_spell = (parent.settings.value("Nato_spelling", NATOSPELL).lower() == "true")
        self.hyphen_spell = (parent.settings.value("Hyphen_spelling", HYPHENSPELL).lower() == "true")
        self.route_caching = (parent.settings.value("Route_caching", ROUTE_CACHING).lower() == "true")
        self.default_jump_length = float(parent.settings.value("Default_jump_length", 0))

        self.Speaker = EliteTalker(nato_spelling=self.nato_spell, hyphen_spelling=self.hyphen_spell)
        print("Nato_spell %s, Hyphen_spell %s" % (self.Speaker.nato, self.Speaker.hyphen))
        # print("Nato_spell %s, Hyphen_spell %s" % (self.nato_spell,self.hyphen_spell))
        all_layout = QVBoxLayout()

        b = self.buttons = []
        button_layout = QHBoxLayout()
        # b.append((QPushButton("Config"),self.open_config))
        b.append((QPushButton("Set Route"), self.set_route_clicked))
        # b.append((QPushButton("Reload Route"),self.reload_route_to_widget))
        b.append((QPushButton("Reverse Route"), self.reverse_route))
        b.append((QPushButton("Find Route"), self.find_route))
        b.append((QPushButton("Help"), self.display_help))

        for b in self.buttons:
            button_layout.addWidget(b[0])
            b[0].clicked.connect(b[1])

        self.donate_btn = btn = QPushButton(";)")
        self.donate_btn.setEnabled(False)
        btn.clicked.connect(self.donate)
        btn.setFixedWidth(30)
        button_layout.addSpacing(50)
        button_layout.addWidget(btn)

        button_layout_2 = QHBoxLayout()

        netlog_btn = QPushButton("Set netlog Path")
        netlog_btn.clicked.connect(self.netlog_path_dialog)
        button_layout_2.addWidget(netlog_btn)

        self.upcoming_cb = QCheckBox("Announce upcoming")
        button_layout_2.addWidget(self.upcoming_cb)
        self.upcoming_flag = True

        self.reroute_cb = QCheckBox("Rerouting")
        button_layout_2.addWidget(self.reroute_cb)

        self.RouteWidget = QTextEdit()
        self.RouteWidget.setFont(QFont("Verdana", 14))
        self.MessageWidget = QTextEdit()
        self.RouteWidget.setFont(QFont("Arial", 12))

        try:
            if self.route_caching:
                self.say("Loading cache!")
            self.systems = EliteSystemsList(caching=self.route_caching,default_jump=self.default_jump_length)
            self.systems.economic_routing = str(parent.settings.value("shortest_route",False)).lower() == "true"
            if self.route_caching:
                if self.systems.pre_cache:
                    self.say("Done!!")
                else:
                    self.say("Failed.")
        except Exception, err:
            print err
            msg = QMessageBox()
            msg.setText(
                "You need the systems.json file for routing, please download it from where you got this program from.")
            msg.exec_()

        all_layout.addLayout(button_layout)
        all_layout.addSpacing(10)
        all_layout.addWidget(QLabel("Route"))
        all_layout.addWidget(self.RouteWidget)
        all_layout.addLayout(button_layout_2)
        all_layout.addSpacing(10)
        all_layout.addWidget(QLabel("Messages"))
        all_layout.addWidget(self.MessageWidget)

        self.setLayout(all_layout)
        # top: buttons
        # upper: Route


    def initialize(self):
        """Sets up the objects doing the work"""
        self.say("At your service Commander!")

        self.set_route_from_widget()
        self.routing = True

        self._setup_watcher()
        self._setup_upcoming()

        self.do_rerouting = True

    @property
    def upcoming_flag(self):
        return self.upcoming_cb.isChecked()

    @property
    def do_rerouting(self):
        return self.reroute_cb.isChecked()

    @do_rerouting.setter
    def do_rerouting(self, bool):
        self.reroute_cb.setChecked(bool)

    @upcoming_flag.setter
    def upcoming_flag(self, bool):
        self.upcoming_cb.setChecked(bool)

    # noinspection PyProtectedMember
    def _setup_watcher(self):
        """Sets up the Watcher, needs self.log_path to be set"""
        if not self.log_path:
            self.message('No netlog-path set. Please navigate to your E:D\'s Logs folder with the button above!')
            QTimer().singleShot(5000, lambda: self._setup_watcher())
            return False

        self.Watcher = LogWatcher(self.log_path)
        self.Watcher.register_callback(self.new_system_callback)

        self.watch_log_timer = QTimer(self)
        self.connect(self.watch_log_timer, SIGNAL("timeout()"), self.check_netlog)
        self.watch_log_timer.start(CHECK_TIME)

        w = self.Watcher
        assert (isinstance(w, LogWatcher))
        fn = w._find_logfile()
        # self.message("Will use file '%s' for jump data (or a newer one if one is created later)\n" % fn)
        print("Will use file '%s' for jump data (or a newer one if one is created later)\n" % fn)

    def check_netlog(self):
        self.donate_btn.setEnabled(False)
        w = self.Watcher
        assert (isinstance(w, LogWatcher))
        if not w:
            return
        self.donate_btn.setEnabled(self.routing)
        w.check()

    def _setup_upcoming(self):
        self.upcoming_timer = QTimer(self)
        self.connect(self.upcoming_timer, SIGNAL("timeout()"), self.speak_next_jumps)
        self.upcoming_timer.start(REPEAT_NEXT_JUMPS_TIME)

    def check_route(self, system=None):
        # QTimer().singleShot(CHECK_TIME,lambda: self.check_route())
        """
        called from Qtimer in new_system_callback and from new route
        """
        if not self.routing:
            return
        if not self.Router or not self.Watcher:
            return

        self.donate_btn.setEnabled(True)

        sys = system or self.Watcher.last_system()
        assert isinstance(sys, str)

        jump = self.Router.next_jump(sys)

        if "not found" in jump.lower():
            if self.do_rerouting:
                if sys in self.no_reroute_systems:
                    self.say("In an unknown system, cannot reroute.")
                    return
                self.say("Not in a waypoint system. Rerouting!")
                self.find_route(sys)
                # make sure new jump announced!
                self.new_system_callback(self.Watcher.last_system())
                return

        if 'arrived' in jump : #or " found" in jump
            self.Speaker.speak_now(jump)
        else:
            self.say('Next jump: ')
            self.Speaker.speak_system(jump)


        self.message(u'Next jump: {0:s}'.format(jump))
        self.reload_route_to_widget(notify=False)
        self.next_jumps_time = time()

        if self.Router.route_complete():
            self.routing = False
            self.say('Routing complete!')

    def new_system_callback(self, system):
        self.next_jumps_time = time()
        self.message('# Entering system "%s"!' % system)
        if self.routing:
            self.Speaker.announce_system(system) #TODO - adapt to self.say() strategy
            QTimer().singleShot(NEXT_JUMP_WAIT_TIME, lambda: self.check_route(system))
            current_route = self.Router.get_route()
            target = current_route[-1]
            #distance = self.systems.distance_between(system, target)
            distance = self.remaining_route_length()
            if distance>0 and self.Router.system_in_route(system):
                message = "%d Light years until %s" % (distance, target)
                self.say(message)
            else:
                self.say("Remaining distance unknown.")
                print "Not announcing distance %d from %s, not in %s" % (distance,system, str(current_route))

    def set_log_path(self, path):
        # self.message('Netlog path set to %s' % path)
        self.log_path = path

    def get_log_path(self):
        return self.log_path

    def set_route_clicked(self):
        self.say('New route set!')
        self.routing = True
        self.set_route_from_widget()
        self.next_jumps_time = 0

        # adapt to rerouting

        #self.Watcher._last_visited = None # triggers arrival in new system logic on nxt check
        #self.find_route(self.Watcher._last_visited )

        #self.new_system_callback(self.Watcher.last_system())
        #
        self.check_route()

        #self.speak_next_jumps()

    def set_route_from_widget(self):
        route_text = self.RouteWidget.toPlainText()
        route = [l.strip() for l in route_text.split("\n")]
        self.Router = EliteRouter(route)

    def close(self, e):
        self.write_route()
        self.save_log()
        self.say("Goodbye Commander.")
        e.accept()
        super(CopilotWidget, self).close()

    def save_log(self):
        log = self.MessageWidget.toPlainText()
        with open("%s.log" % APPNAME, "at") as f:
            # noinspection PyArgumentList
            time_string = QDateTime.toString(QDateTime.currentDateTime())
            f.write("\n*********************************************************\n")
            f.write(time_string)
            f.write("\n*********************************************************\n")
            f.write(log)

    def set_route_text(self, text_or_list):
        # self.message("Sending route in upper editor to router")
        if isinstance(text_or_list, list):
            text = [line.strip() for line in text_or_list.split("\n")]
        elif isinstance(text_or_list, basestring):
            text = str(text_or_list)
        else:
            text = ""

        self.RouteWidget.setText(text)
        self.set_route_from_widget()

    def write_route(self):
        pass
        # raise NotImplementedError

    def open_config(self):
        raise NotImplementedError

    def set_route(self, route_text):
        self.RouteWidget.setText(route_text)

    def say(self, text):
        if self.Speaker:
            self.Speaker.say(text)
        self.message('"'+text+'"')

    def reverse_route(self):
        self.message("Reversing the router's current route")
        self.say("Reversing route!")
        self.routing = True
        # print "reversing ", self.RouteWidget.toPlainText()
        self.set_route_from_widget()
        self.Router.reverse_route()
        self.reload_route_to_widget()

    def reload_route_to_widget(self, notify=True):
        if notify:
            self.message("Putting the router's current route in editor above")
        r = self.Router.get_route()
        r_text = "\n".join(r)
        self.RouteWidget.setText(r_text)

    def get_route_content(self):
        return self.RouteWidget.toPlainText()

    def message(self, text):
        self.MessageWidget.append(text)

    def display_help(self):
        help_text = _HELP
        self.MessageWidget.append(help_text)

    @staticmethod
    def donate():
        write_html("donate.html")
        QDesktopServices().openUrl("donate.html")
        QTimer().singleShot(15000, lambda: os.unlink("donate.html"))

    def speak_next_jumps(self):
        # don't announce if checkbox unset
        if not self.upcoming_flag:
            return

        # don t announce upcoming jumps if we recently got somewhere
        t = time()
        time_since_jump = t - self.next_jumps_time
        if time_since_jump < UPCOMING_ANNOUNCE_BLOCK_TIME:
            print("Not announcing upcoming jumps, we just jumped %.0f s ago" % time_since_jump)
            return
        self.next_jumps_time = t
        r = self.Router
        assert (isinstance(r, EliteRouter))
        jumps = r.remaining_route(UPCOMING_JUMPS_NO)
        if not r.route_complete():
            self.say("Upcoming jumps:")
            for jump in jumps:
                self.Speaker.speak_system(jump)
                if jump != jumps[-1]:
                    self.Speaker.speak(" then ")

    def netlog_path_dialog(self):
        f_name, _ = QFileDialog().getOpenFileName(self, 'Navigate to one of the netLog files', '.', "netlog*.*")
        logpath = os.path.dirname(f_name)
        self.set_log_path(logpath)
        print "Log path set to ", logpath

    def find_route(self, start_system=None):
        self.routing = False
        self.message("\nThis will try to map a route from the first line in the route window")
        self.message("using the jump distance in light years in the second line")
        self.message("to the last line in the route window. It's very simple and may fail.\n")
        txt = self.RouteWidget.toPlainText()
        lines = [l.strip() for l in txt.split("\n")]
        while len(lines[-1]) < 2:
            del lines[-1]

        start = start_system or lines[0]
        start = self.Router._undone(start)

        destination = lines[-1]
        try:
            drive = float(lines[1])
        except:
            self.message("No floating point found in second line, using default")
            drive = -1

        route = self.systems.route(start, destination, drive)
        if not route:
            self.message("Couldn't find a route")
            return

        self.default_jump_length = self.systems.last_routing_jump_distance
        params = (len(route), start, destination, self.default_jump_length)
        self.message("Route with %d steps from %s to %s with %.1f LY jump distance." % params)

        self.RouteWidget.setText("\n".join(route))
        self.routing = True
        self.set_route_from_widget()

        params = len(route), self.systems.route_length(route)
        if params[1] < 0:
            self.say("Couldn't find full route, sorry!")
            print "start", start, "route", route
            if "unknown" in route[0]:
                self.no_reroute_systems.append(start)
                print "Start system %s added to rerouting exclusion list" % start
            if "unknown" in route[-1]:
                self.no_reroute_systems.append(destination)
                print "Destination system %s added to rerouting exclusion list" % destination

        else:
            self.say("Route found. %d steps, %.1f light years total!" % params)
            self.check_route()
            # self.message(",".join(route))


    def remaining_route_length(self):
        route = self.Router.remaining_route()
        light_years = self.systems.route_length(route)
        return light_years

class CopilotWindow(QMainWindow):
    def __init__(self, parent=None):
        super(CopilotWindow, self).__init__(parent)

        fn = '%s.ini' % APPNAME
        print("Reading settings from " + fn)
        self.settings = QSettings(fn, QSettings.IniFormat)

        self.mainWidget = CopilotWidget(self)
        self.setWindowTitle("%s %s" % (APPNAME, APPVERSION))
        self.setCentralWidget(self.mainWidget)

        self.netlog_path = ""

        self.initialize()

    def initialize(self):
        self.netlog_path = self.settings.value("NetlogPath", "")
        route_text = self.settings.value("LastRoute", "DONE: No Route")
        self.mainWidget.set_route_text(route_text)
        self.mainWidget.set_log_path(self.netlog_path)
        self.mainWidget.initialize()

    def write_settings(self):
        self.settings.setValue("NetlogPath", self.mainWidget.get_log_path())
        self.settings.setValue("Nato_spelling", self.mainWidget.nato_spell)
        self.settings.setValue("Hyphen_spelling", self.mainWidget.hyphen_spell)
        self.settings.setValue("Route_caching", self.mainWidget.route_caching)
        self.settings.setValue("LastRoute", self.get_route_text())
        self.settings.setValue("Default_jump_length", self.mainWidget.default_jump_length)

    def get_route_text(self):
        return self.mainWidget.get_route_content()

    def message(self, text):
        self.mainWidget.message(text)

    def closeEvent(self, e):
        self.write_settings()
        self.mainWidget.close(e)
        e.accept()


from sys import argv

app = QApplication(argv)
win = CopilotWindow()
win.show()
app.exec_()
