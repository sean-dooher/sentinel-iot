import React from "react";
import PropTypes from "prop-types";
import {Button, Modal, ModalHeader, ModalBody, ModalFooter, Form, Input, Label, FormGroup, Alert} from 'reactstrap';

export class CreateDatastore extends React.Component {
    getValueInput() {
        if (this.format.value === 'bool') {
            return (
                <Input type="select" name="value" className="form-control custom-select"
                       innerRef={value => this.value = value}>
                    <option>true</option>
                    <option>false</option>
                </Input>);
        } else {
            return (
                <div>
                    <Input name="value" type="text"
                           pattern={this.format.value === 'string' ? "" : "[0-9]+"}
                           innerRef={value => this.value = value}/>
                    {this.format.value === 'number+units' ?
                        <FormGroup>
                            <Label for="units">Units</Label>
                            <Input name="units" type='text' innerRef={units => this.units = units}/>
                        </FormGroup> : null}
                </div>);
        }
    }

    render() {
        return (
            <Modal isOpen={this.props.show} toggle={this.props.toggleCreate}>
                <ModalHeader toggle={this.props.toggleCreate}>Create Datastore</ModalHeader>
                <Form onSubmit={(e) => {
                    e.preventDefault();
                    this.props.createDatastore(this.props.hub, this.name.value,
                        this.format.value, this.value.value, this.units ? this.units.value : undefined);
                }
                }>
                    <ModalBody>
                        {this.props.createErrors.map((error, key) => <Alert color="danger"
                                                                               key={key}>{error}</Alert>)}
                        <FormGroup>
                            <Label for="name">Name</Label>
                            <Input type="text" name="name" placeholder="Name" title="Must be a valid Name"
                                   innerRef={name => this.name = name} required/>
                            <Label for="format">Format</Label>
                            <Input type="select" name="format" innerRef={format => this.format = format}>
                                <option>bool</option>
                                <option>number</option>
                                <option>number+units</option>
                                <option>string</option>
                            </Input>
                            <Label for="value">Value</Label>
                            {/*{this.getValueInput()}*/}
                        </FormGroup>
                    </ModalBody>
                    <ModalFooter>
                        <Button color="primary">Send</Button>{' '}
                        <Button color="secondary" onClick={this.props.toggleCreate}>Cancel</Button>
                    </ModalFooter>
                </Form>
            </Modal>
        );
    }
}

CreateDatastore.propTypes = {
    createErrors: PropTypes.array,
    createDatastore: PropTypes.func,
    toggleCreate: PropTypes.func,
    show: PropTypes.bool,
    hub: PropTypes.number
};
