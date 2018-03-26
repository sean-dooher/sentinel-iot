export function handleToggleDeleteCondition(state, action) {
    let newState = Object.assign({}, state);
    newState.condition.showDelete = !newState.condition.showDelete;

    if(action.name)
        newState.condition.deleteName = action.name;

    if(newState.condition.showDelete)
        newState.condition.deleteErrors = [];

    return newState;
}

export function handleToggleCreateCondition(state, action) {
    let newState = Object.assign({}, state);
    newState.condition.showCreate = !newState.condition.showCreate;

    if(newState.condition.showDelete)
        newState.condition.deleteErrors = [];

    return newState;
}

export function handleAddCreateConditionError(state, action) {
    let newState = Object.assign({}, state);
    newState.condition.deleteErrors = newState.condition.deleteErrors.concat(action.message).slice(-3);
    return newState;
}

export function handleAddDeleteConditionError(state, action) {
    let newState = Object.assign({}, state);
    newState.condition.createErrors = newState.condition.createErrors.concat(action.message).slice(-3);
    return newState;
}