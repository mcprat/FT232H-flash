import board as FTDI
import busio as Serial
import digitalio as GPIO
import time


# Variables

CS_pin = FTDI.D7

baudrate = 10000000


# Constants

command = 0x9f

length = 8


# instantiation, unlock and configure pin and frequency

response = [0] * length

FT232H = Serial.SPI(FTDI.SCLK, FTDI.MOSI, FTDI.MISO)

CS = GPIO.DigitalInOut(CS_pin)
CS.direction = GPIO.Direction.OUTPUT

while not FT232H.try_lock(): pass

FT232H.configure(baudrate)


# main

CS.value = False

FT232H.write_readinto([command], response)

CS.value = True


time.sleep(0.1)
FT232H.unlock()


for i in range(length):
    response[i] = hex(response[i])

print(response)
