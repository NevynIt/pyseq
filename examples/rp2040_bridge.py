import asyncio
import serial_asyncio

# Function to send data when 's' is pressed
async def send_on_keypress(writer):
    while True:
        key = await asyncio.get_event_loop().run_in_executor(None, input, "")
        if key == 's':
            print("Sending data...")
            writer.write(b'\xC0\xEE\x00\x00')  # Send 0xC0 0xEE 0x00 0x00
            await writer.drain()
            print('sent')

# Function to continuously read and display incoming serial data as hex
async def read_serial_data(reader):
    while True:
        data = await reader.read(100)  # Read up to 100 bytes
        if data:
            hex_string = ' '.join(f'{byte:02x}' for byte in data)
            print(hex_string)

async def main():
    # Setup serial connection
    reader, writer = await serial_asyncio.open_serial_connection(url='COM3', baudrate=230400)
    
    # Run both tasks concurrently
    await asyncio.gather(
        read_serial_data(reader),
        send_on_keypress(writer),
    )

# Run the main coroutine
asyncio.run(main())
