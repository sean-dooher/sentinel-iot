# **Sentinel IOT** 

## Sentinel Hub

![Hub Mockup](https://i.imgur.com/H0Fy8BH.png)

<br>
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
This table contains the various ways to use the HTTP API to interface with your Hub. The responses will be the same as the WebSockets API (see [Hub Messages](#hubmess)). Authentication through OAuth?(need to look into that). You can also go to one of the "broader" urls (/leaves/, /devices/, /hub/) and send a JSON request identical to the WebSockets ones below.

| Name | Reciever | HTTP Method | URL |
| ---- | -------- | ----------- | --- |
| Setting Set  | Hub | POST |  https://myhub.sentinel.iot/<hub_id\>/config/?option=\<option\>&value=<value\> |
| Setting Get  | Hub | GET |  https://myhub.sentinel.iot/<hub_id\>/config/?option=\<option\> |
| List Leaves  | Hub | GET |  https://myhub.sentinel.iot/<hub_id\>/leaves/?list=1 |
| List Devices  | Leaf | GET |  https://myhub.sentinel.iot/<hub_id\>/<leaf_id\>/devices/?list=1 |
| Output Set  | Leaf | POST |  https://myhub.sentinel.iot/<hub_id\>/<leaf_id\>/<device_id\>/?value=<value\> |
| Sensor Get  | Leaf | GET |  https://myhub.sentinel.iot/<hub_id\>/<leaf_id\>/<device_id\>/ |
| List Options | Leaf | GET |  https://myhub.sentinel.iot/<hub_id\>/<leaf_id\>/config/?list=1 |
| Option Set  | Leaf | POST |  https://myhub.sentinel.iot/<hub_id\>/<leaf_id\>/config/?option=<option\>&value=<value\> |
| Option Get  | Leaf | GET |  https://myhub.sentinel.iot/<hub_id\>/<leaf_id\>/config/?option=<option\> |


### Leaf Messages
These are the messages a leaf will send to a Sentinel Hub. They are JSON messages in the following form.
```
{
    'type':'[TYPE]',
    'uuid':'[UUID]',
    '[ATTR1]':'[ATTR1_VALUE]',
    '[ATTR2]':'[ATTR2_VALUE]',
    ...
}
```
Only the type and uuid attributes are required, all other attributes are specific to the type of message you are trying to send. Type defines the type of message being sent. UUID is a [unique identifier](https://en.wikipedia.org/wiki/Universally_unique_identifier) for each leaf.

| Name | TYPE | Additional Attributes | Description | Required Uses |
| ---- | ---- | ---------- | ----------- | ---- |
| Name  | NAME | name: english name of the node | The name of the device | After receiving a GET_NAME or SET_NAME message |
| Config  | CONFIG | name: english name of leaf <br> model: model number of the leaf <br> api-version: version of api| Configuration of the device. Used to register a leaf with a hub. | After connecting to a hub or recieving a GET_CONFIG message|
| Device Status | DEVICE_STATUS | device: name of device <br> value: status of device <br> format: format of device <br> mode: mode of device ("IN" or "OUT") | The status for a device will either be it's sensor value (for input devices) or it's current state (for output devices) | After recieving a SET_OUTPUT or GET_DEVICE command |
| Unknown Device | UNKNOWN_DEVICE |  device: name of unknown device | Used to respond to a request regarding a device that the leaf is not configured to accept | After recieving an invalid SET_OPTION or GET_OPTION command, send one for all devices after getting DEVICE_LIST message |
| List Options | OPTION_LIST | device: name of device list is for <br> options: list of all options and their value types | This command lists all the options available for a particular device. For leaf-wide options, the device will simply be 'leaf' | After recieving a LIST_OPTIONS message |
| Unknown Option | UNKNOWN_OPTION |  device: name of device <br> option: name of unknown option | Used to respond to a request regarding an option that a device does not have | After recieving an invalid SET_OUTPUT or GET_DEVICE command |
| Option Update  | OPTION | device: name of device <br> option: name of option <br> value: current setting of option | Gives the current value of an option for a particular device. For leaf-wide options the device will be "leaf". | After recieving a SET_OPTION or GET_OPTION message |
| Invalid Value | INVALID_VALUE |  device: name of device <br> mode: option/device <br> value: the value that was invalid | Used to respond to a request regarding an improper value for an option or output | After recieving an invalid SET_OUTPUT or SET_OPTION command |
| Subscribe | SUBSCRIBE | sub_uuid: uuid of leaf to subscribe to <br> sub_device: device to subscribe to (leaf for every device) | Used to register a subscription to another leaf's device for notifications whenever a value updates | None |
| Unsubscribe | UNSUBSCRIBE | sub_uuid: uuid of leaf to unsubscribe from <br> sub_device: device to unsubscribe from (leaf for every device) | Used to remove a subscription from another leaf's device | None |
| Datastore Create | DATASTORE_CREATE | name: name of datastore to create <br> value: initial value for datastore to have <br> format: format of datastore <br> permissions(optional): dictionary of uuid to permissions for this datastore | Create a datastore. See (#datastore) section | None |
| Get Datastore | DATASTORE_GET | name: name of datastore to get value of | attempt to get the current value of a datastore | None |
| Set Datastore | DATASTORE_SET | name: name of datastore to set value of <br> value: new value of datastore | attempt to set the value of a datastore | None |
| Delete Datastore | DATASTORE_DELETE | name: name of datastore to delete | attempt to delete a datastore | None |
| Create Condition | CONDITION_CREATE | name: name of condition to create <br> predicate: condition that must be true for action to execute <br> action: action for condition to run once the predicate is satisfied | Creates a condition with the name "name" overriding it if one already exists | None |
| Delete Condition | CONDITION_DELETE | name: name of condition to delete | attempt to delete the condition | None |
#### Devices
This section deals with the various formats through which a device can report or receive data.
##### Device Config
When sending a list of devices each element of the list should be in the following format:
```
{
    'device':'[DEVICE_NAME]',
    'format':'[FORMAT_TYPE]',
    'mode':'[IN|OUT]',
}
```
The formats are listed below and mode must take the value of either IN or OUT.
##### Status Updates
When a device reports its status to a Sentinel Hub it will submit a message that follows the following format.
```
{
    'type':'DEVICE_STATUS',
    'uuid':'[UUID]',
    'device':'[DEVICE_NAME]'
    'format':'[FORMAT_TYPE]',
    'value':'[VALUE]',
    '[ATTR1]':'[ATTR1_VALUE]',
    '[ATTR2]':'[ATTR2_VALUE]',
    ...
}
```
##### Data formats
These are all of the currently supported data formats for leaf devices. If an unrecognized format is reported, it will default to being interpreted as a String.

| Name | JSON Representation | Description | Example |
| ---- | ------------------- | ----------- | ------- |
| Number | 'number' | A number | { <br> 'format':'number', <br> 'value':12345132 <br> } |
| Number with Units | 'number+units' | A number and some units | { <br> 'format':'number+units', <br> 'value':12345132, <br> units:'°C' <br>} |
| String | 'string' | A text string | {<br>'format':'string',<br>'value':132123<br>} |
| Boolean | 'bool' | A true/false value represented as  either a 0 or a 1 | {<br>'format':'bool',<br>'value':0<br>} |


##### Options

Options are reported to the server in the following manner:
```
{
    'option':'[OPTION_NAME]',
    'format':'[DATA_FORMAT]',
    'value':'[VALUE]',
}
```
When you send a list of options, simply send a JSON list containing multiple options in this format.

### Hub Messages
These are the messages your leaf must receive and process in order to properly interact with the Sentinel IoT hub it is connected to. The format is as follows:
```
{
    'type':'[OPTION_NAME]',
    'uuid':[UUID of Leaf],
    'hubid':[ID of Hub],
    '[ATTR1]':'[ATTR1_VALUE]',
    '[ATTR2]':'[ATTR2_VALUE]',
    ...
}
```
| Name | TYPE | Additional Attributes | Description | Required Processing |
| ---- | ---- | ---------- | ----------- | ---- |
| Get Configuration  | GET_CONFIG | None| Requests configuration of device, usually sent on initial connection. | Send a CONFIG message|
| Configuration Complete | CONFIG_COMPLETE | None | Sent when configuration of your leaf is completed | None, though you want to wait until you receive this before sending any messages to the hub |
| List Devices  | LIST_DEVICES | None | Requests the current status of all sensors (see [Devices](#devices) for the form of each device) | Send a DEVICE_STATUS message for all devices |
| Get Device | GET_DEVICE | device: name of device | The status for a device will either be it's sensor value (for input devices) or it's current state (for output devices) | Locate device and send DEVICE_STATUS or UNKNOWN_DEVICE message |
| Set Output | SET_OUTPUT | device: name of device <br> value: new value of output| Changes the output state, if valid, of device | Change the device's output value (or send INVALID_VALUE) and send a DEVICE_STATUS message |
| Change Output | CHANGE_OUTPUT | device: name of device <br> value: new value to add to device's current number | Changes an output device by a certain amount (device must be either a number device or a units device) | Change the device's output value (or send INVALID_VALUE) and send a DEVICE_STATUS message |
| List Options | LIST_OPTIONS | device: name of device list is for | This command lists all the options available for a particular device. For leaf-wide options, the device will simply be 'leaf' | Send a OPTION_LIST message |
| Get Option  | GET_OPTION | device: name of device <br> option: name of option  | Requests the current value of an option for a particular device. For leaf-wide options the device will be "leaf". | Send an OPTION message or a UNKNOWN_DEVICE, UNKNOWN_OPTION |
| Set Option  | SET_OPTION | device: name of device <br> option: name of option <br> value: new setting of option | Changes the current value of an option for a particular device. For leaf-wide options the device will be "leaf". | Change option and send OPTION message if sucessful else send UNKNOWN_DEVICE, UNKNOWN_OPTION, or INVALID_VALUE |
| Subscription Update | SUBSCRIPTION_UPDATE | sub_uuid: uuid of leaf you subscribed to <br> sub_device: name of device you subscribed to <br> message: message from your subscription (device_status, etc) | None |
| Permission Denied | PERMISSION_DENIED | request: request type that was denied, <br> name/uuid/device (optional): identifier of denied resource | Given when the leaf tries to access something it does not have permission to | None |
| Datastore Created | DATASTORE_CREATED | name: name of datastore <br> format: data format of datastore | Informs the user a datastore has been successfully created | None |
| Datastore Deleted | DATASTORE_DELETED | name: name of datastore | Informs the user a datastore has been successfully deleted | None |
## Sentinel Backend
The Sentinel Backend processes all of features and interactions defined above. In the current version of Sentinel IoT, The Sentinel is implemented in Django using Django Channels and WebSockets.

### Conditions
Conditions are a complination of a **predicate** (logical statements that evaluate to either _true_ or _false_) and an **action** to execute when the predicate is satisfied. To create a condition, a message like this should be sent:
```
{
    'type': 'CONDITION_CREATE',
    'uuid': [Admin Leaf UUID],
    'predicate': [predicate],
    'action': [action]
}
```
#### Predicates
Predicates are given in [Polish Notation](https://en.wikipedia.org/wiki/Polish_notation) using lists as brackets.
##### Operations
An operator predicate can compare two values. These values can either be device values or literals. See below for a few examples.
```
['[Operator]', ['[Leaf UUID]', '[Device Name']], [Literal or another [uuid, device] pairing]]
```
| Name | Operator |
| --------- | ---- |
| Equals | = |
| Does not equals | != |
| Greater than | > |
| Less than | < |
| Greater than or equal to | >= |
| Less than or equal to | <= |
<br>
Examples:
Device and literal:
```
['=', ['06202ef5-bec3-46d1-b39c-b88910a0ab07', 'sensor_1'], 320212.5]
```
Two devices:
```
['>', ['06202ef5-bec3-46d1-b39c-b88910a0ab07', 'sensor_1'], ['230025f0-9350-4578-9b95-44cb188e70a3', 'sensor_2']]
```
##### Connectors
You can connect two or more predicates together using the boolean connectors in the table below. These can be nested to an arbitrary depth. The format is as follows: <br>
Binary connector:
```
['[Connector]', [Predicate1], [Predicate 2]]
```
Unary connector:
```
['[Connector]', [Predicate]]
```
| Connector | Type |
| --------- | ---- |
| AND | Binary |
| OR | Binary |
| XOR | Binary |
| NOT | Unary |
<br>
Examples:
Unary:
```
['NOT', ['>', ['ce505754-341c-48f8-b7f2-2626041df01c', 'sensor_1'], 0]]
```
Binary:
```
['AND', ['>', ['ce505754-341c-48f8-b7f2-2626041df01c', 'sensor_1'], 0], ['<', ['datastore', '313123'], -123]]
```
Nested:
```
['NOT', ['XOR', ['>', ['ce505754-341c-48f8-b7f2-2626041df01c', 'sensor_1'], 0], ['<', ['datastore', '313123'], -123]]]
```
#### Actions
An action takes the following form:
```
{
    'action_type': ['SET' or 'CHANGE'],
    'target': [uuid of leaf to perform action on],
    'device': [device of leaf to perform action on],
    'value': [value to set/change device by]
}
```
#### Examples
```
{
    'type': 'CONDITION_CREATE',
    'uuid': '230025f0-9350-4578-9b95-44cb188e70a3',
    'predicate':['AND', ['NOT', ['=', ['ce505754-341c-48f8-b7f2-2626041df01c', 'sensor_1'], 1323112], ['=', ['2a11abdc-be9e-4646-96f5-100ee55211e7', 'sensor_2'], 312312]]],
    'action': {
        'action_type': 'SET',
        'target': '2a11abdc-be9e-4646-96f5-100ee55211e7',
        'device': 'output_sensor',
        'value': 33790

    }
}
```
### WebSockets and HTTP

Currently, there are two channels for leaves to interface with the backend: WebSockets (for real-time updates) and HTTP for a more RESTful interface. 