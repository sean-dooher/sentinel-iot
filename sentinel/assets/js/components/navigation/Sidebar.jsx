import React from "react";
import PropTypes from "prop-types";
import {Container, Row} from 'reactstrap';
import HubModal from "../../containers/navigation/HubModal";

export class Sidebar extends React.Component {
    render() {
        return (
                <Container fluid={true}>
                    <Row>
                        <nav className="col-sm-3 col-md-2 d-none d-sm-block bg-light sidebar">
                            <ul className="nav nav-pills flex-column">
                                {
                                    this.props.hubs.map((hub, key) =>
                                        <li className="nav-item" data-toggle="tooltip" data-placement="right" key={key}>
                                            <a className={"nav-link" + (this.props.active === hub.id ? " active" : "")}
                                               href="#"
                                               onClick={() => this.props.changeHub(hub.id)}>{hub.id + " - " + hub.name}</a>
                                        </li>)
                                }
                                <li>
                                    <a className="nav-link" href="#" onClick={this.props.toggleCreate}>Create a Hub</a>
                                </li>
                            </ul>
                        </nav>
                    </Row>
                    <HubModal />
                </Container>);
    }
}

Sidebar.propTypes = {
    hubs: PropTypes.array,
    active: PropTypes.number,
    changeHub: PropTypes.func,
    toggleCreate: PropTypes.func
};