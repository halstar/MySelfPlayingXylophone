# MySelfPlayingXylophone

A homemade ... built on a Raspberry Pi 3 B+ basis, with ...

This repository gathers sources Python scripts to be executed on the Raspberry Pi.

You can see the result at work with this video:

https://www.youtube.com/...

**How to setup the Raspberry Pi for this project**

* From a fresh install, update the whole Pi:

	* sudo apt-get update
	* sudo apt-get upgrade
	
* Enable I2C & SPI interfaces:

    * sudo raspi-config	
	
* Install PIGPIO library for Python:

	sudo pip3 install pigpio

*  In case it's not already installed, install smbus2 I2C library for Python:

	sudo pip3 install smbus2

* Setup I2C bus to its maximum speed:
	
	* sudo vi /boot/config.txt
	* dtparam=i2c_arm=on,i2c_arm_baudrate=4000000
	* sudo reboot

* In case it's not already installed, install SPI library for Python:

    sudo pip3 install spidev

* In case it's not already installed, install Python Imaging Library (PIL-low):

    sudo pip3 install Pillow

* In case it's not already installed, install Numpy library for Python:
 
    * sudo pip3 install numpy

* Install MidiFile library for Python:

    * sudo pip3 install MIDIFile

* Manually start PIGPIO daemon (add this to rc.local or .bashrc or other):

	* sudo pigpiod

**Note**:  so, pigpio is used for GPIO access. Though they are available/activable in this project, RPi.GPIO & gpiozero supports were only partially tested.