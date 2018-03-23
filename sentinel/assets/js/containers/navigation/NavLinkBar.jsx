import { connect } from 'react-redux'
import { HeaderBar } from '../../components/navigation/HeaderBar'

const mapStateToProps = (state) => {
    return {links: state.navbar.links, active: state.navbar.active};
};

const mapDispatchToProps = (state) => {
    return {};
};

let NavLinkBar = connect(mapStateToProps, mapDispatchToProps)(HeaderBar);
export default NavLinkBar;