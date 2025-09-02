#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <SoftwareSerial.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 32
#define OLED_RESET    -1
#define SCREEN_ADDRESS 0x3C
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Use SoftwareSerial for compatibility with all Arduino boards
SoftwareSerial espSerial(10, 11); // RX, TX (TX not used)

// Variables to store parsed data
long irValue = 0;
float bpm = 0.0;
int avgBpm = 0;
bool fingerDetected = false;
unsigned long lastUpdate = 0;

void setup() {
  Serial.begin(9600);  // For debugging
  espSerial.begin(9600); // For receiving from ESP32
  
  // Initialize OLED display
  if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed"));
    for(;;);
  }
  
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("Waiting for data...");
  display.display();
}

void loop() {
  if (espSerial.available() > 0) {
    String data = espSerial.readStringUntil('\n');
    Serial.println("Received: " + data); // Debug output
    
    // Parse the received data
    if (data.startsWith("IR=")) {
      parseData(data);
      
      // Override finger detection based on BPM
      fingerDetected = (bpm > 0.0);
      
      updateDisplay();
      lastUpdate = millis();
    }
  }
  
  // Show "no data" message if no update for 5 seconds
  if (millis() - lastUpdate > 5000) {
    display.clearDisplay();
    display.setCursor(0, 0);
    display.println("No data from ESP32");
    display.display();
  }
  
  delay(100);
}

void parseData(String data) {
  // Find positions of key markers
  int irPos = data.indexOf("IR=");
  int bpmPos = data.indexOf("BPM=");
  int avgPos = data.indexOf("AvgBPM=");
  
  if (irPos != -1 && bpmPos != -1) {
    // Extract IR value
    String irStr = data.substring(irPos + 3, bpmPos - 1);
    irValue = irStr.toInt();
    
    // Extract BPM value
    int commaPos = data.indexOf(',', bpmPos);
    if (commaPos != -1) {
      String bpmStr = data.substring(bpmPos + 4, commaPos);
      bpm = bpmStr.toFloat();
    }
    
    // Extract Average BPM
    if (avgPos != -1) {
      commaPos = data.indexOf(',', avgPos);
      if (commaPos != -1) {
        String avgStr = data.substring(avgPos + 7, commaPos);
        avgBpm = avgStr.toInt();
      }
    }
  }
}

void updateDisplay() {
  display.clearDisplay();
  
  // Display title
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.print("Heart Rate Monitor");
  
  // Draw separator line
  display.drawLine(0, 9, 128, 9, SSD1306_WHITE);
  
  // Display BPM values
  display.setCursor(0, 12);
  display.print("BPM:");
  display.setCursor(30, 12);
  display.print(bpm, 1);
  
  display.setCursor(70, 12);
  display.print("Avg:");
  display.setCursor(100, 12);
  display.print(avgBpm);
  
  // Display IR value and finger status
  display.setCursor(0, 22);
  display.print("IR:");
  display.setCursor(20, 22);
  if (irValue > 1000) {
    display.print(irValue/1000);
    display.print("k");
  } else {
    display.print(irValue);
  }
  
  display.setCursor(70, 22);
  display.print("Fin:");
  display.setCursor(105, 22);
  display.print(fingerDetected ? "Y" : "N");
  
  display.display();
}
