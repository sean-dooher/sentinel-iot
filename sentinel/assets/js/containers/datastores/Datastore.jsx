import { connect } from 'react-redux'
import { DatastoreBase } from '../../components/datastores/DatastoreBase'
import { toggleDeleteDatastore, updateDatastore } from "../../actions/datastoreActions";

const mapStateToProps = state => {
    return {
        hub: state.hub.active,
    };
};

const mapDispatchToProps = dispatch => {
    return {
        toggleDelete: (name) => dispatch(toggleDeleteDatastore(name)),
        updateDatastore: (hub, name, format, value) => dispatch(updateDatastore(hub, name, format, value))
    };
};
let Datastore = connect(mapStateToProps, mapDispatchToProps)(DatastoreBase);
export default Datastore;