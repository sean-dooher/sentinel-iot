import React from "react";
import { Device } from "./device";
import {Modal, ModalHeader, ModalFooter, ModalBody, Card, CardBody, CardHeader, CardFooter, Button, Alert} from "reactstrap";
import PropTypes from "prop-types";

export class Leaf extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            date: new Date(Date.now()).toLocaleTimeString(),
            deleteErrors: [],
            showDeleteModal: false,
        };
        this.addDeleteError = this.addDeleteError.bind(this);
        this.toggleDeleteModal = this.toggleDeleteModal.bind(this);
        this.sendDelete = this.sendDelete.bind(this);
        this.updateTime = this.updateTime.bind(this);
    }

    addDeleteError(text) {
        this.setState((prev, props) => {
            let errors = prev.deleteErrors.concat([text]).slice(-3); // limit number of errors to 3
            return {deleteErrors: errors};
        });
    }

    toggleDeleteModal() {
        this.setState((prev, props) => {return {showDeleteModal: !prev.showDeleteModal};});
    }

    sendDelete() {
        fetch(window.host + "/api/hub/" + window.hub + "/leaves/" + this.props.uuid, deleteHeader).then(r => {
            if(r.ok) {
                this.toggleDeleteModal();
            } else {
                r.json().then(json => this.addDeleteError("Error: " + json.detail)).catch(e => "Error: an unknown error has occurred");
            }
        })
        .catch(r => this.addDeleteError(r))
    }

    updateTime() {
        this.setState({date: new Date(Date.now()).toLocaleTimeString()});
    }

    componentDidUpdate(prevProps, prevState) {
        if(prevProps.is_connected !== this.props.is_connected) {
            this.updateTime();
        }
    }

    render(){
       return (
                <div className="leaf col-sm-12 col-md-12 col-lg-6 col-xl-6">
                    <Card>
                      <CardHeader>
                          <div className="float-left grabber leaf-icon drag-handle"><i className="fas fa-bars"></i></div>
                          <div className="float-left" data-toggle="tooltip" data-placement="bottom" title={this.props.uuid}>{this.props.name} ({this.props.model}) -- {this.props.is_connected ? <span className="badge badge-success">Connected</span> : <span className="badge badge-danger">Disconnected</span>}</div>
                          <div className="float-right" id="leafdropdown" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                            <div className="dropdown-toggle dropdown-toggle-split pointer leaf-icon"></div>
                          </div>
                          <div className="dropdown-menu" aria-labelledby="leafdropdown">
                              <button className="dropdown-item" onClick={this.toggleDeleteModal}>Disconnect Leaf</button>
                          </div>
                          <Modal isOpen={this.state.showDeleteModal} toggle={this.toggleDeleteModal}>
                              <ModalHeader toggle={this.toggleDeleteModal}>Disconnect Leaf</ModalHeader>
                              <ModalBody>
                                {this.state.deleteErrors.map((error, key) => <Alert color="danger" key={key}>{error}</Alert>)}
                                <p>Are you sure you want to disconnect this leaf? It will not be able to reconnect until you register it again.</p>
                              </ModalBody>
                              <ModalFooter>
                                <Button color="danger" onClick={this.sendDelete}>Yes</Button>{' '}
                                <Button color="secondary" onClick={this.toggleDeleteModal}>No</Button>
                              </ModalFooter>
                          </Modal>
                      </CardHeader>
                      <CardBody>
                      { this.props.devices.length > 0 ?
                        <div className="row">
                            <div className="col-md-4"><strong>Device</strong></div>
                            <div className="col-md-3"><strong>Format</strong></div>
                            <div className="col-md-4"><strong>Value</strong></div>
                        </div> : <p>This Leaf has no devices attached</p> }
                            { this.props.devices.map((device, key) =>
                                <Device key={key} leaf={this.props.uuid} sendMessage={this.props.sendMessage} {... device} connected={this.props.is_connected} update={this.updateTime} />)}
                        </CardBody>
                      <CardFooter className="text-muted text-center">
                        Last Updated: { this.state.date }
                      </CardFooter>
                    </Card>
                </div>);
    }

    componentDidMount() {
        $(function () {
          $('[data-toggle="tooltip"]').tooltip()
        });
    }
}

Leaf.propTypes = {
    uuid: PropTypes.string,
    model: PropTypes.string,
    name: PropTypes.string,
    sendMessage: PropTypes.func,
    devices: PropTypes.array,
    is_connected: PropTypes.bool
};