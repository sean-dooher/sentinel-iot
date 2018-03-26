import React from "react";
import {getNameFromUUID} from "../../utils/leafUtils";
import {predicateToString} from "../../utils/conditionUtils";
import PropTypes from "prop-types";
import {Alert, Button} from "reactstrap";
import DeleteConditionModal from "../../containers/conditions/DeleteConditionModal";

export class ConditionSectionBase extends React.Component {
    render() {
        return (
            <div>
                <h2>Conditions <Button color='primary' onClick={this.props.toggleCreate}>Create</Button></h2>
                <DeleteConditionModal/>
                {this.props.conditions.length === 0 ?
                    <Alert color="info">
                        You currently have no conditions. Click the button above to create a new
                        one
                    </Alert> : null}
                {this.props.conditions.length > 0 ?
                    <table className="table table-bordered table-striped text-center">
                        <thead>
                        <tr>
                            <th>Name</th>
                            <th>Predicate</th>
                            <th>Action</th>
                            <th>Action Target</th>
                            <th>Action Value</th>
                            <th/>
                        </tr>
                        </thead>
                        <tbody>
                        {this.props.conditions.map((condition, key) =>
                            <tr key={key}>
                                <td>{condition.name}</td>
                                <td>{predicateToString(condition.predicate, this.props.leaves)
                                    .split('\n').map((item, key) => {
                                    return <span key={key}>{item}<br/></span>
                                })}</td>
                                <td>{condition.action.action_type}</td>
                                <td>
                                    {'<'}
                                    {getNameFromUUID(condition.action.target, this.props.leaves)}, {condition.action.device}
                                    {'>'}
                                </td>
                                <td>{condition.action.value.toString()}</td>
                                <td>
                                    <button className="btn btn-danger"
                                            onClick={() => this.props.toggleDelete(condition.name)}>Delete
                                    </button>
                                </td>
                            </tr>
                        )}
                        </tbody>
                    </table> : null}</div>);
    }
}

ConditionSectionBase.propTypes = {
    leaves: PropTypes.array,
    conditions: PropTypes.array,
    toggleDelete: PropTypes.func,
    toggleCreate: PropTypes.func
};