#include "Device.h"
#include "Leaf.h"
#define USE_SERIAL Serial1
#define API_VERSION "0.1.0"

Leaf::Leaf(char* name, char* model, char* uuid) {
	strcpy(this->name, name);
	strcpy(this->model, model);
	strcpy(this->uuid, uuid);
	num_devices = 0;
	is_connected = true;
}

void Leaf::connect(char* _host, unsigned int _port, char* _url) {
	strcpy(host, _host);
	port = _port;
	strcpy(url, _url);
	webSocket.begin(host, port, url);
	webSocket.onEvent(std::bind(&Leaf::handle_web_socket, this, std::placeholders::_1, std::placeholders::_2, std::placeholders::_3));
	webSocket.setReconnectInterval(5000);
}

void Leaf::disconnect() {
	webSocket.disconnect();
}

void Leaf::update() {
	webSocket.loop();
}

void Leaf::send_device_list() {
	for(int i = 0; i < num_devices; i++) {
		send_status(devices[i]);
	}
}

void Leaf::send_status(Device* device) {
	const size_t bufferSize = JSON_OBJECT_SIZE(5);
	DynamicJsonBuffer jsonBuffer(bufferSize);
	JsonObject& root = jsonBuffer.createObject();

	device->get_status_message(root);
	send_message(root);
}

void Leaf::send_name() {
	const size_t bufferSize = JSON_OBJECT_SIZE(5);
	DynamicJsonBuffer jsonBuffer(bufferSize);

	JsonObject& root = jsonBuffer.createObject();
	root["type"] = "NAME";
	root["uuid"] = uuid;
	root["name"] = name;
	send_message(root);
}

void Leaf::send_status(char* device) {
	send_status(get_device(device));
}

Device* Leaf::get_device(char* name) {
	for(int i = 0; i < num_devices; i++) {
		if(strcmp(devices[i]->name, name) == 0) {
			return devices[i];
			break;
		}
	}
	return NULL;
}

void Leaf::send_message(JsonObject& root) {
	char buffer[512];
	root.printTo(buffer, sizeof(buffer));
	webSocket.sendTXT(buffer); 
}

void Leaf::send_config() {
	const size_t bufferSize = JSON_OBJECT_SIZE(5);
	DynamicJsonBuffer jsonBuffer(bufferSize);

	JsonObject& root = jsonBuffer.createObject();
	root["type"] = "CONFIG";
	root["uuid"] = uuid;
	root["name"] = name;
	root["model"] = model;
	root["api_version"] = API_VERSION;
	char buffer[512];
	root.printTo(buffer, sizeof(buffer));
	// send message to server when Connected
	webSocket.sendTXT(buffer);
}

void Leaf::parse_message(JsonObject& root) {
	const char* type = root["type"];
	if(strcmp(type, "GET_DEVICE") == 0) {
		char name[strlen(root["device"])];
		strcpy(name, root["device"]);
		Device* device = get_device(name);
		if(device) {
			send_status(device);
		}
	} else if (strcmp(type, "SET_OUTPUT") == 0) {
		char name[strlen(root["device"])];
		strcpy(name, root["device"]);
		Device* device = get_device(name);
		if(device) {
			if(strcmp(device->format, "number")) {
				NumberDevice* num_device = (NumberDevice*)device;
				int value = root["value"];
				num_device->set_value(value);
				send_status(device);
			} else if(strcmp(device->format, "bool")) {
				BooleanDevice* bool_device = (BooleanDevice*)device;
				boolean value = root["value"].as<boolean>();
				bool_device->set_value(value);
				send_status(device);
			} else if(strcmp(device->format, "number+units")) {
				UnitDevice* unit_device = (UnitDevice*)device;
				char* units = new char[strlen(root["units"])];
				strcpy(units, root["units"]);
				int value = root["value"].as<int>();
				unit_device->set_value(value);
				send_status(device);
			} else if(strcmp(device->format, "string")) {
				StringDevice* string_device = (StringDevice*)device;
				char* value = new char[strlen(root["value"])];
				strcpy(value, root["value"]);
				string_device->set_value(value);
				send_status(device);
			}
			if(device->on_change)
				device->on_change(*device);
		}
	}
}

void Leaf::register_device(Device& device) {
	devices[num_devices++] = &device;
	device.leaf = this;
	send_status(&device);
}

void Leaf::handle_web_socket(WStype_t type, uint8_t* payload, size_t length){
	switch(type) {
		case WStype_DISCONNECTED:
		  USE_SERIAL.printf("[WSc] Disconnected!\n");
		  is_connected = false;
		  break;
		case WStype_CONNECTED: {
		  send_config();
		  is_connected = true;
		}
	 	break;
		case WStype_TEXT: {
		  // Case: GET_DEVICE websocket event
		  String payloadString = String((char*) payload);
		  const size_t bufferSize = JSON_OBJECT_SIZE(4) + 210;
		  DynamicJsonBuffer jsonBuffer(bufferSize);      
		  JsonObject& root = jsonBuffer.parseObject(payloadString);
		  parse_message(root);
		}
		break;
	}
}