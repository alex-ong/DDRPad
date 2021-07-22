Arduino Libraries
===

Requires installing `joystick.h` and `EEPROMex.h`

Look inside `libraries` folder.

You'll need to install `Arduino Studio 1.8.x`

Code is tested and working on an Arduino Pro Micro, 5V 16Mhz.
I had to download the sparkfun pro micro drivers to get it to work.

GUI
===
If you have python, you can set the debounce/sensitivity values via a gui.
Note that once you write the values in the gui, it saves it to the Arduino's EEPROM (long term memory).
This means you must use the gui from then on to set debounce and sensitivities.

![](https://raw.githubusercontent.com/alex-ong/DDRPad/master/code/serial_monitor/docs/gui-example.png)