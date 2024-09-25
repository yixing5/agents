'''
Author: Sasha
Date: 2024-06-27 11:47:44
LastEditors: Sasha
LastEditTime: 2024-06-27 11:47:45
Description: 
FilePath: /v2/src/__init__.py
'''
from dotenv import load_dotenv

def load_env_file():
    load_dotenv(dotenv_path='.env', override=True)

# 在应用启动时调用
load_env_file()