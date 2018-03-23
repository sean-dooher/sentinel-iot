export function handleCreateHub(state, action) {
    let content = JSON.stringify({
        name: document.querySelector("#hubName").value,
    });
    let headers = Object.assign({}, window.postHeader);
    headers.body = content;
}

export function handleToggleCreateHub(state, action) {
    let newState = Object.assign({}, state);
    newState.hub.showCreate = !state.hub.showCreate;
    return newState;
}