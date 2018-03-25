import React from "react";
import PropTypes from "prop-types";
import {Button, Modal, ModalHeader, ModalBody, ModalFooter, Form, Input, Label, FormGroup, Alert} from 'reactstrap';

export class CreateDatastore extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            name: '',
            format: 'bool',
            value: 'true',
            units: '',
        };

        this.handleChange = (event) => {
            let newState = {};
            let name = event.target.name;
            let value = event.target.value;
            newState[name] = value;

            // change value back to default once switching format to bool
            // prevents dropdown box from showing true and outputting the last non-bool value
            if (name === "format" && value === 'bool') {
                newState['value'] = 'true';
            }
            this.setState(newState);
        };
    }

    getValueInput() {
        if (this.state.format === 'bool') {
            return (
                <Input type="select" name="value" className="form-control custom-select"
                       onChange={this.handleChange}>
                    <option>true</option>
                    <option>false</option>
                </Input>);
        } else {
            return (
                <div>
                    <Input name="value" type="text"
                           pattern={this.state.format === 'string' ? null : "[0-9]+"}
                           onChange={this.handleChange}/>
                    {this.state.format === 'number+units' ?
                        <FormGroup>
                            <Label for="units">Units</Label>
                            <Input name="units" type='text' onChange={this.handleChange}/>
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
                    this.props.createDatastore(this.props.hub, this.state.name,
                        this.state.format, this.state.value,
                        this.state.format === 'number+units' ? this.state.units:undefined);
                }}>
                    <ModalBody>
                        {this.props.createErrors.map((error, key) => <Alert color="danger"
                                                                            key={key}>{error}</Alert>)}
                        <FormGroup>
                            <Label for="name">Name</Label>
                            <Input type="text" name="name" placeholder="Name" title="Must be a valid Name"
                                   onChange={this.handleChange} required/>
                            <Label for="format">Format</Label>
                            <Input type="select" name="format" onChange={this.handleChange}>
                                <option>bool</option>
                                <option>number</option>
                                <option>number+units</option>
                                <option>string</option>
                            </Input>
                            <Label for="value">Value</Label>
                            {this.getValueInput()}
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
