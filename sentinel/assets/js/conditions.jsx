import React from "react";

export class Conditions extends React.Component {
    render(){
        if(this.props.conditions.length > 0) {
            return (
                <table className="table table-bordered table-striped">
                    <thead>
                    <tr>
                        <th>Name</th>
                        <th>Predicate</th>
                        <th>Action</th>
                        <th>Action Target</th>
                        <th>Action Value</th>
                    </tr>
                    </thead>
                    <tbody>
                    {this.props.conditions.map((condition, key) =>
                        <tr key={key}>
                            <td>{condition.name}</td>
                            <td>{condition.predicate}</td>
                            <td>{condition.action.action_type}</td>
                            <td>{condition.action.target}</td>
                            <td>{condition.action.device}</td>
                        </tr>
                    )}
                    </tbody>
                </table>);
        }
        return null;
    }
}