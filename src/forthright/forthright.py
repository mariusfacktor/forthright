
import pickle
from functools import partial, wraps
import os
import io
import inspect


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





def client_api_wrapper(url, caller_module_name, function_name, kwargs, *args):
    import requests

    headers = {'Content-Type': 'application/octet-stream'}

    args_serialized = serialize_arguments(function_name, kwargs, *args)
    response = requests.put(url, data=args_serialized, headers=headers)
    return_args = unserialize_arguments_client(caller_module_name, response.content)

    return return_args

def remote_call_decorator(func):

    @wraps(func)
    def wrapper(url, caller_module_name, func_name, *args, **kwargs):
        # pass kwargs as a dict
        result = client_api_wrapper(url, caller_module_name, func_name, kwargs, *args)
        return result

    return wrapper

@remote_call_decorator
def placeholder_function(url, caller_module_name, func_name, *args, **kwargs):
    pass





class base_forthright_client:
    def __init__(self, url, caller_module_name, class_ptr):
        self.url = os.path.join(url, 'forthright/')
        self.class_ptr = class_ptr
        self.caller_module_name = caller_module_name

    def import_functions(self, *func_names):
        for func_name in func_names:
            named_placeholder_function = partial(placeholder_function, self.url, self.caller_module_name, func_name)
            # Add function to class
            setattr(self.class_ptr, func_name, named_placeholder_function)


def forthright_client(url):

    # Get module name of caller
    frame = inspect.stack()[1]
    caller_module = inspect.getmodule(frame[0])
    caller_module_name = caller_module.__name__

    # Create new class (because we want to add functions to this class with setattr but not add them to a different forthright_client object)
    dynamic_class = type('forthright_client', (base_forthright_client,), {})
    # Instantiate this new class into an object and return the object
    forthright_client_obj = dynamic_class(url, caller_module_name, dynamic_class)
    return forthright_client_obj






class forthright_server:
    def __init__(self, app):
        self.app = app
        self.exported_functions_dict = {}

        # Get module name of caller
        frame = inspect.stack()[1]
        caller_module = inspect.getmodule(frame[0])
        caller_module_name = caller_module.__name__

        self.caller_module_name = caller_module_name

        self.initialize_api()


    def export_functions(self, *funcs):

        for func in funcs:
            self.exported_functions_dict[func.__name__] = func


    def initialize_api(self):
        from flask import request, Response

        @self.app.route('/forthright/', methods=['PUT'])
        def function_wrapper():

            data = request.get_data()
            unserialized = unserialize_arguments_server(self.caller_module_name, data)

            function_name = unserialized[0]
            input_kwargs = unserialized[1]
            input_args = unserialized[2:]

            try:
                outputs = self.exported_functions_dict[function_name](*input_args, **input_kwargs)
            except KeyError:
                raise KeyError('forthright: %s() not found. Use forthright_server.export_functions(%s)' %(function_name, function_name))


            outputs_serialized = serialize_arguments(outputs)

            return Response(outputs_serialized, content_type='application/octet-stream')


    
