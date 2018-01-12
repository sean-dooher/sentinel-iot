from corsheaders.signals import check_request_enabled
import re


def cors_allow_api_to_everyone(sender, request, **kwargs):
    return re.match(r"/hub/([^/]+)/(leaves|conditions|datastores)(/.+){0,1}", request.path)


check_request_enabled.connect(cors_allow_api_to_everyone)