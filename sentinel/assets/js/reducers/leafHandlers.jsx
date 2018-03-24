export function handleToggleDeleteLeaf(state, action) {
    let newState = Object.assign({}, state);
    newState.leaf.showDelete = !state.leaf.showDelete;
    return newState;
}

export function handleToggleRegisterLeaf(state, action) {
    let newState = Object.assign({}, state);
    newState.leaf.showRegister = !state.leaf.showRegister;
    return newState;
}

export function handleChangeRegistrationToken(state, action) {
    let newState = Object.assign({}, state);
    newState.leaf.token = action.token;
    return newState;
}

export function handleAddDeleteLeafError(state, action) {
    let newState = Object.assign({}, state);
    newState.leaf.deleteErrors = newState.leaf.deleteErrors.concat(action.message).slice(-3);
    return newState;
}

export function handleRegisterLeafError(state, action) {
    let newState = Object.assign({}, state);
    newState.leaf.registerErrors = newState.leaf.registerErrors.concat(action.message).slice(-3);
    return newState;
}