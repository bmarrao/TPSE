#include <WiFi.h>
#include <SPI.h>

#define BUTTON_PIN 2
char ssid[] = "S23_Ultra_Network";     // network SSID (name)
char pass[] = "podesaceder8888";      // network password
const int ledPin = 9;
int status = WL_IDLE_STATUS;

IPAddress serverIP(192, 168, 148, 231); // IP address for raspberry
const int port = 8888; // HTTP por  t

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

  //Test if button has been pressed
  if (digitalRead(BUTTON_PIN)) 
  {
  } else {
    // If it has send message to server 
    Serial.println("Button Clicked");
    sendMessageToServer();
    delay(500);
  }  

  // Listen to requests
  client_server = server.available();

  // Test if new connection was made
  if (client_server) {
    // Process request received
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

void sendMessageToServer() {
  Serial.println("Sending Message");


  if (client.connect(serverIP, port)) {
    Serial.println("Connected to server");
    digitalWrite(ledPin, HIGH); // Turn the LED off

    // Send HTTP GET request
    client.println("GET /api/bell HTTP/1.1");
    client.println("Host: 192.168.148.231");
    client.println("Connection: close");
    client.println();
    delay(100); 
    while (client.available()) {

    char c = client.read();

    Serial.write(c);

    }

    // Wait for the client to send its message
    while(client.connected())
    {
      Serial.println("Client Still connected");

    }
    Serial.println();

    Serial.println("disconnecting from server.");
    // When client finised close communication chanels
    client.stop();
    digitalWrite(ledPin, LOW); // Turn the LED off

    Serial.println("HTTP request sent and client stopped");    
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