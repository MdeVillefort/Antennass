#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
My graphical user interface
ECE 584 Antenna Theory and Design
Midterm Project
@Author: Ethan Ross
"""

# System
import os
import sys

# Data
import numpy as np
from .arrays import *

# GUI
from PyQt5.QtWidgets import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.qt_compat import QtCore
plt.style.use('ggplot')

class GUI(QMainWindow):
    """Main gui window"""

    def __init__(self, parent = None):
        super().__init__(parent)

        # Window properties
        self.setWindowTitle("Linear Array Program")
        self.setGeometry(100, 100, 600, 400)

        # Create plotting space
        self.tabs = QTabWidget()
        self.figure = plt.Figure()
        self.figurepolar = plt.Figure()
        self.figure3d = plt.Figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvaspolar = FigureCanvas(self.figurepolar)
        self.canvas3d = FigureCanvas(self.figure3d)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title('Antenna Pattern')
        self.axpolar = self.figurepolar.add_subplot(111, projection = 'polar')
        self.axpolar.set_title('Antenna Pattern')
        self.ax3d = self.figure3d.add_subplot(111, projection = '3d')
        self.ax3d.set_title('Antenna Pattern')
        self.tabs.addTab(self.canvas, "Main")
        self.tabs.addTab(self.canvaspolar, "Polar")
        self.tabs.addTab(self.canvas3d, "3d")
        #self.tabs.currentChanged.connect(self.set_navbar)
        self.setCentralWidget(self.tabs)
        
        # Create tool bars; hide ones for invisible plots
        """
        self.navbar = NavigationToolbar(self.canvas, self)
        self.navbarpolar = NavigationToolbar(self.canvaspolar, self)
        self.navbar3d = NavigationToolbar(self.canvas3d, self)
        self.addToolBar(QtCore.Qt.BottomToolBarArea, self.navbar)
        self.state1 = self.saveState(1)
        self.removeToolBar(self.navbar)
        self.addToolBar(QtCore.Qt.BottomToolBarArea, self.navbarpolar)
        self.state2 = self.saveState(2)
        self.removeToolBar(self.navbarpolar)
        self.addToolBar(QtCore.Qt.BottomToolBarArea, self.navbar3d)
        self.state3 = self.saveState(3)
        self.removeToolBar(self.navbar3d)
        self.restoreState(self.state1, 1)
        """
        
        # Create menu bar
        self.menubar = self.menuBar()
        self.arraymenu = self.menubar.addMenu("&Arrays")
        self.arraymenu.addAction("&New", self.createArray)
        self.arraymenu.addAction("&Clear", self.deleteArray)
        self.arraymenu.addAction("&Plots", self.plot)
        self.quitmenu = self.menubar.addMenu("&Quit")
        self.quitmenu.addAction("&Exit program", self.close)

        # Create status bar
        self.statusbar = QStatusBar()
        self.statusbar.showMessage("No array defined.")
        self.setStatusBar(self.statusbar)

        # The antenna array object
        self.array = None
        
    def set_navbar(self):
        """Adjust navigation tool bar when tab is changed."""
        
        
        if self.tabs.currentIndex() == 0:
            self.restoreState(self.state1, 1)
        elif self.tabs.currentIndex() == 1:
            self.restoreState(self.state2, 2)
        elif self.tabs.currentIndex() == 2:
            self.restoreState(self.state3, 3)

    def createArray(self):
        """Open separate gui to create Array object."""
        
        createArrGUI = MakeArrayGUI(self)
        createArrGUI.exec()

        if self.array:
            self.statusbar.showMessage(f"{repr(self.array)}")

    def deleteArray(self):
        """Remove currently defined array."""

        self.array = None
        self.statusbar.showMessage("No array defined")

    def plot(self):
        pass

class MakeArrayGUI(QDialog):
    """GUI to open when making a new array object."""

    def __init__(self, parent = None):
        super().__init__(parent)
        self.parent = parent

        # Window properties
        self.setWindowTitle("Create an Array")
        self.setGeometry(100, 100, 200, 150)

        # Layout managers
        layout = QVBoxLayout()
        formlayout = QFormLayout()
        self.amplitude = QLineEdit()
        self.phase = QLineEdit()
        self.spacing = QLineEdit()
        self.numElems = QLineEdit()
        formlayout.addRow('Amplitude:', self.amplitude)
        formlayout.addRow('Phase:', self.phase)
        formlayout.addRow('Spacing:', self.spacing)
        formlayout.addRow('# Elements:', self.numElems)
        btns = QDialogButtonBox()
        btns.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        layout.addLayout(formlayout)
        layout.addWidget(btns)
        self.setLayout(layout)

        # Set signal/slot relationship
        btns.rejected.connect(lambda: self.close())
        btns.accepted.connect(self.accept)

    def accept(self):
        try:
            amp = float(self.amplitude.text())
            ph = float(self.phase.text())
            space = float(self.spacing.text())
            N = float(self.numElems.text())
        except:
            print('Invalid input')
            return

        if amp and ph and space and N:
            self.parent.array = Array(amp, ph, space, N)
            self.close()
        elif N % 2 != 0:
            print('N must be even')
            return
        else:
            print('Empty input')
            return

class plotGUI(QDialog):
    """GUI to select plot type"""

    def __init__(self, parent = None):
        super().__init__(parent)
        self.parent = parent

def main():
    app = QApplication([])
    prog = GUI()
    prog.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
