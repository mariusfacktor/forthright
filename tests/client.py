

# relative import
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from src.forthright.forthright import forthright_client

# from forthright import forthright_client

url = 'http://127.0.0.1:8000'
b_safe_mode = False

frc = forthright_client(url, safe_mode=b_safe_mode)
frc.import_functions('calculate_values', 'concat_words', 'increment_age', 'optional_input', 'send_back_same')


# test1 -- mixed type input arguments and multiple outputs
val1, val2 = frc.calculate_values('add', 2, 3, 4)
print('%d %d' %(val1, val2)) # -> 5 7


# test2 -- kwargs input with single output
concat_output = frc.concat_words(word1='aaa', word2='bbb', word3='ccc')
print(concat_output) # -> aaabbbccc


if not b_safe_mode:
    # test3 -- input and output are a custom object
    class Person:
        def __init__(self, name, age):
            self.name = name
            self.age = age

    p1 = Person('john', 38)
    older_person = frc.increment_age(p1)
    print(older_person.age) # -> 39


# test4 -- zero input arguments
default_val = frc.optional_input()
print(default_val) # -> 42


# test5 -- argument is an arbitrary type
output = frc.send_back_same(['this', 'is', 'a', 'list'])
print(output) # -> ['this', 'is', 'a', 'list']
output = frc.send_back_same(b'Hello World')
print(output) # -> b'Hello World'
output = frc.send_back_same({5, 5, 6})
print(output) # -> {5, 6}
output = frc.send_back_same((1, 2, (3, 4), [5, 6], {7}, ()))
print(output) # -> (1, 2, (3, 4), [5, 6], {7}, ())






