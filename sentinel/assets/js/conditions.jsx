import React from "react";
import { Button, Modal, ModalHeader, ModalBody, ModalFooter, Alert} from 'reactstrap';

export class Conditions extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            deleteErrors: [],
            showModal: false,
            name: null,
        }
        this.addDeleteError = this.addDeleteError.bind(this);
        this.toggleDeleteModal = this.toggleDeleteModal.bind(this);
        this.sendDelete = this.sendDelete.bind(this);
    }

    addDeleteError(text) {
        this.setState((prev, props) => {
            let errors = prev.deleteErrors.concat([text]).slice(-3); // limit number of errors to 3
            return {deleteErrors: errors};
        });
    }

    toggleDeleteModal(name) {
        this.setState((prev, props) => {return {showDeleteModal: !prev.showDeleteModal, name: name ? name : prev.name};});
    }

    sendDelete() {
        fetch(window.host + "/api/hub/" + window.hub + "/conditions/" + this.state.name, deleteHeader).then(r => {
            if(r.ok) {
                this.toggleDeleteModal();
            } else {
                r.json().then(json => this.addDeleteError("Error: " + json.detail)).catch(e => "Error: an unknown error has occurred");
            }
        })
        .catch(r => this.addDeleteError(r))
    }

    render(){
        if(this.props.conditions.length > 0) {
            return (
                <table className="table table-bordered table-striped text-center">
                    <thead>
                    <tr>
                        <th>Name</th>
                        <th>Predicate</th>
                        <th>Action</th>
                        <th>Action Target</th>
                        <th>Action Value</th>
                        <th></th>
                    </tr>
                    </thead>
                    <tbody>
                    {this.props.conditions.map((condition, key) =>
                        <tr key={key}>
                            <td>{condition.name}</td>
                            <td>{JSON.stringify(condition.predicate)}</td>
                            <td>{condition.action.action_type}</td>
                            <td>{JSON.stringify([condition.action.target, condition.action.device])}</td>
                            <td>{condition.action.value.toString()}</td>
                            <td><button className="btn btn-danger" onClick={() => this.toggleDeleteModal(condition.name)}>Delete</button></td>
                        </tr>
                    )}
                    <Modal isOpen={this.state.showDeleteModal} toggle={this.toggleDeleteModal}>
                          <ModalHeader toggle={this.toggleDeleteModal}>Delete a Condition</ModalHeader>
                          <ModalBody>
                            {this.state.deleteErrors.map((error, key) => <Alert color="danger" key={key}>{error}</Alert>)}
                            <p>Are you sure you want to delete this condition?</p>
                          </ModalBody>
                          <ModalFooter>
                            <Button color="danger" onClick={this.sendDelete}>Yes</Button>{' '}
                            <Button color="secondary" onClick={this.toggleDeleteModal}>No</Button>
                          </ModalFooter>
                    </Modal>
                    </tbody>
                </table>);
        }
        return null;
    }
}