import React from "react";

export class Header extends React.Component {
    render(){
       return (
            <header>
                <nav className="navbar navbar-expand-md navbar-dark fixed-top bg-dark">
                    <a className="navbar-brand" href="#">Dashboard</a>
                    <button className="navbar-toggler d-lg-none" type="button" data-toggle="collapse" data-target="#main-nav" aria-controls="main-dev" aria-expanded="false" aria-label="Toggle navigation">
                      <span className="navbar-toggler-icon"></span>
                    </button>

                    <div className="collapse navbar-collapse" id="main-nav">
                      <ul className="navbar-nav mr-auto">
                        <li className="nav-item active">
                          <a className="nav-link" href="#">Hub <span className="sr-only">(current)</span></a>
                        </li>
                        <li className="nav-item">
                          <a className="nav-link" href="#">Settings</a>
                        </li>
                        <li className="nav-item">
                          <a className="nav-link" href="#">Profile</a>
                        </li>
                        <li className="nav-item">
                          <a className="nav-link" href="#">Help</a>
                        </li>
                      </ul>
                      <div className="text-white">
                          {window.info.username}<a className="nav-logout" href="/logout"><i className="fa fa-sign-out-alt"></i></a>
                      </div>
                    </div>
                  </nav>
            </header>);
    }
}