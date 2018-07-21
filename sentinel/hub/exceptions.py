class SentinelError(Exception):
    pass


class InvalidDevice(SentinelError):
    UNKNOWN = 'Unknown Device'
    FORMAT = 'Invalid Format'
    MODE = 'Invalid Mode'

    def __init__(self, leaf, device, reason):
        super().__init__(f'{reason}: {leaf.uuid}:{device.name}')
        self.leaf = leaf
        self.device = device
        self.reason = reason

    def get_error_message(self):
        return {
            'type': 'INVALID_DEVICE',
            'leaf': self.leaf.uuid,
            'device': self.device.name,
            'reason': self.reason
        }


class InvalidPredicate(SentinelError):
    def __init__(self, predicate, condition):
        super().__init__(f"Invalid predicate for {condition}: {predicate}")
        self.predicate = predicate
        self.condition = condition

    def get_error_message(self):
        return {
            'type': 'INVALID_PREDICATE',
            'predicate': self.predicate,
            'condition': self.condition
        }


class InvalidLeaf(SentinelError):
    def __init__(self, uuid):
        super().__init__(f"Unknown Leaf: {uuid}")
        self.uuid = uuid

    def get_error_message(self):
        return {
            'type': 'INVALID_LEAF',
            'uuid': self.uuid,
            'reason': 'Unknown Leaf'
        }


class PermissionDenied(SentinelError):
    def __init__(self, requester, request, **kwargs):
        super().__init__(f"Permission denied: {request} to {requester}")
        self.request = request
        self.additional = kwargs

    def get_error_message(self):
        message = {'type': 'PERMISSION_DENIED',
                   'request': self.request}
        for kwarg in self.additional:
            message[kwarg] = self.additional[kwarg]
        return message