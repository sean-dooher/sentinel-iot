import { connect } from 'react-redux'
import { Sidebar } from '../../components/navigation/Sidebar'
import { toggleCreateHub, changeHub } from "../../actions/navigationActions";
import {refreshHubs} from "../../actions/apiActions";

const mapStateToProps = (state) => {
    return {hubs: state.api.hubs, active: state.hub.active};
};

const mapDispatchToProps = dispatch => {
//TODO: addChangeHub, refreshHub here
    return {
        toggleCreate: () => dispatch(toggleCreateHub()),
        changeHub: (id) => dispatch(changeHub(id)),
        refreshHubs: () => dispatch(refreshHubs())
    };
};
let HubSideBar = connect(mapStateToProps, mapDispatchToProps)(Sidebar);
export default HubSideBar;