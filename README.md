# MySelfPlayingXylophone

A homemade self-playing xylophone (actually a glockenspiel) built on a Raspberry Pi 0 WH basis.

This repository gathers sources Python scripts to be executed on the Raspberry Pi.

You can see the result at work with this playlist:

https://www.youtube.com/playlist?list=PLDA98d1k4czCSmF_95BBX-sHuxQW8t7GG

**How to setup the Raspberry Pi for this project**

* From a fresh install, update the whole Pi:

	* sudo apt-get update
	* sudo apt-get upgrade
	
* Enable SSH, SPI & I2C interfaces:

    * sudo raspi-config
    * > 3 Interface Options
    * > P2 SSH > Yes
    * > P4 SPI > Yes
    * > P5 I2C > Yes
	* sudo reboot

* Disable Desktop environment:

    * sudo raspi-config
    * > 1 System Options
    * > S5 Boot / Auto Login
    * > B2 Console Autologin
   	* sudo reboot
	
* Install PIGPIO library for Python:

	sudo pip3 install pigpio

*  In case it's not already installed, install smbus2 I2C library for Python:

	sudo pip3 install smbus2

* Setup I2C bus to its maximum speed:
	
	* sudo vi /boot/config.txt
	*    dtparam=i2c_arm=on,i2c_arm_baudrate=400000 (modify the original line, that was 'dtparam=i2c_arm=on')  
	* sudo reboot

* Disable bluetooth (not needed):

    * sudo systemctl disable hciuart.service
    * sudo systemctl disable bluetooth.service
	* sudo vi /boot/config.txt (add the following line at the very bottom of the file)
    *    dtoverlay=disable-bt 
    * sudo reboot

* In case it's not already installed, install SPI library for Python:

    sudo pip3 install spidev

* In case it's not already installed, install Python Imaging Library (PIL-low):

    sudo pip3 install Pillow

* In case it's not already installed, install Numpy library for Python:
 
    * sudo pip3 install numpy

* Install mido MIDI library for Python:

    * sudo pip3 install mido

* Manually start PIGPIO daemon (add this to rc.local or .bashrc or other):

	* sudo pigpiod
	
**Note**:  so, pigpio is used for GPIO access. Though they are available/activable in this project, RPi.GPIO & gpiozero supports were only partially tested.

* Add xylophone's main script to the Raspberry Pi startup sequence:

    * sudo vim /etc/rc.local (add the following lines before final "exit 0" command)
    *   cd /home/pi/xylo
    *   sudo ./main.sh 2>&1 > /dev/null &
