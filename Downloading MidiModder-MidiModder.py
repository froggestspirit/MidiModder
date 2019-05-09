
#single_byte = i.to_bytes(1, byteorder='big', signed=True)
#i = int.from_bytes(some_bytes, byteorder='big')
echo=True
infile=open("test.mid", "rb")
midiFile=infile.read()
infile.close()

fileSize=len(midiFile)
numTracks=midiFile[11]+(midiFile[10]*256)
timeDivision=midiFile[13]+(midiFile[12]*256)
if(echo): print("File Size: "+str(fileSize))
if(echo): print("Number of Tracks: "+str(numTracks))
if(echo): print("Time Division: "+str(timeDivision))

outfile=open("test.txt",w)
filePos=18 #Skip 'Mtrk'
while(filePos<fileSize):
	delay=0
	val=midiFile[filePos]
	filePos+=1
	if(val>0x7F):
		delay+=(aaa&0x7F)
		delay*=0x80
		val=midiFile[filePos]
		filePos+=1
		if(val>0x7F):
			delay+=(aaa&0x7F)
			delay*=0x80
			val=midiFile[filePos]
			filePos+=1
			if(val>0x7F):
				delay+=(aaa&0x7F)
				delay*=0x80
				val=midiFile[filePos]
				filePos+=1
	delay+=(aaa&0x7F)
	
	command=midiFile[filePos]
	filePos+=1
	textCommand=""
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
		command=midiFile[filePos]
		filePos+=1
		#command=controller	
		filePos+=1
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
	elif(command==0xF0 || command==0xF7):
		#sys-ex event
		textCommand="SysEvent:"
		command=midiFile[filePos]
		outfile.write(textCommand)
		for(i=0; i<command; i+=1):
			arg1=midiFile[filePos]
			filePos+=1
			if(i<command-1): outfile.write(str(arg1)+",")	
			if(i==command-1): outfile.write(str(arg1))	
		outfile.write("\n")		
	elif(command==0xF0 || command==0xF7):
		#meta event
		textCommand="MetaEvent:"
		command=midiFile[filePos]
		filePos+=1
		if(command==0x2F):
			#end of track
			textCommand="EndTrack"
		command=midiFile[filePos]
		filePos+=(command+1)

outfile.close()