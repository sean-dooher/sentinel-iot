export const TOGGLE_CREATE_CONDITION = 'TOGGLE_CREATE_CONDITION';
export const TOGGLE_DELETE_CONDITION = 'TOGGLE_DELETE_CONDITION';
export const ADD_CREATE_CONDITION_ERROR = 'ADD_CREATE_CONDITION_ERROR';
export const ADD_DELETE_CONDITION_ERROR = 'ADD_DELETE_CONDITION_ERROR';

export function toggleCreateCondition() {
    return {
        type: TOGGLE_CREATE_CONDITION
    }
}

export function toggleDeleteCondition(name='') {
    return {
        type: TOGGLE_DELETE_CONDITION,
        name
    }
}

export function addCreateConditionError(message) {
    return {
        type: ADD_CREATE_CONDITION_ERROR,
        message
    }
}

export function addDeleteConditionError(message) {
    return {
        type: ADD_DELETE_CONDITION_ERROR,
        message
    }
}


export function createCondition(hub, name, predicate, action) {
    return dispatch => {
        let condition = {
            name,
            predicate,
            action
        };

        let headers = Object.assign({}, window.postHeader);
        headers.body = JSON.stringify(condition);
        fetch(window.host + "/api/hub/" + hub + "/conditions/", headers)
            .then(r => {
                if(r.ok) {
                    r.json().then(json => {
                            if (json.accepted) {
                                this.toggleConditionModal();
                            } else {
                                dispatch(addCreateConditionError("Error: " + json.reason));
                            }
                        }
                    ).catch(e => dispatch(addCreateConditionError("Error: error occurred parsing response")))
                } else {
                    r.text().then(t => console.log(t));
                    dispatch(addCreateConditionError("Error: " + r.statusText + " (" + r.status + ")"));
                }
            })
            .catch(e => dispatch(addCreateConditionError("Error: an unknown error has occurred")));

    }
}

export function deleteCondition(hub, name) {
    return dispatch => {
        fetch(window.host + "/api/hub/" + hub + "/conditions/" + name, window.deleteHeader).then(r => {
            if(r.ok) {
                dispatch(toggleDeleteCondition());
            } else {
                r.json()
                    .then(json => dispatch(addDeleteConditionError("Error: " + json.detail)))
                    .catch(e =>  dispatch(addDeleteConditionError("Error: an unknown error has occurred")));
            }
        }).catch(e => dispatch(addDeleteConditionError(e.message)));
    }
}

export function updateCondition(hub, name, predicate, action) {
    return dispatch => {
        console.error("Not implemented yet");
    }
}