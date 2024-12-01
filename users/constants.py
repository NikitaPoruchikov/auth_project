import random


def generate_username(username=None):
    if username:
        return username
    return f"user_{random.randint(1000, 9999)}"


AUTH_CODE_LENGTH = 4
INVAITE_CODE_LENGTH = 6
