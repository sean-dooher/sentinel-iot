import { connect } from 'react-redux'
import { LeafBase } from '../../components/leaves/LeafBase'
import { toggleDeleteLeaf } from "../../actions/leafActions";

const mapStateToProps = state => {
    return {};
};

const mapDispatchToProps = dispatch => {
    return {
        toggleDelete: (name) => dispatch(toggleDeleteLeaf(name)),
    };
};
let Leaf = connect(mapStateToProps, mapDispatchToProps)(LeafBase);
export default Leaf;