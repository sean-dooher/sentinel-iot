import React from "react";
import PropTypes from "prop-types";
import {Container, Row} from 'reactstrap';
import CreateHubModal from "../../containers/navigation/CreateHubModal";
import DeleteHubModal from "../../containers/navigation/DeleteHubModal";

export class Sidebar extends React.Component {
    isActive(id) {
        return this.props.active === id;
    }

    render() {
        return (
                <Container fluid={true}>
                    <Row>
                        <nav className="col-sm-3 col-md-2 d-none d-sm-block bg-light sidebar">
                            <ul className="nav nav-pills flex-column">
                                {
                                    this.props.hubs.map((hub, key) =>
                                        <li className="nav-item" data-toggle="tooltip" data-placement="right" key={key}>
                                            <a className={"nav-link" + (this.isActive(hub.id) ? " active" : "")}
                                               href="#" onClick={() => !this.isActive(hub.id) ? this.props.changeHub(hub.id) : null}>
                                                {hub.id + " - " + hub.name}
                                                {this.isActive(hub.id) ?
                                                    <span className="float-right" onClick={this.props.toggleDelete}>&times;</span>
                                                : null}
                                            </a>

                                        </li>)
                                }
                                <li>
                                    <a className="nav-link" href="#" onClick={this.props.toggleCreate}>Create a Hub</a>
                                </li>
                            </ul>
                        </nav>
                    </Row>
                    <CreateHubModal />
                    <DeleteHubModal />
                </Container>);
    }

    componentDidMount() {
        this.props.refreshHubs();
    }

}

Sidebar.propTypes = {
    hubs: PropTypes.array,
    active: PropTypes.number,
    changeHub: PropTypes.func,
    refreshHubs: PropTypes.func,
    toggleCreate: PropTypes.func,
    toggleDelete: PropTypes.func
};