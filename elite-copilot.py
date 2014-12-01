__author__ = 'nico'
APPNAME = "Elite-Copilot"
APPVERSION = "0.11"

CHECK_TIME = 5000
REPEAT_NEXT_JUMPS_TIME = 30000
NEXT_JUMP_WAIT_TIME = 2000
UPCOMING_JUMPS_NO = 2

_HELP = """
HELP
****
To get going, you need to find any of your installation of E:D's netLog files, which are in your Launcher->Products->FORC..->Logs folder! You only need to do this once.
Enter a route in the top window. When you're done, click 'Set Route'. If you edit the route later, remember to also 'Set Route' it so it's being used!
Routes will be saved on program exit and be reloaded next time it's started.

Route items should be *partial* (or full if you're less lazy than me (: ) names of systems you want to go through.

You should include the starting and ending system ideally. The router will give announce your next jump when you are in a new system. It will mark visited systems as DONE.
"""

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


class CopilotWidget(QWidget):
    def __init__(self, parent=None):
        super(CopilotWidget, self).__init__(parent)

        self.Router = None
        self.Watcher = None
        self.Speaker = EliteTalker()
        self.routing = False
        self.log_path = None
        self.watch_log_timer = None
        self.next_jumps_time = time()

        all_layout = QVBoxLayout()

        b = self.buttons = []
        button_layout = QHBoxLayout()
        # b.append((QPushButton("Config"),self.open_config))
        b.append((QPushButton("Set Route"), self.set_route_clicked))
        # b.append((QPushButton("Reload Route"),self.reload_route_to_widget))
        b.append((QPushButton("Reverse Route"), self.reverse_route))
        b.append((QPushButton("Set netlog Path"), self.netlog_path_dialog))
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

        self.RouteWidget = QTextEdit()
        self.MessageWidget = QTextEdit()

        all_layout.addLayout(button_layout)
        all_layout.addSpacing(10)
        all_layout.addWidget(QLabel("Route"))
        all_layout.addWidget(self.RouteWidget)
        all_layout.addSpacing(10)
        all_layout.addWidget(QLabel("Messages"))
        all_layout.addWidget(self.MessageWidget)

        self.setLayout(all_layout)
        # top: buttons
        # upper: Route
        # lower: messages

    def initialize(self):
        """Sets up the objects doing the work"""
        self.say("At your service Commander!")
        # self.message("Should set route to Widget here")
        # self.load_route()

        self.set_route_from_widget()
        self.routing = True

        self._setup_watcher()
        self._setup_upcoming()
        # self.check_route() # kicks off routing

    def _setup_watcher(self):
        """Sets up the Watcher, needs self.log_path to be set"""
        if not self.log_path:
            self.message('No netlog-path set. Please navigate to your E:D\'s Logs folder with the button above!')
            QTimer().singleShot(2000, lambda: self._setup_watcher())
            return False

        self.Watcher = LogWatcher(self.log_path)
        self.Watcher.register_callback(self.new_system_callback)

        self.watch_log_timer = QTimer(self)
        self.connect(self.watch_log_timer, SIGNAL("timeout()"), self.check_netlog)
        self.watch_log_timer.start(CHECK_TIME)

    def check_netlog(self):
        self.donate_btn.setEnabled(False)
        w = self.Watcher
        assert(isinstance(w,LogWatcher))
        if not w:
            return
        self.donate_btn.setEnabled(self.routing)
        w.check()

    def _setup_upcoming(self):
        self.upcoming_timer = QTimer(self)
        self.connect(self.upcoming_timer, SIGNAL("timeout()"), self.speak_next_jumps)
        self.upcoming_timer.start(REPEAT_NEXT_JUMPS_TIME)

    def check_route(self, system):
        # QTimer().singleShot(CHECK_TIME,lambda: self.check_route())
        if not self.routing:
            return
        if not self.Router or not self.Watcher:
            return
        # self.message("Checking")
        # if not self.Watcher:
        #    self.message("No LogWatcher set up, won't know your position :(")
        #    return False

        self.donate_btn.setEnabled(True)

        sys = system
        jump = self.Router.next_jump(sys)
        self.Speaker.say("Next jump: ")
        self.Speaker.speak_system(jump)
        self.message("Next jump: %s  \n" % jump)
        self.reload_route_to_widget(notify=False)
        self.next_jumps_time = time()

        if self.Router.route_complete():
            self.routing = False
            self.Speaker.say("Routing complete!")

    def new_system_callback(self, system):
        self.next_jumps_time = time()
        self.message("\nWelcome in system %s!" % system)
        if self.routing:
            self.Speaker.announce_system(system)
            QTimer().singleShot(NEXT_JUMP_WAIT_TIME, lambda: self.check_route(system))

    def set_log_path(self, path):
        self.message("Netlog path set to %s" % path)
        self.log_path = path

    def get_log_path(self):
        return self.log_path

    def set_route_clicked(self):
        self.say("New route set!")
        self.routing = True
        self.set_route_from_widget()

    def set_route_from_widget(self):
        route_text = self.RouteWidget.toPlainText()
        route = [l.strip() for l in route_text.split("\n")]
        self.Router = EliteRouter(route)

    def load_route(self):
        return
        #self.RouteWidget.setText("#TODO MUST LOAD A ROUTE HERE!")
        #self.message("Route LOADED FROM XXXX")

    def close(self, e):
        self.write_route()
        self.say("Goodbye Commander!")
        e.accept()
        super(CopilotWidget, self).close()

    def set_route_text(self, text_or_list):
        self.message("Sending route in upper editor to router")
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
        # don t announce upcoming jumps if we recently got somewhere
        t = time()
        if t < self.next_jumps_time + 20:
            print("Not announcing upcoming jumps, we just got somewhere %.0f seconds ago" % (t-self.next_jumps_time))
            return
        self.next_jumps_time = t
        r = self.Router
        assert (isinstance(r, EliteRouter))
        jumps = r.remaining_route(UPCOMING_JUMPS_NO)
        if not r.route_complete():
            self.Speaker.say("Upcoming jumps:")
            self.Speaker.speak_system(jumps)

    def netlog_path_dialog(self):
        f_name, _ = QFileDialog().getOpenFileName(self, 'Navigate to one of the netLog files', '.', "netlog*.*")
        logpath = os.path.dirname(f_name)
        self.set_log_path(logpath)
        print "Log path set to ", logpath


class CopilotWindow(QMainWindow):
    def __init__(self, parent=None):
        super(CopilotWindow, self).__init__(parent)

        self.mainWidget = CopilotWidget(self)
        self.setWindowTitle("%s %s" % (APPNAME, APPVERSION))
        self.setCentralWidget(self.mainWidget)

        self.netlog_path = ""

        fn = '%s.ini' % APPNAME
        self.message("Reading settings from " + fn)
        self.settings = QSettings(fn, QSettings.IniFormat)

        self.initialize()

    def initialize(self):
        self.netlog_path = self.settings.value("NetlogPath", "")
        route_text = self.settings.value("LastRoute", "DONE: No Route")
        self.mainWidget.set_route_text(route_text)
        self.mainWidget.set_log_path(self.netlog_path)
        self.mainWidget.initialize()

    def write_settings(self):
        self.settings.setValue("NetlogPath", self.mainWidget.get_log_path())
        self.settings.setValue("LastRoute", self.get_route_text())

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

w = CopilotWindow()
w.show()

app.exec_()
