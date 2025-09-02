# Real-Time Heart Rate Monitoring and Reporting System

## Project Overview

![Pre-UI](https://raw.githubusercontent.com/AbidHasanRafi/Real-Time-Heart-Rate-Monitoring-and-Reporting-Application/main/assets/pre-ui.png)

The Real-Time Heart Rate Monitoring and Reporting System is designed as a comprehensive platform that combines both guided and unguided monitoring approaches to track cardiovascular activity. The guided approach provides direct, on-device visualization of heart rate, while the unguided approach extends monitoring to remote web access, enabling users and healthcare professionals to view data anywhere in real-time. The system integrates hardware sensing, embedded processing, wireless communication, and software visualization into a unified solution. By merging these technologies, the project ensures both immediate feedback and long-term data tracking, making it valuable for health monitoring, patient care, and educational demonstrations.

![Pre-URL UI](https://raw.githubusercontent.com/AbidHasanRafi/Real-Time-Heart-Rate-Monitoring-and-Reporting-Application/main/assets/pre-url-ui.png)

### Key Features

- **Real-Time Monitoring**: Continuous heart rate tracking with sub-second latency
- **Dual Interface**: Local OLED display + Remote web dashboard
- **RESTful API**: JSON endpoints for external integrations
- **Data Visualization**: Interactive charts with historical trending
- **Telegram Alerts**: Automated health reports and anomaly notifications
- **Statistical Analysis**: Real-time health insights and pattern detection
- **IoT Architecture**: Scalable, network-connected health monitoring
- **Low Latency**: Sub-2-second sensor-to-dashboard response time

### System Highlights

![Pre-Server Setup](https://raw.githubusercontent.com/AbidHasanRafi/Real-Time-Heart-Rate-Monitoring-and-Reporting-Application/main/assets/pre-server.png)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MAX30102      │────│      ESP32      │────│   Arduino UNO   │
│  Heart Sensor   │    │  WiFi + Server  │    │  OLED Display   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         v                       v                       v
    [IR Sensing]         [Web Dashboard]          [Local Display]
                               │
                               v
                        [Telegram Bot]
```

![Post-Server Setup](https://raw.githubusercontent.com/AbidHasanRafi/Real-Time-Heart-Rate-Monitoring-and-Reporting-Application/main/assets/post-server.png)

## System Architecture, Circuit Diagrams & Connections

![Circuit Diagram](https://raw.githubusercontent.com/AbidHasanRafi/Real-Time-Heart-Rate-Monitoring-and-Reporting-Application/main/assets/circuit.png)

The system architecture consists of tightly coupled hardware and software components. On the hardware side, the MAX30102 optical heart rate sensor captures raw photoplethysmography signals, which are processed by the ESP32 microcontroller. The ESP32 is responsible not only for handling sensor data but also for managing WiFi connectivity and hosting a web server for remote access. To complement this, an Arduino UNO is employed to manage an OLED display, ensuring that the user receives immediate feedback locally. Communication between ESP32 and Arduino occurs through a UART interface, while the OLED display (SSD1306) connects to the Arduino via I2C for real-time visualization.

### Hardware Architecture

The system employs a distributed hardware approach with specialized components:

1. **Sensing Layer**: MAX30102 optical sensor for photoplethysmography
2. **Processing Layer**: ESP32 for data processing and network connectivity
3. **Display Layer**: Arduino UNO + OLED for local visualization
4. **Communication Layer**: WiFi + UART for data transmission

### Software Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SOFTWARE STACK                           │
├─────────────────────────────────────────────────────────────┤
│  Presentation Layer    │  Streamlit App + Telegram Bot      │
├─────────────────────────────────────────────────────────────┤
│  API Layer            │  ESP32 Web Server + RESTful API    │
├─────────────────────────────────────────────────────────────┤
│  Processing Layer     │  Signal Processing + Data Analysis │
├─────────────────────────────────────────────────────────────┤
│  Hardware Layer       │  MAX30102 + ESP32 + Arduino        │
└─────────────────────────────────────────────────────────────┘
```

The software architecture mirrors this layered design. Firmware on the ESP32 handles raw signal acquisition, beat detection, and data formatting, as well as web server implementation for API endpoints. The Arduino sketch controls the OLED display and interprets serial data from the ESP32. For remote monitoring, a Streamlit web application serves as the visualization dashboard, displaying real-time heart rate and historical trends. Additionally, a Telegram bot integration provides notifications and health reports, extending the system’s usability beyond local and web interfaces.

![API Example](https://raw.githubusercontent.com/AbidHasanRafi/Real-Time-Heart-Rate-Monitoring-and-Reporting-Application/main/assets/api.png)

### ESP32 to MAX30102 Wiring

```
ESP32          MAX30102
──────         ────────
GPIO 21   ──>  SDA
GPIO 22   ──>  SCL
3.3V      ──>  VIN
GND       ──>  GND
```

** Important Notes:**
- Use 3.3V only (5V may damage sensor)
- Add 4.7kΩ pull-up resistors on SDA/SCL if needed
- Keep wires short to minimize I2C noise

### ESP32 to Arduino UART Connection

```
ESP32          Arduino UNO
──────         ───────────
GPIO 16   ──>  Pin 10 (RX)
GPIO 17   <──  Pin 11 (TX)
GND       ──>  GND
```

** Communication Protocol:**
- Baud Rate: 9600
- Data Format: `IR=<value>,BPM=<value>,AvgBPM=<value>,Finger:<status>`
- Update Interval: 1 second

### Arduino UNO to OLED Display

```
Arduino        OLED Display
───────        ────────────
A4 (SDA)  ──>  SDA
A5 (SCL)  ──>  SCL
5V        ──>  VCC
GND       ──>  GND
```

### Complete Circuit Diagram

```
                    ┌─────────────┐
                    │   MAX30102  │
                    │   Sensor    │
                    └──────┬──────┘
                           │ I2C
                    ┌──────▼──────┐
                    │    ESP32    │
                    │ (Main MCU)  │
                    └──────┬──────┘
                           │ UART
                    ┌──────▼──────┐
                    │ Arduino UNO │
                    │(Display MCU)│
                    └──────┬──────┘
                           │ I2C
                    ┌──────▼──────┐
                    │ OLED Display│
                    │  (SSD1306)  │
                    └─────────────┘
```

## System Data and Communication Flow

The data flow within the system begins with the MAX30102 sensor, which detects infrared reflectance variations caused by blood volume changes in the fingertip. These signals are processed by the ESP32 to compute instantaneous beats per minute (BPM) and average BPM. From here, the information is distributed along two distinct paths. The first is the local path, where processed data is sent over UART to the Arduino UNO, which then displays it on the OLED screen. The second is the remote path, where data is transmitted via WiFi through the ESP32’s embedded web server, enabling access through APIs and visualization in the Streamlit dashboard.

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ MAX30102    │ →  │    ESP32    │ →  │  Arduino    │
│ Raw IR Data │    │ Processing  │    │  Display    │
└─────────────┘    └─────────────┘    └─────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │ Web Server  │
                   │ (REST API)  │
                   └─────────────┘
                          │
                          ▼
                   ┌─────────────┐    ┌─────────────┐
                   │ Streamlit   │ →  │ Telegram    │
                   │ Dashboard   │    │    Bot      │
                   └─────────────┘    └─────────────┘
```

The system adopts a simple but structured serial communication protocol. The ESP32 transmits formatted strings containing values such as IR intensity, BPM, average BPM, and finger detection status. These are parsed by the Arduino for OLED display. Simultaneously, the ESP32 hosts RESTful API endpoints that provide JSON-formatted responses, ensuring that both the Streamlit app and external applications can access sensor readings programmatically.

![Serial Logs](https://raw.githubusercontent.com/AbidHasanRafi/Real-Time-Heart-Rate-Monitoring-and-Reporting-Application/main/assets/serial-logs.png)

## Network Configuration

Networking is managed primarily by the ESP32. Upon powering, the device connects to a predefined WiFi network using stored credentials and hosts a lightweight web server at a local IP address. This server exposes both a web-based dashboard and dedicated API endpoints, which can be queried by the Streamlit application for real-time visualization. The Streamlit application not only graphs the data but also performs statistical analysis and integrates with Telegram for notifications. This layered connectivity ensures that the system remains functional locally while enabling advanced remote features.

## Data Visualization

![Streamlit Log](https://raw.githubusercontent.com/AbidHasanRafi/Real-Time-Heart-Rate-Monitoring-and-Reporting-Application/main/assets/streamlit-log.png)

![Valueless Connected Interface](https://raw.githubusercontent.com/AbidHasanRafi/Real-Time-Heart-Rate-Monitoring-and-Reporting-Application/main/assets/valueless-connected-inteface.png)

The visualization framework operates at two levels. Locally, the OLED display provides quick-glance information, including current BPM, average BPM, IR signal strength, and finger detection status. This ensures that the system can be used in standalone mode without requiring internet connectivity. Remotely, the Streamlit dashboard offers richer features, such as real-time charts, historical data tracking, variability analysis, and automated health insights. The web interface also includes alert conditions and graphical indicators that highlight abnormal heart rate values or sensor issues.

![Valued Connected Interface](https://raw.githubusercontent.com/AbidHasanRafi/Real-Time-Heart-Rate-Monitoring-and-Reporting-Application/main/assets/valued-connected-inteface.png)

## Notification System

![Telegram Alert](https://raw.githubusercontent.com/AbidHasanRafi/Real-Time-Heart-Rate-Monitoring-and-Reporting-Application/main/assets/telegram-alert.png)

To enhance usability, the system incorporates a Telegram notification module. Users configure their bot token and chat ID to receive reports directly on their mobile devices. The reports include current and average BPM, variability statistics, and timestamps for better context. The system also sends alerts when predefined thresholds are crossed, such as when the heart rate is abnormally high (>100 BPM), abnormally low (<60 BPM), or when sensor or finger placement issues are detected. This ensures that critical health events are communicated promptly. 

## Hardware Requirements, Setup and Calibration

Setting up the system involves connecting the MAX30102 to the ESP32 over I2C, establishing UART communication between ESP32 and Arduino, and linking the OLED display to the Arduino. Once the hardware is assembled, the ESP32 firmware and Arduino sketch are uploaded with appropriate configurations, including WiFi credentials and display parameters. The Streamlit application must be pointed to the ESP32’s IP address, while the Telegram bot is configured using BotFather credentials. Calibration requires placing a finger on the sensor to establish baseline readings and ensuring stable IR values for consistent performance.

### Components List

| Component | Quantity | Purpose | Specifications |
|-----------|----------|---------|----------------|
| **ESP32 Development Board** | 1 | Main microcontroller | WiFi, Bluetooth, 32-bit dual-core |
| **Arduino UNO R3** | 1 | Display controller | ATmega328P, USB interface |
| **MAX30102 Sensor Module** | 1 | Heart rate sensing | I2C, 3.3V, optical PPG |
| **OLED Display (SSD1306)** | 1 | Local visualization | 128x32 pixels, I2C interface |
| **Breadboards** | 2 | Prototyping | Half-size recommended |
| **Jumper Wires** | 20+ | Connections | Male-to-male, various colors |
| **Resistors** | 2 | I2C pull-ups | 4.7kΩ (if needed) |
| **USB Cables** | 2 | Programming | USB-A to Micro-USB/USB-C |

### Power Requirements

- **ESP32**: 3.3V, ~240mA (WiFi active)
- **Arduino UNO**: 5V, ~50mA
- **MAX30102**: 3.3V, ~50mA
- **OLED Display**: 3.3V/5V, ~20mA
- **Total System**: ~360mA @ 5V

## Installation Guide and Configuration

The Real-Time Heart Rate Monitoring and Reporting System requires both hardware assembly and software setup. This section provides a step-by-step guide to ensure smooth installation and configuration.

### Step 1: Hardware Assembly

Before starting, check that all components are functional and that you have the necessary tools such as a screwdriver and multimeter. Ensure the voltage ratings are compatible with your devices.

1. **Prepare Components**
   Verify each module (MAX30102, ESP32, Arduino UNO, and OLED display) for physical or electrical damage.

2. **Connect MAX30102 to ESP32**
   Connect the MAX30102 sensor to the ESP32 using the I2C interface:

   * SDA → GPIO 21
   * SCL → GPIO 22
   * VIN → 3.3V
   * GND → GND
     After wiring, check continuity with a multimeter.

3. **Connect ESP32 to Arduino UNO**
   Establish serial communication between the ESP32 and Arduino UNO:

   * TX (GPIO 16) → RX (Pin 10)
   * RX (GPIO 17) → TX (Pin 11)
   * Common ground shared between boards
     Test the connection with a simple serial communication sketch.

4. **Connect OLED Display to Arduino UNO**
   Attach the OLED display using I2C pins:

   * SDA → A4
   * SCL → A5
   * VCC → 5V
   * GND → GND
     Upload an example OLED sketch to confirm the display is functional.

### Step 2: Software Installation

1. **Arduino IDE Setup**
   Install Arduino IDE (version 2.x recommended). Add the ESP32 board package via the Board Manager and install required libraries such as `Adafruit_SSD1306`, `Wire`, and `Adafruit_GFX`.

2. **ESP32 Firmware Upload**
   Update the firmware with your WiFi credentials:

   ```cpp
   const char* ssid = "YOUR_WIFI_SSID";
   const char* password = "YOUR_WIFI_PASSWORD";
   ```

   Upload the sketch to the ESP32 and monitor the serial output to obtain its assigned IP address.

3. **Arduino UNO Code Upload**
   Upload the OLED display sketch to the Arduino UNO. Verify that the display shows heart rate and IR values correctly.

4. **Python Environment Setup**
   Create and activate a virtual environment for the Streamlit application:

   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

   Update the configuration file with the ESP32’s IP address.

### Step 3: Initial Configuration

1. **Network Setup**
   Ensure that the ESP32 connects successfully to your WiFi network. Note its local IP address and confirm that the web server is accessible via browser. Adjust firewall settings if required.

2. **Sensor Calibration**
   Place a finger on the MAX30102 sensor. Check that the IR value exceeds 50,000, which indicates proper detection. Verify that BPM readings are stable. Adjust LED brightness if needed.

3. **Display Testing**
   Confirm that the OLED display shows BPM, average BPM, and finger detection status in real time.

### WiFi Configuration (ESP32)

```cpp
const char* ssid = "YOUR_NETWORK_NAME";
const char* password = "YOUR_NETWORK_PASSWORD";
```

### Telegram Bot Configuration

```python
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_FROM_BOTFATHER"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"

HIGH_HR_THRESHOLD = 100
LOW_HR_THRESHOLD = 60
ALERT_COOLDOWN = 300  # seconds
```

### Streamlit Configuration

```python
ESP32_IP = "192.168.1.184"
API_ENDPOINT = f"http://{ESP32_IP}/api"
UPDATE_INTERVAL = 2
MAX_DATA_POINTS = 100
```

## Performance Characteristics

![Stats Connected Interface](https://raw.githubusercontent.com/AbidHasanRafi/Real-Time-Heart-Rate-Monitoring-and-Reporting-Application/main/assets/stats-connected-inteface.png)

The MAX30102 sensor operates at configurable sampling rates, typically around 100Hz, with adjustable LED brightness to accommodate different skin tones. Finger detection is based on an IR threshold, usually set above 50,000. Latency is minimal, with less than one second from sensing to OLED display update and under two seconds for web dashboard updates. The system refresh rate is adjustable between 1 and 10 seconds, balancing responsiveness with network load.

## Contributors

This project was jointly developed by:

* **Md. Abid Hasan Rafi**
* **Mst. Fatematuj Johora**
* **Mohima Binte Rasel**

## Project Context

The system was designed and implemented as the **Lab Final Project** of *ECE 362: Microprocessor and Microcomputer Sessional*. It represents the practical application of embedded systems and IoT concepts learned throughout the course.

## Course Teacher

The project was supervised and guided by **Dr. Tangina Sultana**, Associate Professor, Department of Electronics and Communication Engineering (ECE), Faculty of Computer Science and Engineering, Hajee Mohammad Danesh Science & Technology University (HSTU), Dinajpur.