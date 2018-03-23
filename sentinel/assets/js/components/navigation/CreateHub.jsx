import React from "react";
import PropTypes from "prop-types";
import { Button, Modal, ModalHeader, ModalBody, ModalFooter, Form, Input, Label, FormGroup, Alert } from 'reactstrap';

export class CreateHub extends React.Component {
    render() {
        return (
            <Modal isOpen={this.props.show} toggle={this.props.toggleCreate}>
                <ModalHeader toggle={this.props.toggleCreate}>Create a Hub</ModalHeader>
                <ModalBody>
                    {this.props.createErrors.map((error, key) => <Alert color="danger" key={key}>{error}</Alert>)}
                    <Form>
                        <FormGroup>
                            <Label for="hubName">Hub Name</Label>
                            <Input type="text" name="name" id="hubName" placeholder="Hub Name"/>
                        </FormGroup>
                    </Form>
                </ModalBody>
                <ModalFooter>
                    <Button color="primary" onClick={this.props.createHub}>Create</Button>{' '}
                    <Button color="secondary" onClick={this.props.toggleCreate}>Cancel</Button>
                </ModalFooter>
            </Modal>);
    }
}

CreateHub.propTypes = {
    createErrors: PropTypes.array,
    createHub: PropTypes.func,
    toggleCreate: PropTypes.func,
    show: PropTypes.bool
};