#include <Device.h>
#include <Leaf.h>
#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
#include <ArduinoOTA.h>
#include <elapsedMillis.h>

#include "DHT.h"
#define DHTPIN 5     // what digital pin we're connected to
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

elapsedMillis update;


ESP8266WiFiMulti WiFiMulti;

Leaf leaf("temp_sensor", "1.0.1", "01bc9e4b-15cb-4ecc-901f-0a58906f2e1c", "pass");
UnitDevice temp_sensor("temp", 0, "C", device_mode::IN);
UnitDevice humidity_sensor("humidity", 0, "%", device_mode::IN);

void setup() {
  dht.begin();
  WiFiMulti.addAP("user", "pass");

  while(WiFiMulti.run() != WL_CONNECTED) {
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
  ArduinoOTA.setHostname("Temp-Sensor");
  ArduinoOTA.begin();
  leaf.connect("192.168.1.95", 8000, "/hub/");
  leaf.register_device(temp_sensor);
  leaf.register_device(humidity_sensor);
}

void loop() {
  if(update > 200) {
    float h = dht.readHumidity();
    float t = dht.readTemperature();
    if(!isnan(h)) {
      humidity_sensor.set_value(h);
      leaf.send_status(&humidity_sensor);
    }
    if(!isnan(t)) {
      temp_sensor.set_value(t);
      leaf.send_status(&temp_sensor);
    }
    update = 0;
  }
  ArduinoOTA.handle();
  leaf.update();
}
