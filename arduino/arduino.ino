#include <Wire.h>
#include <UnoWiFiDevEd.h>

const int ledPin = 13;


void setup() {
    pinMode(ledPin, OUTPUT);

    Wifi.begin();
    Wifi.println("REST Server is up");
}


void loop() 
{


    // IF BUTTON IS PRESSED OR MOVEMENT IS DETECED 
    if (true)
    {
      
    }
    if(Wifi.available())
    {
      process(Wifi);
    }
  delay(50);

}

void process(WifiData client) {
  // read the command
  String command = client.readStringUntil('\r');

  // identify the command
  if (command == "turnLightOn")
  {
      digitalWrite(ledPin, HIGH); // Turn the LED on
  }
  else if (command =="turnLightOff")
  {
      digitalWrite(ledPin, LOW); // Turn the LED off
  }
}
