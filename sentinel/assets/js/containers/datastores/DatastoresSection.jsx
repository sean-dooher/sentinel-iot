import { connect } from 'react-redux'
import { DatastoreSectionBase } from '../../components/datastores/DatastoreSectionBase';
import { toggleCreateDatastore } from "../../actions/datastoreActions";

const mapStateToProps = (state) => {
    return {datastores: state.api.datastores};
};

const mapDispatchToProps = dispatch => {
    return {
        toggleCreate: () => dispatch(toggleCreateDatastore())
    }
};
let DatastoresSection = connect(mapStateToProps, mapDispatchToProps)(DatastoreSectionBase);
export default DatastoresSection;