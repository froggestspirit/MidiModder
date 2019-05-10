#Midi-Modder 0.1 by FroggestSpirit
#Parses Midi files to text
#Make backups, this can overwrite files without confirmation
import sys
echo=True
mode=0
print("Midi-Modder 0.1\n")
if(len(sys.argv)<2):
	print("Try running "+sys.argv[0]+" -h for usage.")
	sys.exit()
if(len(sys.argv)<4):
	if(sys.argv[1]=="-h" or sys.argv[1]=="--help"):
		print("Usage: "+sys.argv[0]+" mode input output\nMode:\t-e\tEncode text file to Midi\n\t-d\tDecode Midi to text file\n\t-h\tShow this help message")
		sys.exit()
	else:
		print("Try running "+sys.argv[0]+" -h for usage.")
		sys.exit()

if(sys.argv[2]==sys.argv[3]):
	print("Input and output files cannot be the same")
	sys.exit()
if(sys.argv[1]=="-d" or sys.argv[1]=="--decode"):
	infile=open(sys.argv[2], "rb")
	midiFile=infile.read()
	infile.close()

	fileSize=len(midiFile)
	header=str(chr(midiFile[0]))+str(chr(midiFile[1]))+str(chr(midiFile[2]))+str(chr(midiFile[3]))
	if(header!="MThd"):
		print("Not a MIDI file.")
		sys.exit()
	headerSize=midiFile[7]+(midiFile[6]*0x100)+(midiFile[5]*0x10000)+(midiFile[4]*0x1000000)
	numTracks=midiFile[11]+(midiFile[10]*256)
	timeDivision=midiFile[13]+(midiFile[12]*256)
	if(echo): print("File Size: "+str(fileSize))
	if(echo): print("Number of Tracks: "+str(numTracks))
	if(echo): print("Time Division: "+str(timeDivision))

	trackEnd=True
	lastCommand=0
	outfile=open(sys.argv[3],"w")
	filePos=16+headerSize #Skip 'MTrk' and tracksize
	while(filePos<fileSize):
		if(trackEnd):
			outfile.write("StartTrack\n")
			trackEnd=False
		delay=0
		val=midiFile[filePos]
		filePos+=1
		if(val>0x7F):
			delay+=(val&0x7F)
			delay*=0x80
			val=midiFile[filePos]
			filePos+=1
			if(val>0x7F):
				delay+=(val&0x7F)
				delay*=0x80
				val=midiFile[filePos]
				filePos+=1
				if(val>0x7F):
					delay+=(val&0x7F)
					delay*=0x80
					val=midiFile[filePos]
					filePos+=1
		delay+=(val&0x7F)
		outfile.write("Delay:"+str(delay)+"\n")
		
		command=midiFile[filePos]
		filePos+=1
		textCommand=""
		if(command<0x80): command=lastCommand
		lastCommand=command
		if((command&0xF0)==0x80):
			#note off
			textCommand="NoteOff:"
			arg1=midiFile[filePos]
			filePos+=1
			arg2=midiFile[filePos]
			filePos+=1
			outfile.write(textCommand+str(arg1)+","+str(arg2)+"\n")
		elif((command&0xF0)==0x90):
			#note on
			textCommand="NoteOn:"
			arg1=midiFile[filePos]
			filePos+=1
			arg2=midiFile[filePos]
			filePos+=1
			outfile.write(textCommand+str(arg1)+","+str(arg2)+"\n")
		elif((command&0xF0)==0xA0):
			#key pressure
			textCommand="PolyPressure:"
			arg1=midiFile[filePos]
			filePos+=1
			arg2=midiFile[filePos]
			filePos+=1
			outfile.write(textCommand+str(arg1)+","+str(arg2)+"\n")
		elif((command&0xF0)==0xB0):
			#controller change
			arg1=midiFile[filePos]
			filePos+=1
			arg2=midiFile[filePos]
			filePos+=1
			outfile.write("Controller_"+str(arg1)+":"+str(arg2)+"\n")
		elif((command&0xF0)==0xC0):
			#program change
			textCommand="Instrument:"
			arg1=midiFile[filePos]
			filePos+=1
			outfile.write(textCommand+str(arg1)+"\n")
		elif((command&0xF0)==0xD0):
			#channel pressure
			textCommand="KeyPressure:"
			filePos+=1
			arg1=midiFile[filePos]
			filePos+=1
			outfile.write(textCommand+str(arg1)+"\n")
		elif((command&0xF0)==0xE0):
			#pitch bend
			textCommand="PitchBend:"
			arg1=midiFile[filePos]
			filePos+=1
			arg2=midiFile[filePos]
			filePos+=1
			outfile.write(textCommand+str((arg1*256)+arg2)+"\n")
		elif(command==0xF0 or command==0xF7):
			#sys-ex event
			textCommand="SysEvent:"
			arg1=midiFile[filePos]
			filePos+=1
			outfile.write(textCommand)
			for i in range(arg1):
				arg2=midiFile[filePos]
				filePos+=1
				if(i<arg1-1): outfile.write(str(arg2)+",")	
				if(i==arg1-1): outfile.write(str(arg2))	
			outfile.write("\n")		
		elif(command==0xFF):
			#meta event
			textCommand="MetaEvent_"
			arg1=midiFile[filePos]
			filePos+=1
			if(arg1>=1 and arg1<=7):
				textMode=True
			else:
				textMode=False
			if(arg1==0x2F):
				#end of track
				outfile.write("EndTrack\n\n")
				filePos+=9#skip next 'MTrk' and tracklength
				lastCommand=0
				trackEnd=True
			else:
				outfile.write(textCommand+str(arg1)+":")
				if(textMode): outfile.write('"')
				arg1=midiFile[filePos]
				filePos+=1
				for i in range(arg1):
					arg2=midiFile[filePos]
					filePos+=1
					if(textMode):
						if(i<arg1-1): outfile.write(str(chr(arg2)))	
						if(i==arg1-1): outfile.write(str(chr(arg2))+'"')	
					else:
						if(i<arg1-1): outfile.write(str(arg2)+",")	
						if(i==arg1-1): outfile.write(str(arg2))	
				outfile.write("\n")		
	outfile.close()
elif(sys.argv[1]=="-e" or sys.argv[1]=="--encode"):
	print("Not implemented yet")
else:
	print("Invalid usage")
