import { connect } from 'react-redux'
// import { CreateCondition } from '../../components/conditions/CreateCondition'
import { toggleCreateCondition, createCondition } from "../../actions/conditionActions";

const mapStateToProps = (state) => {
    return {show: state.condition.showCreate,
            createErrors:state.condition.createErrors, hub:state.hub.active};
};

const mapDispatchToProps = (dispatch) => {
    return {
        toggleCreate: () => dispatch(toggleCreateCondition()),
        createCondition: (hub, name, predicate, action) =>
                            dispatch(createCondition(hub, name, predicate, action)),
    };
};

let CreateConditionModal = connect(mapStateToProps, mapDispatchToProps)(CreateCondition);
export default CreateConditionModal;