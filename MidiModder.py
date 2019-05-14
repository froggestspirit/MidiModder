#Midi-Modder by FroggestSpirit
version="0.4"
#Parses Midi files to text for editing then back to midi
#Make backups, this can overwrite files without confirmation
import sys
import math

noteLengthArg=False

class Note:
  def __init__(self, track, arg1, arg2, length):
    self.track = track
    self.arg1 = arg1
    self.arg2 = arg2
    self.length = length
	
def get_note_length(tempPos,chan,note):
	Done=False
	tempPos=tempPos
	noteLen=0
	lastTempCommand=0x90+chan
	while(not Done):
		delay=0
		val=midiFile[tempPos]
		tempPos+=1
		if(val>0x7F):
			delay+=(val&0x7F)
			delay*=0x80
			val=midiFile[tempPos]
			tempPos+=1
			if(val>0x7F):
				delay+=(val&0x7F)
				delay*=0x80
				val=midiFile[tempPos]
				tempPos+=1
				if(val>0x7F):
					delay+=(val&0x7F)
					delay*=0x80
					val=midiFile[tempPos]
					tempPos+=1
		delay+=(val&0x7F)
		noteLen+=delay
		
		tempCommand=midiFile[tempPos]
		tempPos+=1
		textCommand=""
		if(tempCommand<0x80):
			tempCommand=lastTempCommand
			tempPos-=1
		lastTempCommand=tempCommand
		if((tempCommand&0xF0)==0x80):
			#note off
			tempArg1=midiFile[tempPos]
			tempPos+=1
			tempArg2=midiFile[tempPos]
			tempPos+=1
			if(tempArg1==note and (tempCommand&0xF)==chan):	Done=True
		elif((tempCommand&0xF0)==0x90):
			#note on
			tempArg1=midiFile[tempPos]
			tempPos+=1
			tempArg2=midiFile[tempPos]
			tempPos+=1
			if(tempArg2==0 and tempArg1==note and (tempCommand&0xF)==chan):	Done=True
		elif((tempCommand&0xF0)==0xA0):
			#key pressure
			tempPos+=2
		elif((tempCommand&0xF0)==0xB0):
			#controller change
			tempPos+=2
		elif((tempCommand&0xF0)==0xC0):
			#program change
			tempPos+=1
		elif((tempCommand&0xF0)==0xD0):
			#channel pressure
			tempPos+=1
		elif((tempCommand&0xF0)==0xE0):
			#pitch bend
			tempPos+=2
		elif(tempCommand==0xF0 or tempCommand==0xF7):
			#sys-ex event
			tempArg1=midiFile[tempPos]
			tempPos+=tempArg1+1
		elif(tempCommand==0xFF):
			#meta event
			tempArg1=midiFile[tempPos]
			tempPos+=1
			if(tempArg1==0x2F):
				#end of track
				Done=True
			else:
				tempArg1=midiFile[tempPos]
				tempPos+=tempArg1+1
	return noteLen
	
				
sysargv=sys.argv
echo=True
mode=0
print("Midi-Modder "+version+"\n")
infileArg=-1;
outfileArg=-1;
for i in range(len(sysargv)):
	if(i>0):
		if(sysargv[i].startswith("-")):
			if(sysargv[i]=="-d" or sysargv[i]=="--decode"):
				mode=1
			elif(sysargv[i]=="-e" or sysargv[i]=="--encode"):
				mode=2
			elif(sysargv[i]=="-a" or sysargv[i]=="--analyze"):
				mode=3
			elif(sysargv[i]=="-h" or sysargv[i]=="--help"):
				mode=0
			elif(sysargv[i]=="-l"):
				noteLengthArg=True
		else:
			if(infileArg==-1): infileArg=i
			elif(outfileArg==-1): outfileArg=i
			
if(infileArg==-1):
	mode=0
else:
	if(outfileArg==-1):
		if(sysargv[infileArg].find(".mid")!=-1):
			if(mode==0): mode=1
			outfileArg=len(sysargv)
			sysargv.append(sysargv[infileArg].replace(".mid",".txt"))
		elif(sysargv[infileArg].find(".txt")!=-1):
			if(mode==0): mode=2
			outfileArg=len(sysargv)
			sysargv.append(sysargv[infileArg].replace(".txt",".mid"))
		else:
			mode=0
	else:
		if(sysargv[infileArg]==sysargv[outfileArg]):
			print("Input and output files cannot be the same")
			sys.exit()
if(mode==0): #Help
	print("Usage: "+sysargv[0]+" input [mode] [output] [flags]\nMode:\n\t-e\tEncode text file to Midi\n\t-d\tDecode Midi to text file\n\t-a\tAnalyze the Midi and display information\n\t-h\tShow this help message\n\nAdditional Flags:\n\t-l\tNote length added to NoteOn")
	sys.exit()
elif(mode==1): #decode
	infile=open(sysargv[infileArg], "rb")
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
	outfile=open(sysargv[outfileArg],"w")
	outfile.write("TimeDivision:"+str(timeDivision)+"\n\n")
	filePos=16+headerSize #Skip 'MTrk' and tracksize
	trackNum=-1
	while(filePos<fileSize):
		if(trackEnd):
			outfile.write("StartTrack\n")
			trackEnd=False
			delay=0
		curDelay=0
		val=midiFile[filePos]
		filePos+=1
		if(val>0x7F):
			curDelay+=(val&0x7F)
			curDelay*=0x80
			val=midiFile[filePos]
			filePos+=1
			if(val>0x7F):
				curDelay+=(val&0x7F)
				curDelay*=0x80
				val=midiFile[filePos]
				filePos+=1
				if(val>0x7F):
					curDelay+=(val&0x7F)
					curDelay*=0x80
					val=midiFile[filePos]
					filePos+=1
		curDelay+=(val&0x7F)
		delay+=curDelay

		command=midiFile[filePos]
		filePos+=1
		textCommand=""
		if(command<0x80):
			command=lastCommand
			filePos-=1
		lastCommand=command
		if((command&0xF0)!=0x80):
			if(delay>0):
				outfile.write("Delay:"+str(delay)+"\n")
				delay=0
		if((command&0xF0)==0x80):
			#note off
			if(trackNum!=str(command&0xF)):
				outfile.write("Track:"+str(command&0xF)+"\n")
			trackNum=str(command&0xF)
			textCommand="NoteOff:"
			arg1=midiFile[filePos]
			filePos+=1
			arg2=midiFile[filePos]
			filePos+=1
			if(noteLengthArg==False):
				if(delay>0):
					outfile.write("Delay:"+str(delay)+"\n")
					delay=0
				outfile.write(textCommand+str(arg1)+","+str(arg2)+"\n")
		elif((command&0xF0)==0x90):
			#note on
			if(trackNum!=str(command&0xF)):
				outfile.write("Track:"+str(command&0xF)+"\n")
			trackNum=str(command&0xF)
			textCommand="NoteOn:"
			arg1=midiFile[filePos]
			filePos+=1
			arg2=midiFile[filePos]
			filePos+=1
			if(noteLengthArg and arg2>0):
				noteLength=get_note_length(filePos,command&0xF,arg1)
				outfile.write(textCommand+str(arg1)+","+str(arg2)+","+str(noteLength)+"\n")
			else:
				outfile.write(textCommand+str(arg1)+","+str(arg2)+"\n")
		elif((command&0xF0)==0xA0):
			#key pressure
			if(trackNum!=str(command&0xF)):
				outfile.write("Track:"+str(command&0xF)+"\n")
			trackNum=str(command&0xF)
			textCommand="PolyPressure:"
			arg1=midiFile[filePos]
			filePos+=1
			arg2=midiFile[filePos]
			filePos+=1
			outfile.write(textCommand+str(arg1)+","+str(arg2)+"\n")
		elif((command&0xF0)==0xB0):
			#controller change
			if(trackNum!=str(command&0xF)):
				outfile.write("Track:"+str(command&0xF)+"\n")
			trackNum=str(command&0xF)
			arg1=midiFile[filePos]
			filePos+=1
			arg2=midiFile[filePos]
			filePos+=1
			outfile.write("Controller_"+str(arg1)+":"+str(arg2)+"\n")
		elif((command&0xF0)==0xC0):
			#program change
			if(trackNum!=str(command&0xF)):
				outfile.write("Track:"+str(command&0xF)+"\n")
			trackNum=str(command&0xF)
			textCommand="Instrument:"
			arg1=midiFile[filePos]
			filePos+=1
			outfile.write(textCommand+str(arg1)+"\n")
		elif((command&0xF0)==0xD0):
			#channel pressure
			if(trackNum!=str(command&0xF)):
				outfile.write("Track:"+str(command&0xF)+"\n")
			trackNum=str(command&0xF)
			textCommand="KeyPressure:"
			arg1=midiFile[filePos]
			filePos+=1
			outfile.write(textCommand+str(arg1)+"\n")
		elif((command&0xF0)==0xE0):
			#pitch bend
			if(trackNum!=str(command&0xF)):
				outfile.write("Track:"+str(command&0xF)+"\n")
			trackNum=str(command&0xF)
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
				trackNum=-1
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
elif(mode==2): #encode
	Done=False
	notesOn=[]
	lineNum=0
	infile=open(sysargv[infileArg], "r")
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
				
				if(len(notesOn)>0):
					notesToEnd=0
					for i in range(len(notesOn)):
						if(notesOn[i].length<=thisDelay): notesToEnd+=1
					for n in range(notesToEnd):
						soonestNote=0xFFFFFFF
						for i in range(len(notesOn)):
							if(notesOn[i].length<soonestNote):
								soonestNote=notesOn[i].length
								soonestNoteID=i
							elif(notesOn[i].length==soonestNote):
								if(notesOn[i].arg1<notesOn[soonestNoteID].arg1): soonestNoteID=i
						for i in range(len(notesOn)):
							notesOn[i].length-=soonestNote
						thisDelay-=soonestNote
						thisByte=[]
						length=0
						while(soonestNote>0):
							thisByte.append((soonestNote & 127))
							soonestNote-=thisByte[length]
							soonestNote=int(soonestNote/128)
							if(length>0): thisByte[length]+=128
							length+=1
						if(length==0): length=1
						if(len(thisByte)==0): thisByte.append(0)
						if(len(midiFile)<filePos+1): midiFile.append(0)
						midiFile[filePos]=thisByte[length-1]
						filePos+=1
						length-=1
						while(length>0):
							midiFile.append(thisByte[length-1])
							filePos+=1
							length-=1
						midiFile.append(0x80+notesOn[soonestNoteID].track)
						filePos+=1
						midiFile.append(notesOn[soonestNoteID].arg1)
						filePos+=1
						midiFile.append(notesOn[soonestNoteID].arg2)
						filePos+=1
						del notesOn[soonestNoteID]
						
				thisByte=[]
				length=0
				for i in range(len(notesOn)):
					notesOn[i].length-=thisDelay
				while(thisDelay>0):
					thisByte.append((thisDelay & 127))
					thisDelay-=thisByte[length]
					thisDelay=int(thisDelay/128)
					if(length>0): thisByte[length]+=128
					length+=1
				if(length==0): length=1
				if(len(thisByte)==0): thisByte.append(0)
				if(len(midiFile)<filePos+1): midiFile.append(0)
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
				if(len(argument)>2):
					notesOn.append(Note(trackNum,int(argument[0],10),int(argument[1],10),int(argument[2],10)))
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
	outfile=open(sysargv[outfileArg],"wb")
	for i in range(midiSize):
		outfile.write(midiFile[i].to_bytes(1,byteorder='little'))
	outfile.close()
elif(mode==3): #analyze
	infile=open(sysargv[infileArg], "rb")
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
	trackStart=[]
	trackPos=[]
	trackDelay=[]
	lastTrackCommand=[]
	trackEnd=True
	lastCommand=0
	filePos=16+headerSize #Skip 'MTrk' and tracksize
	trackNum=0
	#get the track start locations
	while(filePos<fileSize):
		if(trackEnd):
			trackStart.append(filePos)
			lastTrackCommand.append(0)
			trackDelay.append(0)#get the first delay value
			val=midiFile[filePos]
			filePos+=1
			if(val>0x7F):
				trackDelay[trackNum]+=(val&0x7F)
				trackDelay[trackNum]*=0x80
				val=midiFile[filePos]
				filePos+=1
				if(val>0x7F):
					trackDelay[trackNum]+=(val&0x7F)
					trackDelay[trackNum]*=0x80
					val=midiFile[filePos]
					filePos+=1
					if(val>0x7F):
						trackDelay[trackNum]+=(val&0x7F)
						trackDelay[trackNum]*=0x80
						val=midiFile[filePos]
						filePos+=1
			trackDelay[trackNum]+=(val&0x7F)
			trackPos.append(filePos)
			filePos=trackStart[trackNum]
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

		command=midiFile[filePos]
		filePos+=1
		textCommand=""
		if(command<0x80):
			command=lastCommand
			filePos-=1
		lastCommand=command
		if((command&0xF0)==0x80):
			#note off
			filePos+=2
		elif((command&0xF0)==0x90):
			#note on
			filePos+=2
		elif((command&0xF0)==0xA0):
			#key pressure
			filePos+=2
		elif((command&0xF0)==0xB0):
			#controller change
			filePos+=2
		elif((command&0xF0)==0xC0):
			#program change
			filePos+=1
		elif((command&0xF0)==0xD0):
			#channel pressure
			filePos+=1
		elif((command&0xF0)==0xE0):
			#pitch bend
			filePos+=2
		elif(command==0xF0 or command==0xF7):
			#sys-ex event
			arg1=midiFile[filePos]
			filePos+=arg1+1
		elif(command==0xFF):
			#meta event
			arg1=midiFile[filePos]
			filePos+=1
			if(arg1==0x2F):
				#end of track
				filePos+=9#skip next 'MTrk' and tracklength
				lastCommand=0
				trackEnd=True
				trackNum+=1
			else:
				arg1=midiFile[filePos]
				filePos+=arg1+1
				
	#simulate the midi
	polyphony=0
	maxPoly=0
	instUsed=[]
	for i in range(128): instUsed.append(False)
	numTracks=len(trackStart)
	tracksDone=0
	while(tracksDone<numTracks):
		for i in range(numTracks):
			if(trackPos[i]>0):
				trackDelay[i]-=1;
				while(trackDelay[i]<=0):
					command=midiFile[trackPos[i]]
					trackPos[i]+=1
					textCommand=""
					if(command<0x80):
						command=lastTrackCommand[i]
						trackPos[i]-=1
					lastTrackCommand[i]=command
					if((command&0xF0)==0x80):
						#note off
						if(polyphony>0): polyphony-=1
						trackPos[i]+=2
					elif((command&0xF0)==0x90):
						#note on
						arg1=midiFile[trackPos[i]]
						trackPos[i]+=1
						arg2=midiFile[trackPos[i]]
						trackPos[i]+=1
						if(arg2==0):
							if(polyphony>0): polyphony-=1#velocity of 0 is the same as note off
						else:
							polyphony+=1
					elif((command&0xF0)==0xA0):
						#key pressure
						trackPos[i]+=2
					elif((command&0xF0)==0xB0):
						#controller change
						trackPos[i]+=2
					elif((command&0xF0)==0xC0):
						#program change
						arg1=midiFile[trackPos[i]]
						instUsed[arg1]=True
						trackPos[i]+=1
					elif((command&0xF0)==0xD0):
						#channel pressure
						trackPos[i]+=1
					elif((command&0xF0)==0xE0):
						#pitch bend
						trackPos[i]+=2
					elif(command==0xF0 or command==0xF7):
						#sys-ex event
						arg1=midiFile[trackPos[i]]
						trackPos[i]+=arg1+1
					elif(command==0xFF):
						#meta event
						arg1=midiFile[trackPos[i]]
						trackPos[i]+=1
						if(arg1==0x2F):
							#end of track
							trackPos[i]=0
							tracksDone+=1
							trackDelay[i]=0x0FFFFF
						else:
							arg1=midiFile[trackPos[i]]
							trackPos[i]+=arg1+1
					
					if(trackPos[i]>0):
						trackDelay[i]=0
						val=midiFile[trackPos[i]]
						trackPos[i]+=1
						if(val>0x7F):
							trackDelay[i]+=(val&0x7F)
							trackDelay[i]*=0x80
							val=midiFile[trackPos[i]]
							trackPos[i]+=1
							if(val>0x7F):
								trackDelay[i]+=(val&0x7F)
								trackDelay[i]*=0x80
								val=midiFile[trackPos[i]]
								trackPos[i]+=1
								if(val>0x7F):
									trackDelay[i]+=(val&0x7F)
									trackDelay[i]*=0x80
									val=midiFile[trackPos[i]]
									trackPos[i]+=1
						trackDelay[i]+=(val&0x7F)
		if(polyphony>maxPoly): maxPoly=polyphony
	print("Max Polyphony: "+str(maxPoly)+"\n")
	print("Instruments Used: ")
	for i in range(128): 
		if(instUsed[i]): print(str(i)+", ")
