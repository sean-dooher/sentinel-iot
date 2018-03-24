export const TOGGLE_REGISTER_LEAF = 'TOGGLE_REGISTER_LEAF';
export const TOGGLE_DELETE_LEAF = 'TOGGLE_DELETE_LEAF';
export const ADD_REGISTER_LEAF_ERROR = 'ADD_REGISTER_LEAF_ERROR';
export const ADD_DELETE_LEAF_ERROR = 'ADD_DELETE_LEAF_ERROR';
export const CHANGE_REGISTRATION_TOKEN = 'CHANGE_REGISTRATION_TOKEN';

export function toggleRegisterLeaf() {
    return {
        type: TOGGLE_REGISTER_LEAF
    }
}

export function toggleDeleteLeaf() {
    return {
        type: TOGGLE_DELETE_LEAF
    }
}

export function addRegisterLeafError(message) {
    return {
        type: ADD_REGISTER_LEAF_ERROR,
        message
    }
}

export function addDeleteLeafError(message) {
    return {
        type: ADD_DELETE_LEAF_ERROR,
        message
    }
}

export function changeRegistrationToken(token) {
    return {
        type: CHANGE_REGISTRATION_TOKEN,
        token
    }
}

export function registerLeaf(hubId, uuid) {
    return dispatch => {
        let headers = Object.assign({}, window.postHeader);
        headers.body = JSON.stringify({uuid});
        fetch(window.host + "/hub/" + hubId + "/register", headers)
            .then(r => {
                if (r.ok) {
                    r.json().then(json => {
                            if (json.accepted) {
                                dispatch(changeRegistrationToken(json.token));
                            } else {
                                dispatch(addRegisterLeafError(("Error: " + json.reason)));
                            }
                        }
                    ).catch(e => dispatch(addRegisterLeafError("Error: error occurred while parsing response")));
                } else {
                    dispatch(addRegisterLeafError(("Error: " + r.statusText + " (" + r.status + ")")));
                }
            })
            .catch(e => dispatch(addRegisterLeafError("Error: an unknown error has occurred")));
    }
}

export function deleteLeaf(hubId, uuid) {
    return dispatch => {
        fetch(window.host + "/api/hub/" + hubId + "/leaves/" + uuid, window.deleteHeader).then(r => {
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