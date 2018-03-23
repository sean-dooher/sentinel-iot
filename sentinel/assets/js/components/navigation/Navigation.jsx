import React from "react";
import NavLinkBar from "../../containers/navigation/NavLinkBar";
import HubSideBar from "../../containers/navigation/HubSideBar";

export class Navigation extends React.Component {
    constructor(props) {
        super(props);
    }
    render(){
        return (
            <div>
                <NavLinkBar />
                <HubSideBar />
                <main className="col-sm-9 ml-sm-auto col-md-10 pt-3" role="main">
                    {this.props.children}
                </main>
            </div>
        );
    }
}

