import { connect } from 'react-redux'
import { Sidebar } from '../../components/navigation/Sidebar'
import { toggleCreateHub } from "../../actions/navigationActions";

const mapStateToProps = (state) => {
    return {hubs: state.api.hubs, active: state.hub.active};
};

const mapDispatchToProps = dispatch => {
//TODO: addChangeHub, refreshHub here
    return {
        toggleCreate: () => dispatch(toggleCreateHub())
    };
};
let HubSideBar = connect(mapStateToProps, mapDispatchToProps)(Sidebar);
export default HubSideBar;