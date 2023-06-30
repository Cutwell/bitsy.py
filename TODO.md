# Bitsy.py

## TODO
- [x] Load save data
- [x] Render basic scene
- [x] Render sprites
- [x] Avatar movement
- [x] Tile / sprite animation
- [x] Render dialog box
- [x] Render text on screen
- [x] Render multiple lines of text
- [x] Dialog triggers
- [x] Intro cutscene
- [x] Room exits
- [x] Ending triggers
- [x] Collecting items
- [x] Variables
- [ ] Logic parser (for dialog, exits, endings)
- [ ] Implement branching logic interpreter (dictionary based??)
- [ ] Item requirements for exits
- [ ] Item requirements for dialog
- [ ] Branching logic inter
- [ ] Blips for interactions
- [ ] Game music (tunes)
- [ ] Room transitions


## Logic
* Dialog can contain text triggers (draw sprite, shaking/rainbow/wavy text, changing text color palette). Values of variables / items can also be printed to dialog.
* Exits teleport players to room and coordinates.
* Endings end the game.
* Pagebreaks end current text box, force new text to move onto new box.
* Lists display dialog:
    * Sequence list serves dialog in sequence, returning empty once all dialog is used.
    * Cycle list serves dialog in sequence, resetting to first dialog after reaching end.
    * Shuffle list returns a random dialog from the list each time.
    * Branching list chooses dialog based on logic, returning first valid branch. Branches can be iterative, containing further logic.
* Locked property: indicates if exit or endings can be triggered.
* Palette swap: swaps changes the room palette (persistent)
* Avatar morph: changes avatar to another sprite (persistent)
* Blip: plays a tone
* Tune: change room tone
* The number of an item in the players energy can be set/changed, as can variables.

* Once logic is triggered, it runs till end of logic options.
* Once dialog is entered, new text (from dialog or logic) is stringed together into a complete script. This text is then presented all at once (unless broken up by page breaks). 
