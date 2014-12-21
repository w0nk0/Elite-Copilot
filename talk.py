SP_FAST = 150
SP_SLOW = 100

import pyttsx
import time

from hyphenate import hyphenate_word
from natospell import nato_spell

import ConfigParser


class EliteTalker:
    def __init__(self, nato_spelling=False, hyphen_spelling=False, nato_max_len=7):
        self.speech = self.s = pyttsx.init()
        self.FAST = SP_FAST
        self.SLOW = SP_SLOW

        self.speaking = False
        self.set_normal()
        self.nato = nato_spelling
        self.nato_max_length = nato_max_len
        self.hyphen = hyphen_spelling
        self.read_ini()
        self.set_normal()

    def set_voice(self, voice_id = None, voice_number=None):
        print "Available voices:"
        voices = self.s.getProperty("voices")
        for v in voices:
            print "Name: %-15s - ID: %60s " % (v.name, v.id)

        try:
            if voice_id:
                self.s.setProperty("voice",voice_id)
                print "Setting voice to ", voice_id
            if voice_number:
                self.set_voice_number(voice_number)
        except Exception,e:
            print "Error setting the voice!"
            print e
            print locals()

    def read_ini(self):
        try:
            p = ConfigParser.ConfigParser()
            p.read("speech.ini")
            voice = p.getint("Voice","id")
            self.set_voice(voice_number=voice)
            self.FAST = p.getint("Voice","speed_fast") or SP_FAST
            self.SLOW = p.getint("Voice","speed_slow") or SP_SLOW
        except Exception,e:
            print "Couldn't read speech.ini"
            print e
            print locals()

    def set_voice_number(self, voice_number):
        voices = self.s.getProperty("voices")
        self.s.setProperty("voice",voices[voice_number].id)
        print "Setting voice to ", voices[voice_number].id

    def say(self, text):
        """Just a shorthand for speak()"""
        return self.speak_now(text)

    def speak_now(self, text):
        self.speak(text, not_now=False)
        return self.flush()

    def speak(self, text, not_now=False):
        if "next jump" in text or "entering" in text:
            text = self._numbers_speakify(text)
        self.s.say(text)
        if not_now:
            return
        return self.flush()

    def flush(self):
        if self.speaking:
            print "Already speaking..",

            # this isn't running in a thread! It will never succeed so disabling it

            #counter = 5
            # while counter and self.speaking:
            #     print ".",
            #     counter -= 1
            #     time.sleep(0.1)
            #     #self.s.stop()
            if self.speaking:
                print "stopping."
                #self.s.stop()
                return False
            #print "waited enough."

        self.speaking = True
        try:
            self.s.runAndWait()
        except RuntimeError:
            print "Runtime Error while uttering speech"

        self.speaking = False
        return True

    def set_slow(self):
        self.speech.setProperty("rate", SP_SLOW)

    def set_normal(self):
        #self.speech.setProperty("rate", int((self.FAST*5+self.SLOW*1) / 6))
        self.speech.setProperty("rate", self.FAST)

    def speak_system(self, system):

        #print "## DEBUG Speak system, nato, hyphen", system, self.nato, self.hyphen
        sys = system

        if self.hyphen==True:
            #print "##DEBUG Hyphen speaking"
            sys = self._numbers_speakify(system)
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
    def _numbers_speakify(txt):
        new_txt = ""
        counter = 0
        for c in txt:
            new_txt += c
            if c in "0123456789":
                counter += 1
                if counter > 1:
                    new_txt += " "
                    counter = 0
            else:
                counter = 0
            if c == "-":
                new_txt += "dash"

        return new_txt

    def announce_system(self, system):
        self.s.setProperty("rate", SP_FAST)
        self.say("Entering system ")
        self.speak(system + "!!")

if __name__ == "__main__":
    e = EliteTalker()
    e.say("This is a test!")
    e.flush()
