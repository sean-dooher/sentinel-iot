import React from "react";
import PropTypes from "prop-types";
import {Button} from "reactstrap";
import {LeafSelector} from "../values/LeafSelector";

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
            return <div key={key}>
                {/*<ComparatorPredicate datastores={this.props.datastores} leaves={this.props.leaves}/>*/}
                <LeafSelector literal leaves={this.props.leaves} datastores={this.props.datastores} />
                <Button size="sm" color="danger">-</Button>
            </div>
        });
    }
}

PredicateCreator.propTypes = {
    leaves: PropTypes.array,
    datastores: PropTypes.array
};


