#!/usr/bin/python3

from sys import argv
from re import compile
from shutil import copy
from types import MethodType

from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QMessageBox,
)
from PyQt6.QtGui import (
    QStandardItemModel,
    QStandardItem,
    QIcon,
    QKeySequence,
    QShortcut,
)
from PyQt6 import uic
from UtilityFunctions import *


def _dragEnterEvent(self, event):
    if event.mimeData().hasUrls():
        event.accept()
    else:
        event.ignore()


def _dragMoveEvent(self, event):
    event.accept()


def _dropEvent(self, event):
    items = [u.toLocalFile() for u in event.mimeData().urls()]
    items = list(
        filter(lambda x: x.endswith(".srt") or x.endswith(".txt"), items)
    )
    for item in items:
        x = QStandardItem(item)
        x.setEditable(False)
        self.model().appendRow(x)


# _drag/_drop functions ending with '2' are just for .sub->.srt list view
def _dragEnterEvent2(self, event):
    if event.mimeData().hasUrls():
        event.accept()
    else:
        event.ignore()


def _dragMoveEvent2(self, event):
    event.accept()


def _dropEvent2(self, event):
    items = [u.toLocalFile() for u in event.mimeData().urls()]
    items = list(
        filter(lambda x: x.endswith(".sub") or x.endswith(".txt"), items)
    )
    for item in items:
        x = QStandardItem(item)
        x.setEditable(False)
        self.model().appendRow(x)


class MainWindow(QDialog):
    """Main Window which appears on opening application."""

    TIMESTAMP_LINE_REGEX = compile(
        "[0-9]{2}:[0-5][0-9]:[0-5][0-9],[0-9]{3} --> "
        "[0-9]{2}:[0-5][0-9]:[0-5][0-9],[0-9]{3}"
    )

    SUB_LINE_REGEX = compile(r"\{(\d+)\}\{(\d+)\}\s*(.*)(\r)?(\n)?")

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.ui = uic.loadUi("layout.ui", self)
        self.setWindowIcon(QIcon("icon.png"))
        self.ui.browseFpsPushButton.released.connect(self.browseForSrtSubtitle)
        self.ui.browseCodepagePushButton.released.connect(
            self.browseForSrtSubtitle
        )
        self.ui.browseRewindPushButton.released.connect(
            self.browseForSrtSubtitle
        )
        self.ui.browseConvertToSrtPushButton.released.connect(
            self.browseForSubSubtitle
        )
        self.ui.fixFpsPushButton.released.connect(self.correctSubtitleFps)
        self.ui.translateCodepagePushButton.released.connect(
            self.translateCodepage
        )
        self.ui.rewindPushButton.released.connect(self.rewindSubtitle)
        self.ui.convertToSrtPushButton.released.connect(self.convertToSrt)
        self.model = QStandardItemModel()  # model for .srt files
        self.modelSub = QStandardItemModel()  # model for .sub files
        self.ui.rewindSubtitlesListView.setModel(self.model)
        self.ui.fpsSubtitlesListView.setModel(self.model)
        self.ui.codepageSubtitlesListView.setModel(self.model)
        self.ui.convertToSrtListView.setModel(self.modelSub)
        # self.ui.rewindSubtitlesListView.setSelectionMode(
        #    QAbstractItemView.SelectionMode.NoSelection
        # )
        # self.ui.fpsSubtitlesListView.setSelectionMode(
        #    QAbstractItemView.SelectionMode.NoSelection
        # )
        # self.ui.codepageSubtitlesListView.setSelectionMode(
        #    QAbstractItemView.SelectionMode.NoSelection
        # )
        # self.ui.convertToSrtListView.setSelectionMode(
        #    QAbstractItemView.SelectionMode.NoSelection
        # )
        self.ui.oldCodepageComboBox.currentIndexChanged.connect(
            self.onOldCodepageChanged
        )
        self.ui.cp1250CheckBox.setChecked(False)
        self.ui.cp1250CheckBox.setEnabled(False)
        self.ui.cp1251CheckBox.setChecked(True)
        self.ui.utf8LatCheckBox.setChecked(True)
        self.ui.utf8CyrCheckBox.setChecked(True)
        self.oldCodepageComboBox.setCurrentText(CP1250)
        self.ui.rewindSubtitlesListView.setAcceptDrops(True)
        self.ui.rewindSubtitlesListView.dragEnterEvent = MethodType(
            _dragEnterEvent, self.ui.rewindSubtitlesListView
        )
        self.ui.rewindSubtitlesListView.dragMoveEvent = MethodType(
            _dragMoveEvent, self.ui.rewindSubtitlesListView
        )
        self.ui.rewindSubtitlesListView.dropEvent = MethodType(
            _dropEvent, self.ui.rewindSubtitlesListView
        )
        self.ui.codepageSubtitlesListView.setAcceptDrops(True)
        self.ui.codepageSubtitlesListView.dragEnterEvent = MethodType(
            _dragEnterEvent, self.ui.codepageSubtitlesListView
        )
        self.ui.codepageSubtitlesListView.dragMoveEvent = MethodType(
            _dragMoveEvent, self.ui.codepageSubtitlesListView
        )
        self.ui.codepageSubtitlesListView.dropEvent = MethodType(
            _dropEvent, self.ui.codepageSubtitlesListView
        )
        self.ui.fpsSubtitlesListView.setAcceptDrops(True)
        self.ui.fpsSubtitlesListView.dragEnterEvent = MethodType(
            _dragEnterEvent, self.ui.fpsSubtitlesListView
        )
        self.ui.fpsSubtitlesListView.dragMoveEvent = MethodType(
            _dragMoveEvent, self.ui.fpsSubtitlesListView
        )
        self.ui.fpsSubtitlesListView.dropEvent = MethodType(
            _dropEvent, self.ui.fpsSubtitlesListView
        )
        self.ui.convertToSrtListView.setAcceptDrops(True)
        self.ui.convertToSrtListView.dragEnterEvent = MethodType(
            _dragEnterEvent2, self.ui.convertToSrtListView
        )
        self.ui.convertToSrtListView.dragMoveEvent = MethodType(
            _dragMoveEvent2, self.ui.convertToSrtListView
        )
        self.ui.convertToSrtListView.dropEvent = MethodType(
            _dropEvent2, self.ui.convertToSrtListView
        )

        mykey = QKeySequence.StandardKey.Delete
        self.deleteRewindShortcut = QShortcut(
            mykey,
            self.ui.rewindSubtitlesListView,
            member=self.onDeleteRewindRow,
        )
        self.deleteFpsShortcut = QShortcut(
            mykey, self.ui.fpsSubtitlesListView, member=self.onDeleteFpsRow
        )
        self.deleteCodepageShortcut = QShortcut(
            mykey,
            self.ui.codepageSubtitlesListView,
            member=self.onDeleteCodepageRow,
        )
        self.deleteSubShortcut = QShortcut(
            mykey, self.ui.convertToSrtListView, member=self.onDeleteSubRow
        )
        self.filenames = []
        self.filenamesSub = []

    def checkAllComboBoxes(self):
        self.ui.cp1250CheckBox.setEnabled(True)
        self.ui.cp1251CheckBox.setEnabled(True)
        self.ui.utf8LatCheckBox.setEnabled(True)
        self.ui.utf8CyrCheckBox.setEnabled(True)
        self.ui.cp1250CheckBox.setChecked(True)
        self.ui.cp1251CheckBox.setChecked(True)
        self.ui.utf8LatCheckBox.setChecked(True)
        self.ui.utf8CyrCheckBox.setChecked(True)

    def syncModelWithFilenames(self):
        total = self.model.rowCount()
        if not total == len(self.filenames):
            self.filenames.clear()
            for i in range(total):
                self.filenames.append(self.model.item(i).text())
        total = self.modelSub.rowCount()
        if not total == len(self.filenamesSub):
            self.filenamesSub.clear()
            for i in range(total):
                self.filenamesSub.append(self.modelSub.item(i).text())

    def onDeleteRewindRow(self):
        ixs = self.ui.rewindSubtitlesListView.selectedIndexes()
        for i in ixs:
            q = self.model.takeRow(i.row())
            del q
        self.syncModelWithFilenames()

    # slot
    def onDeleteFpsRow(self):
        ixs = self.ui.fpsSubtitlesListView.selectedIndexes()
        for i in ixs:
            q = self.model.takeRow(i.row())
            del q
        self.syncModelWithFilenames()

    # slot
    def onDeleteCodepageRow(self):
        ixs = self.ui.codepageSubtitlesListView.selectedIndexes()
        for i in ixs:
            q = self.model.takeRow(i.row())
            del q
        self.syncModelWithFilenames()

    # slot
    def onDeleteSubRow(self):
        ixs = self.ui.convertToSrtListView.selectedIndexes()
        for i in ixs:
            q = self.modelSub.takeRow(i.row())
            del q
        self.syncModelWithFilenames()

    # slot
    def onOldCodepageChanged(self):
        text = self.oldCodepageComboBox.currentText()
        if text == CP1250:
            self.checkAllComboBoxes()
            self.ui.cp1250CheckBox.setChecked(False)
            self.ui.cp1250CheckBox.setEnabled(False)
        elif text == CP1251:
            self.checkAllComboBoxes()
            self.ui.cp1251CheckBox.setChecked(False)
            self.ui.cp1251CheckBox.setEnabled(False)
        elif text == UTF8_LAT:
            self.checkAllComboBoxes()
            self.ui.utf8LatCheckBox.setChecked(False)
            self.ui.utf8LatCheckBox.setEnabled(False)
        elif text == UTF8_CYR:
            self.checkAllComboBoxes()
            self.ui.utf8CyrCheckBox.setChecked(False)
            self.ui.utf8CyrCheckBox.setEnabled(False)

    # slot
    def convertToSrt(self):
        """Converts .sub to .srt."""
        self.syncModelWithFilenames()
        if not self.filenamesSub:
            self.failure("Please import subtitles first")
            return
        encoding = self.ui.convertToSrtEncodingComboBox.currentText()
        fps = float(self.ui.convertToSrtFpsComboBox.currentText())
        if encoding == CP1250:
            enc = "cp1250"
        elif encoding == CP1251:
            enc = "cp1251"
        elif encoding == CP1252:
            enc = "cp1252"
        elif encoding == "UTF-8":
            enc = "utf-8"
        else:
            self.failure("Invalid encoding")
            return
        for file in self.filenamesSub:
            with (
                open(file, encoding=enc) as src,
                open(f"{file}.srt", "w", encoding=enc) as dst,
            ):
                for cnt, line in enumerate(src, start=1):
                    match = self.SUB_LINE_REGEX.match(line)
                    if match:
                        startFps = int(match.group(1))
                        endFps = int(match.group(2))
                        content = match.group(3)
                        content = content.replace("|", "\n")
                        # original = (f"[{cnt}] startFps='{startFps}' "
                        #             f"endFps='{endFps}' content='{content}'")
                        startTimestamp = frameToTimestamp(startFps, fps)
                        endTimestamp = frameToTimestamp(endFps, fps)
                        corrected = (
                            f"{cnt}\n{startTimestamp} --> "
                            f"{endTimestamp}\n{content}\n\n"
                        )
                        dst.write(corrected)
                    else:
                        print(f"no match in line {cnt}: {line}")
        self.success("Done!")

    # slot
    def browseForSrtSubtitle(self):
        self.filenames = QFileDialog.getOpenFileNames(
            parent=self,
            caption="Browse for subtitles",
            filter="Subtitle files (*.srt | *.txt)",
        )
        self.filenames = self.filenames[0]
        self.model.clear()
        for file in self.filenames:
            item = QStandardItem(file)
            item.setEditable(False)
            self.model.appendRow(item)

    # slot
    def browseForSubSubtitle(self):
        self.filenamesSub = QFileDialog.getOpenFileNames(
            parent=self,
            caption="Browse for subtitles",
            filter="Subtitle files (*.sub | *.txt)",
        )
        self.filenamesSub = self.filenamesSub[0]
        self.modelSub.clear()
        for file in self.filenamesSub:
            item = QStandardItem(file)
            item.setEditable(False)
            self.modelSub.appendRow(item)

    # slot
    def translateCodepage(self):
        self.syncModelWithFilenames()
        if not self.filenames:
            self.failure("Please import subtitles first")
            return

        oldCodepage = self.ui.oldCodepageComboBox.currentText()
        generateCp1250 = (
            self.ui.cp1250CheckBox.isEnabled()
            and self.ui.cp1250CheckBox.isChecked()
        )
        generateCp1251 = (
            self.ui.cp1251CheckBox.isEnabled()
            and self.ui.cp1251CheckBox.isChecked()
        )
        generateUtf8Lat = (
            self.ui.utf8LatCheckBox.isEnabled()
            and self.ui.utf8LatCheckBox.isChecked()
        )
        generateUtf8Cyr = (
            self.ui.utf8CyrCheckBox.isEnabled()
            and self.ui.utf8CyrCheckBox.isChecked()
        )

        for src in self.filenames:
            if oldCodepage == CP1250:
                if generateCp1251:
                    dst = f"{src[:-4]} cp1251 cyr.srt"
                    copy(src, dst)
                    cp1250ToCp1251(dst)
                    removeTags(dst, CP1251)
                if generateUtf8Lat:
                    dst = f"{src[:-4]} utf-8 lat.srt"
                    copy(src, dst)
                    cp1250ToUtf8(dst)
                    removeTags(dst, UTF8_LAT)
                if generateUtf8Cyr:
                    dst = f"{src[:-4]} utf-8 cyr.srt"
                    copy(src, dst)
                    cp1250ToUtf8(dst)
                    utf8Convert(dst, direction="cyr")
                    removeTags(dst, UTF8_CYR)
            elif oldCodepage == CP1251:
                if generateCp1250:
                    dst = f"{src[:-4]} cp1250 lat.srt"
                    copy(src, dst)
                    cp1251ToCp1250(dst)
                    removeTags(dst, CP1250)
                if generateUtf8Lat:
                    dst = f"{src[:-4]} utf-8 lat.srt"
                    copy(src, dst)
                    cp1251ToUtf8(dst)
                    utf8Convert(dst, direction="lat")
                    removeTags(dst, UTF8_LAT)
                if generateUtf8Cyr:
                    dst = f"{src[:-4]} utf-8 cyr.srt"
                    copy(src, dst)
                    cp1251ToUtf8(dst)
                    removeTags(dst, UTF8_CYR)
            elif oldCodepage == UTF8_LAT:
                if generateCp1250:
                    dst = f"{src[:-4]} cp1250 lat.srt"
                    copy(src, dst)
                    utf8ToCp1250(dst)
                    removeTags(dst, CP1250)
                if generateCp1251:
                    dst = f"{src[:-4]} cp1251 cyr.srt"
                    copy(src, dst)
                    utf8Convert(dst, direction="cyr")
                    utf8ToCp1251(dst)
                    removeTags(dst, CP1251)
                if generateUtf8Cyr:
                    dst = f"{src[:-4]} utf-8 cyr.srt"
                    copy(src, dst)
                    utf8Convert(dst, direction="cyr")
                    removeTags(dst, UTF8_CYR)
            elif oldCodepage == UTF8_CYR:
                if generateCp1250:
                    dst = f"{src[:-4]} cp1250 lat.srt"
                    copy(src, dst)
                    utf8Convert(dst, direction="lat")
                    utf8ToCp1250(dst)
                    removeTags(dst, CP1250)
                if generateCp1251:
                    dst = f"{src[:-4]} cp1251 cyr.srt"
                    copy(src, dst)
                    utf8ToCp1251(dst)
                    removeTags(dst, CP1251)
                if generateUtf8Lat:
                    dst = f"{src[:-4]} utf-8 lat.srt"
                    copy(src, dst)
                    utf8Convert(dst, direction="lat")
                    removeTags(dst, UTF8_LAT)
        self.success("Conversion finished")

    # slot
    def correctSubtitleFps(self):
        self.syncModelWithFilenames()
        if not self.filenames:
            self.failure("Please import subtitles first")
            return
        oldFps = float(self.ui.oldFpsComboBox.currentText())
        newFps = float(self.ui.newFpsComboBox.currentText())
        enc = self.ui.fpsEncodingComboBox.currentText()
        if enc == CP1250:
            encoding = "cp1250"
        elif enc == CP1251:
            encoding = "cp1251"
        elif enc == CP1252:
            encoding = "cp1252"
        elif enc == "UTF-8":
            encoding = "utf-8"
        else:
            self.failure("Invalid encoding")
            return
        for input in self.filenames:
            output = f"{input}.out"
            with (
                open(output, "w", encoding=encoding) as out,
                open(input, encoding=encoding) as f,
            ):
                for line in f:
                    match = self.TIMESTAMP_LINE_REGEX.match(line)
                    if match:
                        result = correctFpsInLine(
                            match.group(), oldFps, newFps
                        )
                        out.write(result + "\n")
                    else:
                        out.write(line)
            rename(output, input)
        self.success(
            (
                f"Conversion {self.ui.oldFpsComboBox.currentText()} --> "
                f"{self.ui.newFpsComboBox.currentText()} FPS finished"
            )
        )

    # slot
    def rewindSubtitle(self):
        self.syncModelWithFilenames()
        if not self.filenames:
            self.failure("Please import subtitles first")
            return
        enc = self.ui.rewindEncodingComboBox.currentText()
        if enc == CP1250:
            encoding = "cp1250"
        elif enc == CP1251:
            encoding = "cp1251"
        elif enc == CP1252:
            encoding = "cp1252"
        elif enc == "UTF-8":
            encoding = "utf-8"
        else:
            self.failure("Invalid encoding")
            return
        try:
            entered = self.ui.rewindMilisecondsLineEdit.text()
            delay = int(entered)
        except ValueError:
            self.failure(
                (
                    f"Wrong value ('{entered}').\n\nPlease enter "
                    f"delay in miliseconds."
                )
            )
            return
        for input in self.filenames:
            output = f"{input}.out"
            with (
                open(output, "w", encoding=encoding) as out,
                open(input, encoding=encoding) as f,
            ):
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
        QMessageBox.information(self, "Success", message)

    def failure(self, message):
        QMessageBox.critical(self, "Failure", message)


# main
if __name__ == "__main__":
    app = QApplication(argv)
    window = MainWindow()
    window.setWindowTitle("Subtitle Fixer")
    window.show()
    app.exec()
