'''
Author: Sasha
Date: 2023-06-16 09:20:06
LastEditors: Sasha
LastEditTime: 2024-06-27 11:53:12
Description: 
FilePath: /v2/core/config.py
'''
import os
import sys
import socket
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REDIS_PORT = os.getenv("REDIS_PORT",6666)

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't need to be reachable
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
    except Exception:
        ip_address = "127.0.0.1"
    finally:
        s.close()
    return ip_address
class Config:
    # DEBUG = False
    # TESTING = False
    # 缓存配置
    CACHE_TTL = 600
    CACHE_HOST = 'localhost'
    CACHE_PORT = REDIS_PORT
    CACHE_DB = 4
    
class DevelopConfig(Config):
 
    pass

class TestingConfig(Config):
    # 日志配置
    LOG_FORMAT = "<green>{time:YYYYMMDD HH:mm:ss}</green> | {process.name} | {thread.name} | <cyan>{module}</cyan>.<cyan>{function}</cyan> :<cyan>{line}</cyan> | <level>{level}</level>: <level>{message}</level>"
    LOG_CONFIG = {
        "handlers": [
            {"sink": os.path.join(BASE_DIR, "log/error.log"), "level": "ERROR", "format": LOG_FORMAT, "rotation": "00:24"},
            {"sink": os.path.join(BASE_DIR, "log/info.log"),  "level": "INFO", "format": LOG_FORMAT, "rotation": "00:24"},
            {"sink": sys.stdout,                                  "level": "DEBUG", "format": LOG_FORMAT},
        ],
    }

class ProductConfig(Config):
    # 日志配置
    LOG_FORMAT = "<green>{time:YYYYMMDD HH:mm:ss}</green> | {process.name} | {thread.name} | <cyan>{module}</cyan>.<cyan>{function}</cyan> :<cyan>{line}</cyan> | <level>{level}</level>: <level>{message}</level>"
    LOG_CONFIG = {
        "handlers": [
            {"sink": os.path.join(BASE_DIR, "log/error.log"), "level": "ERROR", "format": LOG_FORMAT, "rotation": "00:24"},
            {"sink": os.path.join(BASE_DIR, "log/info.log"),  "level": "INFO", "format": LOG_FORMAT, "rotation": "00:24"},
            {"sink": sys.stdout,                                  "level": "DEBUG", "format": LOG_FORMAT},
        ],
    }


IP = get_ip_address()
envs = dict(
    ip_10_30_20_116 =  TestingConfig,
    ip_172_20_16_243 = ProductConfig,
    default = TestingConfig
)

# 获取docker compose 中的环境变量
config  = envs.get(f"ip_{IP.replace('.', '_')}",'default')
