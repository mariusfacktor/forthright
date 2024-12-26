

# relative import
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from src.forthright.forthright import forthright_server

# from forthright import forthright_server

from flask import Flask

app = Flask(__name__)
frs = forthright_server(app, safe_mode=False)



# test1 -- mixed type input arguments and multiple outputs
def calculate_values(operation, x, y, z):
    if operation == 'add':
        result1 = x + y
        result2 = y + z
    elif operation == 'multiply':
        result1 = x * y
        result2 = y * z
    else:
        result1 = x
        result2 = y

    return result1, result2


# test2 -- kwargs input with single output
def concat_words(word1, word2, word3):
    combine = word1 + word2 + word3
    return combine


# test3 -- input and output are a custom object
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

def increment_age(person):
    person.age += 1
    return person


# test4 -- zero input arguments
def optional_input(optional_arg=42):
    return optional_arg


# test5 -- argument is an arbitrary type
def input_list(arg):
    return arg



frs.export_functions(calculate_values, concat_words, increment_age, optional_input, input_list)


if __name__ == '__main__':
    app.run(port=8000)


