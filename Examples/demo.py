from ImageStore import ImageStore

input = [range(0, 30), "this is text"]

ImageStore().write( input ) #Very fast but doesn't look nice
ImageStore( "C:/Test.png" ).write( input, customURL = "http://images.peterhuntvfx.co.uk/music.jpg" ) #Slower but you can choose any image

storedData1 = ImageStore().read() #Read from where no name or path was input
storedData2 = ImageStore( "C:/test.png" ).read() #Read from C:/Test.png, no url needs to be given now

#Check output data is the same as what was input
print type( storedData1[0] )
#Result: <type 'list'>

print type( storedData1[1] )
#Result: <type 'str'>

print storedData1 == storedData2
#Result: True
