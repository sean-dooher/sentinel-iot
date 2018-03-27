import React from "react";
import PropTypes from "prop-types";
import {Button, Modal, ModalHeader, ModalBody, ModalFooter, Alert, Input} from 'reactstrap';
import {PredicateCreator} from "./PredicateCreator";

export class CreateCondition extends React.Component {
    render() {
        return (
            <Modal isOpen={this.props.show} toggle={this.props.toggleCreate} size="lg">
                <ModalHeader toggle={this.props.toggleCreate}>Create Condition</ModalHeader>
                <ModalBody>
                    {this.props.createErrors.map((error, key) => <Alert color="danger" key={key}>{error}</Alert>)}

                    <h4>Name</h4>
                    <Input type="text" name="name" id="name" placeholder="Name" onChange={this.updateConditionName}/>
                    <br/>
                    <h4>Predicate</h4>
                    <PredicateCreator leaves={this.props.leaves} datastores={this.props.datastores}
                                      ref={ref => this.predicate = ref}/>
                    <br/>
                    <h4>Action</h4>
                    {/*<ActionCreator leaves={this.props.leaves} datastores={this.props.datastores}*/}
                                   {/*ref={c => this._action = c}/>*/}

                </ModalBody>
                {/*this.props.createCondition(this.props.hub, this.props.name)}*/}
                <ModalFooter>
                    <Button color="primary" onClick={() => console.log(this.predicate.createPredicate())}>
                        Send
                    </Button>{' '}
                    <Button color="secondary" onClick={this.props.toggleCreate}>Cancel</Button>
                </ModalFooter>
            </Modal>
        );
    }
}

CreateCondition.propTypes = {
    createErrors: PropTypes.array,
    createCondition: PropTypes.func,
    toggleCreate: PropTypes.func,
    show: PropTypes.bool,
    hub: PropTypes.number,
    name: PropTypes.string,
    leaves: PropTypes.array,
    datastores: PropTypes.array
};


