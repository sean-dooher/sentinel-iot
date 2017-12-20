
/*
 * WebSocketClient.ino
 *
 *  Created on: 24.05.2015
 *
 */

#include <Arduino.h>
#include <ArduinoJson.h>



#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
#include <ArduinoOTA.h>
#include <WebSocketsClient.h>
#include <WiegandNG.h>


ESP8266WiFiMulti WiFiMulti;
WebSocketsClient webSocket;

#define USE_SERIAL Serial1
WiegandNG rfidReader;
 
long facilityCode;
long cardCode;

void webSocketEvent(WStype_t type, uint8_t* payload, size_t length) {

  switch(type) {
    case WStype_DISCONNECTED:
      USE_SERIAL.printf("[WSc] Disconnected!\n");
      break;
    case WStype_CONNECTED: {
      const size_t bufferSize = JSON_OBJECT_SIZE(5);
      DynamicJsonBuffer jsonBuffer(bufferSize);

      JsonObject& root = jsonBuffer.createObject();
      root["type"] = "CONFIG";
      root["uuid"] = "0d51974f-90f1-4fec-af45-5bf319186304";
      root["name"] = "RFID_READER";
      root["model"] = "THINLINE_II";
      root["api_version"] = "0.1.0";

      char buffer[512];
      root.printTo(buffer, sizeof(buffer));
      
      
      USE_SERIAL.printf("[WSc] Connected to url: %s\n", payload);
      

      // send message to server when Connected
      webSocket.sendTXT(buffer);
    }
      break;
    case WStype_TEXT: {

      // Case: GET_DEVICE websocket event
      String payloadString = String((char*) payload);
      const size_t bufferSize = JSON_OBJECT_SIZE(4) + 210;
      DynamicJsonBuffer jsonBuffer(bufferSize);      
      JsonObject& root = jsonBuffer.parseObject(payloadString);
      
      const char* type = root["type"]; // "GET_DEVICE
      const char* uuid = root["uuid"]; // "0d51974f-90f1-4fec-af45-5bf319186304"
      const char* hub_id = root["hub_id"]; // "666"
      
      const char* name = root["name"]; // "RFID_THINLINE_II"

      if (strcmp(type, "GET_DEVICE") == 0) {
        sendDeviceStatus();   
      }
      }
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
  rfidReader.begin(5,digitalPinToInterrupt(5), 4, digitalPinToInterrupt(4), 100, 25);
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
  webSocket.begin("192.168.1.4", 8000, "/hub/");


  // event handler
  webSocket.onEvent(webSocketEvent);

  // use HTTP Basic Authorization this is optional remove if not needed
  //webSocket.setAuthorization("user", "Password");

  // try ever 5000 again if connection has failed
  webSocket.setReconnectInterval(5000);

}

void processReaderData(long* facilityCode, long* cardCode) {
  *facilityCode = 0;
  *cardCode = 0;
  volatile unsigned char *buffer=rfidReader.getRawData();
  unsigned int bufferSize = rfidReader.getBufferSize();
  unsigned int countedBits = rfidReader.getBitCounted();
 
  unsigned int countedBytes = (countedBits/8);
  if ((countedBits % 8)>0) countedBytes++;
  unsigned int bitsUsed = countedBytes * 8;
  int index = 0;
  for (int i=bufferSize-countedBytes; i< bufferSize;i++) {
    unsigned char bufByte=buffer[i];
    for(int x=0; x<8;x++) {
      if ( (((bufferSize-i) *8)-x) <= countedBits) {
        if(index > 1 && index < 14) {
          *facilityCode <<=1;
          if((bufByte & 0x80)) {
            *facilityCode |= 1;
          }
        } else if (index >= 14 && index < 34) {
          *cardCode <<=1;
          if((bufByte & 0x80)) {
            *cardCode |= 1;
          }
        }
        index++;
      }
      bufByte<<=1;
    }
  }
}

void sendDeviceStatus() {
  const size_t bufferSize = JSON_OBJECT_SIZE(5);
  DynamicJsonBuffer jsonBuffer(bufferSize);

  JsonObject& root = jsonBuffer.createObject();
  root["type"] = "DEVICE_STATUS";
  root["uuid"] = "0d51974f-90f1-4fec-af45-5bf319186304";
  root["device"] = "rfidReader";
  root["value"] = cardCode;
  root["format"] = "number";

  char buffer[512];
  root.printTo(buffer, sizeof(buffer));

  webSocket.sendTXT(buffer);  
}

void loop() {
  ArduinoOTA.handle();
  if(rfidReader.available())
  {
    processReaderData(&facilityCode, &cardCode); //store data in facilityCode and cardCode global variables
    rfidReader.clear();
    sendDeviceStatus();
  }

  webSocket.loop();
}

