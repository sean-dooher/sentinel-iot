/*
 * WebSocketClient.ino
 *
 *  Created on: 24.05.2015
 *
 */

#include <Arduino.h>

#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>

#include <ArduinoOTA.h>
#include <WebSocketsClient.h>

#include <Hash.h>

ESP8266WiFiMulti WiFiMulti;
WebSocketsClient webSocket;


#define USE_SERIAL Serial1

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {

  switch(type) {
    case WStype_DISCONNECTED:
      USE_SERIAL.printf("[WSc] Disconnected!\n");
      break;
    case WStype_CONNECTED: {
      USE_SERIAL.printf("[WSc] Connected to url: %s\n", payload);

      // send message to server when Connected
      webSocket.sendTXT("Connected");
    }
      break;
    case WStype_TEXT:
      USE_SERIAL.printf("[WSc] get text: %s\n", payload);
      char* buff;
      buff = (char*) malloc(4*sizeof(char));
      int i;
      for(i = 0; i < 3 && *payload != '\0'; i++) {
        buff[i] = (char) *(payload++);
      }
      buff[i] = '\0';
      if(strcmp(buff,"on") == 0) {
        digitalWrite(4, HIGH);
      } else if(strcmp(buff,"off") == 0) {
        digitalWrite(4, LOW);
      } else {
         digitalWrite(4, HIGH);
         delay(1000);                       // wait for a second
         digitalWrite(4, LOW);    // turn the LED off by making the voltage LOW
         delay(1000);      
      }
      free(buff);
      break;
    case WStype_BIN:
      USE_SERIAL.printf("[WSc] get binary length: %u\n", length);
      hexdump(payload, length);

      // send data to server
      // webSocket.sendBIN(payload, length);
      break;
  }

}

void setup() {
  pinMode(4, OUTPUT);
  WiFiMulti.addAP("The Loft", "icysocks019");

  //WiFi.disconnect();
  while(WiFiMulti.run() != WL_CONNECTED) {
    delay(100);
  }
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
  ArduinoOTA.begin();

  // Hostname defaults to esp8266-[ChipID]
  ArduinoOTA.setHostname("RFID-Node");

  // server address, port and URL
  webSocket.begin("192.168.1.2", 8000, "/");

  // event handler
  webSocket.onEvent(webSocketEvent);

  // use HTTP Basic Authorization this is optional remove if not needed
  //webSocket.setAuthorization("user", "Password");

  // try ever 5000 again if connection has failed
  webSocket.setReconnectInterval(5000);

}

void loop() {
  ArduinoOTA.handle();
  webSocket.loop();
}
