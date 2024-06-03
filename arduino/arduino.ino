#include <WiFi.h>
#include <SPI.h>

#define BUTTON_PIN 2
char ssid[] = "Wifi-Cima";     // your network SSID (name)
char pass[] = "letbren3";      // your network password
const int ledPin = 9;
int status = WL_IDLE_STATUS;

// Use the numeric IP address instead of the name for the server
IPAddress serverIP(192, 168, 0, 125); // IP address for example.com
const int port = 3000; // HTTP por  t

WiFiServer server(80);
WiFiClient client;
WiFiClient client_server;

void setup() {
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW); // Turn the LED off
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  // Initialize serial and wait for port to open:
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }
  // Attempt to connect to WiFi network:
  while (status != WL_CONNECTED) {
    Serial.print("Attempting to connect to SSID: ");
    Serial.println(ssid);

    // Connect to WPA/WPA2 network. Change this line if using open or WEP network:
    status = WiFi.begin(ssid, pass);

    // Wait 10 seconds for connection:
    delay(5000);
  }


  Serial.println("Connected to wifi");
  printWifiStatus();

  server.begin();

  Serial.println("\nStarting connection to server...");

  // Print IP address to serial monitor
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

}

void loop() {

    Serial.println("Loop");


  if (digitalRead(BUTTON_PIN)) 
  {
  } else {
    Serial.println("Button Clicked");
    sendMessage();
  }  
  
  client_server = server.available();

  if (client_server) {
    Serial.println("New client connected");
    String request = client_server.readStringUntil('\r');
    Serial.println("Request: " + request);
    process(request);
    client_server.stop();
  }
  delay(50);
}

void process(String command) {
  // Identify the command
  if (command == "turnLightOn") {
    digitalWrite(ledPin, HIGH); // Turn the LED on
  } else if (command == "turnLightOff") {
    digitalWrite(ledPin, LOW); // Turn the LED off
  }
}

void sendMessage() {
  Serial.println("Sending Message");

  if (client.connect(serverIP, 3000)) {
    Serial.println("Connected to server");
    client.print("movementBell\n");
    client.stop();
    Serial.println("Message sent and client stopped");
  } else {
    Serial.println("Connection to server failed");
  }
}

void printWifiStatus() {
  // Print the SSID of the network you're attached to:
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // Print your WiFi shield's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // Print the received signal strength:
  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.print(rssi);
  Serial.println(" dBm");
}
