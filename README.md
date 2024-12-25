
# forthright

forthright is a wrapper around Flask that allows you to (seemingly) directly call functions on the server from the client. It saves you the hassle of needing to pack your arguments into a json and unpack them on the server. 


## A simple example
```
# backend.py
from forthright import forthright_server
from flask import Flask

app = Flask(__name__)
frs = forthright_server(app)

def add_and_sub(numA, numB):
    return numA + numB, numA - numB

frs.export_functions(add_and_sub)

if __name__ == '__main__':
    app.run(port=8000)
```

```
# client.py
from forthright import forthright_client

url = 'http://127.0.0.1:8000'
frc = forthright_client(url)
frc.import_functions('add_and_sub')

sum, diff = frc.add_and_sub(8, 2)
print('%d %d' %(sum, diff)) # -> 10 6
```

## Installation

`pip install -i https://test.pypi.org/simple/ forthright`

## Limitations

You can only pass arguments by value, not by reference. For example, if an argument is a list, the server function will receive a copy of that list. 

If an argument is a custom object, the class definition must be present in both the client code and the server code. 

Warning: This code deserializes pickled data on the server which is unsafe. forthright is only intended for rapid prototyping on a private network. 

