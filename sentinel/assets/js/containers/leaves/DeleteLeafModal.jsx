import { connect } from 'react-redux'
import { DeleteLeaf } from '../../components/leaves/DeleteLeaf'
import { toggleDeleteLeaf, deleteLeaf } from "../../actions/leafActions";

const mapStateToProps = (state) => {
    return {deleteErrors: state.leaf.deleteErrors,
        show: state.leaf.showDelete, hub: state.hub.active};
};

const mapDispatchToProps = (dispatch) => {
//TODO: addChangeHub, refreshHub here
    return {
        toggleDelete: () => dispatch(toggleDeleteLeaf()),
        deleteLeaf: (hub, uuid) => dispatch(deleteLeaf(hub, uuid)),
    };
};

let DeleteLeafModal = connect(mapStateToProps, mapDispatchToProps)(DeleteLeaf);
export default DeleteLeafModal;