import React from "react";
import { OutValue } from "./outValue";
import PropTypes from "prop-types";

export class Device extends React.Component {
    constructor(props) {
        super(props);
        this.sendSet = this.sendSet.bind(this);
    }

    sendSet() {

    }

    getValue() {
        if(this.props.mode === "IN") {
            return this.props.value.toString() + (this.props.format === "number+units" ? this.props.units : "");
        }
        else {
            return <OutValue value={this.props.value} format={this.props.format} small connected={this.props.connected}/>
        }
    }

    componentDidUpdate(prevProps, prevState) {
        if(prevProps.value !== this.props.value) {
            this.props.update();
        }

    }

    render(){
       return (
           <div className="row">
                <div className="col-md-4">{ this.props.name }</div>
                <div className="col-md-3">{ this.props.format }</div>
                <div className="col-md-4">
                    { this.getValue() }
                </div>
                <div className="col-md-1"><i className="fas fa-cog"></i></div>
           </div>
       );
    }
}

Device.propTypes = {
  name: PropTypes.string,
  format: PropTypes.string,
  value: PropTypes.any,
  units: PropTypes.string,
  connected: PropTypes.bool,
};