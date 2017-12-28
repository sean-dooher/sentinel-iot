class Leaf {
	constructor(name, model, uuid, socket=null, password=null) {
		this.devices = [];
		this.name = name;
		this.uuid = uuid;
		this.model = model;
		this.password = password;
		this._isConnected = false;
		this.connect(socket);
		this.subscriptions = {};
		this.messageQueue = [];
	}

	connect(socket) {
		//open new socket
		if (socket) {
			this.disconnect();
			this.socket = new WebSocket(socket);
			this.socket.onopen = event => {
				this._isConnected = true;
				for(var i = 0; i < this.messageQueue.length; i++) {
					this.messageQueue[i]();
				}
				this.messageQueue = [];
				this.sendConfig();
				console.log("Config sent")
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
			password: this.password,
			api_version: '0.1.0',
		};
		this.socket.send(JSON.stringify(leaf));
	}

	subscribe(uuid, callback) {
		if(!this._isConnected){
			this.messageQueue.push(()=>this.subscribe(uuid, callback));
			return;
		}
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
			mode: device.mode,
		};
		this.socket.send(JSON.stringify(message));
		console.log("status sent");
	}

	set_output(device, value) {
	    device = this.getDevice(device);
	    device.value = value;
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
		device.addListener(d => this.sendStatus(d));
		this.sendStatus(device);
	}

	parseMessage(event) {
		var message = JSON.parse(event.data);
		var response = {
			uuid: this.uuid,
		} 
		switch (message.type) {
			case 'SET_NAME':
			 	this.name = message.name;
				response.type = 'NAME';
				response.name = this.name;
				break;
			case 'GET_NAME':
				response.type = 'NAME';
				response.name = this.name;
				break;
			case 'LIST_DEVICES':
				response.type = 'DEVICE_LIST';
				for(var i = 0; i < this.devices.length; i++) {
					this.sendStatus(this.devices[i].name);
				}
				break;
			case 'CONFIG_COMPLETE':
				break;
			case 'SET_OPTION':
				break;
			case 'GET_OPTION':
				break;
			case 'GET_DEVICE':
				this.sendStatus(message.device);
				return;
			case 'SET_OUTPUT':
			    console.log("Output set received")
			    this.set_output(message.device, message.value);
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
		this.onchange = [];
		if(onchange) {
		    this.addListener(onchange);
		}
		this.mode = mode;
	}

	get value() {
		return this._value;
	}

	set value(newValue) {
		this._value = newValue;
		if(this.onchange.length > 0) {
		    for(var i = 0; i < this.onchange.length; i++){
			    this.onchange[i](this);
			}
		}
	}

	get options() {
		return {'auto': true};
	}

	addListener(func) {
	    this.onchange.push(func)
	}
}