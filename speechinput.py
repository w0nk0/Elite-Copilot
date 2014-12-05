__author__ = 'nico'
import speech

while True:
    phrase = speech.input()
    speech.say("You said %s" % phrase)
    if phrase.lower() == "turn off":
        break