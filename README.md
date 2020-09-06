# MidiModder
Version 0.4.2
By FroggestSpirit

Batch Midi Parser for Python 3

Convert Midi files to text for viewing/editing, then back to Midi

For best results, use Midi version 1 files

Usage: MidiModder.py input [mode] [output] [flags]

mode: -e  Encode text file to Midi  | -d  Decode Midi to text file  | -a  Analyze the Midi and display information  | -h  Show help

flags:  -l  add note length to the NoteOn commands instead of writing NoteOff commands (This is for decoding midi->text, while encoding back to midi, both NoteOn (with length) or NoteOff will be accepted automatically)

You can also drag and drop a .mid file to convert to txt with the same filename, or drag a .txt to convert to midi. If doing this, mode does not need to be specified, but the file will convert based on extension!

Keep in mind the program will not ask if you want to overwrite files, so make backups!
