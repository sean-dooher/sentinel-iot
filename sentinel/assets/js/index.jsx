import React from "react";
import {render} from "react-dom";
import {App} from "./app";
import {sentinelApp} from "./reducers/reducers";
import {createStore, applyMiddleware} from 'redux';
import {Provider} from 'react-redux'
import ReduxThunk from 'redux-thunk'
import Cookies from "js-cookie";

window.getHeader = {
    method: 'get',
    credentials: "same-origin",
    headers: {
        "X-CSRFToken": Cookies.get("csrftoken"),
        "Accept": "application/json",
        "Content-Type": "application/json"
    },
    cache: "reload",
};

window.postHeader = {
    method: 'post',
    credentials: "same-origin",
    headers: {
        "X-CSRFToken": Cookies.get("csrftoken"),
        "Accept": "application/json",
        "Content-Type": "application/json"
    },
    cache: "reload",
};

window.putHeader = {
    method: 'put',
    credentials: "same-origin",
    headers: {
        "X-CSRFToken": Cookies.get("csrftoken"),
        "Accept": "application/json",
        "Content-Type": "application/json"
    },
    cache: "reload"
};

window.deleteHeader = {
    method: 'delete',
    credentials: "same-origin",
    headers: {
        "X-CSRFToken": Cookies.get("csrftoken"),
        "Accept": "application/json",
        "Content-Type": "application/json"
    },
    cache: "reload"
};

window.store = createStore(sentinelApp, applyMiddleware(ReduxThunk));

render(<Provider store={store}><App/></Provider>, document.getElementById('react-app'));



