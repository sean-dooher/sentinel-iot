export function handleToggleCreateHub(state, action) {
    let newState = Object.assign({}, state);
    newState.hub.showCreate = !state.hub.showCreate;

    if(newState.hub.showCreate)
        newState.hub.createErrors = [];

    return newState;
}

export function handleToggleDeleteHub(state, action) {
    let newState = Object.assign({}, state);
    newState.hub.showDelete = !state.hub.showDelete;

    if(newState.hub.showDelete)
        newState.hub.deleteErrors = [];

    return newState;
}

export function handleActiveHubUpdate(state, action) {
    let newState = Object.assign({}, state);
    if(action.id === -1)
        newState.hub.active = newState.api.hubs.length > 0 ? newState.api.hubs[0].id : -1;
    else if(action.id !== -1)
        newState.hub.active = action.id;
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
