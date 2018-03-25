import React from "react";
import PropTypes from "prop-types";
import {Button, Modal, ModalHeader, ModalBody, ModalFooter, Alert} from 'reactstrap';

export class DeleteDatastore extends React.Component {
    render() {
        return (
            <Modal isOpen={this.props.show} toggle={this.props.toggleDelete}>
                <ModalHeader toggle={this.props.toggleDelete}>{"Delete Datastore: " + this.props.name}</ModalHeader>
                <ModalBody>
                    {this.props.deleteErrors.map((error, key) => <Alert color="danger" key={key}>{error}</Alert>)}
                    <p>Are you sure you want to delete this datastore?</p>
                </ModalBody>
                <ModalFooter>
                    <Button color="danger" onClick={() => this.props.deleteDatastore(this.props.hub, this.props.name)}>
                        Yes
                    </Button>{' '}
                    <Button color="secondary" onClick={this.props.toggleDelete}>No</Button>
                </ModalFooter>
            </Modal>
        );
    }
}

DeleteDatastore.propTypes = {
    deleteErrors: PropTypes.array,
    deleteDatastore: PropTypes.func,
    toggleDelete: PropTypes.func,
    show: PropTypes.bool,
    hub: PropTypes.number,
    name: PropTypes.string
};


