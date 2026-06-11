/**
 * ASTROPATH Main Controller (Master Node)
 * 
 * Role: 
 * 1. Read GPS data from NEO-6M module
 * 2. Process NMEA sentences using TinyGPS++
 * 3. Sync coordinates to ESP32-CAM via Serial
 * 4. (Optional) Manage vibration/ultrasonic sensors
 */

#include <TinyGPS++.h>
#include <SoftwareSerial.h>

// ===========================
// CONFIGURATION
// ===========================

// GPS Module Connections (NEO-6M)
static const int RXPin = 4, TXPin = 3;
static const uint32_t GPSBaud = 9600;

// Communication Pins
// Note: If using Arduino Mega, use Serial1/Serial2
// If using Arduino Uno, Hardware Serial (0,1) goes to ESP32-CAM
#define CAM_SERIAL Serial

// ===========================
// GLOBAL OBJECTS
// ===========================

TinyGPSPlus gps;
SoftwareSerial ss(RXPin, TXPin);

unsigned long lastSyncTime = 0;
const int syncInterval = 1000; // Sync every 1 second

void setup() {
  // Debug Serial
  // Serial.begin(115200); 
  
  // Communication to ESP32-CAM
  CAM_SERIAL.begin(115200);
  
  // Interface with GPS Module
  ss.begin(GPSBaud);

  // Status LED
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  // 1. Read from GPS Module
  while (ss.available() > 0) {
    if (gps.encode(ss.read())) {
      // Data successfully parsed
    }
  }

  // 2. Sync with ESP32-CAM every second
  if (millis() - lastSyncTime > syncInterval) {
    if (gps.location.isValid()) {
      digitalWrite(LED_BUILTIN, HIGH); // Flash LED on sync
      
      // Send ASTROPATH Protocol String
      CAM_SERIAL.print("GPS:");
      CAM_SERIAL.print(gps.location.lat(), 6);
      CAM_SERIAL.print(",");
      CAM_SERIAL.print(gps.location.lng(), 6);
      CAM_SERIAL.println();
      
      // For local debugging (if using Mega or separate Serial)
      // Serial.println("Synced location to ESP32-CAM");
      
      delay(50);
      digitalWrite(LED_BUILTIN, LOW);
    } else {
      // GPS searching for satellite fix
      // Serial.println("GPS: Waiting for Fix...");
    }
    
    lastSyncTime = millis();
  }

  // 3. Handle data from ESP32-CAM (optional)
  if (CAM_SERIAL.available()) {
    // Logic to handle responses from Camera node
  }
}
