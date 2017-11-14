# Sentinel IOT
Sentinel IOT is a robust and exstensible platform for home automation and IOT development.

Sentinel consists of a few components:
 * Sentinel Hub - The front end interface that allows a user to easily interface with all of the other components
 * Sentinel API - This is the standard interface that allows all of the pieces of Sentinel to
 * Sentinel Backend - This is the piece that connects all of Sentinel together and allows it to
 * Sentinel Arduino Leaf - Library for easily creating devices that implement the Sentinel API with Arduinos
 * Sentinel Alexa - [[[[ARJUN ADD SOME INFO HERE]]]]

## Sentinel Hub

![Hub Mockup](https://i.imgur.com/H0Fy8BH.png)

This is a general mockup of the Hub frontend that a general user will interface with. Nodes in your "hub" (grouping of IoT devices) will be displayed on the same screen and you can drag arrows between nodes to create relations or conditions. The arrow in the bottom right will be used to add software nodes that run on the server for ease of use and implementation.

This is planned to be expanded to include a variety of display options to allow the user to find a comfortable way to control their network of IOT devices. Customizations will include a tabular view, hiding conditions/nodes, custom formatting, etc.

This is planned to be a responsive website so you can access and control all your devices from a phone or tablet as well as your desktop computer or laptop.

## Sentinel Leaves

A "leaf" or "node" is a discrete device that implements the Sentinel API. These devices can be physical or software devices and are one of the core components of the system. A leaf consists of a variety of sensors and outputs which can take a variety of forms and data types (see [API Section](#api)). When a leaf sensor updates, it will report to the backend in one of three options: instantly, at some maximal interval (e.g. only once a second), or only when requested. Once connected to the server, leaves have a variety of options that can be configured by the server to change how they respond. Leaves can also ask the server to pass a JSON message to another leaf in cases that you need to transfer larger amounts of data between nodes (note that using this to bypass the conditional network already implement is **NOT** recommended)\

### Arduino Leaves
This project will come with a Arduino Library that allows you to easily implement the Leaf API for your Arduino IoT device. Various examples that we used in our apartment are included! See more on the [Arduino](arduino) page.


## Sentinel API
The API is how  you interface with both the backend and how the back end interfaces with your Sentinel Leaves. We have both an HTTP and a WebSocket interface both of which us the same JSON responses.

### WebSockets
WebSockets allow for a much more free form interface, simply connect to your "hub" and start sending the following messages. The HTTP interface is more formalized to allow for easier to read API calls. We recommend using WebSockets as the primary communication tool for a Leaf and your Hub. The HTTP is for when a response is *necessary* for your particular use case.

### HTTP Interface
This table descripes the various ways to use the HTTP API to interface with your Hub. The responses will be the same as the WebSockets API (see [Hub Messages](#hubmess)). Authentication through OAuth?(need to look into that). You can also go to one of the "broader" urls (/leaves/, /devices/, /hub/) and send a JSON request identical to the WebSockets ones below.

| Name | Reciever | HTTP Method | URL |
| ---- | -------- | ----------- | --- |
| Setting Set  | Hub | POST |  https://myhub.sentinel.iot/\<hub_id\>/config/?option=\<option\>&value=\<value\> |
| Setting Get  | Hub | GET |  https://myhub.sentinel.iot/\<hub_id\>/config/?option=\<option\> |
| List Leaves  | Hub | GET |  https://myhub.sentinel.iot/\<hub_id\>/leaves/?list=1 |
| List Devices  | Leaf | GET |  https://myhub.sentinel.iot/\<hub_id\>/\<leaf_id\>/devices/?list=1 |
| Output Set  | Leaf | POST |  https://myhub.sentinel.iot/\<hub_id\>/\<leaf_id\>/\<device_id\>/?value=\<value\> |
| Sensor Get  | Leaf | GET |  https://myhub.sentinel.iot/\<hub_id\>/\<leaf_id\>/\<device_id\>/ |
| List Options | Leaf | GET |  https://myhub.sentinel.iot/\<hub_id\>/\<leaf_id\>/config/?list=1 |
| Option Set  | Leaf | POST |  https://myhub.sentinel.iot/\<hub_id\>/\<leaf_id\>/config/?option=\<option\>&value=\<value\> |
| Option Get  | Leaf | GET |  https://myhub.sentinel.iot/\<hub_id\>/\<leaf_id\>/config/?option=\<option\> |

Note that these are ways to interface with the server for a client app. Ways for Leaves to interface via HTML will be added soon.

### Leaf Messages
These are the messages a leaf will send to a hub. They are JSON messages in the following form.
```
{
    'type':'[TYPE]',
    'uuid':'[UUID]',
    '[ATTR1]':'[ATTR1_VALUE]',
    '[ATTR2]':'[ATTR2_VALUE]',
    ...
}
```
Only the type and uid attributes are required, all other attributes are specific to the type of message you are trying to send. Type is for the type of message, UUID is a [unique identifier](https://en.wikipedia.org/wiki/Universally_unique_identifier) for each leaf.

| Name | TYPE | Additional Attributes | Description | Required Uses |
| ---- | ---- | ---------- | ----------- | ---- |
| Name  | NAME | name: english name of the node | The name of the device | After receiving a GET_NAME or SET_NAME message |
| Config  | CONFIG | name: english name of leaf <br> model: model number of the leaf <br> api-version: version of api| Configuration of the device. Used to register a leaf with a hub. | After connecting to a hub or recieving a GET_CONFIG message|
| List Devices  | DEVICE_LIST | devices: JSON list of all devices, their formats, and their mode (input/output) | This returns a list of sensors and all the necessary data to interface with them (see [Devices](#devices) for the form of each device) | After recieving a LIST_DEVICES message| 
| Device Status | DEVICE_STATUS | device: name of device <br> status: status of device | The status for a device will either be it's sensor value (for input devices) or it's current state (for output devices) | After recieving a SET_OUTPUT or GET_DEVICE command |
| Unknown Device | UNKNOWN_DEVICE |  device: name of unknown device | Used to respond to a request regarding a device that the leaf is not configured to accept | After recieving an invalid SET_OPTION or GET_OPTION command |
| List Options | OPTION_LIST | device: name of device list is for <br> options: list of all options and their value types | This command lists all the options available for a particular device. For leaf-wide options, the device will simply be 'leaf' | After recieving a LIST_OPTIONS message |
| Unknown Option | UNKNOWN_OPTION |  device: name of device <br> option: name of unknown option | Used to respond to a request regarding an option that a device does not have | After recieving an invalid SET_OUTPUT or GET_DEVICE command |
| Option Update  | OPTION | device: name of device <br> option: name of option <br> value: current setting of option | Gives the current value of an option for a particular device. For leaf-wide options the device will be "leaf". | After recieving a SET_OPTION or GET_OPTION message |
| Invalid Value | INVALID_VALUE |  device: name of device <br> mode: option/device <br> value: the value that was invalid | Used to respond to a request regarding an improper value for an option or output | After recieving an invalid SET_OUTPUT or SET_OPTION command |
#### Devices
This section deals with the various formatting a device
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
When a device reports it's status to the Hub it will submit a message that looks like this:
```
{
    'type':'DEVICE_STATUS',
    'uuid':'[UUID]',
    'device':'[DEVICE_NAME]'
    'status': {
        'format':'[FORMAT_TYPE]',
        'value':'[VALUE]',
        '[ATTR1]':'[ATTR1_VALUE]',
        '[ATTR2]':'[ATTR2_VALUE]',
        ...
    }
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
Both Leaves themselves and their devices can have options.\
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
These are the messages your leaf must recieve and process in order to properly interact with the Sentinel IoT hub it is connected to. The format is as follows:
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
| Set Name  | SET_NAME | name: new english name of the node | Changes the default name of the leaf | The leaf should update its name and send a NAME message |
| Get Name  | GET_NAME | None | Requests the name of the leaf | The leaf should send a NAME message |
| Get Config  | GET_CONFIG | None| Requests configuration of device, usually sent on initial connection. | Send a CONFIG message|
| List Devices  | LIST_DEVICES | None | Requests a list of sensors and all the necessary data to interface with them (see [Devices](#devices) for the form of each device) | Send a  DEVICE_LIST message |
| Get Device | GET_DEVICE | device: name of device | The status for a device will either be it's sensor value (for input devices) or it's current state (for output devices) | Locate device and send DEVICE_STATUS or UNKNOWN_DEVICE message |
| Set Output | SET_OUTPUT | device: name of device <br> value: new value of output| Changes the output state, if valid, of device | Change the device's output value (or send INVALID_VALUE) and send a DEVICE_STATUS message|
| List Options | LIST_OPTIONS | device: name of device list is for | This command lists all the options available for a particular device. For leaf-wide options, the device will simply be 'leaf' | Send a OPTION_LIST message |
| Get Option  | GET_OPTION | device: name of device <br> option: name of option  | Requests the current value of an option for a particular device. For leaf-wide options the device will be "leaf". | Send an OPTION message or a UNKNOWN_DEVICE, UNKNOWN_OPTION |
| Set Option  | SET_OPTION | device: name of device <br> option: name of option <br> value: new setting of option | Changes the current value of an option for a particular device. For leaf-wide options the device will be "leaf". | Change option and send OPTION message if sucessful else send UNKNOWN_DEVICE, UNKNOWN_OPTION, or INVALID_VALUE |
## Sentinel Backend

The backend is where the magic happens. It's what takes all of these parts and combines them together into something that actually works! The functionality is broadly based on the app IFTT that I used back in highschool (but uh hopefully better because that app was super buggy sometimes). The backend is implemented in Django using Django Channels and websockets.

### Conditions
Condtions are a set of boolean logically statements that evaluate to either _true_ or _false_. There can be either one or multiply statements connected by AND, OR, NOR, NOT, XOR, XNOR, NAND, NOR, etc. Once a condition is satisfied (i.e. the whole statement is true) some code will be run. This code could set a value of another leaf, change a setting, send an alert, post a message on a social media site, or whatever else you want to program it to do. More info on this will be added later.

### Websockets and HTTP

There will be two ways for leaves to interface with the backend: websockets (for real-time updates) and http for a more RESTful interface. Either way is fine, but I find websockets to be generally easier to work with. The HTTP interface will be good if you are writing some sort of client app for Sentinel. More info on this is in the IoT section.

TODO:
*Add CONFIG_COMPLETE
*Change DEVICE_STATUS attributes
*ADD More info to config on limitations