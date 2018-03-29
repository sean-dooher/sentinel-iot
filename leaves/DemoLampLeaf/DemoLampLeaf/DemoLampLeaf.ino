#include <Device.h>
#include <Leaf.h>
#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
#include <ArduinoOTA.h>
#include <elapsedMillis.h>
#include <EEPROM.h>

ESP8266WiFiMulti WiFiMulti;
const short int TOP_OUTLET = 5;
const short int BOTTOM_OUTLET = 4;


Leaf leaf("Whiteboard Outlets", "1.0.1", "uuid", "token");
BooleanDevice top_outlet("Top Outlet", false, device_mode::OUT);
BooleanDevice bottom_outlet("Bottom Outlet", false, device_mode::OUT);

void setup() {
  EEPROM.begin(2);
  WiFiMulti.addAP("user", "pass");

  while (WiFiMulti.run() != WL_CONNECTED) {
    delay(100);
  }
  Serial.println("Connected to wifi");
  ArduinoOTA.setPort(8266);

  ArduinoOTA.onStart([]() {
    Serial.println("Start");
  });
  ArduinoOTA.onEnd([]() {
    Serial.println("\nEnd");
  });
  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
  });
  ArduinoOTA.onError([](ota_error_t error) {
    Serial.printf("Error[%u]: ", error);
    if (error == OTA_AUTH_ERROR) Serial.println("Auth Failed");
    else if (error == OTA_BEGIN_ERROR) Serial.println("Begin Failed");
    else if (error == OTA_CONNECT_ERROR) Serial.println("Connect Failed");
    else if (error == OTA_RECEIVE_ERROR) Serial.println("Receive Failed");
    else if (error == OTA_END_ERROR) Serial.println("End Failed");
  });
  ArduinoOTA.setHostname("Whiteboard Leaves");
  ArduinoOTA.begin();

  leaf.connect("sentinel-iot.net", 80, "/hub/1");
  leaf.register_device(bottom_outlet);
  top_outlet.on_change = handle_change_top;
  
  leaf.register_device(top_outlet);
  bottom_outlet.on_change = handle_change_bottom;
  pinMode(TOP_OUTLET, OUTPUT);
  pinMode(BOTTOM_OUTLET, OUTPUT);

  top_outlet.set_value(EEPROM.read(0));
  bottom_outlet.set_value(EEPROM.read(1));

  digitalWrite(TOP_OUTLET, 1 - top_outlet.get_value());
  digitalWrite(BOTTOM_OUTLET, 1 - bottom_outlet.get_value());
}

void loop() {
  ArduinoOTA.handle();
  leaf.update();
}

void handle_change_top(Device& device) {
  boolean newValue = ((BooleanDevice&) device).get_value();
  digitalWrite(TOP_OUTLET, 1 - newValue);
  EEPROM.write(0, newValue);
  EEPROM.commit();
}

void handle_change_bottom(Device& device) {
  boolean newValue = ((BooleanDevice&) device).get_value();
  digitalWrite(BOTTOM_OUTLET, 1 - newValue);
  EEPROM.write(1, newValue);
  EEPROM.commit();
}

