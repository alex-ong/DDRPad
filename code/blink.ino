#include <Joystick.h>

//This is the LED pin for a Teensy LC, may need to change on other boards
const int LedPin = 17;
//The analog threshold value for triggering a button
const int TriggerThreshold = 500;
unsigned long time_now = 0;
 
void setup() {
 
  Serial.begin(9600);
  pinMode(LedPin, OUTPUT);
 
  //The analog pins are configured with internal pull-up resistors, which makes for a very simple circuit
  //However this method does not support useful pressure sensitivity adjustments
  //By soldering 1K resistors as pull-ups on the board, you can make the buttons require more pressure
  //The first version did that, but making the buttons more difficult didn't seem very desirable
  pinMode(18, INPUT);
  pinMode(19, INPUT);
  pinMode(20, INPUT);
  pinMode(21, INPUT);  
  Joystick.begin(false); 
}

void loop() {
  //pin mappings for where things got soldered
  int p[4] = {18, 19, 20, 21};
  int t[4] = {500,500,500,500};
  //analog read values
  int a[4] = {0};
  //check if any buttons are pressed, so we know whether to light the LED
  bool pressed = false;
    
  //read each pin, and set that Joystick button appropriately
  for(int i = 0; i < 4; ++i)
  {
    a[i] = analogRead(p[i]);
    if(a[i] < t[i])
    {
      pressed = true;
      Joystick.pressButton(i);
      //Joystick.setButton(i, 1);
    }
    else
    {
      Joystick.releaseButton(i);
      //Joystick.button(i, 0);
    }
  }
 
  //Illuminate the LED if a button is pressed
  if(pressed) {
    digitalWrite(LedPin, LOW);
    TXLED1;
  }
  else {
    digitalWrite(LedPin, HIGH);
    TXLED0;
  }
 
  //Enable this block if you need to debug the electricals of the pad
  if(0)
  {
    char buffer [128]; // must be large enough for your whole string!
    sprintf (buffer, "Pins: %d,%d,%d,%d", a[0],a[1],a[2],a[3]);
    Serial.println (buffer);    
    delay(250);
  }
  
  delayMicroseconds(1); //limits the pad to run at 1000hz
  //This limits the pad to run at 200 Hz. This version of the code does not debounce.
  Joystick.sendState();
  while (micros() - time_now < 1000) {}
  time_now = micros();
}
