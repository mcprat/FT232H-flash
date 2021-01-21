import board as FTDI
import busio as Serial
import digitalio as GPIO
#import time



# Variables

block_start = 0

numblocks = 256

sector_start = 0

#numsectors = 16



# Configuration

CS_pin = FTDI.D7

baudrate = 40000000



# Constants

read = 0x03

sector_length = 0x1000

block_sectors = 0x10

sector_pages = 0x10

page_start = 0x00

cell = 0x00



# instantiation, lock board for use, configure frequency, set CS pin

FT232H = Serial.SPI(FTDI.SCLK, FTDI.MOSI, FTDI.MISO)

while not FT232H.try_lock(): pass

FT232H.configure(baudrate)

CS = GPIO.DigitalInOut(CS_pin)
CS.direction = GPIO.Direction.OUTPUT

response = [0] * sector_length
payload = bytearray()
numreads = 0



# main


# handle variable range, set relative variables

block_start += sector_start // block_sectors
block_start_print = block_start
sector_start_print = sector_start = sector_start % block_sectors

if 'numsectors' not in locals():
    numsectors = block_sectors

if numsectors != block_sectors:
    numblocks = (sector_start + numsectors) // block_sectors + 1

# check existance

try:
    check = open('response.bin', 'r+b')
    check.close()
    print('Careful! response.bin already exists, rename it!! \n\n')
    quit()
except:
    pass

# open for read

dump = open('response.bin', 'a+b')

# read cycle

for blocknum in range(numblocks):

    if (numblocks > 1) & (numblocks - 1 == blocknum) & (numsectors != block_sectors) & (sector_start != 0):
        numsectors = (sector_end + numsectors) % block_sectors

    for sectornum in range(numsectors):

        block = block_start + blocknum
        sector = sector_start + sectornum
        page = page_start + (sector * sector_pages)

        if sector == block_sectors:
            if blocknum == 0:
                sector_end = sector_start
            sector_start = 0
            break

        instruction = [read, block, page, cell]

        print('reading block', block, 'sector', sector)
        numreads += 1

        CS.value = False

        FT232H.write(instruction)
        FT232H.readinto(response)

        CS.value = True

        #time.sleep(0.1)

        # write payload to file

        for i in range(sector_length):
            payload.extend(bytes([response[i]]))

        dump.write(payload)
        dump.flush()

        # clear buffers

        response = [0] * sector_length
        payload = bytearray()

        #time.sleep(0.1)



# Close

dump.close()
FT232H.unlock()

print('DONE')
print('read', numreads, 'sectors starting at block', block_start_print, 'sector', sector_start_print)