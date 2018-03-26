import React from "react";
import PropTypes from "prop-types";
import {Button, Modal, ModalHeader, ModalBody, ModalFooter, Form, Input, Label, FormGroup, Alert} from 'reactstrap';
import {DeleteHub} from "../navigation/DeleteHub";

export class DeleteLeaf extends React.Component {
    render() {
        return (
            <Modal isOpen={this.props.show} toggle={this.props.toggleDelete}>
                <ModalHeader toggle={this.props.toggleDelete}>Disconnect Leaf</ModalHeader>
                <ModalBody>
                    {this.props.deleteErrors.map((error, key) => <Alert color="danger" key={key}>{error}</Alert>)}
                    <p>Are you sure you want to disconnect this leaf? It will not be able to reconnect until you
                        register it again.</p>
                </ModalBody>
                <ModalFooter>
                    <Button color="danger" onClick={() => this.props.deleteLeaf(this.props.hub, this.props.uuid)}>
                        Yes
                    </Button>{' '}
                    <Button color="secondary" onClick={this.props.toggleDelete}>No</Button>
                </ModalFooter>
            </Modal>);
    }
}

DeleteHub.propTypes = {
    deleteErrors: PropTypes.array,
    deleteLeaf: PropTypes.func,
    toggleDelete: PropTypes.func,
    show: PropTypes.bool,
    hub: PropTypes.number,
    uuid: PropTypes.string
};