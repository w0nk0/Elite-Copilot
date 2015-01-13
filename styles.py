__author__ = 'W0nk0'

default_style = """
/* DARK style*/

* { alternate-background-color: #222; background: #111; border-color: #630; border-width: 0px; }
QWidget { background: #000; }
QTextEdit { background: #111; border-color: #630; border-style: inset; border-width: 1px; }
QPushButton { background: #b50; color: #eee; padding:  1px; height: 1.25em;}
xQPushButton { background: #333; color: #c60; padding:  1px; height: 1.25em;}
QPushButton { border-width: 4px; border-radius: 2px; padding: 2px;  }
QLineEdit, QCheckBox, QLabel, QComboBox, QComboBox QAbstractItemView { color: #b50; background: #000; }
QLineEdit { background: #333; color: #d70; border-style:none; }
QComboBox { max-width: 9.5em; background-color: #333;  }
xQComboBox QAbstractItemView { background-color: #333; }
QCheckBox { alternate-background-color: #222; spacing: 5px;}


/* LIGHT style

QTextEdit { background: #000; }
QPushButton { background: #c86600; color: white; padding:  1px; height: 1.25em;}
QLineEdit, QCheckBox, QLabel, QComboBox, QComboBox QAbstractItemView { color: #c86600; background: #eee; }
xQLineEdit { background: #eee; color: black; }
QPushButton { border-width: 4px; border-radius: 2px; padding: 2px;  }
QComboBox { max-width: 9.5em; }
QComboBox QAbstractItemView { background-color: #eee; }
QWidget#CopilotWindow { background: #eee; }
*/

"""

overlay_style = """
QPushButton { background: #c86600; color: black; }
QLineEdit, QPushButton { border 4px none #c86600; border-radius: 4px; }
* { color: #c86600; }
* { font: bold 14px ; }
* { background: #000000; }
QLineEdit { color: #d70; background: black; }
xQLineEdit { background: #d70; color: black; }
"""