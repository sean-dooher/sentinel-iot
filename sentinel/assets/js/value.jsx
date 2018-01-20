import React from "react";
import PropTypes from "prop-types";

export class Value extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            value: this.props.value
        };
        this.handleChange = this.handleChange.bind(this);
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

    render(){
        if (this.props.format === "bool") {
            return (<select className={"form-control custom-select" + (this.props.small ? " form-control-sm" : "")}
                            value={this.state.value} onChange={this.handleChange}>
                        <option value="true">true</option>
                        <option value="false">false</option>
                    </select>);
        } else {
            return (<input type="text" pattern={this.getPattern()} onChange={this.handleChange}
                           className={"form-control" + (this.props.small ? " form-control-sm" : "")} aria-label="new_value" />);
        }
    }
}

Value.propTypes = {
    value: PropTypes.any,
    format: PropTypes.string,
    small: PropTypes.bool,
};