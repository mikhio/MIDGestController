import serial

ser = serial.Serial('/dev/cu.wchusbserial14110', 115200)
print(ser.name)
while True:
	print(str(ser.readline())[2:-5])
	# print(str(ser.readline())[2:-5].split(' '))
ser.close() 

