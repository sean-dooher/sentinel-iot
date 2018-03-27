import React from "react";
import PropTypes from "prop-types";
import {Button} from "reactstrap";
import {ComparatorPredicate} from "./ComparatorPredicate";

export class PredicateCreator extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            count: 1,
            predicates: [1]
        };
    }

    render() {
        return this.state.predicates.map((key, predicate) => {
            return <div key={key} className="row">
                <div className="col-11">
                    <ComparatorPredicate datastores={this.props.datastores} leaves={this.props.leaves}/>
                </div>
                <div className="col-1">
                    <Button size="sm" color="danger">-</Button>
                </div>
            </div>
        });
    }
}

PredicateCreator.propTypes = {
    leaves: PropTypes.array,
    datastores: PropTypes.array
};


