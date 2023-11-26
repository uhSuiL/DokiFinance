import logging
import os
import json
import sqlite3

from entity.service import Register
from entity.data import DataBaseHandler


def get_config(config_dir: str) -> dict:
    """Read all config files in specified dir as a config

        - In this project, config is just a dict, not sth else
    """
    config = dict()
    for file in os.listdir(config_dir):
        f_name = file.rstrip(".json")
        with open(f"{config_dir}/{file}", mode='r', encoding='utf-8') as f:
            sub_config = json.load(f)
            config[f_name] = sub_config
    return config


class Log:

    logger = logging.getLogger()
    handler_register = Register()

    @classmethod
    def get_logger(cls, log_config: dict) -> logging.Logger:
        try:
            if not os.path.exists(log_config['logdir']):
                os.mkdir(log_config['logdir'])

            cls.logger.setLevel("INFO")  # the level of logger is compulsively INFO

            for handler_config in log_config['handler']:
                handler_config['output'] = f"{log_config['logdir']}/{handler_config['output']}"
                handler = cls.handler_register[handler_config['type']](handler_config)
                cls.logger.addHandler(handler)

            cls.logger.info("Logger Initialized")
            return cls.logger
        except Exception as e:
            cls.logger.warning("Logger Failed to initialize")
            cls.logger.error(e, exc_info=True)
            raise e

    @staticmethod
    @handler_register("sqlite")
    def sqlite_handler(handler_config: dict) -> logging.Handler:
        _conn = sqlite3.connect(handler_config['output'])
        _handler = DataBaseHandler(_conn)
        _formatter = logging.Formatter(handler_config['format'])

        _handler.setLevel(handler_config['level'])
        _handler.setFormatter(_formatter)
        return _handler

    @staticmethod
    @handler_register("console")
    def console_handler(handler_config: dict) -> logging.Handler:
        _handler = logging.StreamHandler()
        _formatter = logging.Formatter(handler_config['format'])

        _handler.setLevel(handler_config['level'])
        _handler.setFormatter(_formatter)
        return _handler
