# Torus Games handheld game ripper
This is a tool for handheld games made by Torus Games. It converts stuff like sprites and maps from their games into usable formats.

# Requirements
- PIL `pip install pillow` (used for images)
- ndspy `pip install ndspy` (used for Nintendo DS ROM handling)

# Goals
- Support most of the GBA formats
- Support most of the Leapster/Didj formats
- Support some of the DS formats (2D only - mostly carried over from the GBA)
- Support some of the N-Gage formats (such as the PMAN container - other formats might not get support)

If anything from the console games gets supported, it'll just be the PACKFILE containers.

# Supported formats
- DPAK containers (found in most of their games from before the DS)
- GBA sprites (work in progress - very buggy)
- RLE sprites (found in their LeapFrog games)
- GBA music and sound effects (specifically their format, I will not add support for GAX)
- Level maps (work in progress - some come out broken)
- LZB compression (for when I eventually add support for level maps)

# List of games that use this engine
LeapFrog:
- Cars
- Cars: Supercharged
- Didji Racing: Tiki Tropics (has debug symbols!)
- Go, Diego, Go! Animal Rescuer
- NASCAR
- Sonic X

GBA:
- Backyard Football
- Backyard Football 2006
- Backyard Sports Football 2007
- Cabela's Big Game Hunter 2005 Adventures
- Curious George
- Dead to Rights
- Doom II
- Duke Nukem Advance
- Fantastic 4
- Fantastic 4: Flame On
- Gumby vs. the Astrobots
- Ice Nine
- Jackie Chan Adventures: Legend of the Dark Hand
- Minority Report: Everybody Runs
- Pitfall: the Lost Expedition
- Planet of the Apes
- Rapala Pro Fishing
- Shrek Smash n' Crash Racing
- Space Invaders
- Sportsmans Pack: Cabela's Big Game Hunter + Rapala Pro Fishing
- The Invincible Iron Man

DS:
- Barbie: Dreamhouse Party
- Indianapolis 500 Legends
- Madagascar 3
- Monster High: 13 Wishes
- Monster Jam: Urban Assault
- Rise of the Guardians
- Scooby-Doo! and the Spooky Swamp
- Shrek Smash n' Crash Racing
- The Croods: Prehistoric Party
- Turbo: Super Stunt Squad
