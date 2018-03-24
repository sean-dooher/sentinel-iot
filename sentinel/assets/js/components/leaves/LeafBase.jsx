import React from "react";
import Device from "../../containers/leaves/Device";
import DeleteLeafModal from "../../containers/leaves/DeleteLeafModal";
import {Card, CardBody, CardHeader, CardFooter} from "reactstrap";
import PropTypes from "prop-types";

export class LeafBase extends React.Component {
    render(){
       return (
                <div className="leaf col-sm-12 col-md-12 col-lg-6 col-xl-6">
                    <Card>
                      <CardHeader>
                          <div className="float-left grabber leaf-icon drag-handle"><i className="fas fa-bars"/></div>
                          <div className="float-left" data-toggle="tooltip" data-placement="bottom" title={this.props.uuid}>
                              {this.props.name} ({this.props.model}) -- {this.props.is_connected ?
                              <span className="badge badge-success">Connected</span> :
                              <span className="badge badge-danger">Disconnected</span>}
                          </div>
                          <div className="float-right" id="leafdropdown" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                            <div className="dropdown-toggle dropdown-toggle-split pointer leaf-icon"/>
                          </div>
                          <div className="dropdown-menu" aria-labelledby="leafdropdown">
                              <button className="dropdown-item" onClick={this.props.toggleDelete}>Disconnect Leaf</button>
                          </div>
                          <DeleteLeafModal uuid={this.props.uuid}/>
                      </CardHeader>
                      <CardBody className={"devices"}>
                      { this.props.devices.length < 0 ? <p>This Leaf has no devices attached</p> : null }
                            { this.props.devices.map((device, key) =>
                                <Device key={key} leaf={this.props.uuid} {... device} connected={this.props.is_connected} />)}
                        </CardBody>
                      <CardFooter className="text-muted text-center">
                        {/*Last Updated: { this.state.date }*/}
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

LeafBase.propTypes = {
    uuid: PropTypes.string,
    model: PropTypes.string,
    name: PropTypes.string,
    devices: PropTypes.array,
    is_connected: PropTypes.bool,
    toggleDelete: PropTypes.func
};