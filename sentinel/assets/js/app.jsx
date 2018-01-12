import React from "react";
import { Header } from "./header";
import { AdminPage } from "./adminpage";
import { Leaf } from "./leaf";
import { Conditions } from "./conditions";

import Dragula from 'react-dragula';

export class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            leaves: [],
            conditions: [],
        };
    }

    refresh() {
        fetch("http://localhost:8000/hub/1/leaves").then(t => t.json().then(t => this.setState({leaves: t})));
        fetch("http://localhost:8000/hub/1/conditions").then(t => t.json().then(t => this.setState({conditions: t})));
    }

    render(){
        return (
            <AdminPage>
                <section className="leaves">
                    <h2>Leaves</h2>
                    <div className="row" id="leaves">
                        { this.state.leaves.map((leaf, key) => <Leaf key={key} {... leaf} />) }
                    </div>
                    <hr />
                    <h2>Conditions</h2>
                    <Conditions conditions={this.state.conditions}/>
                </section>
            </AdminPage>);
    }

    componentDidMount() {
        this.refresh();

        Dragula([document.querySelector('#leaves')], {
          moves: function (el, container, handle) {
            return handle.classList.contains('drag-handle') || handle.parentNode.classList.contains('drag-handle');
          }
        });
    }
}
