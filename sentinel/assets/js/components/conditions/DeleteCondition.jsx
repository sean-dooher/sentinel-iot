import React from "react";
import PropTypes from "prop-types";
import {Button, Modal, ModalHeader, ModalBody, ModalFooter, Alert} from 'reactstrap';

export class DeleteCondition extends React.Component {
    render() {
        return (
            <Modal isOpen={this.props.show} toggle={this.props.toggleDelete}>
                <ModalHeader toggle={this.props.toggleDelete}>{"Delete Condition: " + this.props.name}</ModalHeader>
                <ModalBody>
                    {this.props.deleteErrors.map((error, key) => <Alert color="danger" key={key}>{error}</Alert>)}
                    <p>Are you sure you want to delete this condition?</p>
                </ModalBody>
                <ModalFooter>
                    <Button color="danger" onClick={() => this.props.deleteCondition(this.props.hub, this.props.name)}>
                        Yes
                    </Button>{' '}
                    <Button color="secondary" onClick={this.props.toggleDelete}>No</Button>
                </ModalFooter>
            </Modal>
        );
    }
}

DeleteCondition.propTypes = {
    deleteErrors: PropTypes.array,
    deleteCondition: PropTypes.func,
    toggleDelete: PropTypes.func,
    show: PropTypes.bool,
    hub: PropTypes.number,
    name: PropTypes.string
};


