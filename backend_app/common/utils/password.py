import random
import string


def get_random_alphanumeric_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join((random.choice(letters_and_digits) for i in range(length)))


def get_random_int_string(length):
    result_str = ''.join((str(random.randint(0, 9)) for i in range(length)))
    return result_str
