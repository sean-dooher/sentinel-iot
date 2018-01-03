#include "WebSocketsClient.h"
#include "ArduinoJson.h"
#include "Arduino.h"
#ifndef Leaf_H_
#define Leaf_H_
class Device;
class Leaf {
	public:
		char name[50];
		char model[30];
		char uuid[40];
		char password[50];
		char host[50];
		char url[30];
		unsigned int port;
		boolean is_connected;

		Leaf(char* name, char* model, char* uuid, char* password);

		void connect(char* _host, unsigned int _port, char* _url);  //done
		void update(); // done
		void disconnect(); // done
		void send_device_list(); // done
		void send_name(); //done
		void parse_message(JsonObject& message); // done
		void send_config(); // done
		void subscribe(char* uuid, char* device, void (*fun)(JsonObject&));
		void send_status(Device* device); // done
		void send_status(char* device); // done
		void register_device(Device& device); // done
		Device* get_device(char* name); // done
	private:
		Device* devices[10];
		int num_devices;
		WebSocketsClient webSocket;
		void handle_web_socket(WStype_t type, uint8_t* payload, size_t length);
		void send_message(JsonObject& message); // done
};
#endif