import json
import os

_CONFIG_FILE_PATH = os.path.expanduser('~/znodemonitor_config.json')

config = {
    "config_name": "default",
    "domain": "znodemonitor.com",
    "secret": "mash your keyboard into this or people will hack your site",
    "database_name": "znodemonitor",
    "database_kvargs": {
        "user": "znodemonitor",
        "password": "password",
        "host": "localhost",
        "port": 3306,
    },
    "node_args": {
        "host": "127.0.0.1",
        "port": 8888,
        "user": "xxx",
        "password": "xxx",
    },
    "show_dev_credit": True,
    "enforce_limit": True,
    "limit": 25,
    "enforce_invite": True,
    "invite": "your_invite_key",
    "mailgun_domain": "znodemonitor.com",
    "mailgun_key": "xxxxx"
}


if os.path.exists(_CONFIG_FILE_PATH):
    with open(_CONFIG_FILE_PATH, mode='r') as handle:
        config = json.load(handle)

config['zcoincli_binary'] = os.path.expanduser(config['zcoincli_binary'])
