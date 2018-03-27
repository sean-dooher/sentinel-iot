import React from "react";
import PropTypes from "prop-types";
import {Button, Input} from "reactstrap";
import {ComparatorPredicate} from "./ComparatorPredicate";

export class PredicateCreator extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            count: 0,
            connectors: [[0, '']]
        };
        this.predicates = [];
    }

    changeConnector(event, index) {
        let value = event.target.value;
        this.setState((lastState) => {
            let pair = lastState.connectors[index];
            let lastValue = pair[1];

            if (value !== '' && lastValue === '') {
                let count = lastState.count + 1;
                let connectors = lastState.connectors.concat([[count, '']]);
                connectors[index] = [connectors[index][0], value];
                return {connectors, count};
            } else if (value === '' && lastValue !== '') {
                let connectors = lastState.connectors.filter((pair, i) => index !== i);
                if (index + 1 < lastState.connectors.length) {
                    connectors[index] = [pair[0], lastState.connectors[index + 1][1]];
                } else {
                    connectors[index] = [pair[0], ''];
                }
                return {connectors};
            } else {
                let connectors = lastState.connectors.concat();
                connectors[index] = [pair[0], value];
                return {connectors}
            }
        });
    }

    createPredicate() {
        let predicate = this.predicates.slice(-1)[0][1].getPredicate();
        console.log(this.state.connectors);
        for(let i = this.predicates.length - 2; i >= 0; i--) {
            let connector = this.state.connectors[i][1];
            predicate = [connector, predicate, this.predicates[i][1].getPredicate()];
        }

        return predicate;
    }

    addPredicate(pair) {
        this.predicates = this.predicates.filter(p => p[0] !== pair[0]);
        this.predicates.push(pair);
    }

    render() {
        return this.state.connectors.map((predicate, index) => {
            return <div key={predicate[0]}>
                <div className="row">
                    <div className="col-12">
                        <ComparatorPredicate datastores={this.props.datastores} leaves={this.props.leaves}
                            ref={(ref) => this.addPredicate([predicate[0], ref])}/>
                    </div>
                </div>
                <br/>
                <div className="row">
                    <div className="col-2">
                        <Input type="select" className="custom-select" value={this.state.connectors[index][1]}
                               onChange={(event) => this.changeConnector(event, index)}>
                            <option/>
                            <option>AND</option>
                            <option>OR</option>
                            <option>XOR</option>
                        </Input>
                    </div>
                </div>
            </div>;
        });
    }
}

PredicateCreator.propTypes = {
    leaves: PropTypes.array,
    datastores: PropTypes.array
};


