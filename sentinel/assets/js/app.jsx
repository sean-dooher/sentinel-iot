import React from "react";
import {connect} from 'react-redux'
import {Navigation} from "./components/navigation/Navigation";
import HubSideBar from "./containers/navigation/HubSideBar";
import LeavesSection from "./containers/leaves/LeavesSection";
import PropTypes from "prop-types";
import DatastoresSection from "./containers/datastores/DatastoresSection";
import ConditionSection from "./containers/conditions/ConditionSection";

export class AppBase extends React.Component {
    render() {
        return (
            <Navigation>
                <HubSideBar />
                {this.props.hub !== -1 ?
                    <main className="col-sm-9 ml-sm-auto col-md-10 pt-3" role="main">
                        <DatastoresSection/>
                        <LeavesSection/>
                        <ConditionSection/>
                    </main> : null}
            </Navigation>);
    }
}

AppBase.propTypes = {
    hub: PropTypes.number
};

const mapStateToProps = (state) => {
    return {
        hub: state.hub.active
    };
};


let App = connect(mapStateToProps, null)(AppBase);
export default App;