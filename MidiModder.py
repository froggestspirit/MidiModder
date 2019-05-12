#Midi-Modder 0.1 by FroggestSpirit
#Parses Midi files to text for editing then back to midi
#Make backups, this can overwrite files without confirmation
import sys
import math

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
	outfile.write("TimeDivision:"+str(timeDivision)+"\n\n")
	filePos=16+headerSize #Skip 'MTrk' and tracksize
	trackData=False
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
		if(delay>0): outfile.write("Delay:"+str(delay)+"\n")
		
		command=midiFile[filePos]
		filePos+=1
		textCommand=""
		if(command<0x80): command=lastCommand
		lastCommand=command
		if((command&0xF0)==0x80):
			#note off
			if not trackData:
				outfile.write("Track:"+str(command&0xF)+"\n")
			trackData=True
			textCommand="NoteOff:"
			arg1=midiFile[filePos]
			filePos+=1
			arg2=midiFile[filePos]
			filePos+=1
			outfile.write(textCommand+str(arg1)+","+str(arg2)+"\n")
		elif((command&0xF0)==0x90):
			#note on
			if not trackData:
				outfile.write("Track:"+str(command&0xF)+"\n")
			trackData=True
			textCommand="NoteOn:"
			arg1=midiFile[filePos]
			filePos+=1
			arg2=midiFile[filePos]
			filePos+=1
			outfile.write(textCommand+str(arg1)+","+str(arg2)+"\n")
		elif((command&0xF0)==0xA0):
			#key pressure
			if not trackData:
				outfile.write("Track:"+str(command&0xF)+"\n")
			trackData=True
			textCommand="PolyPressure:"
			arg1=midiFile[filePos]
			filePos+=1
			arg2=midiFile[filePos]
			filePos+=1
			outfile.write(textCommand+str(arg1)+","+str(arg2)+"\n")
		elif((command&0xF0)==0xB0):
			#controller change
			if not trackData:
				outfile.write("Track:"+str(command&0xF)+"\n")
			trackData=True
			arg1=midiFile[filePos]
			filePos+=1
			arg2=midiFile[filePos]
			filePos+=1
			outfile.write("Controller_"+str(arg1)+":"+str(arg2)+"\n")
		elif((command&0xF0)==0xC0):
			#program change
			if not trackData:
				outfile.write("Track:"+str(command&0xF)+"\n")
			trackData=True
			textCommand="Instrument:"
			arg1=midiFile[filePos]
			filePos+=1
			outfile.write(textCommand+str(arg1)+"\n")
		elif((command&0xF0)==0xD0):
			#channel pressure
			if not trackData:
				outfile.write("Track:"+str(command&0xF)+"\n")
			trackData=True
			textCommand="KeyPressure:"
			arg1=midiFile[filePos]
			filePos+=1
			outfile.write(textCommand+str(arg1)+"\n")
		elif((command&0xF0)==0xE0):
			#pitch bend
			if not trackData:
				outfile.write("Track:"+str(command&0xF)+"\n")
			trackData=True
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
				trackData=False
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
	Done=False
	lineNum=0
	infile=open(sys.argv[2], "r")
	thisLine=""
	while(len(thisLine)==0 and not Done):
		thisLine=infile.readline()
		if not thisLine:
			sys.exit()
		thisLine=thisLine.split(";")
		thisLine=thisLine[0]
		lineNum+=1
	commandLen=thisLine.find(":")
	if(commandLen<1):
		print("Invalid Syntax on line: "+str(lineNum))
		infile.close()
		sys.exit()
	else:
		command=thisLine.split(":")
		argument=command[1].split(",")
	if(command[0]=="TimeDivision"):
		timeDivision=int(argument[0],10)
	else:
		print("Missing TimeDivision")
		infile.close()
		sys.exit()
	
	#Write the header
	filePos=0
	midiFile = []
	midiFile.append(ord('M'))
	midiFile.append(ord('T'))
	midiFile.append(ord('h'))
	midiFile.append(ord('d'))
	midiFile.append(0)#Header size
	midiFile.append(0)
	midiFile.append(0)
	midiFile.append(6)
	midiFile.append(0)#format
	midiFile.append(1)
	midiFile.append(0)#number of channels (this will be updated later)
	midiFile.append(0)
	midiFile.append(math.floor(timeDivision/256))#time division
	midiFile.append((timeDivision%256))
	filePos+=14
	trackEnd=True
	makeHeader=False
	channelData=False#keep false unless the channel contains data like notes, controller changes, etc
	trackNum=0
	physicalTracks=0
	skipDelay=False
	while not Done:
		if(trackEnd):
			midiFile.append(ord('M'))
			midiFile.append(ord('T'))
			midiFile.append(ord('r'))
			midiFile.append(ord('k'))
			midiFile.append(0)#Header size (this will be updated later)
			midiFile.append(0)
			midiFile.append(0)
			midiFile.append(0)
			filePos+=8
			curSizePointer=filePos-4
			trackEnd=False
			trackStart=filePos
			if(channelData): trackNum+=1
			if(trackNum==16): trackNum=0
			channelData=False
		if(skipDelay==False):
			midiFile.append(0)#write delay (this will be overwritten if there is an actual delay
			filePos+=1
		skipDelay=False
		
		thisLine=""
		while(len(thisLine)==0 and not Done):
			thisLine=infile.readline()
			if not thisLine:
				Done=True
			thisLine=thisLine.split(";")
			thisLine=thisLine[0]
			lineNum+=1
		if not Done:
			command=thisLine.split(":")
			if(thisLine.startswith("StartTrack")):
				skipDelay=True
			elif(thisLine.startswith("Track:")):
				argument=command[1].split(",")
				trackNum=int(command[1],10)
				skipDelay=True
			elif(thisLine.startswith("Delay:")):
				argument=command[1].split(",")
				filePos-=1
				thisDelay=int(argument[0],10)
				if(thisDelay>0xFFFFFFF): thisDelay=0xFFFFFFF
				thisByte=[]
				length=0
				while(thisDelay>0):
					thisByte.append((thisDelay & 127))
					thisDelay-=thisByte[length]
					thisDelay=int(thisDelay/128)
					if(length>0): thisByte[length]+=128
					length+=1
				if(length==0): length=1
				midiFile[filePos]=thisByte[length-1]
				filePos+=1
				length-=1
				while(length>0):
					midiFile.append(thisByte[length-1])
					filePos+=1
					length-=1
				skipDelay=True
			elif(thisLine.startswith("NoteOff:")):
				argument=command[1].split(",")
				midiFile.append(0x80+trackNum)
				filePos+=1
				midiFile.append(int(argument[0],10))
				filePos+=1
				midiFile.append(int(argument[1],10))
				filePos+=1
				channelData=True
			elif(thisLine.startswith("NoteOn:")):
				argument=command[1].split(",")
				midiFile.append(0x90+trackNum)
				filePos+=1
				midiFile.append(int(argument[0],10))
				filePos+=1
				midiFile.append(int(argument[1],10))
				filePos+=1
				channelData=True
			elif(thisLine.startswith("PolyPressure:")):
				argument=command[1].split(",")
				midiFile.append(0xA0+trackNum)
				filePos+=1
				midiFile.append(int(argument[0],10))
				filePos+=1
				midiFile.append(int(argument[1],10))
				filePos+=1
				channelData=True
			elif(thisLine.startswith("Controller_")):
				argument=command[1].split(",")
				midiFile.append(0xB0+trackNum)
				filePos+=1
				command=command[0].split("_")
				midiFile.append(int(command[1],10))
				filePos+=1
				midiFile.append(int(argument[0],10))
				filePos+=1
				channelData=True
			elif(thisLine.startswith("Instrument:")):
				argument=command[1].split(",")
				midiFile.append(0xC0+trackNum)
				filePos+=1
				midiFile.append(int(argument[0],10))
				filePos+=1
				channelData=True
			elif(thisLine.startswith("KeyPressure:")):
				argument=command[1].split(",")
				midiFile.append(0xD0+trackNum)
				filePos+=1
				midiFile.append(int(argument[0],10))
				filePos+=1
				channelData=True
			elif(thisLine.startswith("PitchBend:")):
				argument=command[1].split(",")
				midiFile.append(0xE0+trackNum)
				filePos+=1
				midiFile.append(math.floor(int(argument[0],10)/0x100))
				filePos+=1
				midiFile.append((int(argument[0],10)%0x100))
				filePos+=1
				channelData=True
			elif(thisLine.startswith("MetaEvent_")):
				argument=command[1].split(",")
				midiFile.append(0xFF)
				filePos+=1
				command=command[0].split("_")
				midiFile.append(int(command[1],10))
				filePos+=1
				if(int(command[1],10)>=1 and int(command[1],10)<=7):
					argument=thisLine.split('"')
					argument=argument[1]
					numArgs=len(argument)
					if(numArgs>0x7F): numArgs=0x7F
					midiFile.append(numArgs)
					filePos+=1
					for i in range(numArgs):
						midiFile.append(ord(argument[i]))
						filePos+=1
				else:
					numArgs=len(argument)
					if(numArgs>0x7F): numArgs=0x7F
					midiFile.append(numArgs)
					filePos+=1
					for i in range(numArgs):
						midiFile.append(int(argument[i],10))
						filePos+=1
			elif(thisLine.startswith("EndTrack")):
				midiFile.append(0xFF)
				midiFile.append(0x2F)
				midiFile.append(0x00)
				filePos+=3
				trackSize=filePos-trackStart
				midiFile[curSizePointer]=math.floor(trackSize/0x1000000)
				midiFile[curSizePointer+1]=(math.floor(trackSize/0x10000)%0x100)
				midiFile[curSizePointer+2]=(math.floor(trackSize/0x100)%0x100)
				midiFile[curSizePointer+3]=(trackSize%0x100)
				trackEnd=True
				physicalTracks+=1
			else:
				if(len(thisLine)>1):
					midiFile.append(0xFF)
					midiFile.append(0x01)
					midiFile.append(0x00)
					filePos+=3
				else:
					skipDelay=True
	midiFile[10]=math.floor(physicalTracks/0x100)#Header size
	midiFile[11]=(physicalTracks%0x100)
	midiSize=len(midiFile)
	header=str(chr(midiFile[filePos-9]))+str(chr(midiFile[filePos-8]))+str(chr(midiFile[filePos-7]))+str(chr(midiFile[filePos-6]))
	if(header=="MTrk"): midiSize-=9#remove unneeded track header
	outfile=open(sys.argv[3],"wb")
	for i in range(midiSize):
		outfile.write(midiFile[i].to_bytes(1,byteorder='little'))
	outfile.close()
else:
	print("Invalid usage")
