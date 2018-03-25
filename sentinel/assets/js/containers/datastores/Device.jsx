import {connect} from 'react-redux'
import {DeviceBase} from '../../components/leaves/DeviceBase'
import {updateDevice} from "../../actions/leafActions";

const mapStateToProps = state => {
    return {
        hub: state.hub.active
    };
};

const mapDispatchToProps = dispatch => {
    return {
        updateDevice: (leaf, device, format, value) => dispatch(updateDevice(leaf, device, format, value))
    };
};

let Device = connect(mapStateToProps, mapDispatchToProps)(DeviceBase);
export default Device;

