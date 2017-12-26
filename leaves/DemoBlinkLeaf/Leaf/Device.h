#include "ArduinoJson.h"
#include "Arduino.h"
#ifndef Device_H_
#define Device_H_
enum device_mode {IN=0, OUT=1};
class Leaf;
class Device {
	public:
		void (*on_change)(Device&);
		char name[20];
		char format[10];
		device_mode mode;
		Device(char* name, char* format, device_mode mode) {
			strcpy(this->name, name);
			strcpy(this->format, format);
			this->mode = mode;
			on_change = NULL;
		}
		Leaf* leaf;
		virtual void get_status_message(JsonObject& buffer) = 0;
	protected:
		void get_status_template(JsonObject& buffer);
};

class StringDevice : public Device {
	private:
		char* value;
	public:
		char* get_value() {
			return value;
		}
		void set_value(char* value) {
			if(this->value) {
				delete[] this->value;
			}
			this->value = new char[strlen(value)];
			strcpy(this->value, value);
		}
		StringDevice(char* name, char* value, device_mode mode) : Device(name, "string", mode) {
			set_value(value);
		}
		~StringDevice() {
			delete[] value;
		}
		void get_status_message(JsonObject& buffer);
};

class NumberDevice : public Device {
	private:
		int value;
	public:
		int get_value() {
			return value;
		}
		void set_value(int value) {
			this->value = value;
		}
		NumberDevice(char* name, int value, device_mode mode) : Device(name, "number", mode) {
			set_value(value);
		}
		void get_status_message(JsonObject& buffer);
};

class UnitDevice : public Device {
	private:
		int value;
		char units[16];
	public:
		char* get_units() {
			return units;
		}
		char* set_units(char* units) {
			strcpy(this->units, units);
		}
		int get_value() {
			return value;
		}
		void set_value(int value) {
			this->value = value;
		}
		UnitDevice(char* name, int value, char* units, device_mode mode) : Device(name, "number+units", mode) {
			set_value(value);
			set_units(units);
		}
		void get_status_message(JsonObject& buffer);
};

class BooleanDevice : public Device {
	private:
		boolean value;
	public:
		boolean get_value() {
			return value;
		}
		void set_value(boolean value) {
			this->value = value;
		}
		BooleanDevice(char* name, boolean value, device_mode mode) : Device(name, "bool", mode) {
			set_value(value);
		}
		void get_status_message(JsonObject& buffer);
};
#endif