import { connect } from 'react-redux'
import { ConditionSectionBase } from '../../components/conditions/ConditionSectionBase';
import {toggleCreateCondition, toggleDeleteCondition} from "../../actions/conditionActions";

const mapStateToProps = (state) => {
    return {conditions: state.api.conditions, leaves: state.api.leaves};
};

const mapDispatchToProps = dispatch => {
    return {
        toggleCreate: () => dispatch(toggleCreateCondition()),
        toggleDelete: (name) => dispatch(toggleDeleteCondition(name))
    }
};

let ConditionsSection = connect(mapStateToProps, mapDispatchToProps)(ConditionSectionBase);
export default ConditionsSection;