import React from "react";
import {Navigation} from "./components/navigation/Navigation";
import LeavesSection from "./containers/leaves/LeavesSection";

export class App extends React.Component {
    render() {
        return (
            <Navigation>
                {this.props.active !== -1 ?
                    <LeavesSection/> : null}
            </Navigation>);
    }
}

