import { connect } from 'react-redux'
import { LeavesSectionBase } from '../../components/leaves/LeavesSectionBase';
import { toggleRegisterLeaf } from "../../actions/leafActions";

const mapStateToProps = (state) => {
    return {leaves: state.api.leaves};
};

const mapDispatchToProps = dispatch => {
    return {
        toggleRegister: () => dispatch(toggleRegisterLeaf())
    }
};
let LeavesSection = connect(mapStateToProps, mapDispatchToProps)(LeavesSectionBase);
export default LeavesSection;