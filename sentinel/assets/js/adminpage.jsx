import React from "react";
import { Header } from "./header";
import PropTypes from "prop-types";

export class AdminPage extends React.Component {
    render(){
        return (
            <div>
                <Header />
                { this.props.children }
            </div>
        );
    }
}

