import React from "react";
import { Header } from "./header";
import { Sidebar } from "./sidebar";
import PropTypes from "prop-types";

export class AdminPage extends React.Component {
    render(){
        return (
            <div>
                <Header />
                <Sidebar hubs={this.props.hubs} refreshHubs={this.props.refreshHubs} changeHub={this.props.changeHub} activeHub={this.props.activeHub}/>
                <main role="main" className="col-sm-9 ml-sm-auto col-md-10 pt-3">
                    { this.props.children }
                </main>
            </div>
        );
    }
}

AdminPage.propTypes = {
    hubs: PropTypes.array,
    activeHub: PropTypes.number,
    refreshHubs: PropTypes.func,
    changeHub: PropTypes.func,
};

