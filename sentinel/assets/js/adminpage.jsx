import React from "react";
import { Header } from "./header";
import { Sidebar } from "./sidebar";

export class AdminPage extends React.Component {
    render(){
        return (
            <div>
                <Header />
                <Sidebar />
                <main role="main" className="col-sm-9 ml-sm-auto col-md-10 pt-3">
                    { this.props.children }
                </main>
            </div>
        );
    }
}
