from os import remove, rename
from sys import argv
from regex import compile, match
from utility_functions import *

from PyQt5.QtWidgets import QApplication, QWidget, QDialog, QFileDialog, \
    QComboBox, QMessageBox
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
        self.ui.browseFpsPushButton.released.connect(self.browse_for_subtitle)
        self.ui.browseCodepagePushButton.released.connect(self.browse_for_subtitle)
        self.ui.browseRewindPushButton.released.connect(self.browse_for_subtitle)
        self.ui.fixFpsPushButton.released.connect(self.correct_subtitle_fps)
        self.ui.translateCodepagePushButton.released.connect(self.translate_codepage)
        self.ui.rewindPushButton.released.connect(self.rewind_subtitle)


    #slot
    def browse_for_subtitle(self):
        if __platform__ == "Linux":
            directory = "/home"
        elif __platform__ == "Windows":
            directory = "C:\\\\Users"
        self.filename = QFileDialog.getOpenFileName(parent=self, directory=directory,
                                             caption="Browse for subtitle",
                                             filter="Subtitle files (*.srt | *.txt)")
        self.filename = self.filename[0]
        self.ui.filePathFpsLabel.setText(self.filename)
        self.ui.filePathCodepageLabel.setText(self.filename)
        self.ui.filePathRewindLabel.setText(self.filename)

        print(f"filename={self.filename}")


    #slot
    def translate_codepage(self):
        old_codepage = self.ui.oldCodepageComboBox.currentText()
        new_codepage = self.ui.newCodepageComboBox.currentText()
        if old_codepage == "Windows 1250 (Latin)" and\
            new_codepage == "UTF-8 (Latin)":
            # cp1250 --> utf8 latin
            self.cp1250_to_utf8(self.filename)
            self.success("Conversion cp1250 --> utf8(latin) done")
        elif old_codepage == "Windows 1250 (Latin)" and\
             new_codepage == "UTF-8 (Cyrillic)":
            # cp1250 --> utf8 cyrillic
            self.cp1250_to_utf8(self.filename)
            self.utf8_convert(self.filename, direction="cyr")
            remove_tags(self.filename, new_codepage)
            self.success("Conversion cp1250 --> utf8(cyrillic) done")
        elif old_codepage == "UTF-8 (Cyrillic)" and\
             new_codepage == "UTF-8 (Latin)":
            # utf8 cyrillic --> utf8 latin
            self.utf8_convert(self.filename, direction="lat")
            self.success("Conversion utf8(cyrillic) --> utf8(latin) done")
        elif old_codepage == "UTF-8 (Latin)" and\
             new_codepage == "UTF-8 (Cyrillic)":
            # utf8 latin --> utf8 cyrillic
            self.utf8_convert(self.filename, direction="cyr")
            remove_tags(self.filename, new_codepage)
            self.success("Conversion utf8(latin) --> utf8(cyrillic) done")
        elif old_codepage == "UTF-8 (Latin)" and\
             new_codepage == "Windows 1250 (Latin)":
            # utf8 latin --> cp1250
            self.utf8_to_cp1250(self.filename)
            self.success("Conversion utf8(latin) --> cp1250 done")
        elif old_codepage == "UTF-8 (Cyrillic)" and\
             new_codepage == "Windows 1250 (Latin)":
            # utf8 cyrillic --> cp1250
            self.utf8_convert(self.filename, direction="lat")
            self.utf8_to_cp1250(self.filename)
            self.success("Conversion utf8(cyrillic) --> cp1250 done")
        else:
            self.failure("Conversion failed.")


    #slot
    def correct_subtitle_fps(self):
        old_fps = float(self.ui.oldFpsComboBox.currentText())
        new_fps = float(self.ui.newFpsComboBox.currentText())
        enc = self.ui.fpsEncodingComboBox.currentText()
        if enc == "Windows 1250 (Latin)":
            encoding = "cp1250"
        elif enc == "UTF-8":
            encoding = "utf-8"
        else:
            self.failure("Invalid encoding")
            return
        input = self.filename
        output = f"{input}.out"
        with open(output, "w", encoding=encoding) as out:
            with open(input,encoding=encoding) as f:
                for line in f:
                    match = self.TIMESTAMP_LINE_REGEX.match(line)
                    if match:
                        result = self.correct_fps_in_line(match.group(), old_fps, new_fps)
                        out.write(result + "\n")
                    else:
                        out.write(line)



    #slot
    def rewind_subtitle(self):
        enc = self.ui.rewindEncodingComboBox.currentText()
        if enc == "Windows 1250 (Latin)":
            encoding = "cp1250"
        elif enc == "UTF-8":
            encoding = "utf-8"
        else:
            self.failure("Invalid encoding")
            return
        delay = int(self.ui.rewindMilisecondsLineEdit.text())
        input = self.filename
        output = f"{input}.out"
        with open(output, "w", encoding=encoding) as out:
            with open(input, encoding=encoding) as f:
                for line in f:
                    match = self.TIMESTAMP_LINE_REGEX.match(line)
                    if match:
                        result = rewind_line(match.group(), delay)
                        out.write(result + "\n")
                    else:
                        out.write(line)

    def success(self, message):
        window = QMessageBox.information(self, "Done", message)
        
    def failure(self, message):
        window = QMessageBox.critical(self, "Failure", message)

# main
if __name__ == "__main__":
    app = QApplication(argv)
    window = MainWindow()
    window.setWindowTitle("Subtitle Fixer")
    window.show()
    app.exec_()



