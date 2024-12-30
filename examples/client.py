# client.py
from forthright import forthright_client

url = 'http://127.0.0.1:8000'
frc = forthright_client(url)

sum, diff = frc.add_and_sub(8, 2)
print('%d %d' %(sum, diff)) # -> 10 6
