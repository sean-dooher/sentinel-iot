import {
    TOGGLE_CREATE_HUB, UPDATE_ACTIVE_HUB, ADD_DELETE_ERROR, ADD_CREATE_ERROR,
    TOGGLE_DELETE_HUB
} from "../actions/navigationActions";
import {UPDATE_HUBS, UPDATE_LEAVES, UPDATE_TRIGGERS, UPDATE_DATASTORES, UPDATE_CONDITIONS} from "../actions/apiActions";
import {ADD_TRIGGER, ADD_LEAF, ADD_DATASTORE, ADD_CONDITION} from "../actions/apiActions";
import {UPDATE_TRIGGER, UPDATE_CONDITION, UPDATE_LEAF, UPDATE_DATASTORE} from "../actions/apiActions";
import {DELETE_TRIGGER, DELETE_CONDITION, DELETE_LEAF, DELETE_DATASTORE} from "../actions/apiActions";
import {handleToggleCreateHub, handleActiveHubUpdate, handleAddCreateError,
        handleAddDeleteError, handleToggleDeleteHub} from "./navigationHandlers";
import {handleAddItem, handleDeleteItem, handleUpdateItem, handleUpdateItems} from "./apiHandlers";

const initialState = {
    api: {
        hubs: [],
        leaves: [],
        datastores: [],
        conditions: [],
        triggers: [],
    },
    navbar: {
        links: [{name: 'Hub', href: '/dashboard'},
            {name: 'Settings', href: '/dashboard/settings'},
            {name: 'Profile', href: '/dashboard/profile'}],
        active: 'Hub'
    },
    hub: {
        active:-1,
        showCreate: false,
        showDelete: false,
        createErrors: [],
        deleteErrors: [],
    }
};

export function sentinelApp(state = initialState, action) {
    switch (action.type) {
        case TOGGLE_CREATE_HUB:
            return handleToggleCreateHub(state, action);
        case TOGGLE_DELETE_HUB:
            return handleToggleDeleteHub(state, action);
        case ADD_CREATE_ERROR:
            return handleAddCreateError(state, action);
        case ADD_DELETE_ERROR:
            return handleAddDeleteError(state, action);
        case UPDATE_ACTIVE_HUB:
            return handleActiveHubUpdate(state, action);
        // update collections
        case UPDATE_HUBS:
            return handleUpdateItems(state, action, 'hubs', 'hub', 'id');
        case UPDATE_CONDITIONS:
            return handleUpdateItems(state, action, 'conditions', 'condition', 'name');
        case UPDATE_LEAVES:
            return handleUpdateItems(state, action, 'leaves', 'leaf', 'uuid');
        case UPDATE_DATASTORES:
            return handleUpdateItems(state, action, 'datastores', 'datastore', 'name');
        case UPDATE_TRIGGERS:
            return handleUpdateItems(state, action, 'triggers', 'trigger', 'name');

        // update individuals
        case ADD_CONDITION:
            return handleAddItem(state, action, 'conditions', 'condition', 'name');
        case DELETE_CONDITION:
            return handleDeleteItem(state, action, 'conditions', 'condition', 'name');
        case UPDATE_CONDITION:
            return handleUpdateItem(state, action, 'conditions', 'condition', 'name');

        case ADD_LEAF:
            return handleAddItem(state, action, 'leaves', 'leaf', 'uuid');
        case DELETE_LEAF:
            return handleDeleteItem(state, action, 'leaves', 'leaf', 'uuid');
        case UPDATE_LEAF:
            return handleUpdateItem(state, action, 'leaves', 'leaf', 'uuid');

        case ADD_DATASTORE:
            return handleAddItem(state, action, 'datastores', 'datastore', 'name');
        case DELETE_DATASTORE:
            return handleDeleteItem(state, action, 'datastores', 'datastore', 'name');
        case UPDATE_DATASTORE:
            return handleUpdateItem(state, action, 'datastores', 'datastore', 'name');

        case ADD_TRIGGER:
            return handleAddItem(state, action, 'triggers', 'trigger', 'name');
        case DELETE_TRIGGER:
            return handleDeleteItem(state, action, 'triggers', 'trigger', 'name');
        case UPDATE_TRIGGER:
            return handleUpdateItem(state, action, 'triggers', 'trigger', 'name');
        default:
            return state;
    }
}