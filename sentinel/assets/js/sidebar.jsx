import React from "react";
import PropTypes from "prop-types";
import { Button, Modal, ModalHeader, ModalBody, ModalFooter, Form, Input, Label, FormGroup, Alert } from 'reactstrap';
import Cookies from "js-cookie";

export class Sidebar extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            show: false,
            createErrors: [],
        };
        this.toggleCreateModal = this.toggleCreateModal.bind(this);
        this.sendHubCreate = this.sendHubCreate.bind(this);
        this.addCreateError = this.addCreateError.bind(this);
    }

    toggleCreateModal() {
        this.setState({show: !this.state.show});
    }

    addCreateError(text) {
        this.setState((prev, props) => {
            let errors = prev.createErrors.concat([text]).slice(-3); // limit number of errors to 3
            return {createErrors: errors};
        });
    }

    sendHubCreate() {
        let content = JSON.stringify({
            name: document.querySelector("#hubName").value,
        });
        let headers = Object.assign({}, window.postHeader);
        headers.body = content;
        fetch(window.host + "/api/hub/", headers)
            .then(response => {
                if(response.ok) {
                    response.json().then(json => {
                        if(json.accepted) {
                            this.props.refreshHubs();
                            if(this.state.show) {
                                this.toggleCreateModal();
                            }
                        } else {
                            this.addCreateError("Error adding hub: " + json.reason);
                        }
                    })
                    .catch(reason => {
                        this.addCreateError("Error adding hub: " + reason);
                    });
                }
                else {
                    response.text().then(text => this.addCreateError("Error adding hub: " + text));
                }});
    }

    render(){
       return (
       <div className="container-fluid">
          <div className="row">
            <nav className="col-sm-3 col-md-2 d-none d-sm-block bg-light sidebar">
              <ul className="nav nav-pills flex-column">
                  {
                      this.props.hubs.map((hub, key) =>
                      <li className="nav-item" data-toggle="tooltip" data-placement="right" key={key}>
                        <a className={"nav-link" + (this.props.activeHub === hub.id ? " active" : "")}
                           href="#" onClick={() => this.props.changeHub(hub.id)}>{hub.id + " - " + hub.name}</a>
                      </li> )
                  }
                  <li>
                      <a className="nav-link" href="#" onClick={this.toggleCreateModal}>Create a Hub</a>
                  </li>
              </ul>
            </nav>
          </div>
          <Modal isOpen={this.state.show} toggle={this.toggleCreateModal}>
              <ModalHeader toggle={this.toggleCreateModal}>Create a Hub</ModalHeader>
              <ModalBody>
                {this.state.createErrors.map((error, key) => <Alert color="danger" key={key}>{error}</Alert>)}
                <Form>
                    <FormGroup>
                        <Label for="hubName">Hub Name</Label>
                        <Input type="text" name="name" id="hubName" placeholder="Hub Name" />
                    </FormGroup>
                </Form>
              </ModalBody>
              <ModalFooter>
                <Button color="primary" onClick={this.sendHubCreate}>Create</Button>{' '}
                <Button color="secondary" onClick={this.toggleCreateModal}>Cancel</Button>
              </ModalFooter>
          </Modal>
      </div>);
    }
}

Sidebar.propTypes = {
    hubs: PropTypes.array,
    activeHub: PropTypes.number,
    refreshHubs: PropTypes.func,
    changeHub: PropTypes.func,
};