import React from "react";
import PropTypes from "prop-types";
import {Button, Modal, ModalHeader, ModalBody, ModalFooter, Form, Input, Label, FormGroup, Alert} from 'reactstrap';

export class RegisterLeaf extends React.Component {
    render() {
        return (
            <Modal isOpen={this.props.show} toggle={this.props.toggleRegister}>
                <ModalHeader toggle={this.props.toggleRegister}>Register a Leaf</ModalHeader>
                <Form onSubmit={(event) => {
                    event.preventDefault();
                    this.props.registerLeaf(this.props.hub, this.input.value)
                }}>
                    <ModalBody>
                        {this.props.registerErrors.map((error, key) => <Alert color="danger" key={key}>{error}</Alert>)}
                        <FormGroup>
                            <Label for="newUUID">Leaf UUID</Label>
                            <Input type="text" name="uuid" id="newUUID" placeholder="UUID"
                                   title="Must be a valid UUID" required
                                   pattern="[0-9a-f]{8}(?:-{0,1}[0-9a-f]{4}){3}-{0,1}[0-9a-f]{12}"
                                    innerRef={input => this.input = input}
                            />
                        </FormGroup>
                        {this.props.token ? <Alert
                            color="info">{"Enter this token on your device: " + this.props.token}</Alert> : null}
                    </ModalBody>
                    <ModalFooter>
                        <Button color="primary">Send</Button>{' '}
                        <Button color="secondary" onClick={this.props.toggleRegister}>Cancel</Button>
                    </ModalFooter>
                </Form>
            </Modal>);
    }
}

RegisterLeaf.propTypes = {
    registerErrors: PropTypes.array,
    registerLeaf: PropTypes.func,
    toggleRegister: PropTypes.func,
    show: PropTypes.bool,
    token: PropTypes.string,
    hub: PropTypes.number
};

