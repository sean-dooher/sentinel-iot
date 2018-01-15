import React from "react";
import PropTypes from "prop-types";
import { Button, Modal, ModalHeader, ModalBody, ModalFooter, Form, Input, Label, FormGroup } from 'reactstrap';
import Cookies from "js-cookie";

export class Sidebar extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            show: false,
        };
        this.toggleCreateModal = this.toggleCreateModal.bind(this);
        this.sendHubCreate = this.sendHubCreate.bind(this);
    }

    toggleCreateModal() {
        this.setState({show: !this.state.show});
    }

    sendHubCreate() {
        let content = JSON.stringify({
            name: document.querySelector("#hubName").value,
        });
        fetch("http://localhost:8000/api/hub/",
                {
                method:'POST',
                credentials: "same-origin",
                headers: {
                "X-CSRFToken": Cookies.get("csrftoken"),
                "Accept": "application/json",
                "Content-Type": "application/json"
                },
                body: content
            }).then(response => {
                if(response.ok) { /* TODO: Some sort of refreshing of sidebar hub list */
                    response.json().then(json => {
                        if(json.accepted) {
                            this.props.refreshHubs();
                            if(this.state.show) {
                                this.toggleCreateModal();
                            }
                        } else {
                            console.log("Error adding hub: " + json.reason);
                            if(this.state.show) {
                                this.toggleCreateModal();
                            }
                        }
                    });
                }
                else {
                    response.text().then(text => console.log("Error adding hub: " + text));
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
                      <li className="nav-item" key={key}>
                        <a className={"nav-link" + (this.props.activeHub === hub.id ? " active" : "")}
                           href="#" onClick={() => this.props.changeHub(hub.id)}>{hub.name}</a>
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