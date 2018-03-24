import { connect } from 'react-redux'
import { RegisterLeaf } from '../../components/leaves/RegisterLeaf'
import { toggleRegisterLeaf, registerLeaf } from "../../actions/leafActions";

const mapStateToProps = (state) => {
    return {token: state.leaf.token, show: state.leaf.showRegister,
            registerErrors:state.leaf.registerErrors, hub:state.hub.active};
};

const mapDispatchToProps = (dispatch) => {
    return {
        toggleRegister: () => dispatch(toggleRegisterLeaf()),
        registerLeaf: (hub, uuid) => dispatch(registerLeaf(hub, uuid)),
    };
};

let RegisterLeafModal = connect(mapStateToProps, mapDispatchToProps)(RegisterLeaf);
export default RegisterLeafModal;