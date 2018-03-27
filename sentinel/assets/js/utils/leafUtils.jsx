const fakeLeaf = {
    name: 'Fake',
    devices: {},
    is_connected: false,
    model: "1.0.1",
    api_version: "0.1.0"
};

const fakeDevice = {
    name: "Left Couch Lamp",
    format: "bool",
    value: false,
    mode: "OUT"
};

export function getNameFromUUID(uuid, leaves) {
    for (let leaf of leaves) {
        if (leaf.uuid === uuid) {
            return leaf.name;
        }
    }

    if (uuid === 'datastore') {
        return 'datastore';
    }

    return '';
}

export function getLeaves(leaves, format = '', out = false) {
    let isOut = device => (!out || device.mode === 'OUT');
    let formatMatches = device => format === '' || device.format === format;
    if (format) {
        return leaves.filter(leaf => leaf.devices.filter(device => formatMatches(device) && isOut(device)).length > 0);
    } else {
        return leaves.filter(leaf => leaf.devices.filter(isOut).length > 0);
    }
}

export function getDevices(uuid, leaves, datastores, format = '', out = false) {
    if (uuid === 'datastore') {
        return datastores.filter(device => !format || device.format === format)
    }

    let leaf = getLeaf(uuid, leaves);
    if (leaf) {
        return leaf.devices.filter(d => (!format || d.format === format) && (!out || d.mode === 'OUT'));
    }
    return [];
}

export function getLeaf(uuid, leaves, datastores) {
    if (uuid !== 'datastore') {
        let candidates = leaves.filter(leaf => leaf.uuid === uuid);
        if (candidates.length > 0)
            return candidates[0];
    }
    else
        return datastores;
}

export function getDevice(uuid, name, leaves, datastores) {
    let leaf = getLeaf(uuid, leaves, datastores);
    if(leaf) {
        let candidates;

        if (uuid !== 'datastore')
            candidates = leaf.devices.filter(device => device.name === name);
        else
            candidates = datastores.filter(ds => ds.name === name);

        if (candidates.length > 0)
            return candidates[0];
    }
}