from os import remove, rename


Lat2CyrUtf8Dic = {
    65: 1040, #A <--> A
    66: 1041, #B <--> Б
    67: 1062, #C <--> Ц
    68: 1044, #D <--> Д
    69: 1045, #E <--> Е
    70: 1060, #F <--> Ф
    71: 1043, #G <--> Г
    72: 1061, #H <--> Х
    73: 1048, #I <--> И
    74: 1032, #J <--> Ј
    75: 1050, #K <--> К
    76: 1051, #L <--> Л
    77: 1052, #M <--> М
    78: 1053, #N <--> Н
    79: 1054, #O <--> О
    80: 1055, #P <--> П
    82: 1056, #R <--> Р
    83: 1057, #S <--> С
    84: 1058, #T <--> Т
    85: 1059, #U <--> У
    86: 1042, #V <--> В
    90: 1047, #Z <--> З
    381: 1046, #Ž <--> Ж
    262: 1035, #Ć <--> Ћ
    268: 1063, #Č <--> Ч
    352: 1064, #Š <--> Ш
    272: 1026, #Đ <--> Ђ
    97: 1072, #a <--> а
    98: 1073, #b <--> б
    99: 1094, #c <--> ц
    100: 1076, #d <--> д
    101: 1077, #e <--> е
    102: 1092, #f <--> ф
    103: 1075, #g <--> г
    104: 1093, #h <--> х
    105: 1080, #i <--> и
    106: 1112, #j <--> ј
    107: 1082, #k <--> к
    108: 1083, #l <--> л
    109: 1084, #m <--> м
    110: 1085, #n <--> н
    111: 1086, #o <--> о
    112: 1087, #p <--> п
    114: 1088, #r <--> р
    115: 1089, #s <--> с
    116: 1090, #t <--> т
    117: 1091, #u <--> у
    118: 1074, #v <--> в
    122: 1079, #z <--> з
    263: 1115, #ć <--> ћ
    273: 1106, #đ <--> ђ
    269: 1095, #č <--> ч
    353: 1096, #š <--> ш
    382: 1078  #ž <--> ж
    }

Cyr2LatUtf8Dic = {v: k for k, v in Lat2CyrUtf8Dic.items()}

# Removes <и> and <б> tags from file 
def removeTags(fileIn, enc):
    if enc == "UTF-8 (Cyrillic)":
        encoding = "utf-8"
    else:
        return
    with open (f"{fileIn}_", "w", encoding=encoding) as g, \
         open (f"{fileIn}", "r", encoding=encoding) as f:
        for line in f:
            print(line.rstrip().replace("<и>", "").\
                                replace("</и>", "").\
                                replace("<б>","").\
                                replace("</б>",""), file=g)
    remove(fileIn)
    rename(f"{fileIn}_", f"{fileIn}")


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


# cp1250 (aka windows-1250) --------> utf-8
def cp1250ToUtf8(fileIn):

    cp1250 = "abvgdđežzijklljmnnjoprstufhcčdžš".encode("cp1250").decode("cp1250")
    cp1250 += "ABVGDĐEŽZIJKLLJMNNJOPRSTUFHCČDŽŠ".encode("cp1250").decode("cp1250")

    utf8 = "abvgdđežzijklljmnnjoprstufhcčdžš".encode("utf-8").decode("utf-8")
    utf8 += "ABVGDĐEŽZIJKLLJMNNJOPRSTUFHCČDŽŠ".encode("utf-8").decode("utf-8")

    with open(f"{fileIn}.utf8", "w", encoding="utf-8") as g, \
         open(fileIn, "r", errors="ignore", encoding="cp1250") as f:
        for line in f:
            table = line.maketrans(cp1250, utf8)
            line = line.translate(table).rstrip()
            print(line, file=g)
    remove(fileIn)
    rename(f"{fileIn}.utf8", fileIn)

# utf8 ------------> cp1250 (aka windows-1250)
def utf8ToCp1250(fileIn):

    cp1250 = "abvgdđežzijklljmnnjoprstufhcčdžš".encode("cp1250").decode("cp1250")
    cp1250 += "ABVGDĐEŽZIJKLLJMNNJOPRSTUFHCČDŽŠ".encode("cp1250").decode("cp1250")

    utf8 = "abvgdđežzijklljmnnjoprstufhcčdžš".encode("utf-8").decode("utf-8")
    utf8 += "ABVGDĐEŽZIJKLLJMNNJOPRSTUFHCČDŽŠ".encode("utf-8").decode("utf-8")

    with open(f"{fileIn}.cp1250", "w", encoding="cp1250") as g, \
         open(fileIn, "r", errors="ignore", encoding="utf-8") as f:
        for line in f:
            table = line.maketrans(utf8, cp1250)
            line = line.translate(table).rstrip()
            print(line, file=g)
    remove(fileIn)
    rename(f"{fileIn}.cp1250", fileIn)


def utf8Convert(fileIn, direction="cyr"):
    """
    UTF-8 latin <-----------> UTF-8 cyrillic conversion (Serbian language)

    fileIn - input file name
    direction - eighter "cyr"(default) to convert from latin to cyrillic or 
                        "lat" to convert from cyrillic to latin
    """

    enc = "utf-8"

    # latin ------------------------> cyrillic
    if direction == "cyr":
        with open(f"{fileIn}.cyr_", "w", encoding=enc) as out, \
             open(fileIn, "r", encoding=enc) as f:
            for line in f:
                for ch in line: # convert utf-8 number to his corresponding number from dictionary
                    w = ord(ch)
                    v = Lat2CyrUtf8Dic.get(w)  
                    if v != None: 
                        out.write(chr(v))
                    else:
                        out.write(ch)
        # fix letters џ, њ, љ
        with open(f"{fileIn}.cyr", "w", encoding=enc) as out, \
             open(f"{fileIn}.cyr_", "r", encoding=enc) as f:
            for line in f:
                fixedLine = line.replace("дж", "џ").replace("Дж", "Џ").replace("ДЖ", "Џ").replace("НЈ", "Њ").replace("Нј", "Њ").replace("нј","њ").replace("ЛЈ", "Љ").replace("Лј", "Љ").replace("лј","љ")
                out.write(fixedLine)
        
        remove(fileIn)
        remove(f"{fileIn}.cyr_")
        rename(f"{fileIn}.cyr", fileIn)
                    
                    
    # cyrillic ------------------------> latin
    elif direction == "lat":
        with open(f"{fileIn}.lat", "w", encoding=enc) as out, \
             open(fileIn, "r", encoding=enc) as f:
            for line in f:
                # convert utf-8 number to his corresponding 
                # number in dictionary
                for ch in line: 
                    w = ord(ch)
                    v = Cyr2LatUtf8Dic.get(w)  
                    if v != None: 
                        out.write(chr(v))
                    elif w == 1039: # Џ --> Dž 
                        out.write("Dž")
                    elif w == 1119: # џ --> dž
                        out.write("dž")
                    elif w == 1033: # Љ --> Lj
                        out.write("Lj")
                    elif w == 1113: # љ --> lj
                        out.write("lj")
                    elif w == 1034: # Њ --> Nj
                        out.write("Nj")
                    elif w == 1114: # њ --> nj
                        out.write("nj")
                    else:
                        out.write(ch)
        remove(fileIn)
        rename(f"{fileIn}.lat", fileIn)


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