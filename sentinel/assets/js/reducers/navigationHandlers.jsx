export function handleToggleCreateHub(state, action) {
    let newState = Object.assign({}, state);
    newState.hub.showCreate = !state.hub.showCreate;
    return newState;
}

export function handleActiveHubUpdate(state, action) {
    let newState = Object.assign({}, state);
    newState.hub.active = action.id;
    return newState;
}

