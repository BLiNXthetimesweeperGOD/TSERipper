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
- GBA/NDS sprites (work in progress - very buggy)
- GBA music and sound effects (specifically their format, I will not add support for GAX)
- LZB compression (for when I eventually add support for level maps)
