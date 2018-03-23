import React from "react";
import PropTypes from "prop-types";
import { connect } from 'react-redux'

export class HeaderBar extends React.Component {
    render() {
        return <header>
            <div className="navbar navbar-expand-md navbar-dark fixed-top bg-dark">
                <a className="navbar-brand" href="#">Dashboard</a>
                <button className="navbar-toggler d-lg-none" type="button" data-toggle="collapse"
                        data-target="#main-nav" aria-controls="main-dev" aria-expanded="false"
                        aria-label="Toggle navigation">
                    <span className="navbar-toggler-icon"/>
                </button>
                <div className="collapse navbar-collapse" id="main-nav">
                    <ul className="navbar-nav mr-auto">
                        {
                            this.props.links.map((link, key) => {
                                if (this.props.active === link.name) {
                                    return <li className={"nav-item active"} key={key}>
                                        <a className="nav-link" href={link.href}>{link.name}</a>
                                    </li>;
                                } else {
                                    return <li className={"nav-item"} key={key}>
                                        <a className="nav-link" href={link.href}>{link.name}</a>
                                    </li>;
                                }
                            })
                        }
                    </ul>
                    <div className="text-white">
                        {window.info.username}
                        <a className="nav-logout" href="/accounts/logout">
                            <i className="fa fa-sign-out-alt"/>
                        </a>
                    </div>
                </div>
            </div>
        </header>;
    }
}

HeaderBar.propTypes = {
    links: PropTypes.array,
    active: PropTypes.string,
};
