SP_FAST = 130
SP_SLOW = 98

import pyttsx

class EliteTalker:
    def __init__(self):
        self.speech = self.s = pyttsx.init()
        self.speaking = False
        self.set_normal()

    def say(self,text):
        "Just a shorthand for speak()"
        self.speak_now(text)

    def speak_now(self,text):
        self.speak(text)
        self.flush()

    def speak(self, text):
        self.set_normal()
        self.s.say(text)

    def flush(self):
        if self.speaking:
            print "Already speaking.."
            return
        self.speaking = True
        self.s.runAndWait()
        self.speaking = False

    def set_slow(self):
        self.s.setProperty("rate", SP_SLOW)

    def set_normal(self):
        self.s.setProperty("rate", SP_FAST)

    def speak_system(self,system):
        self.set_slow()
        sys=self._system_speakify(system)
        self.speak_now(sys)
        self.set_normal()

    def _system_speakify(self,txt):
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
        self.say("Arrived in system ")
        self.speak_system(system+"!!")
