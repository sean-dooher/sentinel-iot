import { connect } from 'react-redux'
import { DeleteHub } from '../../components/navigation/DeleteHub'
import { toggleDeleteHub, deleteHub } from "../../actions/navigationActions";

const mapStateToProps = (state) => {
    return {deleteErrors: state.hub.deleteErrors, show: state.hub.showDelete, id: state.hub.active};
};

const mapDispatchToProps = (dispatch) => {
//TODO: addChangeHub, refreshHub here
    return {
        toggleDelete: () => dispatch(toggleDeleteHub()),
        deleteHub: (id) => dispatch(deleteHub(id)),
    };
};

let DeleteHubModal = connect(mapStateToProps, mapDispatchToProps)(DeleteHub);
export default DeleteHubModal;