
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
	