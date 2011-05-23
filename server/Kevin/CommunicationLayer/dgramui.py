"""dgramui.py script

This program creates a user interface for dgraminterface.py
"""

__author__ = "Kevin Quinn"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2011/05/09 18:46:00 $"


import sys
from PyQt4 import QtGui, QtCore
CMD={"0101":"MEMORY AREA READ",
     "0102":"MEMORY AREA WRITE",
     "0103":"MEMORY AREA FILL",
     "0104":"MULTIPLE MEMORY AREA READ",
     "0105":"MEMORY AREA TRANSFER",
     "0201":"PARAMETER AREA READ",
     "0202":"PARAMETER AREA WRITE",
     "0203":"PARAMETER AREA CLEAR",
     "0306":"PROGRAM AREA READ",
     "0307":"PROGRAM AREA WRITE",
     "0308":"PROGRAM AREA CLEAR",
     "0401":"RUN",
     "0402":"STOP",
     "0501":"CPU UNIT DATA READ",
     "0502":"CONNECTION DATA READ",
     "0601":"CPU UNIT STATUS READ",
     "0620":"CYCLE TIME READ",
     "0701":"CLOCK READ",
     "0702":"CLOCK WRITE",
     "0920":"MESSAGE CLEAR",
     "0C01":"ACCESS RIGHT ACQUIRE",
     "0C02":"ACCESS RIGHT FORCED ACQUIRE",
     "0C03":"ACCESS RIGHT RELEASE",
     "2101":"ERROR CLEAR",
     "2102":"ERROR LOG READ",
     "2103":"ERROR LOG CLEAR",
     "2140":"FINS WRITE ACCESS LOG READ",
     "2141":"FINS WRITE ACCESS LOG CLEAR",
     "2201":"FILE NAME READ",
     "2202":"SINGLE FILE READ",
     "2203":"SINGLE FILE WRITE",
     "2204":"FILE MEMORY FORMAT",
     "2205":"FILE DELETE",
     "2207":"FILE COPY",
     "2208":"FILE NAME CHANGE",
     "220A":"MEMORY AREA FILE TRANSFER",
     "220B":"PARAMETER AREA FILE TRANS",
     "220C":"PROGRAM AREA FILE TRANSF",
     "2215":"CREATE/DELETE DIRECTORY",
     "2220":"MEMORY CASSETTE TRANSFER",
     "2301":"FORCED SET/RESET ",
     "2302":"FORCED SET/RESET CANCEL"}


class Example(QtGui.QWidget):
  
    def __init__(self):
        super(Example, self).__init__()

        self.initUI()


    def initUI(self):
        self.label = QtGui.QLabel("You selected:", self)
      
        combo = QtGui.QComboBox(self)
        for value in CMD.values():
          combo.addItem(value)

        combo.move(50, 50)
        self.label.move(50, 150)

        self.connect(combo, QtCore.SIGNAL('activated(QString)'), self.onActivated)

        self.setGeometry(250, 200, 350, 250)
        self.setWindowTitle('OMRON PLC Hardware Comm')

    def onActivated(self, text):
        self.label.setText("You selected: %s" % text)
        self.label.adjustSize()


def main():
    app = QtGui.QApplication([])
    ex = Example()
    ex.show()
    app.exec_()    


if __name__ == '__main__':
    main()