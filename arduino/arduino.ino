#include <WiFi.h>
#include <SPI.h>

char ssid[] = "Wifi-Cima";     //  your network SSID (name)
char pass[] = "letbren3";    // your network password
int keyIndex = 0;            // your network key Index number (needed only for WEP)
const int ledPin = 13;
int status = WL_IDLE_STATUS;
// if you don't want to use DNS (and reduce your sketch size)
// use the numeric IP instead of the name for the server:
WiFiServer server(80);
IPAddress comm(74,125,232,128);  // numeric IP for Google (no DNS)
const char* hostname = "my-arduino"; // Change this to your desired hostname



WiFiClient client;
WiFiClient client_server;

#include <UnoWiFiDevEd.h>


void setup() 
{

  pinMode(ledPin, OUTPUT);

  digitalWrite(ledPin, LOW); // Turn the LED off


  //Initialize serial and wait for port to open:

  Serial.begin(9600);

  while (!Serial) {

    ; // wait for serial port to connect. Needed for native USB port only

  }

  // attempt to connect to Wifi network:

  while (status != WL_CONNECTED) {

    Serial.print("Attempting to connect to SSID: ");

    Serial.println(ssid);

    // Connect to WPA/WPA2 network. Change this line if using open or WEP network:

    status = WiFi.begin(ssid, pass);

    // wait 10 seconds for connection:

    delay(10000);

  }

  Serial.println("Connected to wifi");

  printWifiStatus();

  server.begin();

  Serial.println("\nStarting connection to server...");

 // Print IP address to serial monitor
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
 
}
void loop() 
{


    

    // IF BUTTON IS PRESSED OR MOVEMENT IS DETECED 
    if (false)
    {
      sendMessage();
    }
    
    client_server = server.available();
    
    if(client_server) {
        Serial.println("New client connected");
        String request = client_server.readStringUntil('\r');
        Serial.println("Request: " + request);
        process(request);
        client_server.stop(); 
    }
  delay(50);

}

void process(String command) {

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

void sendMessage()
{
  if (client.connect(comm, 80)) 
  {

    Serial.println("connected to server");

    // Make a HTTP request:

    client.println("GET /search?q=arduino HTTP/1.1");

    client.println("Host: www.google.com");

    client.println("Connection: close");

    client.println();
    
    client.stop();

  }
}



void printWifiStatus() {

  // print the SSID of the network you're attached to:

  Serial.print("SSID: ");

  Serial.println(WiFi.SSID());

  // print your WiFi shield's IP address:

  IPAddress ip = WiFi.localIP();

  Serial.print("IP Address: ");

  Serial.println(ip);

  // print the received signal strength:

  long rssi = WiFi.RSSI();

  Serial.print("signal strength (RSSI):");

  Serial.print(rssi);

  Serial.println(" dBm");
}
