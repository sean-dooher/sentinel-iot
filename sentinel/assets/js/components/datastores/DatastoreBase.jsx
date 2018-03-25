import React from "react";
import {
    Card,
    CardBody,
    CardHeader,
    CardFooter,
    Modal,
    ModalBody,
    ModalFooter,
    ModalHeader,
    Button,
    Alert
} from "reactstrap";
import {OutValue} from "../values/OutValue";
import PropTypes from "prop-types";

export class DatastoreBase extends React.Component {
    render() {
        return (
            <div className="leaf col-sm-12 col-md-6 col-lg-4 col-xl-4">
                <Card>
                    <CardHeader>
                        <div className="float-left grabber leaf-icon drag-handle"><i className="fas fa-bars"/></div>
                        <div className="float-left">{this.props.name}</div>
                        <div className="float-right" id="datastore" data-toggle="dropdown" aria-haspopup="true"
                             aria-expanded="false">
                            <div className="dropdown-toggle dropdown-toggle-split pointer leaf-icon"/>
                        </div>
                        <div className="dropdown-menu" aria-labelledby="leafdropdown">
                            <button className="dropdown-item" onClick={() => this.props.toggleDelete(this.props.name)}>
                                Delete Datastore
                            </button>
                        </div>
                    </CardHeader>
                    <CardBody>
                        <div className="row devices">
                            <div class="device">
                                <OutValue format={this.props.format} value={this.props.value}
                                          small connected
                                          updateValue={value =>
                                              this.props.updateDatastore(this.props.hub, this.props.name, this.props.format, value)}
                                />
                            </div>
                        </div>
                    </CardBody>
                    <CardFooter className="text-muted text-center">
                        {/*Last Updated: { this.state.date }*/}
                    </CardFooter>
                </Card>
            </div>);
    }
}

DatastoreBase.propTypes = {
    name: PropTypes.string,
    toggleDelete: PropTypes.func,
    format: PropTypes.string,
    value: PropTypes.any,
    updateDatastore: PropTypes.func,
    hub: PropTypes.number
};