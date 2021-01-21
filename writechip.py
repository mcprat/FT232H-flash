import board as FTDI
import busio as Serial
import digitalio as GPIO
import time



# Variables

block_start = 0

numblocks = 256

page_start = 0x00

numpages = 0x100

data_file = 'urandom-16mb'



# Configuration

CS_pin = FTDI.D7

baudrate = 80000000



# Constants

program = 0x02

disable = 0x04

status = 0x05

enable = 0x06

page_offset = 0x00

lenpages = 0x100

s_write = 0.005

s_latch = 0.015



# instantiation, lock board for use, configure frequency, set CS pin

FT232H = Serial.SPI(FTDI.SCLK, FTDI.MOSI, FTDI.MISO)

while not FT232H.try_lock(): pass

FT232H.configure(baudrate)

CS = GPIO.DigitalInOut(CS_pin)
CS.direction = GPIO.Direction.OUTPUT

response = [0]
busy = 1

lastwrite = None



# main

if input(''.join(['will write "', data_file, '" starting at block ',
str(block_start), ' page ', str(page_start), '...continue? (y/n):  '])) != 'y':
    quit()

data = open(data_file, 'r+b')



# write loops

for blocknum in range(numblocks):

    if lastwrite == True:
        break

    for pagenum in range(numpages):


        # check BUSY

        while busy % 2 != 0:
            print('BUSY')

            response = [0]
            
            CS.value = False
            
            FT232H.write([status])
            FT232H.readinto(response)
            
            CS.value = True

            busy = response[0]


        # prepare payload

        payload = list(data.read(lenpages))

        # check for end of file

        if len(payload) == 0:
            lastwrite = True
            print('end of file reached!\n\n')
            break


        # write enable

        CS.value = False

        FT232H.write([enable])

        CS.value = True

        time.sleep(s_latch)


        # write cycle

        block = block_start + blocknum
        page = page_start + pagenum
        instruction = [program, block, page, page_offset, *payload]

        print('writing at:', hex(block), format(page, 'x'), format(page_offset, 'x'))

        CS.value = False

        FT232H.write(instruction)

        CS.value = True


        # check BUSY

        response = [0]
            
        CS.value = False
            
        FT232H.write([status])
        FT232H.readinto(response)
            
        CS.value = True

        busy = response[0]



# read status register

time.sleep(s_latch)

response = [0]

CS.value = False

FT232H.write([status])
FT232H.readinto(response)

CS.value = True

register_sum = response[0]

response[0] = hex(response[0])

print('status register 1:')
print(response)
print('\nstatus register 1 sum:')
print(register_sum)



# Close

FT232H.unlock()
data.close()

print('\n\n DONE')
