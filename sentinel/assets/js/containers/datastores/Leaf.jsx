import { connect } from 'react-redux'
import { LeafBase } from '../../components/leaves/LeafBase'
import { toggleDeleteLeaf } from "../../actions/leafActions";

const mapDispatchToProps = dispatch => {
//TODO: addChangeHub, refreshHub here
    return {
        toggleDelete: () => dispatch(toggleDeleteLeaf()),
    };
};
let Leaf = connect(null, mapDispatchToProps)(LeafBase);
export default Leaf;