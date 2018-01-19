import React from "react";
import { Device } from "./device";
import {Card, CardBody, CardHeader, CardFooter} from "reactstrap";
import PropTypes from "prop-types";

export class Leaf extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            update_date: new Date(Date.now())
        }
    }

    updateTime() {
        this.setState({update_date: new Date(Date.now())});
    }

    render(){
       return (
                <div className="leaf col-sm-12 col-md-12 col-lg-6 col-xl-6">
                    <Card>
                      <CardHeader>
                          <div className="float-left grabber leaf-icon drag-handle"><i className="fas fa-bars"></i></div>
                          <div className="float-left" data-toggle="tooltip" data-placement="bottom" title={this.props.uuid}>{this.props.name} ({this.props.model}) -- {this.props.is_connected ? <span className="badge badge-success">Connected</span> : <span className="badge badge-danger">Disconnected</span>}</div>
                          <div className="float-right" id="leafdropdown" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                            <div className="dropdown-toggle dropdown-toggle-split pointer leaf-icon"></div>
                          </div>
                          <div className="dropdown-menu" aria-labelledby="leafdropdown">
                              <button className="dropdown-item">Configure Devices</button>
                              <button className="dropdown-item">Hide Leaf</button>
                              <button className="dropdown-item">Disconnect Leaf</button>
                          </div>
                      </CardHeader>
                      <CardBody>
                      { this.props.devices.length > 0 ?
                        <div className="row">
                            <div className="col-md-4"><strong>Device</strong></div>
                            <div className="col-md-3"><strong>Format</strong></div>
                            <div className="col-md-4"><strong>Value</strong></div>
                        </div> : <p>This Leaf has no devices attached</p> }
                            { this.props.devices.map((device, key) =>
                                <Device key={key} leaf={this.props.uuid} sendMessage={this.props.sendMessage} {... device} connected={this.props.is_connected} />)}
                        </CardBody>
                      <CardFooter className="text-muted">
                        Last Updated: { this.state.update_date.toLocaleTimeString() }
                      </CardFooter>
                    </Card>
                </div>);
    }

    componentDidMount() {
        $(function () {
          $('[data-toggle="tooltip"]').tooltip()
        });
    }
}

Leaf.propTypes = {
    uuid: PropTypes.string,
    model: PropTypes.string,
    name: PropTypes.string,
    sendMessage: PropTypes.func,
    devices: PropTypes.array,
    is_connected: PropTypes.bool
};