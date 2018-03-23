import {TOGGLE_CREATE_HUB, CREATE_HUB} from "../actions/navigationActions";
import {handleToggleCreateHub, handleCreateHub} from "./navigationHandlers"

const initialState = {
    api: {
        hubs: [],
        leaves: [],
        datastores: [],
        conditions: [],
        triggers: [],
    },
    navbar: {
        links: [{name: 'Hub', href: '#'},
            {name: 'Settings', href: '/dashboard/settings'},
            {name: 'Profile', href: '/dashboard/profile'}],
        active: 'Hub'
    },
    hub: {
        active:-1,
        showCreate: false,
        createErrors: [],
    }
};
export function sentinelApp(state = initialState, action) {
    switch (action.type) {
        case TOGGLE_CREATE_HUB:
            return handleToggleCreateHub(state, action);
        case CREATE_HUB:
            return handleCreateHub(state, action);
        default:
            return state;
    }
}