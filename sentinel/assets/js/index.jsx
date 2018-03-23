import React from "react";
import { render } from "react-dom";
import { App } from "./app";
import { sentinelApp } from "./reducers/reducers";
import { createStore } from 'redux';
import { Provider } from 'react-redux'

window.store = createStore(sentinelApp);

render(
    <Provider store={store}>
        <App/>
    </Provider>, document.getElementById('react-app'));



