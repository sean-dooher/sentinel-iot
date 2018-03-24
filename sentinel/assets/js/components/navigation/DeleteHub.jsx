import React from "react";
import PropTypes from "prop-types";
import { Button, Modal, ModalHeader, ModalBody, ModalFooter, Form, Input, Label, FormGroup, Alert } from 'reactstrap';

export class DeleteHub extends React.Component {
    render() {
        return (
            <Modal isOpen={this.props.show} toggle={this.props.toggleDelete}>
                <ModalHeader toggle={this.props.toggleDelete}>Delete a Hub</ModalHeader>
                <ModalBody>
                    {this.props.deleteErrors.map((error, key) => <Alert color="danger" key={key}>{error}</Alert>)}
                    <p>Are you sure you want to delete this hub?</p>
                </ModalBody>
                <ModalFooter>
                    <Button color="danger" onClick={() => this.props.deleteHub(this.props.id)}>Delete</Button>{' '}
                    <Button color="secondary" onClick={this.props.toggleDelete}>Cancel</Button>
                </ModalFooter>
            </Modal>);
    }
}

DeleteHub.propTypes = {
    deleteErrors: PropTypes.array,
    deleteHub: PropTypes.func,
    toggleDelete: PropTypes.func,
    show: PropTypes.bool,
    id: PropTypes.number
};