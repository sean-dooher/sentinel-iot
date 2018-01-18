import React from "react";
import { Sidebar } from "./sidebar";
import { AdminPage } from "./adminpage";
import { Leaf } from "./leaf";
import { Conditions } from "./conditions";
import { Button, Modal, ModalHeader, ModalBody, ModalFooter, Alert} from 'reactstrap';
import Cookies from "js-cookie";

import Dragula from 'react-dragula';

window.getHeader = {
    method:'get',
    credentials: "same-origin",
    headers: {
    "X-CSRFToken": Cookies.get("csrftoken"),
    "Accept": "application/json",
    "Content-Type": "application/json"
    }
};

window.postHeader = {
    method:'post',
    credentials: "same-origin",
    headers: {
    "X-CSRFToken": Cookies.get("csrftoken"),
    "Accept": "application/json",
    "Content-Type": "application/json"
    }
};

window.deleteHeader = {
    method:'delete',
    credentials: "same-origin",
    headers: {
    "X-CSRFToken": Cookies.get("csrftoken"),
    "Accept": "application/json",
    "Content-Type": "application/json"
    }
};


window.host = "http://localhost:8000";

export class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            leaves: [],
            conditions: [],
            datastores: [],
            hubs: [],
            activeHub: -1,
            showDeleteModal: false,
            deleteErrors: [],
        };
        this.refreshHubs = this.refreshHubs.bind(this);
        this.changeActiveHub = this.changeActiveHub.bind(this);
        this.toggleDeleteModal = this.toggleDeleteModal.bind(this);
        this.sendDeleteHub = this.sendDeleteHub.bind(this);
        this.addDeleteError = this.addDeleteError.bind(this);
    }

    toggleDeleteModal() {
        this.setState((prev, props) => {return {showDeleteModal: !prev.showDeleteModal};});
    }

    addDeleteError(text) {
        this.setState((prev, props) => {
            let errors = prev.deleteErrors.concat([text]).slice(-3); // limit number of errors to 3
            return {deleteErrors: errors};
        });
    }

    sendMessage(message) {
        message = JSON.stringify(message);
    }

    sendDeleteHub() {
        fetch(window.host + "/api/hub/" + this.state.activeHub, deleteHeader).then(r => {
            if(r.ok && this.state.showDeleteModal) {
                this.toggleDeleteModal();
                this.changeActiveHub(-1);
            } else {
                r.json().then(json => this.addDeleteError("Error: " + json.detail)).catch(e => "Error: an unknown error has occured");
            }
        })
        .catch(r => this.addDeleteError(r))
    }

    is_active() {
        return this.state.activeHub !== -1;
    }

    refresh(hub) {
        if(!hub) {
            hub = this.state.activeHub;
        }
        this.refreshHubs();
        if(this.is_active()) {
            let hub_url = window.host + "/api/hub/" + hub + "/";
            fetch(hub_url + "leaves", getHeader).then(t => t.json().then(res => this.setState({leaves: res})));
            fetch(hub_url + "conditions", getHeader).then(t => t.json().then(res => this.setState({conditions: res})));
        }
    }

    refreshHubs() {
        fetch(window.host + "/api/hub/", getHeader).then(t => t.json().then(res => {
                if(res.length > 0 && this.state.activeHub === -1) {
                    this.changeActiveHub(res[0].id);
                }
                this.setState({hubs: res});
            }));
    }

    changeActiveHub(hub) {
        this.setState({activeHub: hub, leaves:[], conditions:[], datastores:[], deleteErrors:[]});
        this.refresh(hub);
    }

    showLeaves() {
        return <section className="leaves">
            <h2>Leaves</h2>
            <div className="row" id="leaves">
                {this.state.leaves.map((leaf, key) => <Leaf key={key} {...leaf} />)}
            </div>
            <div className="text-right">
                <Button color='primary'>Add Leaf</Button>
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
            <AdminPage>
                <Sidebar hubs={this.state.hubs} refreshHubs={this.refreshHubs} changeHub={this.changeActiveHub} activeHub={this.state.activeHub}/>
                <main role="main" className="col-sm-9 ml-sm-auto col-md-10 pt-3">
                    <div className="text-right">
                        {this.is_active() ? <Button color="danger" onClick={this.toggleDeleteModal}>Delete Hub</Button> : null}
                        <Modal isOpen={this.state.showDeleteModal} toggle={this.toggleDeleteModal}>
                          <ModalHeader toggle={this.toggleDeleteModal}>Delete a Hub</ModalHeader>
                          <ModalBody>
                            {this.state.deleteErrors.map((error, key) => <Alert color="danger" key={key}>{error}</Alert>)}
                            <p>Are you sure you want to delete this hub?</p>
                          </ModalBody>
                          <ModalFooter>
                            <Button color="danger" onClick={this.sendDeleteHub}>Yes</Button>{' '}
                            <Button color="secondary" onClick={this.toggleDeleteModal}>No</Button>
                          </ModalFooter>
                        </Modal>
                    </div>
                    {this.state.datastores.length > 0 ? this.showDatastores() : null}
                    {this.state.leaves.length > 0 ? this.showLeaves() : null}
                    {this.state.conditions.length > 0 ? this.showConditions() : null}
                </main>
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
