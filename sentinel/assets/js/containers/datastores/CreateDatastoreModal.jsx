import { connect } from 'react-redux'
import { CreateDatastore } from '../../components/datastores/CreateDatastore'
import { toggleCreateDatastore, createDatastore } from "../../actions/datastoreActions";

const mapStateToProps = (state) => {
    return {show: state.datastore.showCreate,
            createErrors:state.datastore.createErrors, hub:state.hub.active};
};

const mapDispatchToProps = (dispatch) => {
    return {
        toggleCreate: () => dispatch(toggleCreateDatastore()),
        registerLeaf: (hub, name, format, value, units=undefined) => dispatch(createDatastore(hub, name, format, value, units)),
    };
};

let CreateDatastoreModals = connect(mapStateToProps, mapDispatchToProps)(CreateDatastore);
export default CreateDatastoreModals;