import { connect } from 'react-redux'
import { CreateHub } from '../../components/navigation/CreateHub'
import { toggleCreateHub, createHub } from "../../actions/navigationActions";

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

let CreateHubModal = connect(mapStateToProps, mapDispatchToProps)(CreateHub);
export default CreateHubModal;