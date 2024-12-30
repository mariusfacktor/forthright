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
