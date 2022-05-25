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

    SUB_LINE_REGEX = compile("\{(\d+)\}\{(\d+)\}\s*(.*)(\r)?(\n)?")

    ARROW_SPLIT_REGEX = compile(" --> ")

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.ui = uic.loadUi("layout.ui", self)
        self.setWindowIcon(QIcon("icon.png"))
        self.ui.browseFpsPushButton.released.connect(self.browseForSrtSubtitle)
        self.ui.browseCodepagePushButton.released.connect(self.browseForSrtSubtitle)
        self.ui.browseRewindPushButton.released.connect(self.browseForSrtSubtitle)
        self.ui.browseConvertToSrtPushButton.released.connect(self.browseForSubSubtitle)
        self.ui.fixFpsPushButton.released.connect(self.correctSubtitleFps)
        self.ui.translateCodepagePushButton.released.connect(self.translateCodepage)
        self.ui.rewindPushButton.released.connect(self.rewindSubtitle)
        self.ui.convertToSrtPushButton.released.connect(self.convertToSrt)
        self.model = QStandardItemModel() # model for .srt files
        self.modelSub = QStandardItemModel() # model for .sub files
        self.ui.rewindSubtitlesListView.setModel(self.model)
        self.ui.fpsSubtitlesListView.setModel(self.model)
        self.ui.codepageSubtitlesListView.setModel(self.model)
        self.ui.convertToSrtListView.setModel(self.modelSub)
        self.ui.rewindSubtitlesListView.setSelectionMode(QAbstractItemView.NoSelection)
        self.ui.fpsSubtitlesListView.setSelectionMode(QAbstractItemView.NoSelection)
        self.ui.codepageSubtitlesListView.setSelectionMode(QAbstractItemView.NoSelection)
        self.ui.convertToSrtListView.setSelectionMode(QAbstractItemView.NoSelection)

    #slot
    def convertToSrt(self):
        """
        Converts .sub to .srt
        """
        encoding = self.ui.convertToSrtEncodingComboBox.currentText()
        fps = float(self.ui.convertToSrtFpsComboBox.currentText())
        if encoding == "Windows 1250 (Latin)":
            enc = "cp1250"
        else:
            enc = "utf-8"
        for file in self.filenamesSub:
            with open(file, encoding=enc) as src, \
                 open(f"{file}.srt", "w", encoding=enc) as dst:
                for cnt, line in enumerate(src, start=1):
                    match = self.SUB_LINE_REGEX.match(line)
                    if match:
                        startFps = int(match.group(1))
                        endFps = int(match.group(2))
                        content = match.group(3)
                        content = content.replace("|", "\n")
                        original = f"[{cnt}] startFps='{startFps}' endFps='{endFps}' content='{content}'"
                        startTimestamp = frameToTimestamp(startFps, fps)
                        endTimestamp = frameToTimestamp(endFps, fps)
                        corrected = f"{cnt}\n{startTimestamp} --> {endTimestamp}\n{content}\n\n"
                        dst.write(corrected)
                    else:
                        print(f"no match in line {cnt}: {line}")
        self.success("Done!")

    #slot
    def browseForSrtSubtitle(self):
        if __platform__ == "Linux":
            directory = "/home"
        elif __platform__ == "Windows":
            directory = "C:\\\\Users"
        self.filenames = QFileDialog.getOpenFileNames(parent=self, directory=directory,
                                             caption="Browse for subtitles",
                                             filter="Subtitle files (*.srt | *.txt)")
        self.filenames = self.filenames[0]
        self.model.clear()
        for file in self.filenames:
            item = QStandardItem(file)
            item.setEditable(False)
            self.model.appendRow(item)
    
    #slot
    def browseForSubSubtitle(self):
        if __platform__ == "Linux":
            directory = "/home"
        elif __platform__ == "Windows":
            directory = "C:\\\\Users"
        self.filenamesSub = QFileDialog.getOpenFileNames(parent=self, directory=directory,
                                             caption="Browse for subtitles",
                                             filter="Subtitle files (*.sub | *.txt)")
        self.filenamesSub = self.filenamesSub[0]
        self.modelSub.clear()
        for file in self.filenamesSub:
            item = QStandardItem(file)
            item.setEditable(False)
            self.modelSub.appendRow(item)


    #slot
    def translateCodepage(self):
        oldCodepage = self.ui.oldCodepageComboBox.currentText()
        newCodepage = self.ui.newCodepageComboBox.currentText()
        if oldCodepage == "Windows 1250 (Latin)" and\
            newCodepage == "UTF-8 (Latin)":
            # cp1250 --> utf8 latin
            for file in self.filenames:
                cp1250ToUtf8(file)
            self.success("Conversion cp1250 --> utf8(latin) done")
        elif oldCodepage == "Windows 1250 (Latin)" and\
             newCodepage == "UTF-8 (Cyrillic)":
            # cp1250 --> utf8 cyrillic
            for file in self.filenames:
                cp1250ToUtf8(file)
                utf8Convert(file, direction="cyr")
                removeTags(file, newCodepage)
            self.success("Conversion cp1250 --> utf8(cyrillic) done")
        elif oldCodepage == "UTF-8 (Cyrillic)" and\
             newCodepage == "UTF-8 (Latin)":
            # utf8 cyrillic --> utf8 latin
            for file in self.filenames:
                utf8Convert(file, direction="lat")
            self.success("Conversion utf8(cyrillic) --> utf8(latin) done")
        elif oldCodepage == "UTF-8 (Latin)" and\
             newCodepage == "UTF-8 (Cyrillic)":
            # utf8 latin --> utf8 cyrillic
            for file in self.filenames:
                utf8Convert(file, direction="cyr")
                removeTags(file, newCodepage)
            self.success("Conversion utf8(latin) --> utf8(cyrillic) done")
        elif oldCodepage == "UTF-8 (Latin)" and\
             newCodepage == "Windows 1250 (Latin)":
            # utf8 latin --> cp1250
            for file in self.filenames:
                utf8ToCp1250(file)
            self.success("Conversion utf8(latin) --> cp1250 done")
        elif oldCodepage == "UTF-8 (Cyrillic)" and\
             newCodepage == "Windows 1250 (Latin)":
            # utf8 cyrillic --> cp1250
            for file in self.filenames:
                utf8Convert(file, direction="lat")
                utf8ToCp1250(file)
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
        for input in self.filenames:
            output = f"{input}.out"
            with open(output, "w", encoding=encoding) as out, \
                 open(input,encoding=encoding) as f:
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
        for input in self.filenames:
            output = f"{input}.out"
            with open(output, "w", encoding=encoding) as out, \
                 open(input, encoding=encoding) as f:
                for line in f:
                    match = self.TIMESTAMP_LINE_REGEX.match(line)
                    if match:
                        result = rewindLine(match.group(), delay)
                        out.write(result + "\n")
                    else:
                        out.write(line)
            remove(input)
            rename(output, input)
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



