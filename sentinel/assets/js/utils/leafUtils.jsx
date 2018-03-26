export function getNameFromUUID(uuid, leaves) {
    for(let leaf of leaves) {
        if(leaf.uuid === uuid){
            return leaf.name;
        }
    }

    if(uuid === 'datastore'){
        return 'datastore';
    }

    return '';
}