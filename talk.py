SP_FAST = 130
SP_SLOW = 95

import pyttsx

from hyphenate import hyphenate_word
from natospell import nato_spell


class EliteTalker:
    def __init__(self, nato_spelling=False, hyphen_spelling=False, nato_max_len=7):
        self.speech = self.s = pyttsx.init()
        self.speaking = False
        self.set_normal()
        self.nato = nato_spelling
        self.nato_max_length = nato_max_len
        self.hyphen = hyphen_spelling

    def say(self, text):
        """Just a shorthand for speak()"""
        self.speak_now(text)

    def speak_now(self, text):
        self.speak(text, not_now=False)
        self.flush()

    def speak(self, text, not_now=False):
        self.s.say(text)
        if not_now:
            return
        self.flush()

    def flush(self):
        if self.speaking:
            print "Already speaking.."
            return
        self.speaking = True
        self.s.runAndWait()
        self.speaking = False

    def set_slow(self):
        self.speech.setProperty("rate", SP_SLOW)

    def set_normal(self):
        self.speech.setProperty("rate", SP_FAST)

    def speak_system(self, system):

        #print "## DEBUG Speak system, nato, hyphen", system, self.nato, self.hyphen
        sys = system

        if self.hyphen==True:
            #print "##DEBUG Hyphen speaking"
            sys = self._system_speakify(system)
            sys = " ".join(hyphenate_word(sys))

        if self.nato==True:
            #print "##DEBUG Nato speaking"
            sys = system
            sys_nato = ""
            for w in sys.split(" "):
                if len(w) < self.nato_max_length:
                    sys_nato += " "+nato_spell(w)
                else:
                    sys_nato += " "+w
            sys = sys_nato
        #print "## DEBUG sys", sys

        if self.nato:
            self.set_normal()
        else:
            self.set_slow()

        self.speak_now(sys)
        self.set_normal()

    @staticmethod
    def _system_speakify(txt):
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

    def announce_system(self, system):
        self.s.setProperty("rate", SP_FAST)
        self.say("Entering system ")
        self.speak(system + "!!")
