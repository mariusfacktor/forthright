
# forthright

forthright is a Remote Procedure Call (RPC) package that uses Flask to allow you to call server functions from the client. It saves you the hassle of needing to pack your arguments into a json and unpack them on the server. 


## A simple example
```
# backend.py
from forthright import forthright_server
from flask import Flask

app = Flask(__name__)
frs = forthright_server(app)

def add_and_sub(numA, numB):
    return numA + numB, numA - numB

frs.register_functions(add_and_sub)

if __name__ == '__main__':
    app.run(port=8000)
```

```
# client.py
from forthright import forthright_client

url = 'http://127.0.0.1:8000'
frc = forthright_client(url)

sum, diff = frc.add_and_sub(8, 2)
print('%d %d' %(sum, diff)) # -> 10 6
```

## Installation

`pip install forthright`

## Limitations

You can only pass arguments by value, not by reference. For example, if an argument is a list, the server function will receive a copy of that list. 

If an argument is a custom object, the class definition must be present in both the client code and the server code. 

Warning: By default, this code deserializes pickled data on the server which is unsafe. There is an optional Safe Mode to instead send data with json, but this will prevent you from sending custom objects. To turn on Safe Mode, set `safe_mode=True` when instantiating both forthright_server and forthright_client:

`frs = forthright_server(app, safe_mode=True)`

`frc = forthright_client(url, safe_mode=True)`


