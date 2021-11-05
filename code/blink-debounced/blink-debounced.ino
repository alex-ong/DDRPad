#include <Joystick.h>
#include <EEPROMex.h>

#ifndef cbi
  #define cbi(sfr, bit) (_SFR_BYTE(sfr) &= ~_BV(bit))
#endif
#ifndef sbi
  #define sbi(sfr, bit) (_SFR_BYTE(sfr) |= _BV(bit))
#endif

void SetFastADC()
{

    // set prescale to 16. s == 1, x ==0 from prescale table.
    // 16 == 78000 hz, default is 128 which is 9600hz
    // https://github.com/teejusb/fsr/issues/26
    sbi(ADCSRA,ADPS2) ;
    cbi(ADCSRA,ADPS1) ;
    cbi(ADCSRA,ADPS0) ;

}

//This is the LED pin for a Teensy LC, may need to change on other boards
const int LED_PIN = 17;
//The analog threshold value for triggering a button

unsigned long time_now = 0;

//todo: set these pins
const int LEFT = 18;
const int DOWN = 19;
const int UP = 21;
const int RIGHT = 10;

unsigned long DEBOUNCE_TIME[] = { 5000, 5000, 5000, 5000};  //5000 = 5ms, 50000 = 50ms
int pins[4] = {LEFT,DOWN,UP,RIGHT};
int sens[4] = {800, 350, 775, 550}; //sensitivity. Below = trigger.
bool filtered[4] = {false, false, false, false};
long unsigned int debounce_timer[4] = {0}; //last change to output
bool DEBUG = false;

const int SENS_OFFSET_EEPROM = 0;
const int DEBOUNCE_OFFSET_EEPROM = sizeof(int)*4;


void WriteIntsToEEPROM(int offset, int target[])
{
    for (int i = 0; i < 4; i++) {
        EEPROM.updateInt(offset + i*sizeof(int), target[i]);
    }
}

void ReadIntsFromEEPROM(int offset, int target[])
{
    for (int i = 0; i < 4; i++) {
        uint16_t value = EEPROM.readInt(offset + i*sizeof(int));
        if (value != 0xFFFF)
        {
            target[i] = (int)value;
        }
    }    
}

void ReadLongsFromEEPROM(int offset, int target[])
{
  for (int i = 0; i < 4; i++)
  {    
    uint32_t value = EEPROM.readLong(offset + i*sizeof(long));
    if (value != 0xFFFFFFFF)
    {
      target[i] = (long)value;
    }
  }
}

void WriteLongsToEEPROM(int offset, unsigned long target[])
{
  for (int i = 0; i < 4; i++)
  {
    EEPROM.updateLong(offset + i*sizeof(long), target[i]);
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
  SetFastADC();
  ReadIntsFromEEPROM(SENS_OFFSET_EEPROM, sens);
  //todo: implement.
  //ReadConfigFromEEPROM(DEBOUNCE_OFFSET_EEPROM, DEBOUNCE_TIME);
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
    int value = analogRead(pins[i]);
    if (value >= 1023 || value <= 100) value = filtered[i]; //use old value on error.
    a[i] = value;
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
    char buffer [128]; // must be large enough for your whole string!
    sprintf (buffer, "Pins: %d,%d,%d,%d\n", a[0],a[1],a[2],a[3]);
    Serial.println (buffer);
    sprintf (buffer, "Sens: %d,%d,%d,%d\n", sens[0],sens[1],sens[2],sens[3]);
    Serial.println (buffer);    
    sprintf (buffer, "Debounce: %lu,%lu,%lu,%lu\n", DEBOUNCE_TIME[0], DEBOUNCE_TIME[1], DEBOUNCE_TIME[2], DEBOUNCE_TIME[3]);
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
          ReadIntsFromSerial(sens);
          WriteIntsToEEPROM(SENS_OFFSET_EEPROM, sens);              
      }
      else if (messageType == 4)
      {
          
          ReadLongsFromSerial(DEBOUNCE_TIME);
          WriteLongsToEEPROM(DEBOUNCE_OFFSET_EEPROM, DEBOUNCE_TIME);              
      }
  }
  
  Joystick.sendState();
  
  //busy wait version of delay. More accurate 
  while (micros() - time_now < 1000) {}
  time_now = micros();

  
}

void ReadIntsFromSerial(int target[])
{
    for (int i = 0; i < 4; i++)
    { 
        int v1 = Serial.read();
        int v2 = Serial.read();
        int value = (v1 << 8) + v2;
        target[i] = value;
    }
}

void ReadLongsFromSerial(unsigned long target[])
{
    for (int i = 0; i < 4; i++)
    {
        long v1 = Serial.read();
        long v2 = Serial.read();
        long v3 = Serial.read();
        long v4 = Serial.read();
        long value = (v1 << 24) + (v2 << 16) + (v3 << 8) + v4;
        if (value > 100000){
          value = 100000; //100ms
        }
        target[i] = value;
    }
}
