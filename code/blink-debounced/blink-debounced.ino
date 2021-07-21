#include <Joystick.h>
#include <EEPROM.h>

//This is the LED pin for a Teensy LC, may need to change on other boards
const int LED_PIN = 17;
//The analog threshold value for triggering a button

unsigned long time_now = 0;

//todo: set these pins
const int LEFT = 18;
const int DOWN = 19;
const int UP = 21;
const int RIGHT = 20;

const unsigned long DEBOUNCE_TIME[] = { 5000, 5000, 5000, 5000};  //5000 = 5ms, 50000 = 50ms
int pins[4] = {LEFT,DOWN,UP,RIGHT};
int sens[4] = {800, 350, 775, 550}; //sensitivity. Below = trigger.
bool filtered[4] = {false, false, false, false};
long unsigned int debounce_timer[4] = {0}; //last change to output
bool DEBUG = false;

void writeIntIntoEEPROM(int address, int number)
{ 
  byte byte1 = number >> 8;
  byte byte2 = number & 0xFF;
  EEPROM.write(address, byte1);
  EEPROM.write(address + 1, byte2);
}

int readIntFromEEPROM(int address)
{
  byte byte1 = EEPROM.read(address);
  byte byte2 = EEPROM.read(address + 1);
  return (byte1 << 8) + byte2;
}

void WriteConfigIntoEEPROM()
{
    for (int i = 0; i < 4; i++) {
        writeIntIntoEEPROM(i*sizeof(int), sens[i]);
    }
}

void ReadConfigFromEEPROM()
{
    for (int i = 0; i < 4; i++) {
        int before = sens[i];
        sens[i] = readIntFromEEPROM(i*sizeof(int));
        if (sens[i] == ((255 << 8) + 255))
        {
            sens[i] = before;
        }
    }    
}


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
  ReadConfigFromEEPROM();
  Joystick.begin(false); 
}


void loop() {

  //analog read values
  int a[4] = {0,0,0,0}; 
  
  //check if any buttons are pressed, so we know whether to light the LED
  bool pressed = false;
  
  //read each pin, and set that Joystick button appropriately
  for(int i = 0; i < 4; ++i)
  {
    a[i] = analogRead(pins[i]);
    bool newValue = a[i] < sens[i];
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
  if(DEBUG)
  {
    char buffer [64]; // must be large enough for your whole string!
    sprintf (buffer, "Pins: %d,%d,%d,%d\n", a[0],a[1],a[2],a[3]);
    Serial.println (buffer);
    sprintf (buffer, "Sens: %d,%d,%d,%d\n", sens[0],sens[1],sens[2],sens[3]);
    Serial.println (buffer);    
    delay(10);
  }
  
  if (Serial.available() >= 1)
  {
      int messageType = Serial.read();
      if (messageType == 1)
      {
          DEBUG = true;
      } 
      else if (messageType == 2)
      {
          DEBUG = false;
      } 
      else if (messageType == 3)
      {
          ReadConfigFromSerial();
          WriteConfigIntoEEPROM();              
      }
  }
  
  Joystick.sendState();
  
  //busy wait version of delay. More accurate 
  while (micros() - time_now < 1000) {}
  time_now = micros();

  
}

void ReadConfigFromSerial()
{
    for (int i = 0; i < 4; i++)
    { 
        int v1 = Serial.read();
        int v2 = Serial.read();
        int value = (v1 << 8) + v2;
        sens[i] = value;
    }
}
