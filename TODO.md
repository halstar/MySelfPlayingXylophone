What could be done next, maybe in a V2?...

* Add some more code comments,
* Isolate console in its own module,
* Implement a commands history in console,
* Add some robustness around (e.g. in console),
* Replace polling by callbacks (e.g. in encoders/buttons),
* Integrate tools access in debug console, in order to have a single entry point?
* At startup, in main.sh or main.py, check whether an instance is already running,
* Make I2C, SPI, etc. classes more generic, so that they could easily be reused by other projects,
* Add embedded metronome capability, with a loudspeaker or a buzzer, and an ON/OFF button on display?
* Add a file preview capability, with an amplifier, a loudspeaker & another rotary button to adjust volume?
* Find a way to implement musical nuances and/or a general playing volume level; hardware changes needed (PWMs?). 
