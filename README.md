# Python scripts to use FT232H with SPI NOR flash chips


## Introduction

Each script has a "Variables" block where the offset / block is selected

Each script has a "Constants" block where SPI commands and reused variables are set
 - by default the SPI commands are good for most chips, 

* **chip.py** --------	read ID and status registers
* **erasechip.py** ---	erase by sector / block / whole chip
* **readchip.py** ----	read any sector / block range
* **writechip.py** ---	write any sector / block range


## Dependencies

 * Python 3.x
 * [pyftdi](https://pypi.org/project/pyftdi/)
 * [Adafruit Blinka](https://pypi.org/project/Adafruit-Blinka/)


## Future development

Pull requests are welcome

Eventually make this into a python console program...
