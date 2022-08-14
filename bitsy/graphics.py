import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.animation as animation
from matplotlib.font_manager import FontProperties
from .engine import Engine
import numpy as np

class GraphicsSystem():
    def __init__(self, world):
        # hide toolbar
        plt.rcParams['toolbar'] = 'None'

        # create matplotlib figure
        self.fig = plt.figure()
        self.gameCanvas = self.fig.add_subplot(111)

        # remove axis tickers
        self.gameCanvas.xaxis.set_major_locator(ticker.NullLocator())
        self.gameCanvas.yaxis.set_major_locator(ticker.NullLocator())

        self.fig.canvas.mpl_connect('key_press_event', self.on_press)

        self.font = FontProperties()
        self.font.set_family('monospace')

        # create empty grid of 128x128 zeros
        self.screenData = np.zeros((128, 128, 3), dtype=np.uint8)

        self.im = self.gameCanvas.imshow(self.screenData, interpolation='none')

        self.animation = animation.FuncAnimation(self.fig, self.update, frames=12, interval=10, blit=False)

        self.world = world

        self.inventory = []

        # set window name to game name
        self.fig.canvas.set_window_title(f"{self.world['dialog']['title']['src']} | Bitsy {self.world['versionNumberFromComment']}")

        self.current_room = None

        self.dialogId = None
        self.inDialog = False
        self.dialogLineIndex = 0

        self.cutsceneAnimation = False
        self.ending = False

        self.dialogpalette = [(0,0,0), (255,255,255)]

        # find avatar in sprite list
        for sprite in self.world["sprite"].values():
            if sprite["type"] == "AVA":
                avatarId = sprite["id"]
                break

        # iterate keys in world rooms
        for room_id in self.world["room"].keys():
            if not self.world["room"][room_id]["ava"]:
                self.world["room"][room_id]["ava"] = avatarId
        
        # break dialog into lines of max 20 characters, splitting on whitespace
        for dialog in self.world["dialog"].values():
            dialog["line"] = []
            dialog["lineIndex"] = 0
            curr_line = ""

            for line in dialog["src"].split(" "):
                if len(curr_line) > 20:
                    dialog["line"].append(curr_line)
                    curr_line = ""
                
                curr_line += line + " "
            
            dialog["line"].append(curr_line)

            dialog["lineCount"] = len(dialog["line"])

        self.blankTile = [[[0 for _ in range(8)] for _ in range(8)]]

        # set dialog blinker frames to an 8x8 arrow animation
        self.dialogBlinker = [[
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
        ],
        [
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
        ]]

        self.dialogBlinkerFrameIndex = 0

        self.preloaded = {}
        for room_id in self.world["room"].keys():
            # get all unique tile IDs from tilemap
            tilemap = self.world["room"][room_id]["tilemap"]
            tiles = set([tile for row in tilemap for tile in row])
            # remove key '0' from tiles
            tiles.remove('0')

            pal = self.world["room"][room_id]["pal"]
            palette = self.world["palette"][pal]

            # get palettes for types
            tilepalette = [palette["colors"][0], palette["colors"][1]]
            spritepalette = [palette["colors"][0], palette["colors"][2]]
            itempalette = [palette["colors"][0], palette["colors"][2]]

            # find sprites that exist in room (excluding avatar)
            sprites = [sprite for sprite in self.world["sprite"].values() if sprite["room"] == room_id and sprite["type"] != "AVA"]

            # find items that exist in room
            items = [item for item in self.world["room"][room_id]["items"]]

            # add avatar to sprites list
            sprites.append(self.world["sprite"][avatarId])

            name = self.world["room"][room_id]["name"]

            # add preloaded variables to room dictionary to preloaded dictionary
            self.preloaded[room_id] = {
                "item": items,
                "tilemap": tilemap,
                "tile": tiles,
                "palette": palette,
                "tilepalette": tilepalette,
                "itempalette": itempalette,
                "spritepalette": spritepalette,
                "sprite": sprites,
                "name": name,
            }

    def start(self):
        self.current_room = list(self.world["room"].values())[0]["id"]

        self.cutsceneAnimation = True
        self.inDialog = True
        self.dialogId = "title"
        self.dialogLineIndex = 0
        self.dialogBlinkerFrameIndex = 0

    def on_press(self, event):
        if self.inDialog:
            # if in dialog, any keypress event advances dialog
            # step dialog by 2 lines if possible, else 1
            if (self.world["dialog"][self.dialogId]["lineCount"] - self.dialogLineIndex) >= 2:
                self.dialogLineIndex += 2
            else:
                self.dialogLineIndex += 1

            # check if we've finished dialog
            if self.dialogLineIndex == self.world["dialog"][self.dialogId]["lineCount"]:
                self.inDialog = False
                self.dialogLineIndex = 0
                self.dialogId = None
                self.dialogBlinkerFrameIndex = 0
                self.cutsceneAnimation = False

                if self.ending:
                    # end game
                    plt.close()
        
        else:   # in game
            ava_id = self.world["room"][self.current_room]["ava"]
            ava = self.world["sprite"][ava_id]

            x, y = ava["x"], ava["y"]

            if event.key == 'w':
                y -= 1
            
            elif event.key == 's':
                y += 1
            
            elif event.key == 'a':
                x -= 1
            
            elif event.key == 'd':
                x += 1
            
            # perform bounds check on new x, y
            if x < 0 or x > 15 or y < 0 or y > 15:
                # reject movement update
                return
            
            # check sprite collision
            for sprite in self.world["sprite"].values():
                if sprite["x"] == x and sprite["y"] == y:
                    # check if this sprite has a dialog
                    if sprite["dlg"] != None:
                        # set dialog id to sprite dialog id
                        self.dialogId = sprite["dlg"]
                        # set dialog line index to 0
                        self.dialogLineIndex = 0
                        # set in dialog to true
                        self.inDialog = True
                        # set dialog blinker frame index to 0
                        self.dialogBlinkerFrameIndex = 0

                    # reject movement update
                    return

            # get tile ID at position
            tile_id = self.world["room"][self.current_room]["tilemap"][y][x]
            # check if tile isWall property is true
            if tile_id in self.world["tile"] and self.world["tile"][tile_id]["isWall"]:
                # reject movement update
                return


            # check if new position is a room exit
            for exit in self.world["room"][self.current_room]["exits"]:
                if exit["x"] == x and exit["y"] == y:
                    dest = exit["dest"]

                    # set new room to exit room
                    self.current_room = dest["room"]

                    # set new x, y to exit position
                    x, y = dest["x"], dest["y"]

            # check if new position is an ending
            for ending in self.world["room"][self.current_room]["endings"]:
                if ending["x"] == x and ending["y"] == y:
                    # activate ending cutscene
                    self.cutsceneAnimation = True
                    self.ending = True
                    self.inDialog = True
                    self.dialogId = ending["id"]
                    self.dialogLineIndex = 0
                    self.dialogBlinkerFrameIndex = 0
                    
                    return

            # check if new position is an item
            for item in self.world["room"][self.current_room]["items"]:
                if item["x"] == x and item["y"] == y:
                    # get item data from world
                    item_data = self.world["item"][item["id"]]

                    # add item to inventory
                    self.inventory.append(item_data)

                    # remove item from room
                    self.world["room"][self.current_room]["items"].remove(item)

                    # remove item from preloading
                    self.preloaded[self.current_room]["item"].remove(item)


            # update sprite position
            self.world["sprite"][ava_id]["y"] = y
            self.world["sprite"][ava_id]["x"] = x

    def setRoom(self, id):
        self.current_room = id

        # set figure title to room name
        self.fig.suptitle(self.preloaded[id]["name"])

    def update(self, frame_number):
        # clear text from figure
        for text in self.gameCanvas.texts:
            text.remove()
        
        roomPreloaded = self.preloaded[self.current_room]

        # get list of tile drawings by drw from id in tiles
        tileDrawingIDs = [self.world["tile"][tile]["drw"] for tile in roomPreloaded["tile"]]
        # get list of tile drawings by drw from id in tiles
        tileDrawings = [self.world["drawings"][drw] for drw in tileDrawingIDs]

        # create dictionary mapping tile IDs to tile drawings
        tileDict = {id: drw for id, drw in zip(roomPreloaded["tile"], tileDrawings)}

        # add blanktile to tileDict mapped to '0'
        tileDict['0'] = self.blankTile

        # NOTE: we don't create a new np screendata array every frame because it's slow, so instead we reuse the same array (which is overwritten anyway when we draw the tile background)

        # iterate through x, y of screenData in steps of 8
        for x in range(0, 128, 8):
            for y in range(0, 128, 8):
                # get tile ID at x, y
                tileID = roomPreloaded["tilemap"][y//8][x//8]
                frameIndex = 0

                # get tile data
                if tileID != '0':
                    tile = self.world['tile'][tileID]

                    # check if spite is animated
                    if tile["animation"]["isAnimated"] == True:
                        # get frame index
                        frameIndex = tile["animation"]["frameIndex"]
                        
                        if frame_number == 11:
                        # increment frame index for next frame
                            tile["animation"]["frameIndex"] += 1

                            # check if frame index is greater than length of animation
                            if tile["animation"]["frameIndex"] == tile["animation"]["frameCount"]:
                                # reset frame index
                                tile["animation"]["frameIndex"] = 0

                # get tile drawing
                tileDrawing = tileDict[tileID][frameIndex]
                
                # iterate through x, y of tileDrawing in steps of 8
                for i in range(8):
                    for j in range(8):
                        # get color at x, y of tileDrawing
                        color = tileDrawing[i][j]

                        # get color from tilepalette at color index
                        color = roomPreloaded["tilepalette"][color]

                        # set color at x, y of screenData
                        self.screenData[y+i][x+j] = color

        # iterate through sprites and draw them to screenData
        for itemData in roomPreloaded["item"]:

            # get item data
            item = self.world["item"][itemData["id"]]

            # check if spite is animated
            if item["animation"]["isAnimated"] == True:
                # get frame index
                frameIndex = item["animation"]["frameIndex"]

                if frame_number == 11:
                    # increment frame index for next frame
                    item["animation"]["frameIndex"] += 1

                    # check if frame index is greater than length of animation
                    if item["animation"]["frameIndex"] == item["animation"]["frameCount"]:
                        # reset frame index
                        item["animation"]["frameIndex"] = 0

            # get sprite drawing from world
            itemDrawing = self.world["drawings"][item["drw"]][frameIndex]

            # get sprite x y and scale
            x = itemData["x"] * 8
            y = itemData["y"] * 8

            # iterate through x, y of spriteDrawing
            for i in range(8):
                for j in range(8):
                    # get color at x, y of spriteDrawing
                    color = itemDrawing[i][j]

                    color = roomPreloaded["itempalette"][color]

                    # set color at x, y of screenData
                    self.screenData[y+i][x+j] = color

        # iterate through sprites and draw them to screenData
        for sprite in roomPreloaded["sprite"]:

            # check if spite is animated
            if sprite["animation"]["isAnimated"] == True:
                # get frame index
                frameIndex = sprite["animation"]["frameIndex"]

                if frame_number == 11:
                    # increment frame index for next frame
                    sprite["animation"]["frameIndex"] += 1

                    # check if frame index is greater than length of animation
                    if sprite["animation"]["frameIndex"] == sprite["animation"]["frameCount"]:
                        # reset frame index
                        sprite["animation"]["frameIndex"] = 0

            # get sprite drawing from world
            spriteDrawing = self.world["drawings"][sprite["drw"]][frameIndex]

            # get sprite x y and scale
            x = sprite["x"] * 8
            y = sprite["y"] * 8

            # iterate through x, y of spriteDrawing
            for i in range(8):
                for j in range(8):
                    # get color at x, y of spriteDrawing
                    color = spriteDrawing[i][j]

                    color = roomPreloaded["spritepalette"][color]

                    # set color at x, y of screenData
                    self.screenData[y+i][x+j] = color

        # if in dialog, draw dialog to screenData
        if self.inDialog:
            
            # if intro, make dialog box cover screen
            if self.cutsceneAnimation:
                x, y = 0, 0

                dims = (128, 128) # dialog box width and height

            else:
                x, y = 12, 88

                dims = (32, 104) # dialog box width and height

            dialogColor = (0, 0, 0) # dialog box color

            for i in range(dims[0]):
                for j in range(dims[1]):
                    self.screenData[y+i][x+j] = dialogColor

            # draw dialogBlinker
            if frame_number == 11 or frame_number == 5:
                self.dialogBlinkerFrameIndex += 1

                if self.dialogBlinkerFrameIndex == 2:
                    self.dialogBlinkerFrameIndex = 0

            # get sprite drawing from world
            spriteDrawing = self.dialogBlinker[self.dialogBlinkerFrameIndex]

            # get sprite x y and scale
            x, y = 106, 112

            # iterate through x, y of spriteDrawing
            for i in range(8):
                for j in range(8):
                    # get color at x, y of spriteDrawing
                    color = spriteDrawing[i][j]

                    color = self.dialogpalette[color]

                    # set color at x, y of screenData
                    self.screenData[y+i][x+j] = color
            
            # draw speaker icon
            if not self.cutsceneAnimation:
                # get dialog icon
                speaker = self.world["dialog"][self.dialogId]["name"]
                speakerId = self.world["names"]["dialog"][speaker]

                # find sprite with dlg matching speakerId
                for sprite in roomPreloaded["sprite"]:
                    if sprite["dlg"] == speakerId:
                        # get sprite drawing from world
                        speakerDrawing = self.world["drawings"][sprite["drw"]][0]
                        break

                x, y = 16, 90
                for i in range(8):
                    for j in range(8):
                        # get color at x, y of spriteDrawing
                        color = speakerDrawing[i][j]

                        color = self.dialogpalette[color]

                        # set color at x, y of screenData
                        self.screenData[y+i][x+j] = color


            # draw dialog text
            if self.cutsceneAnimation:
                x1, y1 = 32, 46
                x2, y2 = 32, 58
            else:
                x1, y1 = 32, 96
                x2, y2 = 32, 108

            dialog1 = self.world["dialog"][self.dialogId]["line"][self.dialogLineIndex]

            self.gameCanvas.text(x1, y1, dialog1, color='white', fontsize=12)

            # check if 2nd line is available
            if self.world["dialog"][self.dialogId]["lineCount"] > self.dialogLineIndex + 1:

                dialog2 = self.world["dialog"][self.dialogId]["line"][self.dialogLineIndex+1]

                self.gameCanvas.text(x2, y2, dialog2, color='white', fontsize=12)

        # check if we've finished dialog
        if self.inDialog and self.dialogLineIndex == self.world["dialog"][self.dialogId]["lineCount"]:
            self.inDialog = False
            self.dialogLineIndex = 0
            self.dialogId = None
            self.dialogBlinkerFrameIndex = 0
            self.cutsceneAnimation = False

            if self.ending:
                # end game
                plt.close()
            
        # imshow screen data
        self.im.set_array(self.screenData)

        self.fig.canvas.draw()

        return [self.im]

if __name__ == "__main__":
    from bitsy.test import test

    world = test()
    e = Engine()
    world = e.parseWorld(world)

    g = GraphicsSystem(world)
    g.setRoom('0')
    g.update()

    plt.show()