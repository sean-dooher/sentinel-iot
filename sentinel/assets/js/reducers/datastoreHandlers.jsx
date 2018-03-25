export function handleToggleDeleteDatastore(state, action) {
    let newState = Object.assign({}, state);
    newState.datastore.showDelete = !newState.datastore.showDelete;

    if(action.name)
        newState.datastore.deleteName = action.name;

    if(newState.datastore.showDelete)
        newState.datastore.deleteErrors = [];

    return newState;
}

export function handleToggleCreateDatastore(state, action) {
    let newState = Object.assign({}, state);
    newState.datastore.showCreate = !newState.datastore.showCreate;

    if(newState.datastore.showDelete)
        newState.datastore.deleteErrors = [];

    return newState;
}

export function handleAddCreateDatastoreError(state, action) {
    let newState = Object.assign({}, state);
    newState.datastore.deleteErrors = newState.datastore.deleteErrors.concat(action.message).slice(-3);
    return newState;
}

export function handleAddDeleteDatastoreError(state, action) {
    let newState = Object.assign({}, state);
    newState.datastore.createErrors = newState.datastore.createErrors.concat(action.message).slice(-3);
    return newState;
}