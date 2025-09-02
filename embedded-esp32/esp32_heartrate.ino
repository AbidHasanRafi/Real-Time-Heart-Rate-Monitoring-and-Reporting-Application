#include <Arduino.h>
#include "FS.h"
#include <LittleFS.h>
#include <WiFi.h>
#include <WebServer.h>
#include <Wire.h>
#include "MAX30105.h"
#include "heartRate.h"

// WiFi credentials
const char* ssid = "";
const char* password = "";

// Web server
WebServer server(80);

// MAX30105 sensor
MAX30105 particleSensor;

// Heart rate variables
const byte RATE_SIZE = 4;
byte rates[RATE_SIZE];
byte rateSpot = 0;
long lastBeat = 0;
float beatsPerMinute = 0;
int beatAvg = 0;
long irValue = 0;
bool fingerDetected = false;

// UART Communication
#define RXp2 16
#define TXp2 17

// File system functions
#define FORMAT_LITTLEFS_IF_FAILED true

void listDir(fs::FS &fs, const char *dirname, uint8_t levels) {
  Serial.printf("Listing directory: %s\r\n", dirname);

  File root = fs.open(dirname);
  if (!root) {
    Serial.println("- failed to open directory");
    return;
  }
  if (!root.isDirectory()) {
    Serial.println(" - not a directory");
    return;
  }

  File file = root.openNextFile();
  while (file) {
    if (file.isDirectory()) {
      Serial.print("  DIR : ");
      Serial.println(file.name());
      if (levels) {
        listDir(fs, file.path(), levels - 1);
      }
    } else {
      Serial.print("  FILE: ");
      Serial.print(file.name());
      Serial.print("\tSIZE: ");
      Serial.println(file.size());
    }
    file = root.openNextFile();
  }
}

void readFile(fs::FS &fs, const char *path) {
  Serial.printf("Reading file: %s\r\n", path);

  File file = fs.open(path);
  if (!file || file.isDirectory()) {
    Serial.println("- failed to open file for reading");
    return;
  }

  Serial.println("- read from file:");
  while (file.available()) {
    Serial.write(file.read());
  }
  file.close();
}

void writeFile(fs::FS &fs, const char *path, const char *message) {
  Serial.printf("Writing file: %s\r\n", path);

  File file = fs.open(path, FILE_WRITE);
  if (!file) {
    Serial.println("- failed to open file for writing");
    return;
  }
  if (file.print(message)) {
    Serial.println("- file written");
  } else {
    Serial.println("- write failed");
  }
  file.close();
}

// Web server handlers
void handleRoot() {
  // Serve the HTML page
  File file = LittleFS.open("/index.html", "r");
  if (!file) {
    server.send(500, "text/plain", "Error loading HTML file");
    return;
  }
  
  server.streamFile(file, "text/html");
  file.close();
}

void handleData() {
  // Serve JSON data with heart rate information
  String json = "{\"irValue\":" + String(irValue) + 
                ",\"bpm\":" + String(beatsPerMinute) + 
                ",\"avgBpm\":" + String(beatAvg) + 
                ",\"fingerDetected\":" + String(fingerDetected ? "true" : "false") + "}";
  server.send(200, "application/json", json);
}

void handleAPI() {
  // API endpoint for programmatic access
  String json = "{\"heart_rate\":"
                "{\"current_bpm\":" + String(beatsPerMinute) + 
                ",\"average_bpm\":" + String(beatAvg) + 
                ",\"timestamp\":" + String(millis()) + 
                "},\"sensor\":"
                "{\"ir_value\":" + String(irValue) + 
                ",\"finger_detected\":" + String(fingerDetected ? "true" : "false") + 
                "}}";
  server.send(200, "application/json", json);
}

void handleCSS() {
  // Serve CSS file
  File file = LittleFS.open("/style.css", "r");
  if (!file) {
    server.send(500, "text/plain", "Error loading CSS file");
    return;
  }
  
  server.streamFile(file, "text/css");
  file.close();
}

void handleJS() {
  // Serve JavaScript file
  File file = LittleFS.open("/script.js", "r");
  if (!file) {
    server.send(500, "text/plain", "Error loading JS file");
    return;
  }
  
  server.streamFile(file, "application/javascript");
  file.close();
}

void setup() {
  Serial.begin(115200);
  delay(3000);  // Important: Wait for serial to stabilize
  
  // Initialize UART for communication with Arduino
  Serial2.begin(9600, SERIAL_8N1, RXp2, TXp2);
  delay(100);

  // Initialize I2C with explicit pin assignment
  Wire.begin(21, 22); // SDA, SCL - common ESP32 I2C pins
  Wire.setClock(400000); // Set I2C clock speed to 400kHz

  // Initialize LittleFS
  if (!LittleFS.begin(FORMAT_LITTLEFS_IF_FAILED)) {
    Serial.println("LittleFS Mount Failed");
    return;
  }

  // Create HTML file if it doesn't exist
  if (!LittleFS.exists("/index.html")) {
    writeFile(LittleFS, "/index.html", 
      "<!DOCTYPE html>"
      "<html>"
      "<head>"
      "<title>ESP32 Heart Rate Monitor</title>"
      "<meta name='viewport' content='width=device-width, initial-scale=1'>"
      "<link rel='stylesheet' href='/style.css'>"
      "</head>"
      "<body>"
      "<div class='container'>"
      "<h1>Heart Rate Monitor</h1>"
      "<div class='data-container'>"
      "<div class='data-item'>"
      "<h2>IR Value</h2>"
      "<p id='irValue'>0</p>"
      "</div>"
      "<div class='data-item'>"
      "<h2>Current BPM</h2>"
      "<p id='bpm'>0</p>"
      "</div>"
      "<div class='data-item'>"
      "<h2>Average BPM</h2>"
      "<p id='avgBpm'>0</p>"
      "</div>"
      "</div>"
      "<div id='status'>Place your finger on the sensor</div>"
      "<div class='api-info'>"
      "<h2>API Endpoint</h2>"
      "<p>Access heart rate data programmatically:</p>"
      "<code id='api-url'>/api</code>"
      "<p>Returns JSON data with current_bpm, average_bpm, and sensor status.</p>"
      "</div>"
      "</div>"
      "<script src='/script.js'></script>"
      "</body>"
      "</html>");
  }

  // Create CSS file if it doesn't exist
  if (!LittleFS.exists("/style.css")) {
    writeFile(LittleFS, "/style.css", 
      "body { font-family: Arial, sans-serif; background-color: #f0f0f0; margin: 0; padding: 20px; }"
      ".container { max-width: 800px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }"
      "h1 { color: #e53935; text-align: center; }"
      ".data-container { display: flex; justify-content: space-around; flex-wrap: wrap; margin: 20px 0; }"
      ".data-item { text-align: center; padding: 15px; background-color: #f9f9f9; border-radius: 8px; margin: 10px; flex: 1; min-width: 150px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }"
      ".data-item h2 { margin: 0 0 10px 0; color: #333; font-size: 18px; }"
      ".data-item p { font-size: 24px; font-weight: bold; color: #e53935; margin: 0; }"
      "#status { text-align: center; padding: 10px; margin-top: 20px; font-weight: bold; border-radius: 5px; }"
      ".no-finger { background-color: #fff3cd; color: #856404; }"
      ".finger-detected { background-color: #d4edda; color: #155724; }"
      ".measuring { background-color: #cce5ff; color: #004085; }"
      ".api-info { margin-top: 30px; padding: 15px; background-color: #f8f9fa; border-radius: 8px; }"
      ".api-info h2 { margin-top: 0; color: #6c757d; }"
      "code { display: inline-block; padding: 5px 10px; background-color: #e9ecef; border-radius: 4px; font-family: monospace; }");
  }

  // Create JavaScript file if it doesn't exist
  if (!LittleFS.exists("/script.js")) {
    writeFile(LittleFS, "/script.js", 
      "function updateData() {"
      "fetch('/data')"
      ".then(response => response.json())"
      ".then(data => {"
      "document.getElementById('irValue').textContent = data.irValue;"
      "document.getElementById('bpm').textContent = data.bpm.toFixed(1);"
      "document.getElementById('avgBpm').textContent = data.avgBpm;"
      "const status = document.getElementById('status');"
      "if (!data.fingerDetected) {"
      "status.textContent = 'No finger detected';"
      "status.className = 'no-finger';"
      "} else if (data.avgBpm > 0) {"
      "status.textContent = 'Finger detected - measuring heart rate';"
      "status.className = 'measuring';"
      "} else {"
      "status.textContent = 'Finger detected - waiting for stable reading';"
      "status.className = 'finger-detected';"
      "}"
      "})"
      ".catch(error => console.error('Error:', error));"
      "}"
      "// Update API URL with current host"
      "document.getElementById('api-url').textContent = window.location.origin + '/api';"
      "setInterval(updateData, 1000);"
      "updateData();");
  }

  // Initialize MAX30105 sensor with error handling
  Serial.println("Initializing heart rate sensor...");
  
  // Try to initialize the sensor multiple times
  int maxTries = 5;
  for (int i = 0; i < maxTries; i++) {
    if (particleSensor.begin(Wire, I2C_SPEED_FAST)) {
      Serial.println("MAX30105 sensor found!");
      break;
    } else {
      Serial.println("MAX30105 not found. Attempt " + String(i+1) + "/" + String(maxTries));
      delay(1000);
      
      if (i == maxTries - 1) {
        Serial.println("MAX30105 was not found. Please check wiring/power.");
        while (1); // Halt if sensor not found
      }
    }
  }

  // Configure sensor with settings that work better for heart rate monitoring
  particleSensor.setup();
  particleSensor.setPulseAmplitudeRed(0x0A); // Turn Red LED to low to indicate sensor is running
  particleSensor.setPulseAmplitudeGreen(0); // Turn off Green LED
  
  // Set sample rate and LED pulse amplitude for better detection
  byte ledBrightness = 0x1F; // Options: 0=Off to 255=50mA
  byte sampleAverage = 4; // Options: 1, 2, 4, 8, 16, 32
  byte ledMode = 2; // Options: 1 = Red only, 2 = Red + IR, 3 = Red + IR + Green
  int sampleRate = 100; // Options: 50, 100, 200, 400, 800, 1000, 1600, 3200
  int pulseWidth = 411; // Options: 69, 118, 215, 411
  int adcRange = 4096; // Options: 2048, 4096, 8192, 16384
  
  particleSensor.setup(ledBrightness, sampleAverage, ledMode, sampleRate, pulseWidth, adcRange);

  Serial.println("Place your index finger on the sensor with steady pressure.");

  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  int wifiTimeout = 20; // 10 seconds timeout
  while (WiFi.status() != WL_CONNECTED && wifiTimeout > 0) {
    delay(500);
    Serial.print(".");
    wifiTimeout--;
  }
  
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("\nFailed to connect to WiFi. Please check credentials.");
  } else {
    Serial.println();
    Serial.print("Connected! IP address: ");
    Serial.println(WiFi.localIP());
  }

  // Set up web server routes
  server.on("/", handleRoot);
  server.on("/data", handleData);
  server.on("/api", handleAPI);  // API endpoint
  server.on("/style.css", handleCSS);
  server.on("/script.js", handleJS);

  // Start server
  server.begin();
  Serial.println("HTTP server started");
  Serial.println("API available at: http://" + WiFi.localIP().toString() + "/api");
}

void loop() {
  // Handle client requests
  server.handleClient();

  // Read from the sensor
  irValue = particleSensor.getIR();
  fingerDetected = (irValue > 50000); // Check if finger is detected

  if (checkForBeat(irValue) == true && fingerDetected) {
    // We sensed a beat!
    long delta = millis() - lastBeat;
    lastBeat = millis();

    beatsPerMinute = 60 / (delta / 1000.0);

    if (beatsPerMinute < 255 && beatsPerMinute > 20) {
      rates[rateSpot++] = (byte)beatsPerMinute;
      rateSpot %= RATE_SIZE;

      // Take average of readings
      beatAvg = 0;
      for (byte x = 0 ; x < RATE_SIZE ; x++)
        beatAvg += rates[x];
      beatAvg /= RATE_SIZE;
    }
  }

  // If no finger is detected, reset values
  if (!fingerDetected) {
    beatsPerMinute = 0;
    for (byte x = 0 ; x < RATE_SIZE ; x++)
      rates[x] = 0;
    beatAvg = 0;
    rateSpot = 0;
    lastBeat = 0;
  }

  // Send data to Arduino via UART
  static unsigned long lastUartSend = 0;
  if (millis() - lastUartSend > 1000) { // Send every second
    String data = "IR=" + String(irValue) + 
                 ",BPM=" + String(beatsPerMinute) + 
                 ",AvgBPM=" + String(beatAvg) + 
                 ",Finger:" + (fingerDetected ? "Yes" : "No");
    Serial2.println(data);
    lastUartSend = millis();
  }

  // Print to serial for debugging
  static unsigned long lastSerialPrint = 0;
  if (millis() - lastSerialPrint > 1000) { // Only print every second
    Serial.print("IR=");
    Serial.print(irValue);
    Serial.print(", BPM=");
    Serial.print(beatsPerMinute);
    Serial.print(", Avg BPM=");
    Serial.print(beatAvg);
    Serial.print(", Finger: ");
    Serial.println(fingerDetected ? "Yes" : "No");
    lastSerialPrint = millis();
  }

  // Small delay to avoid flooding the loop
  delay(10);
}