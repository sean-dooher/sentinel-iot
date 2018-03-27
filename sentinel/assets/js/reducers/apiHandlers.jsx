import {addCondition, addDatastore, addLeaf, addTrigger} from "../actions/apiActions";
import {updateCondition, updateDatastore, updateLeaf, updateTrigger} from "../actions/apiActions";
import {deleteCondition, deleteDatastore, deleteLeaf, deleteTrigger} from "../actions/apiActions";
import {updateConditions, updateDatastores, updateLeaves, updateTriggers} from "../actions/apiActions";


function attributeSorter(attribute) {
    return function (a, b) {
        if (a[attribute] < b[attribute])
            return -1;
        else if (a[attribute] > b[attribute])
            return 1;
        else
            return 0;
    }
}

export function handleUpdateItems(state, action, collection, singular, attribute) {
    let newState = Object.assign({}, state);
    newState.api[collection] = action[collection].sort(attributeSorter(attribute));
    return newState;
}

export function handleAddItem(state, action, collection, singular, attribute) {
    let newState = Object.assign({}, state);
    newState.api[collection] = state.api[collection].concat(action[singular]).sort(attributeSorter(attribute));
    return newState;
}

export function handleDeleteItem(state, action, collection, singular, attribute) {
    let newState = Object.assign({}, state);
    newState.api[collection] = state.api[collection].filter(item => item[attribute] !== action[attribute]).sort(attributeSorter(attribute));
    return newState;
}

export function handleUpdateItem(state, action, collection, singular, attribute) {
    let newState = Object.assign({}, state);
    let newCollection = state.api[collection].filter(item => item[attribute] !== action[singular][attribute]);
    console.log(action);
    newState.api[collection] = newCollection.concat(action[singular]).sort(attributeSorter(attribute));
    return newState;
}

export function handleWebsocketMessage(dispatch, message) {
    let data = JSON.parse(message.data);
    switch (data.stream) {
        case 'leaves':
            return handleMessage(dispatch, data, addLeaf, deleteLeaf, updateLeaf, updateLeaves, 'uuid');
        case 'conditions':
            return handleMessage(dispatch, data, addCondition, deleteCondition, updateCondition, updateConditions, 'name');
        case 'datastores':
            return handleMessage(dispatch, data, addDatastore, deleteDatastore, updateDatastore, updateDatastores, 'name');
        case 'triggers':
            return handleMessage(dispatch, data, addTrigger, deleteTrigger, updateTrigger, updateTriggers, 'name');
        case 'default':
            console.error('Unexpected messaged received from databinding');
            break;
    }
}

function handleMessage(dispatch, message, addItem, deleteItem, updateItem, updateItems, attribute) {
    switch(message.payload.action) {
        case 'list':
            dispatch(updateItems(message.payload.data));
            break;
        case 'create':
            dispatch(addItem(message.payload.data));
            break;
        case 'delete':
            dispatch(deleteItem(message.payload.data[attribute]));
            break;
        case 'update':
            dispatch(updateItem(message.payload.data));
            break;
        default:
            return
    }
}