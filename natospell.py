__author__ = 'nico'

nato_alphabet = "Alpha, Bravo, Charlie, Delta, Echo, Foxtrot, Golf, Hotel, India, Juliet, Kilo, Leema, Mike, November, Oscar, Papa, Quebec, Romeo, Sierrah, Tango, Uniform, Victor, Whiskey, X-ray, Yankee, Zulu"
nato_alphabet = [w.strip() for w in nato_alphabet.split(",")]


def nato_letter(letter):
    for word in nato_alphabet:
        if word.lower().startswith(letter.lower()):
            return word
    return letter


def nato_spell(word, separator=", "):
    items = [nato_letter(l) for l in word]
    return separator.join(items)