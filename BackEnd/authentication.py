import time, os, configparser, jwt

config_file = None
if (os.path.isfile('../config/dev.cfg')):
    config_file = '../config/dev.cfg'
else:
    config_file = '../config/settings.cfg'
    
# read the data from the config file
config = configparser.ConfigParser()
config.read(config_file)

# grab the secret and algorithm
JWT_secret = config['JWT']['secret']
JWT_algorithm = config['JWT']['algorithm']

def token_response(token: str):
    return { 'token' : token }

def sign_jwt(username: str, administrator: int):
    """Creates a token with a specified payload (JWT)

    Args:
        username (str): The username of the user
        administrator (int): Whether that user is an administrator (1) or not (0)

    Returns:
        dict: Contains a key called token, and the value of the token
    """
    payload = {
        'username': username,
        'administrator': administrator,
        'expire': (time.time() - (60 * 60))
    }
    token = jwt.encode(payload, JWT_secret, algorithm=JWT_algorithm)
    return token_response(token)

def decode_jwt(token: str):
    """Decodes the JWT token and returns the decoded information if the
    token is not expired.

    Args:
        token (str): The token to decode.

    Returns:
        dict or None: If the token is valid, it returns the decoded token. If the token is expired,
        an empty dictionary is returned. If the token is invalid, None is returned.
    """
    try:
        decoded_token = jwt.decode(token, JWT_secret, JWT_algorithm)
        return decoded_token if decoded_token['expire'] >= time.time() else {} # expired token
    except:
        return None