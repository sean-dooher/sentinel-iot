import { connect } from 'react-redux'
import { toggleDeleteCondition, deleteCondition } from "../../actions/conditionActions";
import {DeleteCondition} from "../../components/conditions/DeleteCondition";

const mapStateToProps = (state) => {
    return {deleteErrors: state.condition.deleteErrors, name: state.condition.deleteName,
        show: state.condition.showDelete, hub: state.hub.active};
};

const mapDispatchToProps = (dispatch) => {
    return {
        toggleDelete: () => dispatch(toggleDeleteCondition()),
        deleteCondition: (hub, name) => dispatch(deleteCondition(hub, name)),
    };
};

let DeleteConditionModal = connect(mapStateToProps, mapDispatchToProps)(DeleteCondition);
export default DeleteConditionModal;