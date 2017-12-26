#include "Device.h"
#include "Leaf.h"
void Device::get_status_template(JsonObject& buffer) {
	buffer["type"] = "DEVICE_STATUS";
	buffer["uuid"] = leaf->uuid;
	buffer["format"] = format;
	buffer["device"] = name;
	if(mode == device_mode::IN){
		buffer["mode"] = "IN";
	} else {
		buffer["mode"] = "OUT";
	}
}

void StringDevice::get_status_message(JsonObject& buffer) {
	get_status_template(buffer);
	buffer["value"] = value;
}

void NumberDevice::get_status_message(JsonObject& buffer) {
	get_status_template(buffer);
	buffer["value"] = value;
}

void UnitDevice::get_status_message(JsonObject& buffer) {
	get_status_template(buffer);
	buffer["value"] = value;
	buffer["units"] = units;
}

void BooleanDevice::get_status_message(JsonObject& buffer) {
	get_status_template(buffer);
	buffer["value"] = value;
}