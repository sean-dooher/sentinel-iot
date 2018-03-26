export function getNameFromUUID(uuid, leaves) {
    let name = '';
    for(let leaf of leaves) {
        if(leaf.uuid === uuid){
            name = leaf.name;
            break;
        }
    }
    return name;
}