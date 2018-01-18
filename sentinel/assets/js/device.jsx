import React from "react";

export class Device extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            value: this.props.value
        };
        this.handleChange = this.handleChange.bind(this);
        this.sendSet = this.sendSet.bind(this);
    }

    getPattern() {
        if(this.props.format === "number" || this.props.format === "number+units") {
            return "^[0-9]+$";
        } else if (this.props.format === "bool") {
            return "^(true|false|0|1)$";
        } else {
            return ".*";
        }
    }

    handleChange(event) {
        this.setState({value: event.target.value});
    }

    sendSet() {

    }

    getValue() {
        if(this.props.mode === "IN") {
            return this.props.value.toString() + (this.props.format === "number+units" ? this.props.units : "");
        }
        else {
            if(this.props.format === "bool") {
                return (
                    <div className="input-group input-group-xs">
                      <select className="form-control custom-select" value={this.state.value.toString()} onChange={this.handleChange}>
                        <option value="true">true</option>
                        <option value="false">false</option>
                      </select>
                      <div className="input-group-append input-group-btn">
                        <button onClick={this.sendSet} className="btn btn-outline-secondary" type="button"><i className="fas fa-angle-right"></i></button>
                      </div>
                    </div>
                );
            } else {
                return (
                    <div className="input-group input-group-xs">
                      <input type="text" pattern={this.getPattern()} onChange={this.handleChange} value={ this.state.value } className="form-control" placeholder="New Value" aria-label="new_value" aria-describedby="basic-addon2" />
                      <div className="input-group-append input-group-btn">
                        <button onClick={this.sendSet} className="btn btn-outline-secondary" type="button"><i className="fas fa-angle-right"></i></button>
                      </div>
                    </div>);
            }
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