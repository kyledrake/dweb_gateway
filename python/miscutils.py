"""
This is a place to put miscellaneous utilities, not specific to this project
"""
import json  # Note dont "from json import dumps" as clashes with overdefined dumps below
from datetime import datetime
import requests
from .Errors import TransportURLNotFound


def mergeoptions(a, b):
    """
    Deep merge options dictionaries
     - note this might not (yet) handle Arrays correctly but handles nested dictionaries

    :param a,b: Dictionaries
    :returns: Deep copied merge of the dictionaries
    """
    c = a.copy()
    for key in b:
        val = b[key]
        if isinstance(val, dict) and a.get(key, None):
            c[key] = mergeoptions(a[key], b[key])
        else:
            c[key] = b[key]
    return c

def dumps(obj):    #TODO-BACKPORT FROM GATEWAY TO DWEB - moved from Transport to miscutils
    """
    Convert arbitrary data into a JSON string that can be deterministically hashed or compared.
    Must be valid for loading with json.loads (unless change all calls to that).
    Exception: UnicodeDecodeError if data is binary

    :param obj:    Any
    :return: JSON string that can be deterministically hashed or compared
    """
    # ensure_ascii = False was set otherwise if try and read binary content, and embed as "data" in StructuredBlock then complains
    # if it cant convert it to UTF8. (This was an example for the Wrenchicon), but loads couldnt handle return anyway.
    # sort_keys = True so that dict always returned same way so can be hashed
    # separators = (,:) gets the most compact representation
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), default=json_default)


def json_default(obj): #TODO-BACKPORT FROM GATEWAY TO DWEB - moved from Transport to miscutils
    """
    Default JSON serialiser especially for handling datetime, can add handling for other special cases here

    :param obj: Anything json dumps can't serialize
    :return: string for extended types
    """
    if isinstance(obj, datetime):    # Using isinstance rather than hasattr because __getattr__ always returns true
    #if hasattr(obj,"isoformat"):  # Especially for datetime
        return obj.isoformat()
    try:
        return obj.dumps()          # See if the object has its own dumps
    except Exception as e:
        raise TypeError("Type %s not serializable (%s %s)" % (obj.__class__.__name__, e.__class__.__name__, e))



def httpget(url):
    # Returns the content - i.e. bytes
    #TODO-STREAMS future work to return a stream

    r = None  # So that if exception in get, r is still defined and can be tested for None
    try:
        r = requests.get(url)
        r.raise_for_status()
        if r.encoding:
            return r.text
        else:
            return r.content  # Should work for PDF or other binary types
        #TODO-STREAM support streams in future

    except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
        if r is not None and (r.status_code == 404):
            raise TransportURLNotFound(url=url)
        else:
            print(e.__class__.__name__, e)
            raise e
    except requests.exceptions.MissingSchema as e:
            print(e.__class__.__name__, e)
            # TODO-LOGGING: logger.error(e)
            raise e  # For now just raise it
