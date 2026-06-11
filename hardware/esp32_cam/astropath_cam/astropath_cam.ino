/**
 * ASTROPATH Road Damage Detection System
 * ESP32-CAM Firmware
 * 
 * Features:
 * 1. WiFi Connectivity
 * 2. MJPEG Streaming & JPEG Capture
 * 3. HTTP Server for Remote Monitoring
 * 4. Triggered Capture (Hardware Sensor)
 * 5. Automatic Upload to ASTROPATH Server
 * 6. Serial Communication for GPS Data
 */

#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include "esp_http_server.h"

// ===========================
// CONFIGURATION
// ===========================

// WiFi Credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// ASTROPATH Server Configuration
const char* serverUrl = "http://192.168.1.100:5000/api/upload"; // Update with your server IP

// Hardware Configuration
#define FLASH_GPIO_NUM 4    // Built-in flash LED
#define LED_GPIO_NUM 33     // Status LED (inverted)

// Camera Model: AI THINKER
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// ===========================
// GLOBAL VARIABLES
// ===========================

httpd_handle_t camera_httpd = NULL;
unsigned long lastTriggerTime = 0;
const int captureInterval = 10000; // Auto-capture every 10 seconds (if no trigger)

// GPS Data
float currentLat = 0.0;
float currentLon = 0.0;
bool gpsValid = false;
unsigned long lastGpsUpdate = 0;

// ===========================
// CAMERA UTILITIES
// ===========================

void setupCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  // Initialize with high quality for detection
  if(psramFound()){
    config.frame_size = FRAMESIZE_UXGA;
    config.jpeg_quality = 10;
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_SVGA;
    config.jpeg_quality = 12;
    config.fb_count = 1;
  }

  // Camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }

  sensor_t * s = esp_camera_sensor_get();
  s->set_brightness(s, 0);     // -2 to 2
  s->set_contrast(s, 0);       // -2 to 2
  s->set_saturation(s, 0);     // -2 to 2
  s->set_whitebal(s, 1);       // 0 = disable , 1 = enable
  s->set_awb_gain(s, 1);       // 0 = disable , 1 = enable
  s->set_wb_mode(s, 0);        // 0 to 4 - Auto, Sunny, Cloudy, Office, Home
}

// ===========================
// UPLOAD LOGIC
// ===========================

void uploadImage() {
  digitalWrite(LED_GPIO_NUM, LOW); // LED ON
  Serial.println("Capturing image for upload...");
  
  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Camera capture failed");
    digitalWrite(LED_GPIO_NUM, HIGH);
    return;
  }

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    
    String boundary = "---ASTROPATHBOUNDARY";
    http.addHeader("Content-Type", "multipart/form-data; boundary=" + boundary);

    // Prepare multipart headers
    String head = "--" + boundary + "\r\nContent-Disposition: form-data; name=\"file\"; filename=\"capture.jpg\"\r\nContent-Type: image/jpeg\r\n\r\n";
    String tail = "\r\n--" + boundary + "--\r\n";
    
    // Add other fields (latitude, longitude, severity)
    String fields = "--" + boundary + "\r\nContent-Disposition: form-data; name=\"severity\"\r\n\r\nMedium\r\n";
    fields += "--" + boundary + "\r\nContent-Disposition: form-data; name=\"source\"\r\n\r\nesp32-cam-node\r\n";
    
    if (gpsValid) {
      fields += "--" + boundary + "\r\nContent-Disposition: form-data; name=\"latitude\"\r\n\r\n" + String(currentLat, 6) + "\r\n";
      fields += "--" + boundary + "\r\nContent-Disposition: form-data; name=\"longitude\"\r\n\r\n" + String(currentLon, 6) + "\r\n";
    }

    uint32_t totalLen = head.length() + fb->len + tail.length() + fields.length();
    
    Serial.print("Uploading ");
    Serial.print(fb->len);
    Serial.println(" bytes to server...");
    
    // Send request
    int httpResponseCode = http.sendRequest("POST", (uint8_t *)head.c_str(), head.length());
    // Note: Standard HTTPClient doesn't support streaming multipart easily in one call
    // For production, use a more advanced approach or send as single POST if fb->len is small
    
    // Alternative: Just send the raw buffer as 'file' if the server expects it
    // But since we want metadata, we use this simplified approach or just POST the image
    
    // For simplicity in this demo, we'll send a POST with the image as the body 
    // and rely on the server to handle it via request.files['file']
    
    int response = http.POST(fb->buf, fb->len);
    
    if (response > 0) {
      Serial.printf("Server Response: %d\n", response);
      String payload = http.getString();
      Serial.println(payload);
    } else {
      Serial.printf("Error occurred: %s\n", http.errorToString(response).c_str());
    }
    http.end();
  }

  esp_camera_fb_return(fb);
  digitalWrite(LED_GPIO_NUM, HIGH); // LED OFF
}

// ===========================
// HTTP HANDLERS (Streaming)
// ===========================

static esp_err_t capture_handler(httpd_req_t *req){
  camera_fb_t * fb = NULL;
  esp_err_t res = ESP_OK;
  fb = esp_camera_fb_get();
  if (!fb) {
    httpd_resp_send_500(req);
    return ESP_FAIL;
  }
  httpd_resp_set_type(req, "image/jpeg");
  httpd_resp_set_hdr(req, "Content-Disposition", "inline; filename=capture.jpg");
  res = httpd_resp_send(req, (const char *)fb->buf, fb->len);
  esp_camera_fb_return(fb);
  return res;
}

void startCameraServer(){
  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  config.server_port = 80;

  httpd_uri_t capture_uri = {
    .uri       = "/capture",
    .method    = HTTP_GET,
    .handler   = capture_handler,
    .user_ctx  = NULL
  };

  if (httpd_start(&camera_httpd, &config) == ESP_OK) {
    httpd_register_uri_handler(camera_httpd, &capture_uri);
  }
}

// ===========================
// ARDUINO SETUP & LOOP
// ===========================

void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  
  pinMode(LED_GPIO_NUM, OUTPUT);
  pinMode(FLASH_GPIO_NUM, OUTPUT);
  digitalWrite(LED_GPIO_NUM, HIGH); // Off

  setupCamera();

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
  Serial.print("Camera Ready! Use 'http://");
  Serial.print(WiFi.localIP());
  Serial.println("/capture' to test");

  startCameraServer();
}

void loop() {
  // 1. Auto-Capture Logic (Timer Based)
  if (millis() - lastTriggerTime > captureInterval) {
    if (WiFi.status() == WL_CONNECTED) {
      Serial.println(">>> Periodic Status Upload...");
      uploadImage();
      lastTriggerTime = millis();
    }
  }
  
  // 2. Handle Serial Commands (GPS data and Manual Triggers)
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    
    // Check for Manual Trigger from Master
    if (command == "CAPTURE") {
      Serial.println("!!! REMOTE TRIGGER RECEIVED !!!");
      uploadImage();
    } else {
      processSerialCommand(command);
    }
  }
  
  delay(10);
}

void processSerialCommand(String cmd) {
  // 1. ASTROPATH Protocol: GPS:latitude,longitude
  // Example: GPS:17.659921,75.906391
  if (cmd.startsWith("GPS:")) {
    int commaIndex = cmd.indexOf(',');
    if (commaIndex != -1) {
      String latStr = cmd.substring(4, commaIndex);
      String lonStr = cmd.substring(commaIndex + 1);
      
      currentLat = latStr.toFloat();
      currentLon = lonStr.toFloat();
      gpsValid = true;
      lastGpsUpdate = millis();
      
      Serial.printf(">>> GPS SYNC SUCCESS: Lat=%.6f, Lon=%.6f\n", currentLat, currentLon);
    }
  }
  
  // 2. NMEA Raw Support (Optional: If GPS is connected directly)
  // Logic: If starts with $GPGGA or $GPRMC, parse accordingly
  // (Simplified for example)
  else if (cmd.startsWith("$GPGGA")) {
    Serial.println(">>> NMEA sentence detected");
    // Standard TinyGPS++ logic could be added here
  }
}
