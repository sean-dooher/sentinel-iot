class Leaf {
	constructor(name, model, uuid, socket=null) {
		this.devices = [];
		this.name = name;
		this.uuid = uuid;
		this.model = model;
		this.connect(socket);
		this._isConnected = false;
		this.subscriptions = {};
	}

	connect(socket) {
		//open new socket
		if (socket) {
			this.disconnect();
			this.socket = new WebSocket(socket);
			this.socket.onopen = event => {
				this._isConnected = true;
				this.sendConfig();
			};
			this.socket.onmessage = event => this.parseMessage(event);
		}
	}

	disconnect() {
		//close currently open socket
		if (this.socket) {
			this.socket.close();
			this._isConnected = false;
		}
	}

	sendConfig() {
		if(!this._isConnected) {
			return;
		}

		var leaf = {
			type: 'CONFIG',
			uuid: this.uuid,
			model: this.model,
			name: this.name,
			api_version: '0.1.0',
		};
		this.socket.send(JSON.stringify(leaf));
	}

	subscribe(uuid, callback) {
		var message = {
			type: 'SUBSCRIBE',
			uuid: this.uuid,
			sub_uuid: uuid,
		};
		this.subscriptions[uuid] = callback;
		this.socket.send(JSON.stringify(message));
	}

	sendStatus(device) {
		if(!this._isConnected) {
			return;
		}

		if(typeof(device) === 'string' || device instanceof String) {
			device = this.getDevice(device);
		}
		var message = {
			type: 'DEVICE_STATUS',
			uuid: this.uuid,
			device: device.name,
			format: device.format,
			value: device.value,
		};
		this.socket.send(JSON.stringify(message));
	}

	getDevice(device) {
		for(var i = 0; i < this.devices.length; i++) {
			if(this.devices[i].name === device){
				device = this.devices[i];
				break;
			}
		}
		return device;
	}

	registerDevice(device) {
		this.devices.push(device);
		device.onchange = d => this.sendStatus(d);
		this.sendStatus(device);
	}

	parseMessage(event) {
		var message = JSON.parse(event.data);
		var response = {
			uuid: this.uuid,
		} 
		switch (message.type) {
			case 'SET_NAME':
			 	this.name = message.data;
				response.type = 'NAME';
				response.name = this.name;
				break;
			case 'GET_NAME':
				response.type = 'NAME';
				response.name = this.name;
				break;
			case 'LIST_DEVICES':
				response.type = 'DEVICE_LIST';
				var devices = [];
				for(var i = 0; i < this.devices.length; i++) {
					devices.push([{
						name:this.devices[i].name,
						format:this.devices[i].format,
						mode:this.devices[i].mode,
						options:this.devices[i].options,
					}]);
				}
				response.devices = devices;
				break;
			case 'CONFIG_COMPLETE':
				for(var i = 0; i < this.devices.length; i++) {
					this.sendStatus(this.devices[i]);
				};
				break;
			case 'SET_OPTION':
				// if(message.data.device === 'rfid' && message.data.option === 'auto') {
				// 	isAuto = parseInt(message.data.value, 10);
				// 	document.querySelector("#auto").innerHTML = isAuto;
				// 	response.type = "OPTION";
				// 	response.option = message.data.option;
				// 	response.value = isAuto;
				// } else if (message.data.device == 'rfid') {
				// 	response.type = "UNKNOWN_OPTION";
				// 	response.option = message.data.option;
				// } else {
				// 	response.type = "UNKNOWN_DEVICE";
				// 	response.device = message.data.device;
				// }
				break;
			case 'GET_OPTION':
				// if(message.data.device === 'rfid' && message.data.option === 'auto') {
				// 	response.type = "OPTION";
				// 	response.option = message.data.option;
				// 	response.value = isAuto;
				// } else if (message.data.device == 'rfid') {
				// 	response.type = "UNKNOWN_OPTION";
				// 	response.option = message.data.option;
				// } else {
				// 	response.type = "UNKNOWN_DEVICE";
				// 	response.device = message.data.device;
				// }
				break;
			case 'GET_DEVICE':
				this.sendStatus(name);
				if (message.data.device === 'rfid') {
					response.type = 'DEVICE_STATUS';
					response.value = lastRead;
					response.format = "number";
				} else {
					response.type = 'UNKNOWN_DEVICE';
				}
				break;
			case 'GET_CONFIG':
				this.sendConfig();
				return;
			case 'SUBSCRIBER_UPDATE':
				var remoteMessage = JSON.parse(message["message"]);
				if ("uuid" in remoteMessage && remoteMessage["uuid"] in this.subscriptions) {
					this.subscriptions[remoteMessage["uuid"]](remoteMessage);
				}
				return;
			default:
				break;
		}
		this.socket.send(JSON.stringify(response));
	}
}

var DeviceMode = {
	IN:"IN",
	OUT:"OUT"
}
class Device {
	constructor(name, initial, format, mode=DeviceMode.IN, units=null, onchange=null) {
		this.name = name;
		this._value = initial;
		this.format = format;
		this.units = units;
		this.onchange = onchange;
	}

	get value() {
		return this._value;
	}

	set value(newValue) {
		this._value = newValue;
		if(this.onchange) {
			this.onchange(this);
		}
	}

	get options() {
		return {'auto': true};
	}
}