'''
Author: Sasha
Date: 2024-06-24 12:48:09
LastEditors: Sasha
LastEditTime: 2024-06-27 14:11:56
Description: 
FilePath: /v2/core/logger.py
'''

from loguru import logger
from core.config import config
logger.configure(**config.LOG_CONFIG)
__all__ = ["logger"]