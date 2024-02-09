def find_ff_blocks(filename):
    with open(filename, 'rb') as file:
        data = file.read()  # Read the entire file into memory

    blocks = []
    block_start = None

    for i in range(len(data)):
        # Check if we are at the start of a 0xFF block
        if data[i] == 0xFF:
            if block_start is None:  # Mark the beginning of a new block
                block_start = i
            # If this is the last byte in the file and it's part of a block, close the block
            if i == len(data) - 1 and block_start is not None and (i - block_start) >= 3:
                blocks.append((block_start, i))
        else:
            # If we have left a block of 0xFF and it's at least 4 bytes long, record it
            if block_start is not None and (i - block_start) >= 4:
                blocks.append((block_start, i - 1))
            block_start = None  # Reset block start since we're no longer in a 0xFF block

    return blocks

# Replace 'memdump.bin' with your filename if different
filename = r'rp2040\flash\memdump.bin'
ff_blocks = find_ff_blocks(filename)

for start, end in ff_blocks:
    if end - start + 1 > 16:
        print(f"0xFF block from {start} to {end} (size: {end - start + 1} bytes)")
