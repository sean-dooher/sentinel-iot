import React from "react";
import {FormGroup, Label, Input} from "reactstrap";
import PropTypes from "prop-types";
import {Value} from "./value";

export class LeafSelector extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            selected_leaf: '',
            selected_device: '',
        };
        this.handleDeviceChange = this.handleDeviceChange.bind(this);
        this.handleLeafChange = this.handleLeafChange.bind(this);
        this.componentDidUpdate = this.componentDidUpdate.bind(this);
    }

    getDevice(uuid, device) {
        if(uuid === 'datastore') {
            for (let d of this.props.datastores) {
                if (d.name === device) {
                    return d;
                }
            }
        }

        let leaf = this.getLeaf(uuid);
        for(let d of leaf.devices) {
            if(d.name === device) {
                return d;
            }
        }
    }

    getLeaf(uuid) {
        for(let i = 0; i < this.props.leaves.length; i++) {
            if(this.props.leaves[i].uuid === this.state.selected_leaf) {
                return this.props.leaves[i];
            }
        }
    }

    getLeaves() {
        let isOut = device => (!this.props.output || device.mode === 'OUT');
        let formatMatches = device => device.format === this.props.format;
        if(this.props.format) {
            return this.props.leaves.filter(leaf => leaf.devices.filter(device => formatMatches(device) && isOut(device)).length > 0);
        } else {
            return this.props.leaves.filter(leaf => leaf.devices.filter(isOut).length > 0);
        }
    }

    getDevices() {
        if(this.state.selected_leaf === 'datastore') {
            return this.props.datastores.filter(device => !this.props.format || device.format === this.props.format)
        }

        let leaf = this.getLeaf(this.state.selected_leaf);
        if(leaf) {
            return leaf.devices.filter(d =>
                (!this.props.format || d.format === this.props.format) && (!this.props.output || d.mode === 'OUT'));
        }
        return [];
    }

    handleLeafChange(event) {
        this.setState({selected_leaf: event.target.value});
    }

    handleDeviceChange(event) {
        this.setState({selected_device: event.target.value});
    }

    componentDidMount() {
        if(this.props.literal) {
            this.setState({selected_leaf: 'literal'});
        } else if(this.props.datastores && this.props.datastores.length > 0) {
            return this.setState({selected_leaf: 'datastore'})
        }
        else if (this.props.leaves.length > 0) {
            this.setState({selected_leaf: this.props.leaves[0].uuid})
        }
    }

    componentDidUpdate(prevProps, prevState) {
        if(this.state.selected_leaf !== 'literal') {
            if (this.state.selected_device !== prevState.selected_device && this.props.formatChanged) {
                let device = this.getDevice(this.state.selected_leaf, this.state.selected_device);
                this.props.formatChanged(device.format);
            }
            if (this.state.selected_leaf !== prevState.selected_leaf) {
                if(this.state.selected_leaf === 'datastore') {
                    this.setState({selected_device: this.props.datastores[0].name})
                } else {
                    this.setState({selected_device: this.getLeaf(this.state.selected_leaf).devices[0].name})
                }
            }
        } else if (this.state.selected_leaf !== prevState.selected_leaf) {
            this.setState({selected_device: "true"})
        }
    }

    render(){
       return (<div className="row">
           <div className="col-md-6">
               Leaf:
               <select name="leaf" className="form-control custom-select form-control-sm"
                              value={this.state.selected_leaf} onChange={this.handleLeafChange}>
                   { this.props.literal ? <option value="literal">Literal</option> : null}
                   { this.props.datastores && this.props.datastores.length > 0 ? <option value="datastore">Datastore</option> : null}
                   {this.getLeaves().map((leaf, key) => <option key={key} value={leaf.uuid}>{leaf.name}</option>)}
               </select>
           </div>
           <div className="col-md-6">
               {this.state.selected_leaf === 'literal' ? "Literal: " : "Device: "}
               {this.state.selected_leaf !== 'literal' ?
               <select name="device" className="form-control custom-select form-control-sm" onClick={this.handleDeviceChange}>
                   {this.getDevices().map((device, key) => <option key={key} value={device.name}>{device.name}</option>)}
               </select> : <Value small format={this.props.format} onChange={this.handleDeviceChange}/>}
           </div>
       </div>);
    }
}

LeafSelector.propTypes = {
    leaves: PropTypes.array,
    format: PropTypes.string,
    literal: PropTypes.bool,
    formatChanged: PropTypes.func,
    output: PropTypes.bool,
    datastores: PropTypes.array
};