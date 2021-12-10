import os

#Conexión Google Cloud.
#os.system('export $(cat .env.example | grep -v ^# | xargs)')


driver = os.getenv('driver')
user = os.getenv('user')
password = os.getenv('password')
host = os.getenv('host')
db = os.getenv('db')
table = os.getenv('table')
