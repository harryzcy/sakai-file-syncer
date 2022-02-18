import os
from pathlib import Path
import yaml


config = {}


def init():
    """initialize configurations"""
    with open("config.yaml", 'r') as stream:
        global config
        config = yaml.safe_load(stream)


def get_username():
    username = os.getenv('SAKAI_USERNAME')
    if not username:
        print('SAKAI_USERNAME not specified')
        exit(1)
    return username


def get_password():
    password = os.getenv('SAKAI_PASSWORD')
    if not password:
        print('SAKAI_PASSWORD not specified')
        exit(1)
    return password


def get_current_term() -> str:
    return config['term']['current']


def get_site_enable(site: str) -> bool:
    try:
        return config['sites'][site]['enable']
    except:
        return False


def get_download_directory(site: str) -> str or None:
    try:
        return config['sites'][site]['download-directory']
    except:
        return config['sites']['default']['download-directory']


def get_skip_directories(site: str) -> list[str]:
    base = get_download_directory(site)

    dirs: list[str] = []
    try:
        dirs = config['sites'][site]['skip-directories']
    except:
        pass
    dirs = [str(Path(base, dir).expanduser()) if not dir.startswith(
        '/') else dir for dir in dirs]
    return dirs
