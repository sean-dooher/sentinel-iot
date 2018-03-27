import React from "react";
import PropTypes from "prop-types";
import {Button} from "reactstrap";

export class ComparatorPredicate extends React.Component {
    render() {
        return this.state.predicates.map((key, predicate) => {
            return <div>
                {/*<ComparatorPredicate datastores={this.props.datastores} leaves={this.props.leaves}/>*/}
                <Button size="sm" color="danger">-</Button>
            </div>
        });
    }
}

ComparatorPredicate.propTypes = {
    leaves: PropTypes.array,
    datastores: PropTypes.array
};


