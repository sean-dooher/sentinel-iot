import React from "react";
import {getNameFromUUID} from "../../utils/leafUtils";
import {actionToString, predicateToString} from "../../utils/conditionUtils";
import PropTypes from "prop-types";
import {Alert, Button} from "reactstrap";
import DeleteConditionModal from "../../containers/conditions/DeleteConditionModal";
import CreateConditionModal from "../../containers/conditions/CreateConditionModal";

export class ConditionSectionBase extends React.Component {
    render() {
        return (
            <div>
                <h2>Conditions <Button color='primary' onClick={this.props.toggleCreate}>Create</Button></h2>
                <DeleteConditionModal/>
                <CreateConditionModal/>
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
                            <th>Actions</th>
                            <th/>
                        </tr>
                        </thead>
                        <tbody>
                        {this.props.conditions.map((condition, key) =>
                            <tr key={key}>
                                {console.log(condition)}
                                <td>{condition.name}</td>
                                <td>{predicateToString(condition.predicate, this.props.leaves)
                                    .split('\n').map((item, key) => {
                                    return <span key={key}>{item}<br/></span>
                                })}</td>
                                <td>
                                    {condition.actions.map((action, key) => {
                                        return (
                                            <div key={key}>
                                                {actionToString(action, this.props.leaves)}
                                                <br/>
                                            </div>);
                                    })}
                                </td>
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