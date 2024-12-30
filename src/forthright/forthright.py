
import pickle
from functools import partial, wraps
import os
import io
import inspect
import json
import base64


# https://stackoverflow.com/questions/15721363/preserve-python-tuples-with-json
class MyJsonEncoder(json.JSONEncoder):
    def encode(self, obj):
        def specify_type(item):
            if isinstance(item, tuple):
                return {'__tuple__': True, 'items': [specify_type(e) for e in item]}
            elif isinstance(item, set):
                return {'__set__': True, 'items': [specify_type(e) for e in item]}
            elif isinstance(item, bytes):
                return {'__bytes__': True, 'items': base64.b64encode(item).decode('utf8')}
            elif isinstance(item, list):
                return [specify_type(e) for e in item]
            elif isinstance(item, dict):
                return {key: specify_type(value) for key, value in item.items()}
            else:
                return item

        return super(MyJsonEncoder, self).encode(specify_type(obj))


def specify_type_hook(obj):
    if '__tuple__' in obj:
        return tuple(obj['items'])
    elif '__set__' in obj:
        return set(obj['items'])
    elif '__bytes__' in obj:
        return base64.b64decode(obj['items'])
    else:
        return obj


# https://stackoverflow.com/questions/50465106/attributeerror-when-reading-a-pickle-file
class MyCustomUnpickler(pickle.Unpickler):

    def __init__(self, bytes_stream, caller_module_name):
        self.caller_module_name = caller_module_name
        pickle.Unpickler.__init__(self, bytes_stream)

    def find_class(self, module, name):

        # If there's a custom object in the bytes_stream, 
        # change the module name to the name of the module that instantiated this forthright_client object
        # because that's where the class should be defined
        module_name = self.caller_module_name

        try:
            # try same module as sender (works for numpy)
            return super().find_class(module, name)
        except:
            # try module in which forthright was instantiated (works for custom class)
            return super().find_class(module_name, name)



def serialize_arguments(*args):

    args_tuple = tuple(args)
    args_serialized = pickle.dumps(args_tuple)

    return args_serialized

def unserialize_arguments_client(caller_module_name, args_serialized):

    bytes_stream = io.BytesIO(args_serialized)

    unpickler = MyCustomUnpickler(bytes_stream, caller_module_name)
    args_tuple = unpickler.load()

    if len(args_tuple) == 1:
        args_tuple = args_tuple[0]

    return args_tuple


def unserialize_arguments_server(caller_module_name, args_serialized):

    bytes_stream = io.BytesIO(args_serialized)

    unpickler = MyCustomUnpickler(bytes_stream, caller_module_name)
    args_tuple = unpickler.load()

    return args_tuple






def client_api_wrapper(url, safe_mode, caller_module_name, function_name, kwargs, *args):
    import requests

    json_encoder = MyJsonEncoder()


    if safe_mode:
        headers = {'Content-Type': 'application/json'}
        data = [function_name, kwargs, *args]
        args_processed = json_encoder.encode(data)

    else:
        headers = {'Content-Type': 'application/octet-stream'}
        args_processed = serialize_arguments(function_name, kwargs, *args)


    response = requests.put(url, data=args_processed, headers=headers)

    if safe_mode:
        return_values = json.loads(response.content, object_hook=specify_type_hook)
    else:
        return_values = unserialize_arguments_client(caller_module_name, response.content)

    return return_values


class forthright_client:
    def __init__(self, url, safe_mode=False):
        self.url = os.path.join(url, 'forthright/')
        self.safe_mode = safe_mode

        # Get module name of caller
        frame = inspect.stack()[1]
        caller_module = inspect.getmodule(frame[0])
        caller_module_name = caller_module.__name__

        self.caller_module_name = caller_module_name

    # https://medium.com/@taraszhere/coding-remote-procedure-call-rpc-with-python-3b14a7d00ac8
    # Call arbitrary function name
    def __getattr__(self, __name: str):

        def execute(*args, **kwargs):
            result = client_api_wrapper(self.url, self.safe_mode, self.caller_module_name, __name, kwargs, *args)
            return result

        return execute





class forthright_server:
    def __init__(self, app, safe_mode=False):
        self.app = app
        self.exported_functions_dict = {}
        self.safe_mode = safe_mode

        self.json_encoder = MyJsonEncoder()

        # Get module name of caller
        frame = inspect.stack()[1]
        caller_module = inspect.getmodule(frame[0])
        caller_module_name = caller_module.__name__

        self.caller_module_name = caller_module_name

        self.initialize_api()


    def register_functions(self, *funcs):

        for func in funcs:
            self.exported_functions_dict[func.__name__] = func


    def initialize_api(self):
        from flask import request, Response

        @self.app.route('/forthright/', methods=['PUT'])
        def function_wrapper():

            data = request.get_data()

            if self.safe_mode:
                unserialized = json.loads(data, object_hook=specify_type_hook)
            else:
                unserialized = unserialize_arguments_server(self.caller_module_name, data)

            function_name = unserialized[0]
            input_kwargs = unserialized[1]
            input_args = unserialized[2:]

            try:
                outputs = self.exported_functions_dict[function_name](*input_args, **input_kwargs)
            except KeyError:
                raise KeyError('forthright: %s() not found. Use forthright_server.register_functions(%s)' %(function_name, function_name))


            if self.safe_mode:
                outputs_serialized = self.json_encoder.encode(outputs)
                content_type = 'application/json'

            else:
                outputs_serialized = serialize_arguments(outputs)
                content_type = 'application/octet-stream'

            return Response(outputs_serialized, content_type=content_type)




    
