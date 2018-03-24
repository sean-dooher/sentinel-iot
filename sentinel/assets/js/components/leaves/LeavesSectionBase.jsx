import React from "react";
import PropTypes from "prop-types";
import {Button, Alert, Row} from "reactstrap";
import RegisterLeafModal from "../../containers/leaves/RegisterLeafModal";
import Leaf from "../../containers/leaves/Leaf";

export class LeavesSectionBase extends React.Component {
    render() {
        return (
            <section className="leaves">
                <RegisterLeafModal />
                <h2>Leaves <Button color='primary' onClick={this.toggleRegister}>Register</Button></h2>
                {this.props.leaves.length === 0 ?
                    <Alert color="info">You currently have no leaves registered. Click the button above to register a
                        new one</Alert> : null}
                <Row>
                    {this.props.leaves.map((leaf, key) => <Leaf key={key} {...leaf} />)}
                </Row>
                <hr/>
            </section>
        );
    }
}
// TODO: add dragula support
LeavesSectionBase.propTypes = {
    leaves: PropTypes.array,
    toggleRegister: PropTypes.func
};