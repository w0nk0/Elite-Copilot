DEBUG_VERSION = False

# ### DEBUG ####
#
if DEBUG_VERSION:
    import sys

    debug_file = open("elite-copilot-debug.txt", "w")
    sys.stdout = debug_file
#
#### DEBUG ###


# DONE - Test and finalize combo box route selection
# DONE - Optimize routing messages for failed routing etc
# Done - scroll to nxt waypoint
# probably not: System-wide player chat
# TODO - Links button / page
# TODO - Tooltips (partially done)
# TODO - Route on "repeat" for endless trading runs back/forth
# TODO - list of rare goods route stops for rare traders in separate window or text file for now
#        used upon "routing complete" to plan next route

# main window palette.button -> black commented out re Sharkan's black buttons bug

__author__ = 'w0nk0'
APPNAME = 'Elite-Copilot'
APPVERSION = '0.41beta'

CHECK_TIME = 4000
REPEAT_NEXT_JUMPS_TIME = 45000
NEXT_JUMP_WAIT_TIME = 6000
UPCOMING_JUMPS_NO = 3
UPCOMING_ANNOUNCE_BLOCK_TIME = 30

NATOSPELL = 'True'
HYPHENSPELL = 'False'
ROUTE_CACHING = "True"

DEFAULT_SYSTEMS_DATA = "systems.json"

from raregoods import RareGoodsRoute, ROUTE_FILE
import os

DO_RARE_GOOD_RUN = os.path.exists(ROUTE_FILE)
rare_goods_route = RareGoodsRoute()

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
         "If it doesn't work for you, you can try the \"..-console.exe\" version which will show debug output in a console window.\n")

inactive_help = """The 'Reload Route' button will put the waypoints back into the editor that the router currently
uses for routing, so you can change and 'Set Route' them again.
"""

MUTE_ICON_FILE = ":/mute-speaker.png"
UNMUTE_ICON_FILE = ":/unmute-speaker.png"

import os
from time import time

from PySide.QtGui import *
from PySide.QtCore import *

from route import EliteRouter
from watchlog import LogWatcher
from talk import EliteTalker
from donate import write_html
from elitesystems import EliteSystemsList
from time import asctime
import styles
import raregoods

import elitebuttons


global_hotkey_func_1 = None
global_hotkey_func_2 = None
global_hotkey_func_3 = None

global_hot_key_1 = "F20"
global_hot_key_2 = "F21"
global_hot_key_3 = "F22"


# noinspection PyBroadException
def receive_keyboard_event(event):
    # print dir(event)
    # ## assert(isinstance(event,pyHook.HookManager.ke))
    print ".",
    if 0:
        try:
            print "Key:", event.Key, " - Key ID:", event.KeyID,
            print " Alt:", event.Alt,
            print " Extended:", event.Extended,
            print " event: ascii", event.Ascii
        except:
            print "error :("

    if event.Alt == 32 and event.KeyID == 67:
        # ALT-c
        print "Key received!"

    if event.Key == global_hot_key_1:
        print "Hot key 1"
        try:
            global_hotkey_func_1()
        except Exception, e:
            print e
            print "Failed to call hook function", global_hotkey_func_1

    if event.Key == global_hot_key_2:
        print "Hot key 2"
        try:
            global_hotkey_func_2()
        except Exception, e:
            print e
            print "Failed to call hook function", global_hotkey_func_2

    if event.Key == global_hot_key_3:
        print "Hot key 3"
        try:
            global_hotkey_func_3()
        except Exception, e:
            print e
            print "Failed to call hook function", global_hotkey_func_3

    return True


def hook_setup(old_hook=None):
    import pyHook

    if old_hook:
        old_hook.UnhookKeyboard()
        # old_hook.disconnect()
        del old_hook

    hm = pyHook.HookManager()
    hm.KeyDown = receive_keyboard_event
    hm.HookKeyboard()
    return hm


class IngameOverlay(QWidget):
    def __init__(self, parent):
        super(IngameOverlay, self).__init__(parent)
        self.text_field = QLineEdit()
        self.text_field.setText("<- Click to move overlay")

        self.window_mode = -1
        self.style = ""

        pal = QPalette()
        pal.setColor(QPalette.Base, QColor(10, 10, 10))
        pal.setColor(QPalette.Foreground, QColor("orange"))
        pal.setColor(QPalette.Text, QColor("orange"))

        self.layout = QHBoxLayout()
        self.btn = QPushButton(" ")
        # print "btn style"
        #self.btn.setStyleSheet( "* { background: #d07000;}")
        self.btn.setMaximumWidth(11)
        self.btn.setMaximumHeight(11)
        #self.btn.setPalette(pal)
        self.btn.clicked.connect(self.change_window_mode)
        self.layout.addWidget(self.btn)
        self.layout.addWidget(self.text_field)
        self.setLayout(self.layout)

        self.setMinimumWidth(350)

        self.setWindowTitle("Nav hint")
        style = styles.overlay_style
        #print "ingameovl style"
        self.setStyleSheet(style)

        pal.setColor(QPalette.Text, QColor(220, 110, 0))
        self.text_field.setPalette(pal)
        #print "txtfld style", self.text_field
        self.text_field.setStyleSheet("* { border-style: 0px;}")
        self.text_field.setFont(QFont("Arial", 12))
        self.move(QPoint(20, 20))
        self.set_splash()

        self.styleTimer = QTimer().singleShot(200, lambda: self.load_style_sheet())

    def load_style_sheet(self, filename="style-overlay.txt"):
        try:
            with open(filename, "rt") as f:
                style = f.read()
        except Exception:
            style = styles.overlay_style
        self.styleTimer = QTimer().singleShot(10000, lambda: self.load_style_sheet())
        if self.style == style:
            return
        self.style = style
        self.setStyleSheet(style)
        print "Overlay style loaded"

    def set_splash(self):
        self.setWindowFlags(Qt.SplashScreen | Qt.WindowStaysOnTopHint)
        print("Splash")

    def set_dialog(self):
        self.setWindowFlags(Qt.Dialog)
        print("Dialog")

    def set_message(self, txt):
        self.text_field.setText(txt)

    # noinspection PyUnusedLocal
    def change_window_mode(self, msg=None):
        self.window_mode = -self.window_mode
        pos = self.pos()
        self.hide()
        if self.window_mode > 0:
            self.set_dialog()
        else:
            self.set_splash()
        self.show()
        mode = self.window_mode
        self.move(pos.x() - 10 * mode, pos.y() - 10 * mode)


class QueuedTalker(EliteTalker):
    def __init__(self, nato_spelling=False, hyphen_spelling=False, nato_max_len=7):
        EliteTalker.__init__(self, nato_spelling, hyphen_spelling, nato_max_len)
        self.queue = []
        self.last_message = ""
        # QTimer.singleShot(200, lambda: self.work())

    def speak(self, text, not_now=False):
        if "next jump" in text or "entering" in text:
            text = self._numbers_speakify(text)
        # self.s.say(text)
        #if not_now:
        #    return
        #else:
        #    return self.flush()

        self.queue.append(text)
        if not_now:
            QTimer.singleShot(500, lambda: self.work(set_timer=False))
        else:
            self.work()

    def work(self, set_timer=False):
        # print ".",
        if set_timer:
            QTimer.singleShot(450, lambda: self.work())
        #if not len(self.queue): return
        #print "w",len(self.queue),
        if len(self.queue):
            msg = self.queue.pop(0)
            self.last_message = msg
            self.s.say(msg)

        try:
            self.speaking = True
            self.s.runAndWait()
            self.speaking = False
            print "ok:", msg,
        except:
            self.queue.insert(0, self.last_message)
            print "fail, q:", len(self.queue),
            QTimer.singleShot(200, lambda: self.work(False))

    def _work(self, set_timer=True):
        # print ".",
        if set_timer:
            QTimer.singleShot(250, lambda: self.work())
        if not len(self.queue): return
        #print "w",len(self.queue),

        try:
            self.speaking = True
            msg = self.queue[0]
            self.s.say(msg)
            self.s.runAndWait()
            self.speaking = False
            self.queue.remove(msg)
            print "ok:", msg,
        except:
            print "fail, q:", len(self.queue),
            #QTimer.singleShot(200, lambda: self.work())

    def __getattr__(self, item):
        return getattr(EliteTalker, item)


# noinspection PyBroadException
class CopilotWidget(QWidget):
    def __init__(self, parent=None):
        super(CopilotWidget, self).__init__(parent)
        self.Router = None
        self.Watcher = None
        self.Rares = raregoods.RareGoodsInfos()
        self.routing = False
        self.log_path = None
        self.watch_log_timer = None
        self.next_jumps_time = time()
        self.no_reroute_systems = []
        self.bad_systems = []  # systems to avoid when routing
        self.hotkey_hook = None
        self.hook_timer = QTimer()  # initialized later, needs to be reinitialized regularly so it doesnt break
        self.searching_route = False
        self.copy_jump_to_clipboard = (parent.settings.value("CopyJumpToClipboard", "True").lower() == "true")

        self.verbose = (parent.settings.value("Verbose", "False").lower() == "true")
        self.nato_spell = (parent.settings.value("Nato_spelling", NATOSPELL).lower() == "true")
        self.hyphen_spell = (parent.settings.value("Hyphen_spelling", HYPHENSPELL).lower() == "true")
        self.route_caching = (parent.settings.value("Route_caching", ROUTE_CACHING).lower() == "true")
        # self.route_caching = True
        self.default_jump_length = float(parent.settings.value("Default_jump_length", 0))
        self.style = ""

        settings = parent.settings

        global global_hot_key_1
        global_hot_key_1 = str(settings.value("Hotkey_1", global_hot_key_1))
        global global_hot_key_2
        global_hot_key_2 = str(settings.value("Hotkey_2", global_hot_key_2))
        global global_hot_key_3
        global_hot_key_3 = str(settings.value("Hotkey_3", global_hot_key_3))

        try:
            # self.Speaker = EliteTalker(nato_spelling=self.nato_spell, hyphen_spelling=self.hyphen_spell)
            self.Speaker = QueuedTalker(nato_spelling=self.nato_spell, hyphen_spelling=self.hyphen_spell)
            print("Nato_spell %s, Hyphen_spell %s" % (self.Speaker.nato, self.Speaker.hyphen))
        except Exception, err:
            print "!! Exception setting up speech: %s" % err.message
            self.Speaker = None

        all_layout = QVBoxLayout()

        # upper button row

        b = self.buttons = []
        button_layout = QHBoxLayout()
        # b.append((QPushButton("Config"),self.open_config))
        b.append((QPushButton("&Confirm jump"), self.confirm_jump, 0))
        b[-1][0].setToolTip("Set the next way point as visited")
        b.append((QPushButton("&Avoid system"), self.avoid_next_jump, 20))
        b[-1][0].setToolTip("Plot a new route without the next waypoint")
        # b.append((QPushButton("&Find Route"), self.find_route,0))
        b.append((QPushButton("&Go back"), self.reverse_route, 40))
        b[-1][0].setToolTip("Reverse the route to go back to your origin")
        b.append((QPushButton("&Set Route"), self.set_route_clicked, 00))
        b[-1][0].setToolTip("Use the text in the route box for routing announcements")
        # b.append((QPushButton("Reload Route"),self.reload_route_to_widget))
        b.append((QPushButton("Help"), self.display_help, 0))
        b[-1][0].setToolTip("Display some help in the lower text box")

        for b in self.buttons:
            button_layout.addWidget(b[0])
            if b[2]:
                button_layout.addSpacing(b[2])
            b[0].clicked.connect(b[1])

        b[0].setFixedWidth(50)
        # Hotkey setup
        self.setup_hook()  # why is this here and not up top again?!

        # Route planning combo boxes etc
        combo_layout = QHBoxLayout()
        self.start_system_cb = QComboBox()
        lbl1 = QLabel("From:")
        lbl1.setBuddy(self.start_system_cb)
        lbl1.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.destination_system_cb = QComboBox()
        lbl2 = QLabel("To:")
        lbl2.setBuddy(self.destination_system_cb)
        lbl2.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        combo_layout.addWidget(lbl1)
        combo_layout.addWidget(self.start_system_cb, 2)
        combo_layout.addWidget(lbl2)
        combo_layout.addWidget(self.destination_system_cb, 2)

        lbl3 = QLabel("with")
        lbl3.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.drive_entry = QLineEdit()
        self.drive_entry.setText(str(self.default_jump_length))
        self.drive_entry.setFixedWidth(40)
        self.drive_entry.setToolTip("Jump distance in light years, with or without decimal places")
        lbl3.setBuddy(self.drive_entry)
        combo_layout.addWidget(lbl3)
        combo_layout.addWidget(self.drive_entry)
        lbl4 = QLabel("LY")
        lbl4.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        lbl4.setBuddy(self.drive_entry)
        combo_layout.addWidget(lbl4)
        self.route_btn = QPushButton(" &Find Route ")
        self.route_btn.clicked.connect(self.find_route)
        combo_layout.addWidget(self.route_btn)

        # lower button row
        button_layout_2 = QHBoxLayout()

        self.upcoming_cb = QCheckBox("Repeat upcoming")
        button_layout_2.addWidget(self.upcoming_cb)
        self.upcoming_flag = False  # not default anymore because jump detection is back!

        self.reroute_cb = QCheckBox("Rerouting")
        button_layout_2.addWidget(self.reroute_cb)
        self.do_rerouting = True

        self.econ_routing_cb = QCheckBox("Save fuel")
        button_layout_2.addWidget(self.econ_routing_cb)
        self.econ_routing_cb.stateChanged.connect(self.econ_routing_changed)
        self.econ_routing = False

        self.mute_button = QPushButton(self)
        self.mute_button.setFixedWidth(30)
        self.mute_button.setIcon(QIcon(MUTE_ICON_FILE))
        self.mute_button.setCheckable(True)
        self.mute_button.setAutoExclusive(False)
        self.mute_button.clicked.connect(self.mute_toggle)
        self.muted = False
        button_layout_2.addWidget(self.mute_button)

        self.RouteWidget = w = QTextEdit()
        pal = QPalette()
        pal.setColor(QPalette.Base, QColor(10, 10, 10))
        pal.setColor(QPalette.Foreground, QColor("red"))
        # text1color = settings.value("text1color", "(20, 240, 20)")
        # QSettings doesn't give me tuples like I need :/
        pal.setColor(QPalette.Text, QColor(20, 240, 20))
        w.setPalette(pal)
        w.setFont(QFont("Arial", 14))
        w.setTextColor(QColor(20, 240, 0))
        # w.setTextBackgroundColor(QColor(60,60,60))

        self.MessageWidget = w = QTextEdit()
        self.RouteWidget.setFont(QFont("Arial", 13))
        pal = QPalette()
        pal.setColor(QPalette.Base, QColor("Black"))
        #w.setPalette(pal)
        w.setTextColor(QColor(110, 90, 255))
        #w.setTextBackgroundColor(QColor("black"))

        button_layout_3 = QHBoxLayout()

        self.log_button = btn = QPushButton("Jump log")
        btn.clicked.connect(self.show_jump_log)
        button_layout_3.addWidget(btn)
        button_layout_3.addSpacing(200)

        netlog_btn = QPushButton("Set netlog Path")
        netlog_btn.clicked.connect(self.netlog_path_dialog)
        # netlog_btn.setEnabled(False)

        icon = QIcon(":/PPbtn.png")
        self.donate_btn = btn = QPushButton(icon, 'Donate!')

        btn.clicked.connect(self.donate)
        btn.setFixedWidth(82)
        button_layout_3.addWidget(btn)
        button_layout_3.addSpacing(10)
        button_layout_3.addWidget(netlog_btn)

        splash_btn = QPushButton("x")
        splash_btn.clicked.connect(self.setSplashMode)
        button_layout_3.addWidget(splash_btn)  # NOT WORKING LIKE THIS :(

        # self.clicked.connect(self.was_clicked)

        print "Showing overlay"
        self.overlayWindow = IngameOverlay(None)
        self.overlayWindow.show()

        try:
            if not os.path.exists(EliteSystemsList.cache_filename()):
                self.route_caching = False
            print "Caching:", str(self.route_caching)
            if self.route_caching:
                self.say("Loading cache!")

            systems_data = str(parent.settings.value("Systems_data_filename", DEFAULT_SYSTEMS_DATA))
            self.message("Using data from %s" % systems_data)
            self.systems = EliteSystemsList(caching=self.route_caching, default_jump=self.default_jump_length,
                                            filename=systems_data)

            self.systems.economic_routing = str(parent.settings.value("shortest_route", False)).lower() == "true"
            self.econ_routing = self.systems.economic_routing
            if self.route_caching:
                if self.systems.pre_cache:
                    self.say("Done.")
                else:
                    self.say("Failed.")
        except Exception, err:
            print "Error with loading systems data:", err
            msg = QMessageBox()
            msg.setText(
                "You need the systems.json file for routing, please download it from where you got this program from."
                "\n\nError:" + str(err.message))
            msg.exec_()

        all_layout.addLayout(button_layout, 0)
        all_layout.addSpacing(10)
        all_layout.addWidget(QLabel("Route"))
        all_layout.addWidget(self.RouteWidget, 2)
        all_layout.addLayout(combo_layout, 0)
        all_layout.addSpacing(10)
        all_layout.addLayout(button_layout_2, 0)
        all_layout.addSpacing(10)
        all_layout.addWidget(QLabel("Messages"), 0)
        all_layout.addWidget(self.MessageWidget, 1)
        all_layout.addLayout(button_layout_3)

        self.setLayout(all_layout)

        self.setStyleSheet(styles.default_style)

        from cherryserver import MiniWebServer

        self.web_display = None
        try:
            self.web_display = MiniWebServer()
            self.web_display.main = "Elite Copilot has started"
            from findip4address import address

            self.message("You can use http://%s:8080 in your smartphone as an external display!" % address())
        except:
            print "Couldn't set up Webserver for smartphone display :("

    def mousePressEvent(self, event, more=None):
        print "clicked:", event.pos()
        self._clicked_at = event.pos()

    def mouseReleaseEvent(self, event, more=None):
        print "released", event.pos()
        r = event.pos()
        c = self._clicked_at
        p = self.parent().pos()
        self.parent().move(p.x() + r.x() - c.x(), p.y() + r.y() - c.y())

    def setSplashMode(self, event=None):
        try:
            splash = self.splashed
        except:
            splash = False

        print "Splash mode!"
        flag = Qt.SplashScreen
        if splash:
            flag = Qt.MSWindowsFixedSizeDialogHint

        p = self.parent()
        pos = self.pos()
        ppos = p.pos()
        print pos, ppos
        # self.parent.__init__()
        for w in [p]:
            w.setWindowFlags(flag)
            #w.hide()
            w.show()
            #w.repaint()

        #self.move(ppos.x(),ppos.y())
        p.move(QPoint(ppos))

        self.splashed = not splash

    def initialize(self):
        """Sets up the objects doing the work"""
        self.say("Copilot ready!")

        self.set_route_from_widget()
        print self.Router.remaining_route()
        self.routing = True

        self._setup_watcher()
        self._setup_upcoming()

        if self.Watcher:
            self.fill_first_system()  # needs Watcher to be set up

        self.load_style_sheet()
        # noinspection PyCallByClass,PyTypeChecker
        QTimer.singleShot(500, lambda: self.initialize_combo_boxes())

    def initialize_combo_boxes(self):
        cb = self.start_system_cb
        all_systems = self.systems.all_system_names()
        all_systems.sort()
        cb.addItems(all_systems)
        cb.setEditable(True)

        cb = self.destination_system_cb
        cb.addItems(all_systems)
        cb.setEditable(True)
        if self.Watcher:
            try:
                self.start_system_cb.setEditText(self.Watcher._last_visited)
            except Exception, err:
                print "Failed to set start system from Watcher in init_combo_boxes"
                print err

        rnd = int(qrand() / 100.0 * len(all_systems))

        cb.setEditText(all_systems[rnd])

    def load_style_sheet(self, filename="style-main.txt"):
        try:
            with open(filename, "rt") as f:
                style = f.read()
            self.style_timer = QTimer().singleShot(5000, lambda: self.load_style_sheet())
        except:
            print "No main style file found. Not restyling."
            style = styles.default_style

        if self.style == style:
            return
        self.style = style

        self.setStyleSheet(style)
        print "Main style loaded"

    def fill_first_system(self):
        route_text = self.RouteWidget.toPlainText()
        done = [l.strip() for l in route_text.split("\n") if "DONE" in l]
        if done:
            last_done = done[-1].replace("DONE: ", "")
        else:
            try:
                last_done = route_text.split("\n")[0].strip()
            except:
                print "Couldnt pop first system for Watcher"
                last_done = None
        print "Putting system %s in Watcher as current" % last_done
        if last_done:
            self.Watcher.fake_system(last_done)
            self.start_system_cb.setEditText(last_done)

    def setup_hook(self):
        global global_hotkey_func_1
        global_hotkey_func_1 = self.repeat_jump

        global global_hotkey_func_2
        global_hotkey_func_2 = self.next_best_jumps

        global global_hotkey_func_3
        global_hotkey_func_3 = self.avoid_next_jump

        self.hotkey_hook = hook_setup(None)

        self.hook_timer = QTimer(self)
        self.connect(self.hook_timer, SIGNAL("timeout()"), self.reload_hook)
        self.hook_timer.start(30000)

    def reload_hook(self):
        # print "Reloading hook"
        self.hotkey_hook = hook_setup(self.hotkey_hook)
        # print "new hook: ", self.hotkey_hook

    @property
    def upcoming_flag(self):
        return self.upcoming_cb.isChecked()

    @property
    def do_rerouting(self):
        return self.reroute_cb.isChecked()

    @do_rerouting.setter
    def do_rerouting(self, flag):
        self.reroute_cb.setChecked(flag)

    @property
    def do_econ_routing(self):
        return self.econ_routing_cb.isChecked()

    @do_econ_routing.setter
    def do_econ_routing(self, flag):
        self.econ_routing_cb.setChecked(flag)
        self.systems.economic_routing = flag

    def mute_toggle(self):
        state = self.muted
        print "State:", state
        if state:
            self.muted = False
            self.say("Hello again!")
        else:
            self.say("My lips are sealed.")
            self.muted = True

    @property
    def muted(self):
        value = self.mute_button.isCheckable()
        # print "Muted:", value
        return value

    @muted.setter
    def muted(self, flag):
        # print "Setting to",flag
        if flag:
            self.mute_button.setIcon(QIcon(MUTE_ICON_FILE))
            self.mute_button.setCheckable(False)
            self.mute_button.setCheckable(True)
        else:
            self.mute_button.setIcon(QIcon(UNMUTE_ICON_FILE))
            self.mute_button.setCheckable(False)

    def econ_routing_changed(self, flag):
        self.econ_routing = flag
        print "Econ routing:", flag

    @upcoming_flag.setter
    def upcoming_flag(self, flag):
        self.upcoming_cb.setChecked(flag)

    # noinspection PyProtectedMember
    def _setup_watcher(self):
        """Sets up the Watcher, needs self.log_path to be set"""
        if not self.log_path:
            self.message('No netlog-path set. Please navigate to your E:D\'s Logs folder with the button above!')
            self.say("No net log path set")
            QTimer().singleShot(15000, lambda: self._setup_watcher())
            return False

        self.Watcher = LogWatcher(self.log_path)
        self.Watcher.register_callback(self.new_system_callback)

        if not self.Watcher.is_logging_active():
            message = "Verbose logging is not actice in your AppConfig.xml file.\nElite Copilot can't know where you're going. :("
            message += '\n\nPlease put a VerboseLogging="1" entry in the Network section of AppConfig.xml in your E:D directory'
            mb = QMessageBox()
            mb.setText(message)
            mb.exec_()

        self.watch_log_timer = QTimer(self)
        self.connect(self.watch_log_timer, SIGNAL("timeout()"), self.check_netlog)
        self.watch_log_timer.start(CHECK_TIME)

        w = self.Watcher
        assert (isinstance(w, LogWatcher))
        fn = w._find_logfile()
        # self.message("Will use file '%s' for jump data (or a newer one if one is created later)\n" % fn)
        print("Will use file '%s' for jump data (or a newer one if one is created later)\n" % fn)

    def check_netlog(self):
        w = self.Watcher
        assert (isinstance(w, LogWatcher))
        if not w:
            return
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
        try:
            assert isinstance(sys, basestring)
        except AssertionError:
            print "sys is not a string:", sys

        jump = self.Router.next_jump(sys)

        if "not found" in jump.lower():
            if self.do_rerouting:
                if sys in self.no_reroute_systems:
                    self.say("In an unknown system, cannot reroute.")
                    return
                self.say("Not in a waypoint system.")
                self.find_route(sys)
            else:
                self.say("You're off course with rerouting disabled.")
                return

        dist = 0

        if 'arrived' in jump:  # or " found" in jump
            self.Speaker.speak_now(jump)
        else:
            try:
                dist = self.systems.distance_between(sys, jump)
                if dist:
                    txt = 'Next jump is: %d light years to ' % (dist or 0)
                    txt += self.Speaker.process_system_name(jump) + '!'
                    self.say(txt, not_now=False)
                    # self.Speaker.speak_system(jump)
                    self.message(" " + str(jump).upper() + ": %.1f LY" % dist)
                    if self.copy_jump_to_clipboard:
                        clipboard.setText(jump)
                        #os.system("echo %s | clip" % jump) # copy system to clipboard

                    if self.web_display:
                        self.web_display.main = '%s - %.1f LY jump' % (jump.upper(), dist or 0)
                        if raregoods.announcement(sys):
                            self.web_display.secondary = sys.upper() + ": " + raregoods.announcement(sys)
                        else:
                            self.web_display.secondary = '%.1f LY to ' % self.remaining_route_length()
                            self.web_display.secondary += str(self.Router.get_route()[-1]).upper()

                    if self.overlayWindow:
                        left = self.remaining_route_length()
                        self.overlayWindow.set_message('%s - %.1f LY (%.1f LY left)' % (jump.upper(), dist or 0, left))
                else:
                    self.say("Next jump: unknown.")
                    print "Unknown dist from ", sys, "to", jump
            except Exception, err:
                print "Error in check_route:", str(err)
                print locals()
                # raise

        self.next_jumps_time = time()
        if dist:
            self.reload_route_to_widget(notify=False)
            self.scroll_to_text(jump)

        if self.Router.route_complete():
            self.routing = False
            self.say('Routing complete!')
            if DO_RARE_GOOD_RUN:
                next_stop = rare_goods_route.pop()
                if not next_stop: return
                self.routing = True
                self.say("Trade run mode active! Next stop is %s!" % next_stop)
                self.find_route(start_system=system, destination_system=next_stop)

    def new_system_callback(self, system):
        self.next_jumps_time = time()
        self.start_system_cb.setEditText(system)
        self.message('# Entering system "%s" @ %s' % (system, asctime()))
        if self.routing:
            self.say('Entering system "%s . "' % system + raregoods.announcement(system), True)
            #self.say()
            QTimer().singleShot(NEXT_JUMP_WAIT_TIME, lambda: self.check_route(system))
            # self.Speaker.announce_system(system)  # TODO - adapt to self.say() strategy

            current_route = self.Router.get_route()
            target = current_route[-1]

            distance = self.remaining_route_length()

            if distance > 0 and self.Router.system_in_route(system):
                message = "%.1f Light years until %s" % (distance, target)
                self.say(message, not_now=False)
            else:
                self.say("Remaining distance unknown.")
                print "Not announcing distance %d from %s, not in %s" % (distance, system, str(current_route))

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

        # self.Watcher._last_visited = None # triggers arrival in new system logic on nxt check
        # self.find_route(self.Watcher._last_visited )

        # self.new_system_callback(self.Watcher.last_system())
        #
        self.check_route()

        # self.speak_next_jumps()

    def set_route_from_widget(self):
        route_text = self.RouteWidget.toPlainText()
        route = [l.strip() for l in route_text.split("\n")]
        self.Router = EliteRouter(route)

    def close(self, e):
        self.write_route()
        self.save_log()
        self.say("Goodbye Commander.")
        if self.web_display:
            self.web_display.stop()
        try:
            self.overlayWindow.close()
        except:
            print "Couldn't close overlay"
        e.accept()
        super(CopilotWidget, self).close()

    def save_log(self):
        log = self.MessageWidget.toPlainText()
        with open("%s.log" % APPNAME, "at") as f:
            # noinspection PyArgumentList
            time_string = QLocale(QLocale.English).toString(QDateTime.currentDateTime(), QLocale.ShortFormat)
            f.write("\n*********************************************************\n")
            f.write(time_string)
            f.write("\n*********************************************************\n")
            f.write(log)

    @staticmethod
    def read_log(lines=99999):
        log = []
        with open("%s.log" % APPNAME, "rt") as f:
            log = f.readlines()
            log = log[-lines:]

        return log

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

    def say(self, text, not_now=False):
        self.message('"' + text + '"')
        if self.muted:
            return
        try:
            # add message to queue
            # check if speaker busy
            # if not busy:
            # speak oldest message in queue
            # else
            # re-schedule in 0.5 seconds
            if self.Speaker:
                self.Speaker.speak(text, not_now)
        except Exception, err:
            print "!! Exception when speaking %s : %s %s" % (text, err.message, err.args)

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
        self.RouteWidget.setText(r_text.upper())

    def get_route_content(self):
        return self.RouteWidget.toPlainText()

    def message(self, text):
        self.MessageWidget.append(text)
        try:
            if self.verboseOverlay:
                self.overlayWindow.set_message(text)
        except:
            pass

    def display_help(self):
        help_text = _HELP
        self.MessageWidget.append(help_text)

    @staticmethod
    def donate():
        write_html("donate.html")
        QDesktopServices().openUrl("donate.html")
        QTimer().singleShot(15000, lambda: os.unlink("donate.html"))

    def speak_next_jumps(self, ignore_flags=False):
        # don't announce if checkbox unset
        if not self.upcoming_flag and not ignore_flags:
            return

        # don t announce upcoming jumps if we recently got somewhere
        t = time()
        time_since_jump = t - self.next_jumps_time
        if time_since_jump < UPCOMING_ANNOUNCE_BLOCK_TIME and not ignore_flags:
            print("Not announcing upcoming jumps, we just jumped %.0f s ago" % time_since_jump)
            return
        self.next_jumps_time = t
        r = self.Router
        assert (isinstance(r, EliteRouter))
        jumps = r.remaining_route(UPCOMING_JUMPS_NO)
        if not r.route_complete():
            self.say("Upcoming jumps:")
            prev = self.Watcher.last_system()
            for jump in jumps:
                dist = self.systems.distance_between(prev, jump)
                self.say("%d light years to " % int(dist), not_now=True)
                if not self.muted:
                    self.Speaker.speak_system(jump)
                prev = jump

                if jump != jumps[-1]:
                    self.say(" then ", not_now=True)

    def netlog_path_dialog(self):
        f_name, _ = QFileDialog().getOpenFileName(self, 'Navigate to one of the netLog files', '.', "netlog*.*")
        logpath = os.path.dirname(f_name)
        if logpath:
            self.set_log_path(logpath)
            print "Log path set to ", logpath

    def find_route(self, start_system=None, destination_system=None):
        print "searching currently:", str(self.searching_route)
        if self.searching_route:
            self.message("Already routing, wait a moment please.")
            self.say("Still busy finding a route, one moment please.")
            return

        self.route_btn.setEnabled(False)
        self.route_btn.setText("in progress")
        self.routing = False
        self.searching_route = True
        self.say("Routing ")
        if self.do_econ_routing:
            self.say("in low fuel mode!")
        self.message("\nThis will try to map a route according to the From/To boxes.")
        self.message("It's not fully optimized and may fail if your jump distance is small.")
        self.message("In 'save fuel' mode it will prefer shorter jumps to reduce fuel usage.\n")

        txt = self.RouteWidget.toPlainText()
        lines = [l.strip() for l in txt.split("\n")]
        while len(lines[-1]) < 2:
            del lines[-1]

        # start = start_system or lines[0]
        # start = self.Router._undone(start)
        start = start_system or self.start_system_cb.currentText()

        destination = destination_system or self.destination_system_cb.currentText()  # = lines[-1]
        try:
            # drive = float(lines[1])
            drive = float(self.drive_entry.text()) * 1.0  # possibly add system data inaccuracy workaround?

        except:
            self.message("No floating point found in second line, using default")
            drive = -1

        self.systems.economic_routing = self.do_econ_routing

        route = self.systems.route(start, destination, drive, avoid_systems=self.bad_systems)

        self.searching_route = False
        if not route:
            self.message("Couldn't find a route")
            self.searching_route = False
            self.route_btn.setEnabled(True)
            self.route_btn.setText("Find Route")
            return

        self.default_jump_length = self.systems.last_routing_jump_distance
        params = (len(route) - 1, start, destination, self.default_jump_length)
        self.message("Route with %d jumps from %s to %s with %.1f LY jump distance." % params)

        self.RouteWidget.setText("\n".join(route))
        self.routing = True
        self.set_route_from_widget()

        params = len(route) - 1, self.systems.route_length(route)
        if params[1] < 0:
            self.say("No route found, you might need to upgrade your F S D.")
            print "start", start, "route", route
            if "unknown" in route[0]:
                self.no_reroute_systems.append(start)
                print "Start system %s added to rerouting exclusion list" % start
            if "unknown" in route[-1]:
                self.no_reroute_systems.append(destination)
                print "Destination system %s added to rerouting exclusion list" % destination

        else:
            self.say("Route found. %d jumps, %d light years total." % params)
            # self.confirm_jump(start)
            QTimer().singleShot(200, lambda: self.check_route())
            # self.message(",".join(route))

        self.searching_route = False
        self.route_btn.setEnabled(True)
        self.route_btn.setText("Find Route")

    def remaining_route_length(self):
        route = self.Router.remaining_route()
        light_years = self.systems.route_length(route)
        return light_years

    def confirm_jump(self, system=None):
        next_system = system or self.Router.remaining_route()[0]
        self.reload_route_to_widget()
        self.Watcher.fake_system(next_system)
        self.new_system_callback(next_system)

    def next_best_jumps(self, system=None):
        import math

        r = self.Router
        s = self.systems
        assert (isinstance(r, EliteRouter))

        route = r.remaining_route(99)
        start = s.guess_system_name(self.Watcher.last_system(), True)
        target = s.guess_system_name(route[0])
        try:
            dist = s.distance_between(start, target)

            systems = s.econ_neighbor_ranks(start, target, min(dist * 0.8, 14.0), self.bad_systems)
            self.say("Possible jump targets from %s to %s" % (start, target))
            if self.verbose:
                self.say("which is %.0f light years away" % dist)
        except Exception, e:
            print "Error in next_best_jumps :(", e
            print locals()
            systems = []

        spoken = 0
        for sys in systems[:4]:
            system_name = sys[0][0]
            new_dist = math.sqrt(sys[1])
            print system_name, new_dist
            jump_dist = s.distance_between(start, system_name)
            if system_name == target:
                continue
            if new_dist > dist or jump_dist > dist:
                continue
            if spoken >= 3:
                continue
            # if new_dist > dist: continue
            self.say("%.0f Light years to" % new_dist, not_now=True)
            self.Speaker.speak_system(str(system_name), not_now=True)
            self.say("%.0f light years left" % jump_dist)
            spoken += 1

        if not spoken:
            self.say("Sorry, no alternatives found.")

    def repeat_jump(self):
        r = self.Router
        s = self.systems
        start = s.guess_system_name(self.Watcher.last_system(), True)
        route = r.remaining_route(99)
        target = s.guess_system_name(route[0])
        dist = s.distance_between(start, target)
        self.say("Please jump %d light years to %s" % (dist, target))

    def avoid_next_jump(self):
        next_jump = self.Router.remaining_route(1)[0]
        self.say("Avoiding %s" % next_jump)
        self.bad_systems.append(next_jump)
        try:
            start_sys = self.Watcher.last_system()
        except:
            start_sys = None
        self.find_route(start_sys)

    def show_jump_log(self):
        # read previous sessions
        log = self.read_log()
        # add the current session
        current_log = [line + "\n" for line in self.MessageWidget.toPlainText().split("\n")]
        log.extend(current_log)
        # print "curr:", current_log
        # print "log:", log
        jumps = [l.replace("!", "") for l in log if l.startswith("#") or " 201" in l]

        previous = None
        old_date = None
        filtered = []
        for jump in jumps:
            if " 201" in jump:
                if jump[:8] != old_date:
                    filtered.append(jump)
                old_date = jump[:8]
                continue

            if jump != previous:
                filtered.append(jump)
                previous = jump

        filtered.reverse()

        with open("jumps.log", "wt") as f:
            try:
                f.writelines(filtered)
                QDesktopServices().openUrl("jumps.log")
            except Exception, err:
                print "Error:", err
                print "filtered:", filtered

    def scroll_to_text(self, jump):
        # self.say("Delaying things a little bit")
        print "Scrolling to %s" % jump
        #self.RouteWidget.setFocus(Qt.MouseFocusReason)

        tc = self.RouteWidget.textCursor()
        #print "TC pos",tc.position()

        found = self.RouteWidget.find(jump)
        if not found:
            return

        # select line with jump target
        tc.select(QTextCursor.LineUnderCursor)

        return

        # debug stuff below, turns out reload_route_to_widget was the problem, cursor was fine here!

        #print "Found: %s" % str(found)
        #pos = tc.position()
        #print "TC pos",pos
        #self.say("Delaying things a little more")
        #cur = QTextCursor()
        #cur.setPosition(pos)
        #self.RouteWidget.setTextCursor(cur)
        #self.RouteWidget.moveCursor()
        #QTextCursor.sel


class CopilotWindow(QMainWindow):
    def __init__(self, parent=None):
        super(CopilotWindow, self).__init__(parent)

        fn = '%s.ini' % APPNAME
        print("Reading settings from " + fn)
        self.settings = QSettings(fn, QSettings.IniFormat)

        self.mainWidget = CopilotWidget(self)
        self.setWindowTitle("%s %s" % (APPNAME, APPVERSION))
        self.setCentralWidget(self.mainWidget)

        self.autoFillBackground()

        pal = QPalette()
        # x# bgcolor = self.settings.value("bgcolor", None) # no easy way to get something that works from QSettings :S

        #x#pal.setColor(QPalette.Background, QColor(40, 30, 40))
        pal.setColor(QPalette.Background, QColor(200, 90, 10))

        # fgcolor = self.settings.value("fgcolor", None)
        #x#pal.setColor(QPalette.Foreground, QColor(40, 235, 40))

        # pal.setColor(QPalette.Button, QColor("black"))
        # pal.setColor(QPalette.Window,QColor("Black"))
        #x#pal.setColor(QPalette.Disabled, QPalette.Background, QColor(50, 50, 50))
        #x#pal.setColor(QPalette.Inactive, QPalette.Background, QColor(50, 50, 50))
        #w.setPalette(pal)
        #w.setFont(QFont("Arial narrow", 11))
        # w.setTextColor(QColor("green"))
        # w.setTextBackgroundColor(QColor("black"))

        if not self.settings.value("resizable_window", "False").lower() == "true":
            self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)
        #self.setWindowFlags(Qt.SplashScreen)
        self.netlog_path = ""

        self.setStyleSheet("* {background-color: #000;}")
        try:
            self.setStyleSheet(open("style-background.txt".read()))
        except Exception, err:
            print "No main style sheet", err.message

        self.initialize()

    def initialize(self):
        self.netlog_path = self.settings.value("NetlogPath", "")
        route_text = self.settings.value("LastRoute", "DONE: No Route")

        # self.setStyleSheet(styles.default_style)

        self.mainWidget.set_route_text(route_text)
        self.mainWidget.set_log_path(self.netlog_path)
        self.mainWidget.initialize()

        tim = QTimer() # = self.styletimer =
        tim.timeout.connect(self.restyle)
        tim.start(10000)

    def restyle(self):
        mine = self.styleSheet()
        main = self.mainWidget.styleSheet()
        if mine == main:
            return
        if self.mainWidget.style == styles.default_style:
            return
        print "Restyling main window"
        self.setStyleSheet(main)

    def write_settings(self):
        global global_hot_key_1, global_hot_key_2, global_hot_key_3
        self.settings.setValue("NetlogPath", self.mainWidget.get_log_path())
        self.settings.setValue("Nato_spelling", self.mainWidget.nato_spell)
        self.settings.setValue("Hyphen_spelling", self.mainWidget.hyphen_spell)
        # self.settings.setValue("Route_caching", self.mainWidget.route_caching)
        self.settings.setValue("LastRoute", self.get_route_text())
        self.settings.setValue("Default_jump_length", self.mainWidget.default_jump_length)
        self.settings.setValue("Hotkey_1", global_hot_key_1)
        self.settings.setValue("Hotkey_2", global_hot_key_2)
        self.settings.setValue("Hotkey_3", global_hot_key_3)
        self.settings.setValue("Verbose", self.mainWidget.verbose)

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
clipboard = app.clipboard()
win = CopilotWindow()
win.show()
app.exec_()
