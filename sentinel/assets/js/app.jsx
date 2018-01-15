import React from "react";
import { Header } from "./header";
import { AdminPage } from "./adminpage";
import { Leaf } from "./leaf";
import { Conditions } from "./conditions";
import Cookies from "js-cookie";

import Dragula from 'react-dragula';

var getHeader = {
    method:'get',
    credentials: "same-origin",
    headers: {
    "X-CSRFToken": Cookies.get("csrftoken"),
    "Accept": "application/json",
    "Content-Type": "application/json"
    }
};

export class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            leaves: [],
            conditions: [],
            datastores: [],
            hubs: [],
            active_hub: -1,
        };
        this.refreshHubs = this.refreshHubs.bind(this);
        this.changeActiveHub = this.changeActiveHub.bind(this);
    }

    is_active() {
        return this.state.active_hub !== -1;
    }
    refresh(hub) {
        if(!hub) {
            hub = this.state.active_hub;
        }
        this.refreshHubs();
        if(this.is_active()) {
            let hub_url = "http://localhost:8000/api/hub/" + hub + "/";
            fetch(hub_url + "leaves", getHeader).then(t => t.json().then(res => this.setState({leaves: res})));
            fetch(hub_url + "conditions", getHeader).then(t => t.json().then(res => this.setState({conditions: res})));
        }
    }

    refreshHubs() {
        fetch("http://localhost:8000/api/hub/", getHeader).then(t => t.json().then(res => {
                if(res.length > 0 && this.state.active_hub === -1) {
                    this.changeActiveHub(res[0].id);
                }
                this.setState({hubs: res});
            }));
    }

    changeActiveHub(hub) {
        this.setState({active_hub: hub, leaves:[], conditions:[], datastores:[]});
        this.refresh(hub);
    }

    showLeaves() {
        return <section className="leaves">
            <h2>Leaves</h2>
            <div className="row" id="leaves">
                {this.state.leaves.map((leaf, key) => <Leaf key={key} {...leaf} />)}
            </div>
            <hr/>
        </section>;
    }

    showConditions() {
        return <section className="conditions">
            <h2>Conditions</h2>
            <Conditions conditions={this.state.conditions}/>
        </section>;
    }

    showDatastores() {
        return null;
    }

    render(){
        return (
            <AdminPage hubs={this.state.hubs} activeHub={this.state.active_hub} refreshHubs={this.refreshHubs} changeHub={this.changeActiveHub}>
                {this.state.datastores.length > 0 ? this.showDatastores() : null}
                {this.state.leaves.length > 0 ? this.showLeaves() : null}
                {this.state.conditions.length > 0 ? this.showConditions() : null}
            </AdminPage>);
    }

    componentDidMount(){
        this.refresh();

        Dragula([document.querySelector('#leaves')], {
          moves: function (el, container, handle) {
            return handle.classList.contains('drag-handle') || handle.parentNode.classList.contains('drag-handle');
          }
        });
    }
}
