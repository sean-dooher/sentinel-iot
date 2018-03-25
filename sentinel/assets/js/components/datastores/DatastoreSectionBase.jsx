import React from "react";
import PropTypes from "prop-types";
import {Button, Alert, Row} from "reactstrap";
import CreateDatastoreModal from "../../containers/datastores/CreateDatastoreModal";
import Datastore from "../../containers/datastores/Datastore";
import Dragula from 'react-dragula';

export class DatastoreSectionBase extends React.Component {
    dragulaDecorator(component) {
        if (component) {
            let options = {
                invalid: function (el, handle) {
                    console.log(handle.tagName);
                    return !handle.classList.contains('drag-handle') && !handle.parentNode.classList.contains('drag-handle');
                }
            };
            Dragula([component], options);
        }
    }

    render() {
        return (
            <section className="datastores">
                <h2>Datastores <Button color='primary' onClick={this.toggleDatastoreModal}>Create</Button></h2>

                {this.state.datastores.length === 0 ?
                    <Alert color="info">You currently have no datastores. Click the button above to create a new
                        one</Alert> : null}
                <div className="row" ref={this.dragulaDecorator}>
                    {this.props.datastores.map((datastore, key) => <Datastore delete={this.sendDeleteDatastore}
                                                                              key={key} {...datastore} />)}
                </div>
                <hr/>
            </section>
        );
    }
}

DatastoreSectionBase.propTypes = {
    leaves: PropTypes.array,
    toggleRegister: PropTypes.func
};