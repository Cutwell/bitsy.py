# utilities for converting bitsyGameData files into objects
import re
import logging


class Engine():
    def __init__(self):
        self.tilesize = 8
        self.mapsize = 16
        self.width = self.mapsize * self.tilesize
        self.height = self.mapsize * self.tilesize
        self.scale = 4
        self.textScale = 2

        self.titleDialogId = "title"
        self.tileColorStartIndex = 16

        self.TextDirection = {
            "LeftToRight" : "LTR",
            "RightToLeft" : "RTL"
        }

        self.defaultFontName = "ascii_small"

        self.barLength = 16
        self.minTuneLength = 1
        self.maxTuneLength = 16

        self.Note = {
            "NONE" 		: -1,
            "C" 			: 0,
            "C_SHARP" 	: 1,
            "D" 			: 2,
            "D_SHARP" 	: 3,
            "E" 			: 4,
            "F" 			: 5,
            "F_SHARP" 	: 6,
            "G" 			: 7,
            "G_SHARP" 	: 8,
            "A" 			: 9,
            "A_SHARP" 	: 10,
            "B" 			: 11,
            "COUNT" 		: 12
        }

        self.Solfa = {
            "NONE" 	: -1,
            "D" 		: 0,	# Do
            "R" 		: 1,	# Re
            "M" 		: 2,	# Mi
            "F" 		: 3,	# Fa
            "S" 		: 4,	# Sol
            "L" 		: 5,	# La
            "T" 		: 6,	# Ti
            "COUNT" 	: 7
        }

        self.Octave = {
            "NONE": -1,
            "2": 0,
            "3": 1,
            "4": 2, # octave 4: middle C octave
            "5": 3,
            "COUNT": 4
        }

        self.Tempo = {
            "SLW": 0, # slow
            "MED": 1, # medium
            "FST": 2, # fast
            "XFST": 3 # extra fast (aka turbo)
        }

        self.SquareWave = {
            "P8": 0, # pulse 1 / 8
            "P4": 1, # pulse 1 / 4
            "P2": 2, # pulse 1 / 2
            "COUNT": 3
        }

        self.ArpeggioPattern = {
            "OFF": 0,
            "UP": 1, # ascending triad chord
            "DWN": 2, # descending triad chord
            "INT5": 3, # 5 step interval
            "INT8": 4 # 8 setp interval
        }

    def createWorldData(self):
        logging.debug("creating world data")

        return {
            "room" : {},
            "tile" : {},
            "sprite" : {},
            "item" : {},
            "dialog" : {},
            "end" : {}, # pre-7.0 ending data for backwards compatibility
            "palette" : { # start off with a default palette
                "default" : {
                    "name" : "default",
                    "colors" : [[0,0,0],[255,255,255],[255,255,255]]
                }
            },
            "variable" : {},
            "tune" : {},
            "blip" : {},
            "versionNumberFromComment" : -1, # -1 indicates no version information found
            "fontName" : self.defaultFontName,
            "textDirection" : self.TextDirection["LeftToRight"],
            "flags" : self.createDefaultFlags(),
            "names" : {},
            # source data for all drawings (todo: better name?)
            "drawings" : {},
        }
    
    def createDrawingData(self, type, id):
        logging.debug("creating drawing data")

        drwId = "SPR" if type == "AVA" else type
        drwId = drwId + "_" + id;

        drawingData = {
            "type" : type,
            "id" : id,
            "name" : None,
            "drw" : drwId,
            "col" : 1 if type == "TIL" else 2, # foreground color
            "bgc" : 0, # background color
            "animation" : {
                "isAnimated" : False,
                "frameIndex" : 0,
                "frameCount" : 1,
            },
        }

        if type == "TIL":
            drawingData["isWall"] = None
        
        if type == "AVA" or type == "SPR":
            drawingData["room"] = None
            drawingData["x"] = -1
            drawingData["y"] = -1
            drawingData["inventory"] = {}
        
        if type == "AVA" or type == "SPR" or type == "ITM":
            drawingData["dlg"] = None
            drawingData["blip"] = None
        
        return drawingData

    def createTuneData(self, id):
        logging.debug("creating tune data")

        return  {
            "id" : id,
            "name" : None,
            "melody" : [],
            "harmony" : [],
            "key": None, # a null key indicates a chromatic scale (all notes enabled)
            "tempo": self.Tempo["MED"],
            "instrumentA" : self.SquareWave["P2"],
            "instrumentB" : self.SquareWave["P2"],
            "arpeggioPattern" : self.ArpeggioPattern["OFF"],
        }
    
    def createTuneBarData(self):
        logging.debug("creating tune bar data")

        bar = []
        for i in range(self.barLength):
            bar.append({ "beats": 0, "note": self.Note["C"], "octave": self.Octave["4"] })

        return bar

    def createTuneKeyData(self):
        logging.debug("creating tune key data")

        key = {
            "notes": [],
            "scale": [],
        }

        for i in range(self.Solfa["COUNT"]):
            key["notes"].append(self.Note["NONE"])

        return key
    
    def createBlipData(self, id):
        logging.debug("creating blip data")

        return {
            "id": id,
            "name": None,
            "pitchA": { "beats": 0, "note": self.Note["C"], "octave": self.Octave["4"] },
            "pitchB": { "beats": 0, "note": self.Note["C"], "octave": self.Octave["4"] },
            "pitchC": { "beats": 0, "note": self.Note["C"], "octave": self.Octave["4"] },
            "envelope": {
                "attack": 0,
                "decay": 0,
                "sustain": 0,
                "length": 0,
                "release": 0,
            },
            "beat": {
                "time": 0,
                "delay": 0,
            },
            "instrument": self.SquareWave["P2"],
            "doRepeat": False,
        }
    
    def createDefaultFlags(self):
        logging.debug("creating default flags")

        return {
            "VER_MAJ": -1,
            "VER_MIN": -1,
            "ROOM_FORMAT": 0,
            "DLG_COMPAT": 0,
            "TXT_MODE": 0,
        }
    
    def createDialogData(self, id):
        logging.debug("creating dialog data")

        return {
            "src": "",
            "name": None,
            "id": id,
        }

    def parseWorld(self, file):
        logging.debug("parsing world")

        world = self.createWorldData()

        parseState = {
            "lines": file.split("\n"),
            "index": 0,
            "spriteStartLocations": {}
        }

        while parseState["index"] < len(parseState["lines"]):
            i = parseState["index"]
            lines = parseState["lines"]
            curLine = lines[i]

            if i == 0:
                i = self.parseTitle(parseState, world)
            
            elif len(curLine) > 0 and curLine[0] == "#":
                if curLine.startswith("# BITSY VERSION"):
                    world["versionNumberFromComment"] = float(curLine.replace("# BITSY VERSION ", ""))
                
                i += 1

            elif self.getType(curLine) == "PAL":
                i = self.parsePalette(parseState, world)
            
            elif self.getType(curLine) == "ROOM" or self.getType(curLine) == "SET":
                i = self.parseRoom(parseState, world)
            
            elif self.getType(curLine) == "TIL":
                i = self.parseTile(parseState, world)
            
            elif self.getType(curLine) == "SPR":
                i = self.parseSprite(parseState, world)
            
            elif self.getType(curLine) == "ITM":
                i = self.parseItem(parseState, world)
            
            elif self.getType(curLine) == "DLG":
                i = self.parseDialog(parseState, world)

            elif self.getType(curLine) == "END":
                i = self.parseEnding(parseState, world)

            elif self.getType(curLine) == "VAR":
                i = self.parseVariable(parseState, world)
            
            elif self.getType(curLine) == "DEFAULT_FONT":
                i = self.parseDefaultFont(parseState, world)
            
            elif self.getType(curLine) == "TEXT_DIRECTION":
                i = self.parseTextDirection(parseState, world)
            
            elif self.getType(curLine) == "FONT":
                i = self.parseFont(parseState, world)

            elif self.getType(curLine) == "TUNE":
                i = self.parseTune(parseState, world)
            
            elif self.getType(curLine) == "BLIP":
                i = self.parseBlip(parseState, world)
            
            elif self.getType(curLine) == "!":
                i = self.parseFlag(parseState, world)
            
            else:
                i += 1

            parseState["index"] = i

        world["names"] = self.createNameMapsForWorld(world)

        self.placeSprites(parseState, world)

        if world["flags"]["VER_MAJ"] < 7:
            world["flags"]["DLG_COMPAT"] = 1
        
        return world
    
    def parseTitle(self, parseState, world):
        logging.debug("parsing title")

        i = parseState["index"]
        lines = parseState["lines"]

        results = { "script": lines[i], "index": (i + 1) }

        world["dialog"][self.titleDialogId] = self.createDialogData(self.titleDialogId)
        world["dialog"][self.titleDialogId]["src"] = results["script"]

        i = results["index"]
        i += 1

        return i
    
    def parsePalette(self, parseState, world):
        logging.debug("parsing palette")

        i = parseState["index"]
        lines = parseState["lines"]

        id = self.getId(lines[i])
        i += 1

        colors = []
        name = None

        while i < len(lines) and len(lines[i]) > 0:
            args = lines[i].split(" ")
            if args[0] == "NAME":
                name = re.split(r"\s(.+)", lines[i])[1]
            
            else:
                col = []
                for _ in lines[i].split(","):
                    col.append(int(_))
                
                colors.append(col)

            i+=1
        
        world["palette"][id] = {
            "id": id,
            "name": name,
            "colors": colors,
        }

        return i
    
    def createRoomData(self, id):
        logging.debug("creating room data")

        return {
            "id": id,
            "name": None,
            "tilemap": [],
            "walls": [],
            "exits": [],
            "endings": [],
            "items": [],
            "pal": None,
            "ava": None,
            "tune": "0",
        }
    
    def parseRoom(self, parseState, world):
        logging.debug("parsing room")

        i = parseState["index"]
        lines = parseState["lines"]
        id = self.getId(lines[i])

        roomData = self.createRoomData(id)

        i += 1

        if world["flags"]["ROOM_FORMAT"] == 0:
            raise Exception("ROOM_FORMAT 0 not supported")
        
        elif world["flags"]["ROOM_FORMAT"] == 1:
            end = i + self.mapsize
            y = 0

            for i in range(i, end):
                roomData["tilemap"].append([])
                lineSep = lines[i].split(",")

                for x in range(0, self.mapsize):
                    roomData["tilemap"][y].append(lineSep[x])

                y += 1

        while i < len(lines) and len(lines[i]) > 0:
            if self.getType(lines[i]) == "SPR":
                sprId = self.getId(lines[i])
                if sprId.index(",") == -1 and len(lines[i].split(" ")) >- 3:
                    sprCoord = lines[i].split(" ")[2].split(",")

                    parseState["spriteStartLocations"][sprId] = {
                        "room": id,
                        "x": int(sprCoord[0]),
                        "y": int(sprCoord[1]),
                    }
            
                elif world["flags"]["ROOM_FORMAT"] == 0:
                    raise Exception("ROOM_FORMAT 0 not supported")
            
            elif self.getType(lines[i]) == "ITM":
                itmId = self.getId(lines[i])
                itmCoord = lines[i].split(" ")[2].split(",")
                itm = {
                    "id": itmId,
                    "x": int(itmCoord[0]),
                    "y": int(itmCoord[1]),
                }
                roomData["items"].append(itm)

            elif self.getType(lines[i]) == "WAL":
                roomData["walls"] = self.getId(lines[i]).split(",")
            
            elif self.getType(lines[i]) == "EXT":
                exitArgs = lines[i].split(" ")
                exitCoords = exitArgs[1].split(",")
                destName = exitArgs[2]
                destCoords = exitArgs[3].split(",")
                ext = {
                    "x": int(exitCoords[0]),
                    "y": int(exitCoords[1]),
                    "dest": {
                        "room": destName,
                        "x": int(destCoords[0]),
                        "y": int(destCoords[1]),
                    },
                    "transition_effect": None,
                    "dlg": None,
                }

                # optional arguments
                exitArgIndex = 4
                while exitArgIndex < len(exitArgs):
                    if exitArgs[exitArgIndex] == "FX":
                        ext["transition_effect"] = exitArgs[exitArgIndex + 1]
                        exitArgIndex += 2
                    
                    elif exitArgs[exitArgIndex] == "DLG":
                        ext["dlg"] = exitArgs[exitArgIndex + 1]
                        exitArgIndex += 2
                    
                    else:
                        exitArgIndex += 1
                
                roomData["exits"].append(ext)
            
            elif self.getType(lines[i]) == "END":
                endId = self.getId(lines[i])
                endCoords = self.getCoord(lines[i], 2)

                end = {
                    "id": endId,
                    "x": int(endCoords[0]),
                    "y": int(endCoords[1]),
                }
                roomData["endings"].append(end)
            
            elif self.getType(lines[i]) == "PAL":
                roomData["pal"] = self.getId(lines[i])
            
            elif self.getType(lines[i]) == "AVA":
                roomData["ava"] = self.getId(lines[i])
            
            elif self.getType(lines[i]) == "TUNE":
                roomData["tune"] = self.getId(lines[i])
            
            elif self.getType(lines[i]) == "NAME":
                roomData["name"] = lines[i].split(" ")[1]
            
            i += 1
        
        world["room"][id] = roomData

        return i
    
    def parseTile(self, parseState, world):
        logging.debug("parsing tile")

        i = parseState["index"]
        lines = parseState["lines"]

        id = self.getId(lines[i])
        tileData = self.createDrawingData("TIL", id)
        
        i += 1

        i = self.parseDrawingCore(lines, i, tileData["drw"], world)

        tileData["animation"]["frameCount"] = self.getDrawingFrameCount(world, tileData["drw"])

        tileData["animation"]["isAnimated"] = tileData["animation"]["frameCount"] > 1

        while i < len(lines) and len(lines[i]) > 0:
            if self.getType(lines[i]) == "COL":
                tileData["col"] = self.getId(lines[i])
            
            elif self.getType(lines[i]) == "BGC":
                bgcId = self.getId(lines[i])
                if bgcId == "*":
                    tileData["bgc"] = (-1 * self.tileColorStartIndex)
                
                else:
                    tileData["bgc"] = int(bgcId)
                
            
            elif self.getType(lines[i]) == "NAME":
                tileData["name"] = self.getNameArg(lines[i])
            
            elif self.getType(lines[i]) == "WAL":
                wallArg = self.getArg(lines[i]), 1
                
                if wallArg == True:
                    tileData["isWall"] = True
                
                elif wallArg == False:
                    tileData["isWall"] = False
                
            i += 1

        world["tile"][id] = tileData

        return i
    
    def parseSprite(self, parseState, world):
        logging.debug("parsing sprite")

        i = parseState["index"]
        lines = parseState["lines"]
        
        id = self.getId(lines[i])
        type = "AVA" if id == "A" else "SPR"
        spriteData = self.createDrawingData(type, id)

        i += 1

        i = self.parseDrawingCore(lines, i, spriteData["drw"], world)

        spriteData["animation"]["frameCount"] = self.getDrawingFrameCount(world, spriteData["drw"])

        spriteData["animation"]["isAnimated"] = spriteData["animation"]["frameCount"] > 1

        while i < len(lines) and len(lines[i]) > 0:
            if self.getType(lines[i]) == "COL":
                spriteData["col"] = int(self.getId(lines[i]))
            
            elif self.getType(lines[i]) == "BGC":
                bgcId = self.getId(lines[i])
                if bgcId == "*":
                    spriteData["bgc"] = (-1 * self.spriteColorStartIndex)
                
                else:
                    spriteData["bgc"] = int(bgcId)
            
            elif self.getType(lines[i]) == "POS":
                posArgs = lines[i].split(" ")
                roomId = posArgs[1]
                coordArgs = posArgs[2].split(",")

                parseState["spriteStartLocations"][id] = {
                    "room": roomId,
                    "x": int(coordArgs[0]),
                    "y": int(coordArgs[1]),
                }

            elif self.getType(lines[i]) == "DLG":
                spriteData["dlg"] = self.getId(lines[i])
            
            elif self.getType(lines[i]) == "NAME":
                spriteData["name"] = self.getNameArg(lines[i])
            
            elif self.getType(lines[i]) == "ITM":
                itemId = self.getId(lines[i])
                itemCount = float(self.getArg(lines[i], 2))

                spriteData["inventory"][itemId] = itemCount
            
            elif self.getType(lines[i]) == "BLIP":
                blipId = self.getId(lines[i])
                spriteData["blip"] = blipId
            
            i += 1
        
        world["sprite"][id] = spriteData

        return i
    
    def parseItem(self, parseState, world):
        logging.debug("parsing item")

        i = parseState["index"]
        lines = parseState["lines"]

        id = self.getId(lines[i])
        itemData = self.createDrawingData("ITM", id)

        i += 1

        i = self.parseDrawingCore(lines, i, itemData["drw"], world)

        itemData["animation"]["frameCount"] = self.getDrawingFrameCount(world, itemData["drw"])

        itemData["animation"]["isAnimated"] = itemData["animation"]["frameCount"] > 1

        while i < len(lines) and len(lines[i]) > 0:
            if self.getType(lines[i]) == "COL":
                itemData["col"] = int(self.getArg(lines[i], 1))

            elif self.getType(lines[i]) == "BGC":
                bgcId = self.getId(lines[i])
                if bgcId == "*":
                    itemData["bgc"] = (-1 * self.itemColorStartIndex)
                
                else:
                    itemData["bgc"] = int(bgcId)
            
            elif self.getType(lines[i]) == "DLG":
                itemData["dlg"] = self.getId(lines[i])
            
            elif self.getType(lines[i]) == "NAME":
                itemData["name"] = self.getNameArg(lines[i])
            
            elif self.getType(lines[i]) == "BLIP":
                blipId = self.getId(lines[i])
                itemData["blip"] = blipId
            
            i += 1
        
        world["item"][id] = itemData

        return i

    def parseDrawingCore(self, lines, i, drwId, world):
        logging.debug("parsing drawing core")

        frameList = []

        frameList.append([])
        
        frameIndex = 0

        y = 0

        while y < self.tilesize:
            line = lines[i + y]
            row = []

            for x in range(0, self.tilesize):
                row.append(int(line[x]))

            frameList[frameIndex].append(row)
            y += 1

            if y == self.tilesize:
                i = i + y

                if lines[i] != None and lines[i][0] == ">":
                    frameList.append([])
                    frameIndex += 1
                    y = 0
                    i += 1
        
        self.storeDrawingData(world, drwId, frameList)

        return i
    
    def parseDialog(self, parseState, world):
        logging.debug("parsing dialog")

        i = parseState["index"]
        lines = parseState["lines"]

        id = self.getId(lines[i])

        i = self.parseScript(lines, i, world["dialog"])

        if i < len(lines) and len(lines[i]) > 0 and self.getType(lines[i]) == "NAME":
            world["dialog"][id]["name"] = self.getNameArg(lines[i])
            i += 1
        
        return i

    def parseScript(self, lines, i, data):
        logging.debug("parsing script")

        id = self.getId(lines[i])
        i += 1

        results = self.ReadDialogScript(lines, i)

        #results = { "script": lines[i], "index": (i + 1)};

        data[id] = self.createDialogData(id)
        data[id]["src"] = results["script"]

        i = results["index"]

        return i

    def ReadDialogScript(self, lines, i):
        if lines[i] == '"""':
            # has logic
            i += 1

            script = []
            logicSnippet = ""

            # iterate characters until we reach the end of the dialog
            depth = 0
            while lines[i] != '"""':
                for c in lines[i]:
                    # increase / decrease depth
                    if  c == '{':
                        depth += 1
                    elif c == '}':
                        depth -= 1

                    # add the character to the logic snippet
                    logicSnippet += c

                    # once found complete logic snippet, add to script
                    if depth == 0:
                        script.append(logicSnippet)
                        logicSnippet = ""
                
                logicSnippet += "\n"

                i += 1
            
            # skip closing """
            i += 1
        
        else:
            # single line dialog
            script = [lines[i]]
            i += 1
        
        return { "script": script, "index": i }
    
    def parseVariable(self, parseState, world):
        logging.debug("parsing variable")

        i = parseState["index"]
        lines = parseState["lines"]
        id = self.getId(lines[i])

        i += 1

        value = lines[i]

        i += 1

        world["variable"][id] = value
        
        return i
    
    def parseFontName(self, parseState, world):
        logging.debug("parsing font name")

        i = parseState["index"]
        lines = parseState["lines"]
        world["fontName"] = self.getArg(lines[i], 1)

        i += 1

        return i
    
    def parseTextDirection(self, parseState, world):
        logging.debug("parsing text direction")

        i = parseState["index"]
        lines = parseState["lines"]
        world["textDirection"] = self.getArg(lines[i], 1)

        i += 1

        return i
    
    def parseFontData(self, parseState, world):
        logging.debug("parsing font data")

        i = parseState["index"]
        lines = parseState["lines"]
        world["fontData"] = lines[i]
        
        i += 1

        return i
    
    def parseTune(self, parseState, world):
        logging.debug("parsing tune")

        i = parseState["index"]
        lines = parseState["lines"]
        
        id = self.getId(lines[i])

        i += 1

        tuneData = self.createTuneData(id)

        barIndex = 0

        while barIndex < self.maxTuneLength:
            # MELODY
            melodyBar = self.createTuneBarData()
            melodyNotes = lines[i].split(",")

            for j in range(0, self.barLength):
                pitch = { "beats": 0, "note": self.Note["C"], "octave": self.Octave["4"], }

                if j < len(melodyNotes):
                    pitchSplit = melodyNotes[j].split("~")
                    pitchStr = pitchSplit[0]
                    pitch = self.parsePitch(melodyNotes[j])

                    if len(pitchSplit) > 1:
                        blipId = pitchSplit[1]
                        pitch["blip"] = blipId
                
                melodyBar[j] = pitch
            
            tuneData["melody"].append(melodyBar)

            i += 1

            # HARMONY
            harmonyBar = self.createTuneBarData()
            harmonyNotes = lines[i].split(",")

            for j in range(0, self.barLength):
                pitch = { "beats": 0, "note": self.Note["C"], "octave": self.Octave["4"], }

                if j < len(harmonyNotes):
                    pitchSplit = harmonyNotes[j].split("~")
                    pitchStr = pitchSplit[0]
                    pitch = self.parsePitch(harmonyNotes[j])

                    if len(pitchSplit) > 1:
                        blipId = pitchSplit[1]
                        pitch["blip"] = blipId
                
                harmonyBar[j] = pitch
            
            tuneData["harmony"].append(harmonyBar)

            i += 1

            if lines[i] == ">":
                barIndex += 1
                i += 1
            else:
                barIndex = self.maxTuneLength
            
        while i < len(lines) and len(lines[i]) > 0:
            if self.getType(lines[i]) == "KEY":
                tuneData["key"] = self.createTuneKeyData()

                keyNotes = self.getArg(lines[i], 1)

                if keyNotes:
                    keyNotes = keyNotes.split(",")
                    for j in range(0, len(keyNotes)):
                        if j >= len(tuneData["key"]["notes"]):
                            break

                        pitch = self.parsePitch(keyNotes[j])
                        tuneData["key"]["notes"][j] = pitch["note"]

                
                keyScale = self.getArg(lines[i], 2)
                
                if keyScale:
                    keyScale = keyScale.split(",")

                    for j in range(0, len(keyScale)):
                        pitch = self.parsePitch(keyScale[j])

                        if pitch["note"] > self.Solfa["NONE"] and pitch["note"] < self.Solfa["COUNT"]:
                            tuneData["key"]["scale"].append(pitch["note"])
                        
            elif self.getType(lines[i]) == "TMP":
                tempoId = self.getId(lines[i])
                if self.Tempo[tempoId] != None:
                    tuneData["tempo"] = self.Tempo[tempoId]
                
            elif self.getType(lines[i]) == "SQR":
                squareWaveIdA = self.getArg(lines[i], 1)

                if self.SquareWave[squareWaveIdA] != None:
                    tuneData["instrumentIdA"] = self.SquareWave[squareWaveIdA]
                
                squareWaveIdB = self.getArg(lines[i], 2)

                if self.SquareWave[squareWaveIdB] != None:
                    tuneData["instrumentIdB"] = self.SquareWave[squareWaveIdB]
                
            elif self.getType(lines[i]) == "ARP":
                arp = self.getId(lines[i])

                if self.ArpeggioPattern[arp] != None:
                    tuneData["arp"] = self.ArpeggioPattern[arp]
                
            elif self.getType(lines[i]) == "NAME":
                name = re.split(r'\s(.+)', lines[i])[1]
                tuneData["name"] = name
            
            i += 1
        
        world["tune"] = tuneData

        return i
    
    def parseBlip(self, parseState, world):
        logging.debug("parsing blip")

        i = parseState["index"]
        lines = parseState["lines"]
        id = self.getId(lines[i])

        i += 1
        
        blipData = self.createBlipData(id)
        
        notes = lines[i].split(",")

        if len(notes) >= 1:
            blipData["pitchA"] = self.parsePitch(notes[0])

        if len(notes) >= 2:
            blipData["pitchB"] = self.parsePitch(notes[1])
        
        if len(notes) >= 3:
            blipData["pitchC"] = self.parsePitch(notes[2])
        
        i += 1
    
        while i < len(lines) and len(lines[i]) > 0:
            if self.getType(lines[i]) == "ENV":
                blipData["envelope"]["attack"] = self.getArg(lines[i], 1)
                blipData["envelope"]["decay"] = self.getArg(lines[i], 2)
                blipData["envelope"]["sustain"] = self.getArg(lines[i], 3)
                blipData["envelope"]["length"] = self.getArg(lines[i], 4)
                blipData["envelope"]["release"] = self.getArg(lines[i], 5)
            
            elif self.getType(lines[i]) == "BEAT":
                blipData["beat"]["time"] = int(self.getArg(lines[i], 1))
                blipData["beat"]["delay"] = int(self.getArg(lines[i], 2))
            
            elif self.getType(lines[i]) == "SQR":
                squareWaveId = self.getArg(lines[i], 1)

                if self.SquareWave[squareWaveId] != None:
                    blipData["instrumentId"] = self.SquareWave[squareWaveId]
                
            elif self.getType(lines[i]) == "RPT":
                if int(self.getArg(lines[i], 1)) == 1:
                    blipData["doRepeat"] = True
                
            elif self.getType(lines[i]) == "NAME":
                name = re.split(r'\s(.+)', lines[i])[1]
                blipData["name"] = name
            
            i += 1
        
        world["blip"][id] = blipData

        return i
    
    def parsePitch(self, pitchStr):
        logging.debug("parsing pitch: " + pitchStr)

        pitch = { "beats": 0, "note": self.Note["C"], "octave": self.Octave["4"], }

        beatsToken = ""
        for i in range(0, len(pitchStr)):
            if not pitchStr[i].isdigit():
                break

            beatsToken += pitchStr[i]
        
        if len(beatsToken) > 0:
            pitch["beats"] = int(beatsToken)
        
        noteName = ""
        if i < len(pitchStr):
            # uppercase letters represent chromatic notes
            if pitchStr[i] == pitchStr[i].upper():
                noteType = self.Note
                noteName += pitchStr[i]
                i += 1

                if i < len(pitchStr) and pitchStr[i] == "#":
                    noteName += "_SHARP"
                    i += 1
                
            else:
                noteType = self.Solfa
                noteName += pitchStr[i].upper()
                i += 1

        if noteName in noteType:
            pitch["note"] = noteType[noteName]
        
        octaveToken = ""
        if i < len(pitchStr):
            octaveToken += pitchStr[i]
            
        if octaveToken in self.Octave:
            pitch["octave"] = self.Octave[octaveToken]
        
        return pitch

    def parseFlag(self, parseState, world):
        logging.debug("parsing flag")

        i = parseState["index"]
        lines = parseState["lines"]
        id = self.getId(lines[i])

        valStr = lines[i].split(" ")[2]
        
        world["flags"][id] = int(valStr)

        i += 1

        return i
    
    def getDrawingFrameCount(self, world, drwId):
        logging.debug("getting drawing frame count")

        return len(world["drawings"][drwId])
    
    def storeDrawingData(self, world, drwId, drawingData):
        logging.debug("storing drawing data")

        world["drawings"][drwId] = drawingData
    
    def placeSprites(self, parseState, world):
        logging.debug("placing sprites")

        for id in parseState["spriteStartLocations"]:
            world["sprite"][id]["room"] = parseState["spriteStartLocations"][id]["room"]
            world["sprite"][id]["x"] = parseState["spriteStartLocations"][id]["x"]
            world["sprite"][id]["y"] = parseState["spriteStartLocations"][id]["y"]
        
    def createNameMapsForWorld(self, world):
        logging.debug("creating name maps for world")

        nameMaps = {}

        def createNameMap(objectStore):
            map = {}

            for id in objectStore:
                if type(objectStore[id]) == dict and objectStore[id]["name"] != None:
                    map[objectStore[id]["name"]] = id

        
            return map
        
        nameMaps["room"] = createNameMap(world["room"])
        nameMaps["tile"] = createNameMap(world["tile"])
        nameMaps["sprite"] = createNameMap(world["sprite"])
        nameMaps["item"] = createNameMap(world["item"])
        nameMaps["dialog"] = createNameMap(world["dialog"])
        nameMaps["palette"] = createNameMap(world["palette"])
        nameMaps["tune"] = createNameMap(world["tune"])
        nameMaps["blip"] = createNameMap(world["blip"])

        return nameMaps
    
    def getType(self, line):
        return self.getArg(line, 0)
    
    def getId(self, line):
        return self.getArg(line, 1)

    def getCoord(self, line, arg):
        return self.getArg(line, arg).split(",")
    
    def getArg(self, line, arg):
        return line.split(" ")[arg]
    
    def getNameArg(self, line):
        name = re.split(r'\s(.+)', line)[1]
        return name


if __name__ == "__main__":
    # set logging level to debug
    #logging.basicConfig(level=logging.DEBUG)

    from .test import test
    from pprint import pprint

    world = test()
    e = Engine()
    world = e.parseWorld(world)

    # remove 'tune' and 'blip' from the world
    del world['tune']
    del world['blip']

    pprint(world)