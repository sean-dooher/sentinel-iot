import React from "react";
import NavLinkBar from "../../containers/navigation/NavLinkBar";

export class Navigation extends React.Component {
    constructor(props) {
        super(props);
    }
    render(){
        return (
            <div>
                <NavLinkBar />
                {this.props.children}
            </div>
        );
    }
}

