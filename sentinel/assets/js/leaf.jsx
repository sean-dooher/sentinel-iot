import React from "react";
import { Device } from "./device";

export class Leaf extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            hidden_devices: [],
            update_date: new Date(Date.now())
        }
    }

    updateTime() {
        this.setState({update_date: new Date(Date.now())});
    }

    render(){
       return (
                <div className="leaf col-sm-12 col-md-12 col-lg-6 col-xl-6">
                    <div className="card text-center">
                      <div className="card-header">
                          <div className="float-left grabber leaf-icon drag-handle"><i className="fas fa-bars"></i></div>
                          <div className="float-left" data-toggle="tooltip" data-placement="bottom" title={this.props.uuid}>{this.props.name} ({this.props.model}) -- {this.props.is_connected ? <span className="badge badge-success">Connected</span> : <span className="badge badge-danger">Disconnected</span>}</div>
                          <div className="float-right" id="leafdropdown" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                            <div className="dropdown-toggle dropdown-toggle-split pointer leaf-icon"></div>
                          </div>
                          <div className="dropdown-menu" aria-labelledby="leafdropdown">
                              <button className="dropdown-item" data-toggle="modal" data-target={"#" + this.props.uuid + "-modal"}>Configure Devices</button>
                              <button className="dropdown-item">Hide Leaf</button>
                          </div>
                          <div className="modal fade" id={this.props.uuid + "-modal"} role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true">
                              <div className="modal-dialog" role="document">
                                <div className="modal-content">
                                  <div className="modal-header">
                                    <h5 className="modal-title">Leaf configuration</h5>
                                    <button type="button" className="close" data-dismiss="modal" aria-label="Close">
                                      <span aria-hidden="true">&times;</span>
                                    </button>
                                  </div>
                                  <div className="modal-body">
                                    <input type="checkbox" className="form-check-input" id="device-name-1" />
                                    <label className="form-check-label" htmlFor="device-name-1">Door</label>
                                  </div>
                                  <div className="modal-footer">
                                    <button type="button" className="btn btn-secondary" data-dismiss="modal">Close</button>
                                    <button type="button" className="btn btn-primary">Save changes</button>
                                  </div>
                                </div>
                              </div>
                          </div>
                      </div>
                      <div className="card-body">
                      { this.props.devices.filter((device) => !this.state.hidden_devices.includes(device)).length > 0 ?
                        <div className="row">
                            <div className="col-md-4"><strong>Device</strong></div>
                            <div className="col-md-3"><strong>Format</strong></div>
                            <div className="col-md-4"><strong>Value</strong></div>
                        </div> : <p>This Leaf has no devices attached</p> }
                            { this.props.devices.filter((device) => !this.state.hidden_devices.includes(device)).map((device, key) => <Device key={key} {... device} onChange={this.updateTime.bind(this)} />)}
                        </div>
                      <div className="card-footer text-muted">
                        Last Updated: { this.state.update_date.toLocaleTimeString() }
                      </div>
                    </div>
                </div>);
    }

    componentDidMount() {
        $(function () {
          $('[data-toggle="tooltip"]').tooltip()
        });
    }
}