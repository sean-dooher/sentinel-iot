import React from "react";
import {ComparatorPredicate} from "./comparatorPredicate";
import { ActionCreator } from "./actionCreator";
import PropTypes from "prop-types";
import { Input, FormGroup, Label } from "reactstrap";

export class ConditionCreator extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            operator: '',
            conditionName: ''
        };
        this.handleOperatorChange = this.handleOperatorChange.bind(this);
        this.updateConditionName = this.updateConditionName.bind(this);
        this.getCondition = this.getCondition.bind(this);
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
                    <option value='NOT'>NOT</option>
                    <option value='AND'>AND</option>
                    <option value='OR'>OR</option>
                    <option value='XOR'>XOR</option>
                </select>
            </div>
        </div>);
    }

    updateConditionName(event) {
        event.preventDefault();
        this.setState({conditionName: event.target.value});
    }

    getCondition() {
        let predicate;
        if(this.state.operator === '') {
            predicate = this._firstPred.getPredicate();
        } else if (this.state.operator === 'NOT') {
            predicate = ['NOT', this._firstPred.getPredicate()];
        } else {
            predicate = [this.state.operator, this._firstPred.getPredicate(), this._secondPred.getPredicate()];
        }
        return {
            name: this.state.conditionName,
            predicate: predicate,
            action: this._action.getAction()
        }
    }

    render(){
       return <div>
            <h4>Name</h4>
            <Input type="text" name="name" id="name" placeholder="Name" onChange={this.updateConditionName} />
            <br />
            <h4>Predicate</h4>
            {this.booleanSelector()}
            <ComparatorPredicate datastores={this.props.datastores} leaves={this.props.leaves} ref={(c) => this._firstPred = c}/>
            {this.state.operator !== '' && this.state.operator !== 'NOT' ?
                <ComparatorPredicate datastores={this.props.datastores} leaves={this.props.leaves} ref={(c) => this._secondPred = c}/> : null}
            <br />
            <h4>Action</h4>
            <ActionCreator leaves={this.props.leaves} datastores={this.props.datastores} ref={c => this._action = c}/>
       </div>;
    }
}

ConditionCreator.propTypes = {
    leaves: PropTypes.array,
    datastores: PropTypes.array
};