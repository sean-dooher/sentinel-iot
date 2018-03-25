import { connect } from 'react-redux'
import { CreateDatastore } from '../../components/datastores/CreateDatastore'
import { toggleRegisterLeaf, registerLeaf } from "../../actions/datastoreActions";

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

let CreateDatastoreModals = connect(mapStateToProps, mapDispatchToProps)(CreateDatastore);
export default CreateDatastoreModals;