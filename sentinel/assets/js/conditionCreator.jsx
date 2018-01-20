import React from "react";
import {ComparatorPredicate} from "./comparatorPredicate";
import PropTypes from "prop-types";
import {Value} from "./value";

export class ConditionCreator extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            operator: '',
        };
        this.handleOperatorChange = this.handleOperatorChange.bind(this);
    }

    handleOperatorChange(event) {
        this.setState({operator: event.target.value});
    }

    booleanSelector() {
        return (<div className="row">
            <div className="col-md-3">
                Operator:
                <select name="operator" className="form-control custom-select form-control-sm"
                        value={this.state.operator} onChange={this.handleOperatorChange}>
                    <option value='' />
                    <option value='AND'>AND</option>
                    <option value='OR'>OR</option>
                    <option value='XOR'>XOR</option>
                </select>
            </div>
        </div>);
    }

    render(){
       return <div>
            <h3>Predicate</h3>
            <ComparatorPredicate leaves={this.props.leaves} ref={(c) => this._firstPred = c}/>
            {this.booleanSelector()}
            {this.state.operator !== '' ? <ComparatorPredicate leaves={this.props.leaves} ref={(c) => this._secondPred = c}/> : null}
            <br />
            <h3>Action</h3>
       </div>;
    }
}

ConditionCreator.propTypes = {
    leaves: PropTypes.array
};