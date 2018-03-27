import React from "react";
import PropTypes from "prop-types";
import ToggleButton from 'react-toggle-button';
import {Input} from "reactstrap";

export class Value extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            value: this.props.value
        };
        this.handleChange = this.handleChange.bind(this);
        this.sendChange = this.sendChange.bind(this);
    }

    getPattern() {
        if (this.props.format === "number" || this.props.format === "number+units") {
            return "^[0-9]+$";
        } else if (this.props.format === "bool") {
            return "^(true|false|0|1)$";
        } else {
            return ".*";
        }
    }

    handleChange(event) {
        this.setState({value: event.target.value});
        if (this.props.onChange)
            this.props.onChange(event.target.value);
    }

    sendChange(value) {
        if (value === undefined)
            value = this.state.value;

        if (this.props.format !== 'string') {
            value = JSON.parse(value);
        }
        this.props.updateValue(value);
    }

    componentDidUpdate(prevProps, prevState) {
        if (prevProps.value !== this.props.value) {
            if (this.props.format === 'bool') {
                this.setState({value: this.props.value});
            }
        }
    }

    render() {
        if (this.props.format === "bool") {
            if (this.props.boolSelect) {
                return (
                    <div>
                        <div className={"input-group" + (this.props.small ? " input-group-xs" : "")}>
                            <Input type="select" onChange={this.handleChange}
                                   className="custom-select" aria-label="new_value"
                                   disabled={!this.props.connected && this.props.out}>
                                <option>{"true" + (this.props.value ? " (current)" : "")}</option>
                                <option>{"false" + (this.props.value !== undefined && !this.props.value ? " (current)" : "")}</option>
                            </Input>
                            <div className="input-group-append input-group-btn">
                                <button type="button" hidden={!this.props.out} disabled={!this.props.connected}
                                        onClick={this.sendChange} className="btn btn-outline-secondary">
                                    <i className="fas fa-angle-right"/>
                                </button>
                            </div>
                        </div>
                    </div>);
            }
            return (
                <div className="d-inline-block">
                    <ToggleButton
                        value={this.state.value || false}
                        onToggle={() => {
                            this.setState({value: !this.state.value});
                            this.sendChange(!this.state.value);
                        }} disabled={!this.props.connected && this.props.out}/>
                </div>);
        } else {
            return (
                <div>
                    <div className={"input-group" + (this.props.small ? " input-group-xs" : "")}>
                        <input type="text" pattern={this.getPattern()} onChange={this.handleChange}
                               className="form-control" aria-label="new_value"
                               placeholder={this.props.value ? this.props.value + "(current)" : null}
                               aria-describedby="basic-addon2" disabled={!this.props.connected && this.props.out}/>
                        <div className="input-group-append input-group-btn">
                            <button type="button" hidden={!this.props.out} disabled={!this.props.connected}
                                    onClick={this.sendChange} className="btn btn-outline-secondary">
                                <i className="fas fa-angle-right"/>
                            </button>
                        </div>
                    </div>
                </div>);
        }
    }
}

Value.propTypes = {
    small: PropTypes.bool,
    value: PropTypes.any,
    format: PropTypes.string,
    connected: PropTypes.bool,
    updateValue: PropTypes.func,
    onChange: PropTypes.func,
    out: PropTypes.bool,
    boolSelect: PropTypes.bool
};