import React from "react";

export class Sidebar extends React.Component {
    constructor(props) {
        super(props);
    }

    render(){
       return (
       <div className="container-fluid">
          <div className="row">
            <nav className="col-sm-3 col-md-2 d-none d-sm-block bg-light sidebar">
              <ul className="nav nav-pills flex-column">
                <li className="nav-item">
                  <a className="nav-link active" href="#leaves">Leaves</a>
                </li>
                <li className="nav-item">
                  <a className="nav-link" href="#conditions">Conditions</a>
                </li>
              </ul>
            </nav>
          </div>
        </div>);
    }
}