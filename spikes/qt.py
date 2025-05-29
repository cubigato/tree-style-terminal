#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple PyQt5 Terminal Widget Application
"""

from PyQt5.QtWidgets import QApplication, QMainWindow
from qtermwidget import QTermWidget

app = QApplication([])
win = QMainWindow()
term = QTermWidget()
term.setColorScheme("Linux")
term.startShellProgram()    # z.B. /bin/bash
win.setCentralWidget(term)
win.resize(800, 600)
win.show()
app.exec_()
