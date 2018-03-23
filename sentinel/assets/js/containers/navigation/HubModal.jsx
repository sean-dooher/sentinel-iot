import { connect } from 'react-redux'
import { CreateHub } from '../../components/navigation/CreateHub'
import { toggleCreateHub, createHub } from "../../actions/navigationActions";
import {refreshHubs} from "../../actions/apiActions";

const mapStateToProps = (state) => {
    return {createErrors: state.hub.createErrors, show: state.hub.showCreate};
};

const mapDispatchToProps = (dispatch) => {
//TODO: addChangeHub, refreshHub here
    return {
        toggleCreate: () => dispatch(toggleCreateHub()),
        createHub: (name) => dispatch(createHub(name)),
    };
};

let HubModal = connect(mapStateToProps, mapDispatchToProps)(CreateHub);
export default HubModal;