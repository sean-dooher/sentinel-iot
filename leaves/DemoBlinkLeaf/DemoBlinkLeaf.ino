#include <Device.h>
#include <Leaf.h>

/* 
 * WebSocketClient.ino
 *
 *  Created on: 24.05.2015
 *
 */
#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
#include <ArduinoOTA.h>
//#include <WiegandNG.h>
#include <elapsedMillis.h>


ESP8266WiFiMulti WiFiMulti;
const short int BUILTIN_LED1 = 2; //GPIO2

//WiegandNG rfidReader;

Leaf leaf("tester_2", "1.0.1", "01bc9e4b-15cb-4ecc-901f-0a58906f2e1c");
BooleanDevice door_device("door_open", false, device_mode::OUT);

void setup() {
  //rfidReader.begin(5,digitalPinToInterrupt(5), 4, digitalPinToInterrupt(4), 100, 25);
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
  ArduinoOTA.begin();

  // Hostname defaults to esp8266-[ChipID]
  ArduinoOTA.setHostname("RFID-Node");
  leaf.connect("192.168.1.95", 8000, "/hub/");
  leaf.register_device(door_device);
  door_device.on_change = handle_change;
  pinMode(BUILTIN_LED1, OUTPUT); // Initialize the BUILTIN_LED1 pin as an output
  digitalWrite(BUILTIN_LED1, HIGH);
}

//void processReaderData(long* facilityCode, long* cardCode) {
//  *facilityCode = 0;
//  *cardCode = 0;
//  volatile unsigned char *buffer=rfidReader.getRawData();
//  unsigned int bufferSize = rfidReader.getBufferSize();
//  unsigned int countedBits = rfidReader.getBitCounted();
// 
//  unsigned int countedBytes = (countedBits/8);
//  if ((countedBits % 8)>0) countedBytes++;
//  unsigned int bitsUsed = countedBytes * 8;
//  int index = 0;
//  for (int i=bufferSize-countedBytes; i< bufferSize;i++) {
//    unsigned char bufByte=buffer[i];
//    for(int x=0; x<8;x++) {
//      if ( (((bufferSize-i) *8)-x) <= countedBits) {
//        if(index > 1 && index < 14) {
//          *facilityCode <<=1;
//          if((bufByte & 0x80)) {
//            *facilityCode |= 1;
//          }
//        } else if (index >= 14 && index < 34) {
//          *cardCode <<=1;
//          if((bufByte & 0x80)) {
//            *cardCode |= 1;
//          }
//        }
//        index++;
//      }
//      bufByte<<=1;
//    }
//  }
//}

void loop() {
  ArduinoOTA.handle();
  leaf.update();
}

void handle_change(Device& device) {
  boolean newValue = ((BooleanDevice&) device).get_value();
  if(newValue == 1) {
    digitalWrite(BUILTIN_LED1, LOW);
  } else {
    digitalWrite(BUILTIN_LED1, HIGH);
  }
}

