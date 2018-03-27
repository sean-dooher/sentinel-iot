import React from "react";
import PropTypes from "prop-types";
import {Input} from "reactstrap";
import {Value} from "./Value";
import {getDevice, getDevices, getLeaf, getLeaves} from "../../utils/leafUtils";

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

    handleLeafChange(event) {
        this.setState({selected_leaf: event.target.value});
    }

    handleDeviceChange(event) {
        if(event.target)
            this.setState({selected_device: event.target.value});
        else
            this.setState({selected_device: event});
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
        // console.log(this.state);
        if(this.state.selected_leaf !== 'literal') {
            if (this.state.selected_device !== prevState.selected_device && this.props.formatChanged) {
                let device = getDevice(this.state.selected_leaf, this.state.selected_device, this.props.leaves);
                this.props.formatChanged(device.format);
            }
            if (this.state.selected_leaf !== prevState.selected_leaf) {
                if(this.state.selected_leaf === 'datastore') {
                    this.setState({selected_device: this.props.datastores[0].name})
                } else {
                    this.setState({selected_device: getLeaf(this.state.selected_leaf, this.props.leaves).devices[0].name})
                }
            }
        } else if (this.state.selected_leaf !== prevState.selected_leaf) {
            this.setState({selected_device: "true"})
        }
    }

    render(){
       return (<div className="row">
           <div className="col-md-6">
               <Input type="select" name="leaf" className="form-control custom-select"
                              value={this.state.selected_leaf} onChange={this.handleLeafChange}>
                   { this.props.literal ? <option value="literal">Literal</option> : null}
                   { this.props.datastores && this.props.datastores.length > 0 ? <option value="datastore">Datastore</option> : null}
                   {getLeaves(this.props.leaves, this.props.format, this.props.out)
                       .map((leaf, key) => <option key={key} value={leaf.uuid}>{leaf.name}</option>)}
               </Input>
           </div>
           <div className="col-md-6">
               {this.state.selected_leaf !== 'literal' ?
               <Input type="select" name="device" className="form-control custom-select" onClick={this.handleDeviceChange}>
                   {getDevices(this.state.selected_leaf, this.props.leaves,
                       this.props.datastores, this.props.format, this.props.out)
                       .map((device, key) => <option key={key} value={device.name}>{device.name}</option>)}
               </Input>
                   : <Value format={this.props.format} onChange={this.handleDeviceChange}/>}
           </div>
       </div>);
    }
}

LeafSelector.propTypes = {
    leaves: PropTypes.array,
    format: PropTypes.string,
    literal: PropTypes.bool,
    formatChanged: PropTypes.func,
    out: PropTypes.bool,
    datastores: PropTypes.array
};