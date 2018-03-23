// TODO: sendCreateHub, deleteHub, changeHub

import {updateHubs, updateConditions, updateTriggers, updateLeaves, updateDatastores, refreshHubs} from "./apiActions";
import {handleWebsocketMessage} from "../reducers/apiHandlers";
import ReconnectingWebSocket from "reconnecting-websocket";
import 'whatwg-fetch';


export const TOGGLE_CREATE_HUB = 'TOGGLE_CREATE_HUB';
export const TOGGLE_DELETE_HUB = 'TOGGLE_DELETE_HUB';
export const ADD_CREATE_ERROR = 'ADD_CREATE_ERROR';
export const ADD_DELETE_ERROR = 'ADD_DELETE_ERROR';
export const UPDATE_ACTIVE_HUB = 'UPDATE_ACTIVE_HUB';

export function toggleCreateHub() {
    return {
        type: TOGGLE_CREATE_HUB
    }
}

export function toggleDeleteHub() {
    return {
        type: TOGGLE_DELETE_HUB
    }
}

export function addCreateError(message) {
    return {
        type: ADD_CREATE_ERROR,
        message
    }
}

export function addDeleteError(message) {
    return {
        type: ADD_DELETE_ERROR,
        message
    }
}

export function deleteHub(id) {
    return dispatch => {
        fetch(window.host + "/api/hub/" + id, window.deleteHeader)
            .then(r => {
                if (r.ok) {
                    dispatch(toggleDeleteHub());
                    dispatch(updateActiveHub(-1));
                } else {
                    r.json()
                        .then(json => dispatch(addDeleteError("Error: " + json.detail)))
                        .catch(e => dispatch(addDeleteError("Error: an unknown error has occurred")));
                }
            })
            .catch(r => dispatch(addDeleteError(r)))
    }
}

export function createHub(name) {
    return dispatch => {
        let headers = Object.assign({}, window.postHeader);
        headers.body = JSON.stringify({name});
        fetch(window.host + "/api/hub/", headers)
            .then(response => {
                if (response.ok) {
                    response.json().then(json => {
                        if (json.accepted) {
                            dispatch(toggleCreateHub());
                            dispatch(refreshHubs());
                        } else {
                            dispatch(addCreateError("Error adding hub: " + json.reason));
                        }
                    })
                        .catch(reason => {
                            dispatch(addCreateError("Error adding hub: " + reason));
                        });
                }
                else {
                    response.text().then(text => dispatch(addCreateError("Error adding hub: " + text)));
                }
            });
    }
}

export function updateActiveHub(id) {
    return {
        type: UPDATE_ACTIVE_HUB,
        id
    }
}

export function changeHub(id) {
    return dispatch => {
        dispatch(updateActiveHub(id));
        if (window.info.demo) {
            fetch(window.host + "/api/hub/" + id + "/leaves", window.getHeader)
                .then(t => t.json())
                .then(leaves => dispatch(updateLeaves(leaves)));
            fetch(window.host + "/api/hub/" + id + "/conditions", window.getHeader)
                .then(t => t.json())
                .then(conditions => dispatch(updateConditions(conditions)));
            fetch(window.host + "/api/hub/" + id + "/datastores", window.getHeader)
                .then(t => t.json())
                .then(datastores => dispatch(updateDatastores(datastores)));
            return;
        }
        if (window.socket) {
            window.socket.close(1000, '', {keepClosed: true});
        }
        if (id !== -1) {
            window.socket = new ReconnectingWebSocket("ws://" + location.host + "/client/" + id);
            window.socket.onmessage = (message) => handleWebsocketMessage(dispatch, message);
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
                // set timeouts to prevent server from forcibly disconnected
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
    }
}
