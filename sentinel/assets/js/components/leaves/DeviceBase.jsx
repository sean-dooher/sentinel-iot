import React from "react";
import PropTypes from "prop-types";
import {OutValue} from "../values/OutValue";

export class DeviceBase extends React.Component {
    getValue() {
        if (this.props.mode === "IN") {
            return this.props.value.toString() + (this.props.format === "number+units" ? this.props.units : "");
        }
        else {
            return <OutValue value={this.props.value} format={this.props.format} small connected={this.props.connected}
                             updateValue={(value) => this.props.updateDevice(this.props.hub, this.props.leaf,
                                                        this.props.name, this.props.format, value)}/>
        }
    }

    render() {
        return (
            <div className="row">
                <div className="col-md-6">{this.props.name}</div>
                <div className="col-md-6">{this.getValue()}</div>
            </div>
        );
    }
}

DeviceBase.propTypes = {
    name: PropTypes.string,
    format: PropTypes.string,
    value: PropTypes.any,
    units: PropTypes.string,
    hub: PropTypes.number,
    leaf: PropTypes.string,
    connected: PropTypes.bool,
    updateDevice: PropTypes.func
};