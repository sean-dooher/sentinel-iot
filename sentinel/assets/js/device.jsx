import React from "react";
import { OutValue } from "./outValue";
import PropTypes from "prop-types";

export class Device extends React.Component {
    constructor(props) {
        super(props);
        this.sendSet = this.sendSet.bind(this);
    }

    sendSet(value) {
        let headers = Object.assign({}, window.putHeader);
        headers.body = JSON.stringify({value: value, format: this.props.format, device:this.props.name});
        fetch(window.host + "/api/hub/" + window.hub + "/leaves/" + this.props.leaf, headers)
            .then(r => {
                if(r.ok) {
                    r.json().then(json => {
                            if (!json.accepted) {
                                console.log("Error: " + json.reason);
                            }
                        }
                    ).catch(() => console.log("Error: error occured parsing response"))
                } else {
                    r.text().then(text => console.log(text));
                    console.log("Error: " + r.statusText + " (" + r.status + ")");
                }
            })
            .catch((e) => console.log("Error: an unknown error has occured\n"+e));
    }

    getValue() {
        if(this.props.mode === "IN") {
            return this.props.value.toString() + (this.props.format === "number+units" ? this.props.units : "");
        }
        else {
            return <OutValue value={this.props.value} format={this.props.format} small connected={this.props.connected} send={this.sendSet}/>
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
                <div className="col-md-4">{ this.props.format }</div>
                <div className="col-md-4">
                    { this.getValue() }
                </div>
           </div>
       );
    }
}

Device.propTypes = {
  name: PropTypes.string,
  format: PropTypes.string,
  value: PropTypes.any,
  units: PropTypes.string,
  leaf: PropTypes.string,
  connected: PropTypes.bool,
};