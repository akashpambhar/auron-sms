import os


def get_list_from_env(key, delimiter=","):
    value = os.getenv(key)
    if value:
        return value.split(delimiter)
    else:
        return []
