=> Add couple more commands in console,
=> Finalize welcome screen & welcome music

=> Display: add like scroll bar arrows in track selection part?
=> Display: add play/pause status indicator?
=> Add embedded metronome capability, with a loudspeaker, ON/OFF button on display? 

List of track that could be included:

=> Velvet Underground / Sunday morning
=> Bach / Ode à la joie
=> Ravel / Bolero
=> French Cancan 
=> Greenleaves
=> Jingle bells
=> Silent night
=> We wish you a merry christmas
=> Twinkle, twinkle, little star
=> Tracks from studies piano book

What could be done next?...

* Add some code comments,
* Add some robustness around,
* Isolate console in its own module,
* Implement a commands history in debug console,
* Replace polling by callbacks (e.g. in encoders/buttons),
* Integrate tools access in debug console, in order to have a single entry point?
* Make I2C, SPI, etc. classes more generic, so that they could easily be reused by other projects.

