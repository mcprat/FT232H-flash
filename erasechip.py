import board as FTDI
import busio as Serial
import digitalio as GPIO
import time



# Variables

erase_type = 'chip'

block_start = 50

numblocks = 5

sector_start = 50

numsectors = 50



# Configuration

CS_pin = FTDI.D7

baudrate = 40000000



# Constants

chip = 0xc7

block = 0xd8

sector = 0x20

disable = 0x04

status = 0x05

enable = 0x06

page_start = 0x00

page_offset = 0x00

lenpages = numpages = 0x100

block_sectors = 0x10

s_write = 0.005

s_latch = 0.015



# instantiation, lock board for use, configure frequency, set CS pin

FT232H = Serial.SPI(FTDI.SCLK, FTDI.MOSI, FTDI.MISO)

while not FT232H.try_lock(): pass

FT232H.configure(baudrate)

CS = GPIO.DigitalInOut(CS_pin)
CS.direction = GPIO.Direction.OUTPUT

response = [0]
erasenum = 0
busy = 0




# main



if erase_type == 'chip':
    command = chip
    if input(''.join(['will erase entire chip',
            '...continue? (y/n):  '])) != 'y':
        quit()
    block_start = sector_start = 0
    block_sectors = last_sectors = numsectors = numblocks = 1
elif erase_type == 'block':
    command = block
    if input(''.join(['will erase ', str(numblocks), ' block(s) ',
            'starting at block ', str(block_start), ' sector 0',
            '...continue? (y/n):  '])) != 'y':
        quit()
    sector_start = 0
    block_sectors = last_sectors = numsectors = 1
elif erase_type == 'sector':
    command = sector
    if sector_start >= block_sectors:
        block_start += sector_start // block_sectors
        sector_start = sector_start % block_sectors
    if input(''.join(['will erase ', str(numsectors), ' sector(s) ',
            'starting at block ', str(block_start), ' sector ',
            str(sector_start), '...continue? (y/n):  '])) != 'y':
        quit()
    if ((sector_start + numsectors) > block_sectors):
        numblocks = ((sector_start + numsectors) // block_sectors) + 1
        last_sectors = ((numsectors % block_sectors) + (block_sectors - (block_sectors - sector_start))) % block_sectors
    else:
        numblocks = 1
        last_sectors = numsectors
    numsectors = block_sectors - sector_start
else:
    print('check variables and try again')
    quit()






# erase cycle

for blocknum in range(numblocks):


    if blocknum > 0:
        numsectors = block_sectors

    if (numblocks - blocknum == 1):
        numsectors = last_sectors

    for sectornum in range(numsectors):


        block = block_start + blocknum

        if blocknum == 0:
            sector = (sector_start + sectornum) * block_sectors
        else:
            sector = sectornum * block_sectors

        instruction = [command, block, sector, page_offset]


        # write enable

        CS.value = False

        FT232H.write([enable])

        CS.value = True

        time.sleep(s_latch)


        # erase

        if erase_type != 'chip':
            print('erasing:', hex(block), format(sector, 'x'), format(page_offset, 'x'))
        else:
            instruction = [chip]
            print('erasing whole chip...')

        print(instruction)

        CS.value = False

        FT232H.write(instruction)

        CS.value = True

        time.sleep(s_write)

        erasenum += 1



        # check status

        CS.value = False

        FT232H.write([status])
        FT232H.readinto(response)

        CS.value = True

        time.sleep(s_latch)

        busy = sum(response)

        while busy % 2 != 0:

            print('erasing...')

            response = [0]

            CS.value = False

            FT232H.write([status])
            FT232H.readinto(response)

            CS.value = True

            time.sleep(1)

            busy = sum(response)

            response[0] = hex(response[0])

            print('status register 1 : ', response)
            print('status register 1 sum : ', busy)




# write disable

time.sleep(s_latch)

CS.value = False

FT232H.write([disable])

CS.value = True



# read status register

time.sleep(s_latch)

CS.value = False

FT232H.write([status])
FT232H.readinto(response)

CS.value = True

time.sleep(s_latch)


busy = sum(response)

response[0] = hex(response[0])

print('\n\nfinal status:\n')

print('status register 1 : ', response)
print('status register 1 sum : ', busy)

print('\nerased', erasenum, erase_type, '(s)')


# Close

FT232H.unlock()
print('DONE')