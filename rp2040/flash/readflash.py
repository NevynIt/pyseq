import serial
import time

# Open serial port with a 1-second timeout to detect end of data transmission
ser = serial.Serial('COM5', 2000000, timeout=1)

# Wait for 1 second to ensure the connection is established
time.sleep(1)

print("Data reception start.")
ser.write(b'dump\n')

i=0
# Open a file to save the incoming data
with open(r'rp2040\flash\memdump.bin', 'wb') as file:
    while True:
        data = ser.read(512)  # Read data in chunks; adjust the chunk size if necessary
        if not data:
            # If no data is received for more than the timeout period, break the loop
            break
        file.write(data)
        i=i+1
        if i % 1000 == 0:
            print(".",end='')

# Close the serial connection
ser.close()

print("\nData reception completed, file 'memdump.bin' is saved.")
