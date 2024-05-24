import time, os, configparser, jwt

config_file = None
if (os.path.isfile('dev.cfg')):
    config_file = 'dev.cfg'
else:
    config_file = 'settings.cfg'
    
# read the data from the config file
config = configparser.ConfigParser()
config.read(config_file)

# grab the secret and algorithm
JWT_secret = config['JWT']['secret']
JWT_algorithm = config['JWT']['algorithm']

def token_response(token: str):
    return { 'token' : token }

def sign_jwt(username: str, administrator: int):
    payload = {
        'username': username,
        'administrator': administrator
    }
    pass

def decode_jwt(token: str):
    pass