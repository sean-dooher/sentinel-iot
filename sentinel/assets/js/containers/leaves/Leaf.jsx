import { connect } from 'react-redux'
import { LeafBase } from '../../components/leaves/LeafBase'
import { toggleDeleteLeaf } from "../../actions/leafActions";

const mapStateToProps = (state) => {};

const mapDispatchToProps = dispatch => {
//TODO: addChangeHub, refreshHub here
    return {
        toggleDelete: () => dispatch(toggleDeleteLeaf()),
    };
};
let Leaf = connect(mapStateToProps, mapDispatchToProps)(LeafBase);
export default Leaf;