import { connect } from 'react-redux'
import { toggleDeleteDatastore, deleteDatastore } from "../../actions/datastoreActions";
import {DeleteDatastore} from "../../components/datastores/DeleteDatastore";

const mapStateToProps = (state) => {
    return {deleteErrors: state.datastore.deleteErrors, name: state.datastore.deleteName,
        show: state.datastore.showDelete, hub: state.hub.active};
};

const mapDispatchToProps = (dispatch) => {
    return {
        toggleDelete: () => dispatch(toggleDeleteDatastore()),
        deleteDatastore: (hub, name) => dispatch(deleteDatastore(hub, name)),
    };
};

let DeleteDatastoreModal = connect(mapStateToProps, mapDispatchToProps)(DeleteDatastore);
export default DeleteDatastoreModal;