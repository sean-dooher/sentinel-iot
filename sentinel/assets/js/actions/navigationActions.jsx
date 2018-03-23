// TODO: add toggleCreateHubModal, sendCreateHub, deleteHub, changeHub

export const TOGGLE_CREATE_HUB = 'TOGGLE_CREATE_HUB';
export const CREATE_HUB = 'CREATE_HUB';

export function toggleCreateHub() {
    return {
        type: TOGGLE_CREATE_HUB
    }
}

export function createHub(name) {
    return {
        type: TOGGLE_CREATE_HUB,
        name: name
    }
}