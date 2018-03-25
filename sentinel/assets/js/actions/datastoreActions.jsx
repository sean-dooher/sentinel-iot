export const TOGGLE_CREATE_DATASTORE = 'TOGGLE_CREATE_DATASTORE';
export const TOGGLE_DELETE_DATASTORE = 'TOGGLE_DELETE_DATASTORE';
export const ADD_CREATE_DATASTORE_ERROR = 'ADD_CREATE_DATASTORE_ERROR';
export const ADD_DELETE_DATASTORE_ERROR = 'ADD_DELETE_DATASTORE_ERROR';

export function toggleCreateDatastore() {
    return {
        type: TOGGLE_CREATE_DATASTORE
    }
}

export function toggleDeleteDatastore() {
    return {
        type: TOGGLE_DELETE_DATASTORE
    }
}

export function addCreateDatastoreError(message) {
    return {
        type: ADD_CREATE_DATASTORE_ERROR,
        message
    }
}

export function addDeleteDatastoreError(message) {
    return {
        type: ADD_DELETE_DATASTORE_ERROR,
        message
    }
}


export function createDatastore(hub, name, format, value, units=undefined) {
    return dispatch => {
        let data = {
            name,
            format,
            value,
            units
        };

        if(format !== 'string')
            data.value = JSON.parse(value);

        let headers = Object.assign({}, window.postHeader);
        headers.body = JSON.stringify(data);
        console.log(headers.body);
        fetch(window.host + "/api/hub/" + hub + "/datastores/", headers)
            .then(r => {
                if(r.ok) {
                    r.json().then(json => {
                            if (json.accepted) {
                                dispatch(toggleCreateDatastore());
                            } else {
                                dispatch(addCreateDatastoreError("Error: " + json.reason));
                            }
                        }
                    ).catch(e => dispatch(addCreateDatastoreError("Error: error occurred parsing response")));
                } else {
                    r.text().then(t => console.log(t));
                    dispatch(addCreateDatastoreError("Error: " + r.statusText + " (" + r.status + ")"));
                }
            })
            .catch(e => dispatch(addCreateDatastoreError("Error: an unknown error has occurred")));
    }
}

export function deleteDatastore(hub, name) {
    return dispatch => {
        fetch(window.host + "/api/hub/" + hub + "/leaves/" + uuid, window.deleteHeader).then(r => {
            if(r.ok) {
                dispatch(toggleDeleteLeaf());
            } else {
                r.json()
                    .then(json => dispatch(addDeleteLeafError("Error: " + json.detail)))
                    .catch(e =>  dispatch(addDeleteLeafError("Error: an unknown error has occurred")));
            }
        }).catch(e => dispatch(addDeleteLeafError(e.message)));
    }
}

export function updateDatastore(hub, name, format, value) {
    return dispatch => {
        let headers = Object.assign({}, window.putHeader);
        headers.body = JSON.stringify({value, format});
        fetch(window.host + "/api/hub/" + hub + "/datastores/" + name, headers)
            .then(r => {
                if(r.ok) {
                    r.json().then(json => {
                            if (!json.accepted) {
                                console.log("Error: " + json.reason);
                            }
                        }
                    ).catch(() => console.log("Error: error occured parsing response"))
                } else {
                    r.text().then(text => console.log(text));
                    console.log("Error: " + r.statusText + " (" + r.status + ")");
                }
            })
            .catch((e) => console.log("Error: an unknown error has occured\n"+e));
    }
}