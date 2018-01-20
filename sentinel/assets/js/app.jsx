import React from "react";
import { Sidebar } from "./sidebar";
import { AdminPage } from "./adminpage";
import { Leaf } from "./leaf";
import { Conditions } from "./conditions";
import { Datastore } from "./datastore";
import {ConditionCreator, conditionCreator} from "./conditionCreator";
import { Button, Modal, ModalHeader, ModalBody, ModalFooter, Alert} from 'reactstrap';
import { FormGroup, Input, Form, Label} from 'reactstrap';

import Cookies from "js-cookie";

import Dragula from 'react-dragula';
import {LeafSelector} from "./leafSelector";

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
            leafErrors: [],
            datastoreErrors: [],
            conditionErrors: [],
            showLeafModal: false,
            token: '',
            showDatastoreModal: false,
            showConditionsModal: false,
            newDatastoreFormat: 'bool',
            newDatastoreValue: true,
        };
        this.refreshHubs = this.refreshHubs.bind(this);
        this.refresh = this.refresh.bind(this);
        this.changeActiveHub = this.changeActiveHub.bind(this);
        this.toggleDeleteModal = this.toggleDeleteModal.bind(this);
        this.sendDeleteHub = this.sendDeleteHub.bind(this);
        this.addDeleteError = this.addDeleteError.bind(this);
        this.toggleLeafModal = this.toggleLeafModal.bind(this);
        this.toggleConditionModal = this.toggleConditionModal.bind(this);
        this.toggleDatastoreModal = this.toggleDatastoreModal.bind(this);
        this.registerLeaf = this.registerLeaf.bind(this);
        this.getDatastoreInput = this.getDatastoreInput.bind(this);
        this.handleDatastoreFormat = this.handleDatastoreFormat.bind(this);
        this.handleDatastoreValue = this.handleDatastoreValue.bind(this);
        this.createDatastore = this.createDatastore.bind(this);
        this.sendDeleteDatastore = this.sendDeleteDatastore.bind(this);
        this.sendCreateCondition = this.sendCreateCondition.bind(this);
    }

    toggleDeleteModal() {
        this.setState((prev, props) => {return {showDeleteModal: !prev.showDeleteModal};});
    }

    toggleLeafModal() {
        this.setState((prev, props) => {return {showLeafModal: !prev.showLeafModal, token: ''};});
    }

    toggleDatastoreModal() {
        this.setState((prev, props) => {return {showDatastoreModal: !prev.showDatastoreModal, newDatastoreFormat: "bool", newDatastoreValue: true};});
    }

    toggleConditionModal() {
        this.setState((prev, props) => {return {showConditionsModal: !prev.showConditionsModal};});
    }

    addDeleteError(text) {
        this.setState((prev, props) => {
            let errors = prev.deleteErrors.concat([text]).slice(-3); // limit number of errors to 3
            return {deleteErrors: errors};
        });
    }

    addLeafError(text) {
        this.setState((prev, props) => {
            let errors = prev.leafErrors.concat([text]).slice(-3); // limit number of errors to 3
            return {leafErrors: errors};
        });
    }

    addDatastoreError(text) {
        this.setState((prev, props) => {
            let errors = prev.datastoreErrors.concat([text]).slice(-3); // limit number of errors to 3
            return {datastoreErrors: errors};
        });
    }

    addConditionError(text) {
        this.setState((prev, props) => {
            let errors = prev.conditionErrors.concat([text]).slice(-3); // limit number of errors to 3
            return {conditionErrors: errors};
        });
    }

    sendDeleteHub() {
        fetch(window.host + "/api/hub/" + this.state.activeHub, deleteHeader).then(r => {
            if(r.ok && this.state.showDeleteModal) {
                this.toggleDeleteModal();
                this.changeActiveHub(-1);
            } else {
                r.json().then(json => this.addDeleteError("Error: " + json.detail)).catch(e => "Error: an unknown error has occurred");
            }
        })
        .catch(r => this.addDeleteError(r))
    }

    sendDeleteDatastore(datastore) {
        fetch(window.host + "/api/hub/" + this.state.activeHub + "/datastores/" + datastore.props.name , deleteHeader)
            .then(r => {
                if(r.ok) {
                    datastore.toggleDeleteModal();
                    this.refresh();
                } else {
                    r.json().then(json => datastore.addDeleteError("Error: " + json.detail)).catch(e => "Error: an unknown error has occurred");
                }
            })
            .catch(r => this.addDeleteError(r))
            .finally(() => datastore.toggleDeleteModal());
    }

    registerLeaf(event) {
        event.preventDefault();
        let data = new FormData(event.target);
        let headers = Object.assign({}, window.postHeader);
        headers.body = JSON.stringify({uuid: data.get('uuid')});
        fetch(window.host + "/hub/" + this.state.activeHub + "/register", headers)
            .then(r => {
                if(r.ok) {
                    r.json().then(json => {
                            if (json.accepted) {
                                this.setState({token: json.token});
                            } else {
                                this.addLeafError("Error: " + json.reason);
                            }
                        }
                    ).catch(e => this.addLeafError("Error: error occured parsing response"))
                } else {
                    r.text().then(text => console.log(text));
                    this.addLeafError("Error: " + r.statusText + " (" + r.status + ")");
                }
            })
            .catch(e => this.addLeafError("Error: an unknown error has occured"));
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
            fetch(hub_url + "datastores", getHeader).then(t => t.json().then(res => this.setState({datastores: res})));
        }
    }

    refreshHubs() {
        fetch(window.host + "/api/hub/", getHeader).then(t => t.json().then(res => {
                if(res.length > 0 && !this.is_active()) {
                    this.changeActiveHub(res[0].id);
                }
                this.setState({hubs: res});
            }));
    }

    changeActiveHub(hub) {
        this.setState(
            {
                activeHub: hub,
                leaves:[],
                conditions:[],
                datastores:[],
                deleteErrors:[],
                leafErrors: [],
                datastoreErrors: [],
                conditionErrors: [],
                newDatastoreFormat: "bool",
                newDatastoreValue: true,
                token: '',
            });
        this.refresh(hub);
    }

    showLeaves() {
        return (<section className="leaves">
            <h2>Leaves <Button color='primary' onClick={this.toggleLeafModal}>Register</Button></h2>
            <Modal isOpen={this.state.showLeafModal} toggle={this.toggleLeafModal}>
              <ModalHeader toggle={this.toggleLeafModal}>Register a Leaf</ModalHeader>
              <Form onSubmit={this.registerLeaf}>
                  <ModalBody>
                    {this.state.leafErrors.map((error, key) => <Alert color="danger" key={key}>{error}</Alert>)}
                        <FormGroup>
                          <Label for="newUUID">Leaf UUID</Label>
                          <Input type="text" name="uuid" id="newUUID" placeholder="UUID" title="Must be a valid UUID" required pattern="[0-9a-f]{8}(?:-{0,1}[0-9a-f]{4}){3}-{0,1}[0-9a-f]{12}" />
                        </FormGroup>
                      {this.state.token ? <Alert color="info">{"Enter this token on your device: " + this.state.token}</Alert>: null}
                  </ModalBody>
                  <ModalFooter>
                    <Button color="primary" onClick={this.sendRegisterLeaf}>Send</Button>{' '}
                    <Button color="secondary" onClick={this.toggleLeafModal}>Cancel</Button>
                  </ModalFooter>
              </Form>
            </Modal>
            {this.state.leaves.length === 0 ? <Alert color="info">You currently have no leaves registered. Click the button above to register a new one</Alert> : null}
            <div className="row" id="leaves">
                {this.state.leaves.map((leaf, key) => <Leaf key={key} {...leaf} />)}
            </div>
            <hr/>
        </section>);
    }

    sendCreateCondition(event) {
        event.preventDefault();
        let condition = this._condition.getCondition();
        let headers = Object.assign({}, window.postHeader);
        headers.body = JSON.stringify(condition);
        fetch(window.host + "/api/hub/" + this.state.activeHub + "/conditions/", headers)
            .then(r => {
                if(r.ok) {
                    r.json().then(json => {
                            if (json.accepted) {
                                this.toggleConditionModal();
                                this.refresh();
                            } else {
                                this.addConditionError("Error: " + json.reason);
                            }
                        }
                    ).catch(e => this.addConditionError("Error: error occured parsing response"))
                } else {
                    r.text().then(t => console.log(t));
                    this.addConditionError("Error: " + r.statusText + " (" + r.status + ")");
                }
            })
            .catch(e => this.addConditionError("Error: an unknown error has occurred"));
    }

    showConditions() {
        return <section className="conditions">
            <h2>Conditions <Button color='primary' onClick={this.toggleConditionModal}>Create</Button></h2>
            <Modal size="lg" isOpen={this.state.showConditionsModal} toggle={this.toggleConditionModal}>
              <ModalHeader toggle={this.toggleConditionModal}>Create a condition</ModalHeader>
              <Form onSubmit={this.sendCreateCondition}>
                  <ModalBody>
                    {this.state.conditionErrors.map((error, key) => <Alert color="danger" key={key}>{error}</Alert>)}
                    <ConditionCreator leaves={this.state.leaves} datastores={this.state.datastores} ref={c => this._condition = c}/>
                  </ModalBody>
                  <ModalFooter>
                    <Button color="primary">Send</Button>{' '}
                    <Button color="secondary" onClick={this.toggleConditionModal}>Cancel</Button>
                  </ModalFooter>
              </Form>
            </Modal>
            {this.state.conditions.length === 0 ? <Alert color="info">You currently have no conditions. Click the button above to create one</Alert> : null}
            <Conditions conditions={this.state.conditions}/>
            <hr/>
        </section>;
    }

    handleDatastoreFormat(e) {
        let newFormat = e.target.value;
        let defaultValue;
        if(newFormat === 'string' || newFormat === 'number' || newFormat === 'number+units') {
            defaultValue = "";
        } else {
            defaultValue = true;
        }
        this.setState({newDatastoreFormat: newFormat, newDatastoreValue: defaultValue});
    }

    handleDatastoreValue(e) {
        this.setState({newDatastoreValue: e.target.value});
    }

    getDatastoreInput() {
        if(this.state.newDatastoreFormat == 'bool') {
           return <select name="value" className="form-control custom-select"
                          value={this.state.newDatastoreValue.toString()} onChange={this.handleDatastoreValue}>
                    <option value="true">true</option>
                    <option value="false">false</option>
                </select>
        } else {
            return <div>
                    <Input name="value" type="text" pattern={this.state.newDatastoreFormat === 'string' ? "" : "[0-9]+"} />
                        {this.state.newDatastoreFormat === 'number+units' ? <FormGroup>
                            <Label for="units">Units</Label>
                            <Input name="units" type='text' />
                        </FormGroup>: null}
                   </div>;
        }
    }

    createDatastore(event) {
        event.preventDefault();
        let formData = new FormData(event.target);
        let data = {};
        for (let key of formData.keys()) {
            if(key !== 'value' || this.state.newDatastoreFormat === 'string') {
                data[key] = formData.get(key);
            } else {
                data[key] = JSON.parse(formData.get(key));
            }
        }
        let headers = Object.assign({}, window.postHeader);
        headers.body = JSON.stringify(data);
        console.log(headers.body);
        fetch(window.host + "/api/hub/" + this.state.activeHub + "/datastores/", headers)
            .then(r => {
                if(r.ok) {
                    r.json().then(json => {
                            if (json.accepted) {
                                this.toggleDatastoreModal();
                                this.refresh();
                            } else {
                                this.addDatastoreError("Error: " + json.reason);
                            }
                        }
                    ).catch(e => this.addDatastoreError("Error: error occured parsing response"))
                } else {
                    r.text().then(t => console.log(t));
                    this.addDatastoreError("Error: " + r.statusText + " (" + r.status + ")");
                }
            })
            .catch(e => this.addDatastoreError("Error: an unknown error has occurred"));
    }

    showDatastores() {
        return <section className="datastores">
            <h2>Datastores <Button color='primary' onClick={this.toggleDatastoreModal}>Create</Button></h2>
            <Modal isOpen={this.state.showDatastoreModal} toggle={this.toggleDatastoreModal}>
              <ModalHeader toggle={this.toggleDatastoreModal}>Create Datastore</ModalHeader>
              <Form onSubmit={this.createDatastore}>
                  <ModalBody>
                    {this.state.datastoreErrors.map((error, key) => <Alert color="danger" key={key}>{error}</Alert>)}
                    <FormGroup>
                        <Label for="name">Name</Label>
                        <Input type="text" name="name" id="name" placeholder="Name" title="Must be a valid Name" required/>
                        <Label for="format">Format</Label>
                        <select name="format" className="form-control custom-select" value={this.state.newDatastoreFormat}
                                    onChange={this.handleDatastoreFormat}>
                            <option value="bool">bool</option>
                            <option value="number">number</option>
                            <option value="number+units">number+units</option>
                            <option value="string">string</option>
                        </select>
                        <Label for="value">Value</Label>
                        { this.getDatastoreInput() }
                    </FormGroup>
                  </ModalBody>
                  <ModalFooter>
                    <Button color="primary">Send</Button>{' '}
                    <Button color="secondary" onClick={this.toggleDatastoreModal}>Cancel</Button>
                  </ModalFooter>
              </Form>
            </Modal>
            {this.state.datastores.length === 0 ? <Alert color="info">You currently have no datastores. Click the button above to create a new one</Alert> : null}
            <div className="row" id="leaves">
                {this.state.datastores.map((datastore, key) => <Datastore delete={this.sendDeleteDatastore} key={key} {...datastore} />)}
            </div>
            <hr/>
        </section>;
    }

    render(){
        return (
            <AdminPage>
                <Sidebar hubs={this.state.hubs} refreshHubs={this.refreshHubs} changeHub={this.changeActiveHub} activeHub={this.state.activeHub}/>
                {this.is_active() ?
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
                    {this.showDatastores()}
                    {this.showLeaves()}
                    {this.showConditions()}
                </main> : null}
            </AdminPage>);
    }

    componentDidMount(){
        this.refresh();
        setInterval(this.refresh, 500);
        Dragula([document.querySelector('#leaves')], {
          moves: function (el, container, handle) {
            return handle.classList.contains('drag-handle') || handle.parentNode.classList.contains('drag-handle');
          }
        });
    }
}
