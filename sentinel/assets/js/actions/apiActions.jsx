import {updateActiveHub} from "./navigationActions";

export const UPDATE_HUBS = "UPDATE_HUBS";
export const UPDATE_LEAVES = "UPDATE_LEAVES";
export const UPDATE_TRIGGERS = "UPDATE_TRIGGERS";
export const UPDATE_DATASTORES = "UPDATE_DATASTORES";
export const UPDATE_CONDITIONS = "UPDATE_CONDITIONS";

export const ADD_LEAF = "ADD_LEAF";
export const UPDATE_LEAF = "UPDATE_LEAF";
export const DELETE_LEAF = "DELETE_LEAF";

export const ADD_DATASTORE = "ADD_LEAF";
export const UPDATE_DATASTORE = "UPDATE_DATASTORE";
export const DELETE_DATASTORE = "DELETE_DATASTORE";

export const ADD_CONDITION = "ADD_CONDITION";
export const UPDATE_CONDITION = "UPDATE_CONDITION";
export const DELETE_CONDITION = "DELETE_CONDITION";

export const ADD_TRIGGER = "ADD_TRIGGER";
export const UPDATE_TRIGGER = "UPDATE_TRIGGER";
export const DELETE_TRIGGER = "DELETE_TRIGGER";

export function updateDatastores(datastores) {
    return {
        type: UPDATE_DATASTORES,
        datastores
    }

}

export function updateLeaves(leaves) {
    return {
        type: UPDATE_LEAVES,
        leaves
    }

}

export function updateHubs(hubs) {
    return {
        type: UPDATE_HUBS,
        hubs
    }
}

export function updateConditions(conditions) {
    return {
        type: UPDATE_CONDITIONS,
        conditions
    }
}

export function updateTriggers(triggers) {
    return {
        type: UPDATE_TRIGGERS,
        triggers
    }
}

export function addDatastore(datastore){
    return {
        type: ADD_DATASTORE,
        datastore
    }
}

export function deleteDatastore(name){
    return {
        type: DELETE_DATASTORE,
        name
    }
}

export function updateDatastore(datastore){
    return {
        type: UPDATE_DATASTORE,
        datastore
    }
}

export function addLeaf(leaf){
    return {
        type: ADD_LEAF,
        leaf
    }
}

export function deleteLeaf(uuid){
    return {
        type: DELETE_LEAF,
        uuid
    }
}

export function updateLeaf(leaf){
    return {
        type: UPDATE_LEAF,
        leaf
    }
}

export function addCondition(condition){
    return {
        type: ADD_CONDITION,
        condition
    }
}

export function deleteCondition(name){
    return {
        type: DELETE_CONDITION,
        name
    }
}

export function updateCondition(condition){
    return {
        type: UPDATE_CONDITION,
        condition
    }
}


export function addTrigger(trigger){
    return {
        type: ADD_TRIGGER,
        trigger
    }
}

export function deleteTrigger(name){
    return {
        type: DELETE_TRIGGER,
        name
    }
}

export function updateTrigger(trigger){
    return {
        type: UPDATE_TRIGGER,
        trigger
    }
}

export function refreshHubs() {
    return dispatch => fetch(window.host + "/api/hub", window.getHeader)
        .then(r => r.json().then(hubs => {
            dispatch(updateHubs(hubs));
            dispatch(updateActiveHub(-1));
        }));
}