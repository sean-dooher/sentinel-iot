import ReconnectingWebSocket from "reconnecting-websocket/dist/index";
import {handleWebsocketMessage} from "./apiHandlers";

export function handleToggleCreateHub(state, action) {
    let newState = Object.assign({}, state);
    newState.hub.showCreate = !state.hub.showCreate;

    if (newState.hub.showCreate)
        newState.hub.createErrors = [];

    return newState;
}

export function handleToggleDeleteHub(state, action) {
    let newState = Object.assign({}, state);
    newState.hub.showDelete = !state.hub.showDelete;

    if (newState.hub.showDelete)
        newState.hub.deleteErrors = [];

    return newState;
}

export function handleActiveHubUpdate(state, action) {
    let newState = Object.assign({}, state);
    if (action.id === -1)
        newState.hub.active = newState.api.hubs.length > 0 ? newState.api.hubs[0].id : -1;
    else if (action.id !== -1)
        newState.hub.active = action.id;

    if(!window.info.demo)
        connectToHub(newState.hub.active);

    return newState;
}

export function handleAddCreateError(state, action) {
    let newState = Object.assign({}, state);
    newState.hub.createErrors = newState.hub.createErrors.concat(action.message).slice(-3);
    return newState;
}

export function handleAddDeleteError(state, action) {
    let newState = Object.assign({}, state);
    newState.hub.deleteErrors = newState.hub.deleteErrors.concat(action.message).slice(-3);
    return newState;
}


function connectToHub(id) {
    if (window.socket) {
        window.socket.close(1000, '', {keepClosed: true});
    }

    if (location.protocol === 'https:')
        window.socket = new ReconnectingWebSocket("wss://" + location.host + "/client/" + id);
    else
        window.socket = new ReconnectingWebSocket("ws://" + location.host + "/client/" + id);

    window.socket.onmessage = window.websocketMessageHandler;
    window.socket.onopen = (e) => {
        console.log("Connecting to hub");
        let messages = [{
            stream: 'leaves',
            payload: {
                action: 'subscribe',
                data: {action: 'create'}
            }
        }, {
            stream: 'leaves',
            payload: {
                action: 'subscribe',
                data: {action: 'update'}
            }
        }, {
            stream: 'leaves',
            payload: {
                action: 'subscribe',
                data: {action: 'delete'}
            }
        }, {
            stream: 'leaves',
            payload: {
                action: 'list'
            }
        }];
        for (let message of messages) {
            window.socket.send(JSON.stringify(message));
        }
        // set timeouts to prevent server from forcibly disconnecting
        setTimeout(() => {
            for (let message of messages) {
                message.stream = 'datastores';
                window.socket.send(JSON.stringify(message));
            }
        }, 5);
        setTimeout(() => {
            for (let message of messages) {
                message.stream = 'conditions';
                window.socket.send(JSON.stringify(message));
            }
        }, 10);
    }
}