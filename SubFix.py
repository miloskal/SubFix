#!/usr/bin/python3

from sys import argv
from regex import compile, match
from utilityFunctions import *

from PyQt5.QtWidgets import QApplication, QWidget, QDialog, QFileDialog, \
    QComboBox, QMessageBox, QAbstractItemView, QShortcut
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QKeySequence, QIcon
import PyQt5.uic as uic
from pathlib import Path
from platform import system

__platform__ = system()

class MainWindow(QDialog):

    TIMESTAMP_LINE_REGEX = compile("[0-9]{2}:[0-5][0-9]:[0-5][0-9],[0-9]{3} --> "\
                   "[0-9]{2}:[0-5][0-9]:[0-5][0-9],[0-9]{3}")

    ARROW_SPLIT_REGEX = compile(" --> ")

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.ui = uic.loadUi("layout.ui", self)
        self.setWindowIcon(QIcon("icon.png"))
        self.ui.browseFpsPushButton.released.connect(self.browseForSubtitle)
        self.ui.browseCodepagePushButton.released.connect(self.browseForSubtitle)
        self.ui.browseRewindPushButton.released.connect(self.browseForSubtitle)
        self.ui.fixFpsPushButton.released.connect(self.correctSubtitleFps)
        self.ui.translateCodepagePushButton.released.connect(self.translateCodepage)
        self.ui.rewindPushButton.released.connect(self.rewindSubtitle)
        self.model = QStandardItemModel()
        self.ui.rewindSubtitlesListView.setModel(self.model)
        self.ui.fpsSubtitlesListView.setModel(self.model)
        self.ui.codepageSubtitlesListView.setModel(self.model)
        self.ui.rewindSubtitlesListView.setSelectionMode(QAbstractItemView.NoSelection)
        self.ui.fpsSubtitlesListView.setSelectionMode(QAbstractItemView.NoSelection)
        self.ui.codepageSubtitlesListView.setSelectionMode(QAbstractItemView.NoSelection)

    #slot
    def browseForSubtitle(self):
        if __platform__ == "Linux":
            directory = "/home"
        elif __platform__ == "Windows":
            directory = "C:\\\\Users"
        self.filenames = QFileDialog.getOpenFileNames(parent=self, directory=directory,
                                             caption="Browse for subtitles",
                                             filter="Subtitle files (*.srt | *.txt)")
        self.filenames = self.filenames[0]
        for filename in self.filenames:
            item = QStandardItem(filename)
            item.setEditable(False)
            self.model.appendRow(item)


    #slot
    def translateCodepage(self):
        oldCodepage = self.ui.oldCodepageComboBox.currentText()
        newCodepage = self.ui.newCodepageComboBox.currentText()
        if oldCodepage == "Windows 1250 (Latin)" and\
            newCodepage == "UTF-8 (Latin)":
            # cp1250 --> utf8 latin
            for filename in self.filenames:
                cp1250ToUtf8(filename)
            self.success("Conversion cp1250 --> utf8(latin) done")
        elif oldCodepage == "Windows 1250 (Latin)" and\
             newCodepage == "UTF-8 (Cyrillic)":
            # cp1250 --> utf8 cyrillic
            for filename in self.filenames:
                cp1250ToUtf8(filename)
                utf8Convert(filename, direction="cyr")
                removeTags(filename, newCodepage)
            self.success("Conversion cp1250 --> utf8(cyrillic) done")
        elif oldCodepage == "UTF-8 (Cyrillic)" and\
             newCodepage == "UTF-8 (Latin)":
            # utf8 cyrillic --> utf8 latin
            for filename in self.filenames:
                utf8Convert(filename, direction="lat")
            self.success("Conversion utf8(cyrillic) --> utf8(latin) done")
        elif oldCodepage == "UTF-8 (Latin)" and\
             newCodepage == "UTF-8 (Cyrillic)":
            # utf8 latin --> utf8 cyrillic
            for filename in self.filenames:
                utf8Convert(filename, direction="cyr")
                removeTags(filename, newCodepage)
            self.success("Conversion utf8(latin) --> utf8(cyrillic) done")
        elif oldCodepage == "UTF-8 (Latin)" and\
             newCodepage == "Windows 1250 (Latin)":
            # utf8 latin --> cp1250
            for filename in self.filenames:
                utf8ToCp1250(filename)
            self.success("Conversion utf8(latin) --> cp1250 done")
        elif oldCodepage == "UTF-8 (Cyrillic)" and\
             newCodepage == "Windows 1250 (Latin)":
            # utf8 cyrillic --> cp1250
            for filename in self.filenames:
                utf8Convert(filename, direction="lat")
                utf8ToCp1250(filename)
            self.success("Conversion utf8(cyrillic) --> cp1250 done")
        else:
            self.failure("Conversion failed.")


    #slot
    def correctSubtitleFps(self):
        oldFps = float(self.ui.oldFpsComboBox.currentText())
        newFps = float(self.ui.newFpsComboBox.currentText())
        enc = self.ui.fpsEncodingComboBox.currentText()
        if enc == "Windows 1250 (Latin)":
            encoding = "cp1250"
        elif enc == "UTF-8":
            encoding = "utf-8"
        else:
            self.failure("Invalid encoding")
            return
        for filename in self.filenames:
            input = filename
            output = f"{input}.out"
            with open(output, "w", encoding=encoding) as out:
                with open(input,encoding=encoding) as f:
                    for line in f:
                        match = self.TIMESTAMP_LINE_REGEX.match(line)
                        if match:
                            result = correctFpsInLine(match.group(), oldFps, newFps)
                            out.write(result + "\n")
                        else:
                            out.write(line)

    #slot
    def rewindSubtitle(self):
        enc = self.ui.rewindEncodingComboBox.currentText()
        if enc == "Windows 1250 (Latin)":
            encoding = "cp1250"
        elif enc == "UTF-8":
            encoding = "utf-8"
        else:
            self.failure("Invalid encoding")
            return
        delay = int(self.ui.rewindMilisecondsLineEdit.text())
        for filename in self.filenames:
            input = filename
            output = f"{input}.out"
            with open(output, "w", encoding=encoding) as out:
                with open(input, encoding=encoding) as f:
                    for line in f:
                        match = self.TIMESTAMP_LINE_REGEX.match(line)
                        if match:
                            result = rewindLine(match.group(), delay)
                            out.write(result + "\n")
                        else:
                            out.write(line)
            remove (input)
            rename (output, input)
        self.success("Done")

    def success(self, message):
        window = QMessageBox.information(self, "Success", message)
        
    def failure(self, message):
        window = QMessageBox.critical(self, "Failure", message)

# main
if __name__ == "__main__":
    app = QApplication(argv)
    window = MainWindow()
    window.setWindowTitle("Subtitle Fixer")
    window.show()
    app.exec_()



