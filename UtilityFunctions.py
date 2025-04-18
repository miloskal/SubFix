from os import remove, rename
from CONSTANTS import *


Lat2CyrUtf8Dic = {
    65: 1040,  # A <--> A
    66: 1041,  # B <--> Б
    67: 1062,  # C <--> Ц
    68: 1044,  # D <--> Д
    69: 1045,  # E <--> Е
    70: 1060,  # F <--> Ф
    71: 1043,  # G <--> Г
    72: 1061,  # H <--> Х
    73: 1048,  # I <--> И
    74: 1032,  # J <--> Ј
    75: 1050,  # K <--> К
    76: 1051,  # L <--> Л
    77: 1052,  # M <--> М
    78: 1053,  # N <--> Н
    79: 1054,  # O <--> О
    80: 1055,  # P <--> П
    82: 1056,  # R <--> Р
    83: 1057,  # S <--> С
    84: 1058,  # T <--> Т
    85: 1059,  # U <--> У
    86: 1042,  # V <--> В
    90: 1047,  # Z <--> З
    381: 1046,  # Ž <--> Ж
    262: 1035,  # Ć <--> Ћ
    268: 1063,  # Č <--> Ч
    352: 1064,  # Š <--> Ш
    272: 1026,  # Đ <--> Ђ
    97: 1072,  # a <--> а
    98: 1073,  # b <--> б
    99: 1094,  # c <--> ц
    100: 1076,  # d <--> д
    101: 1077,  # e <--> е
    102: 1092,  # f <--> ф
    103: 1075,  # g <--> г
    104: 1093,  # h <--> х
    105: 1080,  # i <--> и
    106: 1112,  # j <--> ј
    107: 1082,  # k <--> к
    108: 1083,  # l <--> л
    109: 1084,  # m <--> м
    110: 1085,  # n <--> н
    111: 1086,  # o <--> о
    112: 1087,  # p <--> п
    114: 1088,  # r <--> р
    115: 1089,  # s <--> с
    116: 1090,  # t <--> т
    117: 1091,  # u <--> у
    118: 1074,  # v <--> в
    122: 1079,  # z <--> з
    263: 1115,  # ć <--> ћ
    273: 1106,  # đ <--> ђ
    269: 1095,  # č <--> ч
    353: 1096,  # š <--> ш
    382: 1078,  # ž <--> ж
}

Cyr2LatUtf8Dic = {v: k for k, v in Lat2CyrUtf8Dic.items()}


# Removes <и> and <б> tags from file
def removeTags(file, enc):
    if enc == UTF8_CYR:
        encoding = "utf-8"
        with (
            open(f"{file}_", "w", encoding=encoding) as g,
            open(f"{file}", "r", encoding=encoding) as f,
        ):
            for line in f:
                print(
                    line.rstrip()
                    .replace("<и>", "")
                    .replace("</и>", "")
                    .replace("<б>", "")
                    .replace("</б>", ""),
                    file=g,
                )
    elif enc == UTF8_LAT:
        encoding = "utf-8"
        with (
            open(f"{file}_", "w", encoding=encoding) as g,
            open(f"{file}", "r", encoding=encoding) as f,
        ):
            for line in f:
                print(
                    line.rstrip()
                    .replace("<i>", "")
                    .replace("</i>", "")
                    .replace("<b>", "")
                    .replace("</b>", ""),
                    file=g,
                )
    elif enc == CP1250:
        encoding = "cp1250"
        with (
            open(f"{file}_", "w", encoding=encoding) as g,
            open(f"{file}", "r", encoding=encoding) as f,
        ):
            for line in f:
                print(
                    line.rstrip()
                    .replace("<i>", "")
                    .replace("</i>", "")
                    .replace("<b>", "")
                    .replace("</b>", ""),
                    file=g,
                )
    elif enc == CP1251:
        encoding = "cp1251"
        with (
            open(f"{file}_", "w", encoding=encoding) as g,
            open(f"{file}", "r", encoding=encoding) as f,
        ):
            for line in f:
                print(
                    line.rstrip()
                    .replace("<и>", "")
                    .replace("</и>", "")
                    .replace("<б>", "")
                    .replace("</б>", ""),
                    file=g,
                )
    else:
        return

    remove(file)
    rename(f"{file}_", f"{file}")


def frameToTimestamp(currentFrame, fps):
    milisecondsPerFrame = 1000 / fps
    miliseconds = milisecondsPerFrame * currentFrame
    timestamp = milisecondsToTimestamp(miliseconds)
    return timestamp


def timestampToFrame(timestamp, fps):
    milisecondsPerFrame = 1000 / fps
    ms = float(timestampToMiliseconds(timestamp))
    frame = ms // milisecondsPerFrame
    return frame


def timestampToMiliseconds(timestamp):
    hours, minutes, secsAndMs = timestamp.split(":")
    hours = float(hours)
    minutes = float(minutes)
    seconds, miliseconds = secsAndMs.split(",")
    seconds = float(seconds)
    miliseconds = float(miliseconds)
    totalMs = miliseconds + seconds * 1000 + minutes * 60000 + hours * 3600000
    return totalMs


def milisecondsToTimestamp(ms):
    miliseconds = int(ms % 1000)
    seconds = int(ms // 1000)
    hours = int(seconds // 3600)
    seconds %= 3600
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    result = f"{hours:02d}:{minutes:02d}:{secs:02d},{miliseconds:03d}"
    return result


def replaceBadChars(file, encoding):
    with (
        open(f"{file}_", "w", encoding=encoding) as g,
        open(file, encoding=encoding) as f,
    ):
        for line in f:
            line = line.replace("´", "'").replace("ě", "i").replace("ň", "n")
            print(line.rstrip(), file=g)
    remove(file)
    rename(f"{file}_", file)


def cp1250ToUtf8(file):
    replaceBadChars(file, "cp1250")
    with (
        open(f"{file}.utf8", "w", encoding="utf-8") as g,
        open(file, "r", errors="ignore", encoding="cp1250") as f,
    ):
        for line in f:
            print(line.rstrip(), file=g)
    remove(file)
    rename(f"{file}.utf8", file)


def cp1251ToUtf8(file):
    replaceBadChars(file, "cp1251")
    with (
        open(f"{file}.utf8", "w", encoding="utf-8") as g,
        open(file, "r", errors="ignore", encoding="cp1251") as f,
    ):
        for line in f:
            print(line.rstrip(), file=g)
    remove(file)
    rename(f"{file}.utf8", file)


def cp1250ToCp1251(file):
    replaceBadChars(file, "cp1250")
    cp1250ToUtf8(file)
    utf8Convert(file, direction="cyr")
    utf8ToCp1251(file)


def cp1251ToCp1250(file):
    replaceBadChars(file, "cp1251")
    cp1251ToUtf8(file)
    utf8Convert(file, direction="lat")
    utf8ToCp1250(file)


def utf8ToCp1250(file):
    replaceBadChars(file, "utf-8")
    with (
        open(f"{file}_", "w", encoding="cp1250") as g,
        open(file, "r", errors="ignore", encoding="utf-8") as f,
    ):
        for line in f:
            print(line.rstrip(), file=g)
    remove(file)
    rename(f"{file}_", file)


def utf8ToCp1251(file):
    replaceBadChars(file, "utf-8")
    with (
        open(f"{file}_", "w", encoding="cp1251") as g,
        open(file, "r", errors="ignore", encoding="utf-8") as f,
    ):
        for line in f:
            print(line.rstrip(), file=g)
    remove(file)
    rename(f"{file}_", file)


def utf8Convert(file, direction="cyr"):
    """
    UTF-8 latin <-----------> UTF-8 cyrillic conversion (Serbian language)

    file - input file name
    direction - eighter "cyr"(default) to convert from latin to cyrillic or
                        "lat" to convert from cyrillic to latin
    """

    enc = "utf-8"

    # latin ------------------------> cyrillic
    if direction == "cyr":
        with (
            open(f"{file}.cyr_", "w", encoding=enc) as out,
            open(file, "r", encoding=enc) as f,
        ):
            for line in f:
                for ch in line:  # convert utf-8 number to his corresponding
                    # number from dictionary
                    w = ord(ch)
                    v = Lat2CyrUtf8Dic.get(w)
                    if v is not None:
                        out.write(chr(v))
                    else:
                        out.write(ch)
        # fix letters џ, њ, љ
        with (
            open(f"{file}.cyr", "w", encoding=enc) as out,
            open(f"{file}.cyr_", "r", encoding=enc) as f,
        ):
            for line in f:
                fixedLine = (
                    line.replace("дж", "џ")
                    .replace("Дж", "Џ")
                    .replace("ДЖ", "Џ")
                    .replace("НЈ", "Њ")
                    .replace("Нј", "Њ")
                    .replace("нј", "њ")
                    .replace("ЛЈ", "Љ")
                    .replace("Лј", "Љ")
                    .replace("лј", "љ")
                )
                out.write(fixedLine)

        remove(file)
        remove(f"{file}.cyr_")
        rename(f"{file}.cyr", file)

    # cyrillic ------------------------> latin
    elif direction == "lat":
        with (
            open(f"{file}.lat", "w", encoding=enc) as out,
            open(file, "r", encoding=enc) as f,
        ):
            for line in f:
                # convert utf-8 number to his corresponding
                # number in dictionary
                for ch in line:
                    w = ord(ch)
                    v = Cyr2LatUtf8Dic.get(w)
                    if v is not None:
                        out.write(chr(v))
                    elif w == 1039:  # Џ --> Dž
                        out.write("Dž")
                    elif w == 1119:  # џ --> dž
                        out.write("dž")
                    elif w == 1033:  # Љ --> Lj
                        out.write("Lj")
                    elif w == 1113:  # љ --> lj
                        out.write("lj")
                    elif w == 1034:  # Њ --> Nj
                        out.write("Nj")
                    elif w == 1114:  # њ --> nj
                        out.write("nj")
                    else:
                        out.write(ch)
        remove(file)
        rename(f"{file}.lat", file)


def rewindLine(line, delay):
    timestamp1, timestamp2 = line.split(" --> ")
    ms1 = timestampToMiliseconds(timestamp1)
    ms2 = timestampToMiliseconds(timestamp2)
    ms1 += delay
    ms2 += delay
    timestamp1 = milisecondsToTimestamp(ms1)
    timestamp2 = milisecondsToTimestamp(ms2)
    result = f"{timestamp1} --> {timestamp2}"
    return result


def correctFpsInLine(line, oldFps, newFps):
    timestamp1, timestamp2 = line.split(" --> ")
    frame1 = timestampToFrame(timestamp1, oldFps)
    timestamp1 = frameToTimestamp(frame1, newFps)
    frame2 = timestampToFrame(timestamp2, oldFps)
    timestamp2 = frameToTimestamp(frame2, newFps)
    result = f"{timestamp1} --> {timestamp2}"
    return result


def dragEnterEvent(self, event):
    if event.mimeData().hasUrls():
        event.accept()
        print("Drag event")
    else:
        event.ignore()


def dropEvent(self, event):
    files = [u.toLocalFile() for u in event.mimeData().urls()]
    for f in files:
        print(f)


def dragMoveEvent(self, event):
    event.accept()
