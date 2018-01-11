# Sentinel IOT

## Sentinel Hub

![Hub Mockup](https://i.imgur.com/H0Fy8BH.png)
**The Sentinel Hub** is the main dashboard which allows the user to visualize and control all of their connected devices. Users can drag and drop arrows between individual **leaves**, which are groups of devices and sensors, in order to create a connection between two or more leaves. This connection can serve different functions including a **subscription** which enables a leaf to routinely update another on its status. Another type of connection is a **conditional connection**, which specifies how one leaf responds to changes in the status of another leaf.

## Sentinel Leaves

A **leaf** is a discrete group of one or more devices which interacts with the Sentinel Hub. A leaf consists of a variety of sensors and outputs which can take a variety of forms and data types (see [API Section](#api)). When a leaf sensor updates, it will report to the backend in one of three options: instantly, periodically (e.g. only once a second), or only when requested. 

### Arduino Leaves
This project will come with a Arduino Library that allows you to easily implement the Leaf API for your Arduino IoT device. See more on the [Arduino](arduino) page.

### Software leaves
Leaves can also be software defined rather than existing as a physical device. For example, a user may want to have a leaf which checks the weather from a website and reports it to your thermostat to change the temperature. 


## The Sentinel API
The Sentinel API enables developers to set up a Sentinel Hub and easily configure and connect leaves.

### WebSockets
WebSockets support a more dynamic interface for interacting with leaves. Simply connect to your Sentinel Hub and start sending the messages defined in the **Leaf Messages** section below. 

### HTTP Interface
A Sentinel Hub contains a REST API to access and change leaves, conditions, devices and options.

| Name | HTTP Methods Supported | URL | Notes | Query Parameters |
| ---- | ---------------------- | --- | ----- | ---------------- |
| List Leaves | GET |  https://sentinel.iot/hub_id/leaves/ | None | None |
| View Leaf | GET |  https://sentinel.iot/hub_id/leaves/uuid | None | None |
| List Devices | GET |  https://sentinel.iot/hub_id/uuid/devices | None | None |
| View Device  | GET, POST |  https://sentinel.iot/hub_id/leaves/uuid/devices/name | Post only allowed for output devices | value: new value of device (POST only) |
| List Conditons | GET | https://sentinel.iot/hub/hub_id/conditions | None | None |
| View Conditon | GET, PUT, DELETE | https://sentinel.iot/hub/hub_id/conditions/name | PUT overrides an existing condition or creates one | predicate, action (PUT only; See [Conditions](#conditions) for format) |
| List Datastores | GET | https://sentinel.iot/hub/hub_id/datastores | None | None |
| View Datastore | GET, PUT, POST, DELETE | https://sentinel.iot/hub/hub_id/datastores/name | None | PUT: name, format <br> POST/PUT: value |
#### REST API Format Examples
Conditions:
```JSON
{
        "name": "lamp1_on",
        "predicate": ["=", ["f7bfd74c-a876-41da-ab37-6c5752e94a25", "rfid"], 3032042781.0],
        "action": {
            "action_type": "SET",
            "target": "b549b7b9-ca65-4552-9e72-3e07dec02568",
            "device": "left_lamp_on",
            "format": "bool",
            "value": true
        }
    }
```
Leaves:
```JSON
{
        "uuid": "f7bfd74c-a876-41da-ab37-6c5752e94a25",
        "name": "RFID Scanner",
        "model": "rfid01",
        "api_version": "0.1.0",
        "is_connected": false,
        "devices": [
            {
                "name": "rfid",
                "format": "number",
                "value": 3032042781.0,
                "mode": "IN"
            }
        ]
    }
```
Datastores:
```JSON
{
    "name": "is_home",
    "format": "bool",
    "value": "false"
}
```
### Leaf Messages
These are the messages a leaf will send to a Sentinel Hub. They are JSON messages in the following form.
```
{
    "type":"[TYPE]",
    "uuid":"[UUID]",
    "[ATTR1]":"[ATTR1_VALUE]",
    "[ATTR2]":"[ATTR2_VALUE]",
    ...
}
```
Only the type and uuid attributes are required, all other attributes are specific to the type of message you are trying to send. Type defines the type of message being sent. UUID is a [unique identifier](https://en.wikipedia.org/wiki/Universally_unique_identifier) for each leaf.

| Name | TYPE | Additional Attributes | Description | Required Uses |
| ---- | ---- | ---------- | ----------- | ---- |
| Name  | NAME | name: english name of the node | The name of the device | After receiving a GET_NAME or SET_NAME message |
| Config  | CONFIG | name: english name of leaf <br> model: model number of the leaf <br> api-version: version of api| Configuration of the device. Used to register a leaf with a hub. | After connecting to a hub or receiving a GET_CONFIG message|
| Device Status | DEVICE_STATUS | device: name of device <br> status: status of device | The status for a device will either be it's sensor value (for input devices) or it's current state (for output devices) | After receiving a SET_OUTPUT or GET_DEVICE command |
| List Options | OPTION_LIST | device: name of device list is for <br> options: list of all options and their value types | This command lists all the options available for a particular device. For leaf-wide options, the device will simply be 'leaf' | After receiving a LIST_OPTIONS message |
| Invalid Option | INVALID_OPTION |  device: name of device <br> option: name of unknown or invalid option | Used to respond to a request regarding an option that a device does not have | After receiving an invalid SET_OUTPUT or GET_DEVICE command |
| Option Update  | OPTION | device: name of device <br> option: name of option <br> value: current setting of option | Gives the current value of an option for a particular device. For leaf-wide options the device will be "leaf". | After recieving a SET_OPTION or GET_OPTION message |
| Invalid Value | INVALID_VALUE |  device: name of device <br> mode: option/device <br> value: the value that was invalid | Used to respond to a request regarding an improper value for an option or output | After receiving an invalid SET_OUTPUT or SET_OPTION command |
| Subscribe | SUBSCRIBE | sub_uuid: uuid of leaf to subscribe to <br> sub_device: device to subscribe to | Creates a subscription so that whenever a device or leaf is updated, the new status is sent to this leaf | None |
| Unsubscribe | UNSUBSCRIBE | sub_uuid: uuid of leaf to unsubscribe from <br> sub_device: device to unsubscribe from | Removes a subscription so you no longer receive updates from a device | None |
| Create Condition | CONDITION_CREATE | name: name of condition to create, predicate: predicate condition has to satisfy, action: what the condition does when the predicate is *true* | Creates a condition, deleting an existing condition with the same name if necessary | None |
| Delete Condition | CONDITION_DELETE | name: name of condition to delete | Deletes a condition | None |
| Create Datastore | DATASTORE_CREATE | name: name of datastore to create, format: data format of datastore, value: initial value for the datastore | Creates a datastore of a certain data type with an initial value | None |
| Update Datastore | DATASTORE_SET | name: name of datastore to create, value: new value for the datastore | Updates the current value of a datastore | None |
| Delete Datastore | DATASTORE_CREATE | name: name of datastore to create, format: data format of datastore, value: initial value for the datastore | Deletes the specified datastore | None |
#### Devices
This section deals with the various formats through which a device can report or receive data.
##### Device Config
When sending a list of devices each element of the list should be in the following format:
```
{
    "device":"[DEVICE_NAME]",
    "format":"[FORMAT_TYPE]",
    "mode":"[IN|OUT]",
}
```
The formats are listed below and mode must take the value of either IN or OUT.
##### Status Updates
When a device reports its status to a Sentinel Hub it will submit a message that follows the following format.
```
{
    "type":"DEVICE_STATUS",
    "uuid":"[UUID]",
    "device":"[DEVICE_NAME]"
    "format":"[FORMAT_TYPE]",
    "value":"[VALUE]",
    "[ATTR1]":"[ATTR1_VALUE]",
    "[ATTR2]":"[ATTR2_VALUE]",
    ...
}
```
##### Data formats
These are all of the currently supported data formats for leaf devices. If an unrecognized format is reported, it will default to being interpreted as a String.

| Name | JSON Representation | Description | Example |
| ---- | ------------------- | ----------- | ------- |
| Number | "number" | A number | { <br> "format":"number", <br> "value":12345132 <br> } |
| Number with Units | "number+units" | A number and some units | { <br> "format":"number+units", <br> "value":12345132, <br> units:"°C" <br>} |
| String | "string" | A text string | {<br>"format":"string",<br>"value":132123<br>} |
| Boolean | "bool" | A true/false value (0, 1, true, or false)| {<br>"format":"bool",<br>"value":true<br>} |


##### Options

Options are reported to the server in the following manner:
```
{
    "option":"[OPTION_NAME]",
    "format":"[DATA_FORMAT]",
    "value":"[VALUE]",
}
```
When you send a list of options, simply send a JSON list containing multiple options in this format.

### Hub Messages
These are the messages your leaf must receive and process in order to properly interact with the Sentinel IoT hub it is connected to. The format is as follows:

```JSON
{
    "type":"[OPTION_NAME]",
    "[ATTR1]":"[ATTR1_VALUE]",
    "[ATTR2]":"[ATTR2_VALUE]",
    ...
}
```

| Name | TYPE | Additional Attributes | Description | Required Processing |
| ---- | ---- | ---------- | ----------- | ---- |
| Set Name  | SET_NAME | name: new english name of the node | Changes the default name of the leaf | Update its name and send a NAME message |
| Get Name  | GET_NAME | None | Requests the name of the leaf | Send a NAME message |
| Get Config  | GET_CONFIG | None| Requests configuration of device, usually sent on initial connection. | Send a CONFIG message|
| List Devices  | LIST_DEVICES | None | Requests a list of sensors and all the necessary data to interface with them (see [Devices](#devices) for the form of each device) | Send a DEVICE_STATUS message for each device |
| Get Device | GET_DEVICE | device: name of device | The status for a device will either be it's sensor value (for input devices) or it's current state (for output devices) | Locate device and send DEVICE_STATUS or UNKNOWN_DEVICE message |
| Set Output | SET_OUTPUT | device: name of device <br> value: new value of output| Changes the output state, if valid, of device | Change the device's output value (or send INVALID_VALUE) and send a DEVICE_STATUS message|
| List Options | LIST_OPTIONS | device: name of device list is for | This command lists all the options available for a particular device. For leaf-wide options, the device will simply be 'leaf' | Send a OPTION_LIST message |
| Get Option  | GET_OPTION | device: name of device <br> option: name of option  | Requests the current value of an option for a particular device. For leaf-wide options the device will be "leaf". | Send an OPTION message or a UNKNOWN_DEVICE, UNKNOWN_OPTION |
| Set Option  | SET_OPTION | device: name of device <br> option: name of option <br> value: new setting of option | Changes the current value of an option for a particular device. For leaf-wide options the device will be "leaf". | Change option and send OPTION message if sucessful else send UNKNOWN_DEVICE, UNKNOWN_OPTION, or INVALID_VALUE |
| Invalid Device | INVALID_DEVICE | leaf: uuid of leaf <br> device: name of device that couldn't be accessed <br> reason: reason why it couldn't be accessed | Sent back to a device when it tries to access a device in an invalid way (such as in creating a condition) | None |
| Invalid Leaf | INVALID_LEAF | leaf: uuid of leaf that couldn't be accessed <br> reason: reason why it couldn't be accessed | Sent back to a device when it tries to access a leaf in an invalid way (such as in creating a condition) | None |

## Sentinel Backend
The Sentinel Backend processes all of features and interactions defined above. In the current version of Sentinel IoT, the backend is implemented in Django using Django Channels and WebSockets.

### Conditions
Conditions in Sentinel have two main components: a predicate and an action. The predicate is the "if" part of the condition; it is some expression that will evaluate to either *true* or *false*. The action is what will happen if the predicate evaluates to *true*. To create a condition, a leaf can send a message as follows:
```JSON
{
    "type": "CONDITION_CREATE",
    "name": "[name of condition]",
    "predicate": [predicate],
    "action": {
        "action_type": "[Action Type]",
        "target": "[Target of action]",
        "device": "[Device to target]",
        "value": "[Value to use in action]"
    }
}
```
### Predicates
Predicates use values available to the hub to control specific leaves and devices. If the types of a predicate do not match up, for example if you try to compare a string to a number device, the entire condition will be rejected.

##### Comparator Predicates
These predicates compare a device or datastore with another device or a specific value. They follow the following format:
```
["[Operator]", ["leaf1_uuid", "leaf1_device"], [value or another [leaf, device] pairing]]
```
Valid operators are as follows:

| Name | Operator |
| ---- | -------- |
| Equals | = |
| Does not equal | != |
| Less Than | < |
| Greater Than | >|
| Less Than or Equal To | <= |
| Greater Than or Equal To | >= |

##### Compound Predicates and Logical Operators
These are predicates that combine one or more predicates with some logical operator. They follow the following format:
```
["[Logical Operator]", [First Predicate], [Second Predicate (if applicable)]]
```
Valid logical operators are as follows:

| Operator | Number of Predicates |
| -------- | ------------------- |
| NOT | 1 |
| AND | 2 |
| OR | 2 |
| XOR | 2 |

### Actions
Actions specify what happens when a predicate is satisfied. Invalid or mismatched types will again cause the entire condition to be rejected. In addition, if an action targets a device, it must be an output device or the condition will be rejected.
Valid actions are as follows:

| Action Type | Description |
| ------ | ----------- |
| SET | Set an output device to a specific output value |
| CHANGE | Change a number or unit device to by a specific offset |

### Condition Examples
This condition would tell a leaf configured to open a door to open if a valid person scans in on another leaf configured to be a RFID reader.
```
{
    "type":"CONDITION_CREATE",
    "name":"open_door",
    "predicate":['OR', ["=", ["474a3f28-bb3e-478c-b723-1f7eb6b990c3", "rfid"], 303205852], ["=", ["474a3f28-bb3e-478c-b723-1f7eb6b990c3", "rfid"], 303204392]],
    "action": {
        "action_type":"SET",
        "target":"894c2698-0d0d-40cb-ab4d-2abad4d5f287",
        "device":"door_open",
        "value":true
    }
}
```