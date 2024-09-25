'''
Author: Sasha
Date: 2024-06-25 12:00:05
LastEditors: Sasha
LastEditTime: 2024-06-28 11:06:55
Description: 
FilePath: /v2/src/actions/google_search.py
'''
import os
import time
import requests
from typing import List, Dict, Optional,Annotated
from src.actions import register_function

class GoogleSearch():
    """使用谷歌搜索问题"""

    description = '使用谷歌搜索问题，它的输入是一个问题，参数名为 query，输出是搜索结果。'
    
    def __init__(self, api_key: Optional[str] = None, topk: int = 5) -> None:
        self.api_key = api_key or os.getenv('SERPER_API_KEY')
        self.base_url = 'https://google.serper.dev/search'
        self.topk = topk

    def __call__(self, query: str) -> str:
        headers = {'x-api-key': self.api_key, 'Content-Type': 'application/json'}
        response = requests.post(self.base_url, params={'q': query}, headers=headers)
        results = self._parse_snippets(response.json())
        return ' '.join(results)
    
    def _parse_snippets(self, results: dict) -> str:
        # copy from https://github.com/langchain-ai/langchain
        snippets = []

        if results.get('answerBox'):
            answer_box = results.get('answerBox', {})
            if answer_box.get('answer'):
                return [answer_box.get('answer')]
            elif answer_box.get('snippet'):
                return [answer_box.get('snippet').replace('\n', ' ')]
            elif answer_box.get('snippetHighlighted'):
                return answer_box.get('snippetHighlighted')

        if results.get('knowledgeGraph'):
            kg = results.get('knowledgeGraph', {})
            title = kg.get('title')
            entity_type = kg.get('type')
            if entity_type:
                snippets.append(f'{title}: {entity_type}.')
            description = kg.get('description')
            if description:
                snippets.append(description)
            for attribute, value in kg.get('attributes', {}).items():
                snippets.append(f'{title} {attribute}: {value}.')

        for result in results['organic'][:self.topk]:
            if 'snippet' in result:
                snippets.append(result['snippet'])
            for attribute, value in result.get('attributes', {}).items():
                snippets.append(f'{attribute}: {value}.')

        if len(snippets) == 0:
            assert False, 'No snippets found in the search results.'

        return snippets
    
    
@register_function
def google_search(
    query: Annotated[str, "用户需要搜索的问题", True]
    ):
    """
    使用谷歌搜索问题，它的输入是一个问题，参数名为 query，输出是搜索结果。
    """
    return  GoogleSearch()(query)
    
    
@register_function
def current_time():
    """获取当前时间的工具，它不接受输入，输出是当前时间。"""
    currtent_time = time.asctime(time.localtime(time.time()))
    return currtent_time
