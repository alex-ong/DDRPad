#include <Joystick.h>

//This is the LED pin for a Teensy LC, may need to change on other boards
const int LED_PIN = 17;
//The analog threshold value for triggering a button

unsigned long time_now = 0;

//todo: set these pins
const int LEFT = 18;
const int DOWN = 19;
const int RIGHT = 20;
const int UP = 21;
const unsigned long DEBOUNCE_TIME[] = { 5000, 5000, 5000, 5000};  //5000 = 5ms, 50000 = 50ms
bool filtered[4] = {false, false, false, false};
long unsigned int debounce_timer[4] = {0}; //last change to output

void setup() {
 
  Serial.begin(9600);
  pinMode(LED_PIN, OUTPUT);
 
  //The analog pins are configured with internal pull-up resistors, which makes for a very simple circuit
  //However this method does not support useful pressure sensitivity adjustments
  //By soldering 1K resistors as pull-ups on the board, you can make the buttons require more pressure
  //The first version did that, but making the buttons more difficult didn't seem very desirable
  pinMode(LEFT, INPUT);
  pinMode(DOWN, INPUT);
  pinMode(RIGHT, INPUT);
  pinMode(UP, INPUT);  
  Joystick.begin(false); 
}

void loop() {
  //pin mappings for where things got soldered
  //left, down, right, up
  int p[4] = {LEFT,DOWN,RIGHT,UP};
  int t[4] = {800,350,550,775};
  //analog read values
  int a[4] = {0,0,0,0}; 
  
  //check if any buttons are pressed, so we know whether to light the LED
  bool pressed = false;
  
  //read each pin, and set that Joystick button appropriately
  for(int i = 0; i < 4; ++i)
  {
    a[i] = analogRead(p[i]);
    bool newValue = a[i] < t[i];
    bool oldValue = filtered[i];
    bool timerValid = (time_now - debounce_timer[i]) >= DEBOUNCE_TIME[i];
    
    if (timerValid && newValue != oldValue)
    {
        if (newValue) {          
            Joystick.pressButton(i);          
            filtered[i] = true;
            debounce_timer[i] = time_now;
        } else if (!newValue) {
            Joystick.releaseButton(i);
            filtered[i] = false;
            debounce_timer[i] = time_now;
        }
    }
    
    
    if (filtered[i])
    {
        pressed = true;
    }
  }
 
  //Illuminate the LED if a button is pressed
  if(pressed) {
    digitalWrite(LED_PIN, LOW);
    TXLED1;
  }
  else {
    digitalWrite(LED_PIN, HIGH);
    TXLED0;
  }
 
  //Enable this block if you need to debug the electricals of the pad
  if(0)
  {
    char buffer [128]; // must be large enough for your whole string!
    sprintf (buffer, "Pins: %d,%d,%d,%d", a[0],a[1],a[2],a[3]);
    Serial.println (buffer);    
    delay(100);
  }
  
  Joystick.sendState();
  
  //busy wait version of delay. More accurate 
  while (micros() - time_now < 1000) {}
  time_now = micros();

  
}
