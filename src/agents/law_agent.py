'''
Author: Sasha
Date: 2024-06-27 18:40:49
LastEditors: Sasha
LastEditTime: 2024-06-28 15:34:15
Description: 
FilePath: /v2/src/agents/law_agent.py
'''
from typing import  List, Union
from src.actions import ActionExecutor,get_tools
from src.agents.base_agent import BaseAgent
from src.llms import BaseAPIModel
from src.schema import AgentReturn
from src.actions.schema import database_schema
from core.logger import logger

CALL_PROTOCOL_CN = f"""你是一位金融法律专家，你的任务是根据用户给出的query，调用给出的工具接口，获得用户想要查询的答案。
所提供的工具接口可以查询四张数据表的信息，数据表的schema如下:
{database_schema}
"""
class LawAgent(BaseAgent):
    def __init__(self,
                 llm: Union[BaseAPIModel],
                 action_executor: ActionExecutor,
                 max_turn: int = 10) -> None:
        self.max_turn = max_turn
        super().__init__(
            llm=llm, action_executor=action_executor)

    def chat(self, message: Union[str, dict, List[dict]],
             **kwargs) -> AgentReturn:
        if isinstance(message, str):
            inner_history = [dict(role='user', content=message)]
        elif isinstance(message, dict):
            inner_history = [message]
        elif isinstance(message, list):
            inner_history = message[:]
        else:
            raise TypeError(f'unsupported type: {type(message)}')
        
        inner_history = [
            {"role": "system", "content": CALL_PROTOCOL_CN},
            {"role": "user", "content": message}
        ]
        offset = len(inner_history)
        agent_return = AgentReturn()
        default_response = 'Sorry that I cannot answer your question.'
        for _ in range(self.max_turn):
            response = self._llm.chat(inner_history, tools = self._action_executor.get_actions_info()) #
            inner_history.append(response)
            if response['tool_calls'] :
                    tools_call = response['tool_calls'][0]
                    tool_name = tools_call['function']['name']
                    args = tools_call['function']['arguments']
                    obs = self._action_executor(tool_name, args, "007")
                    inner_history.append({
                        "role": "tool", 
                        "content": f"{obs.result}",
                        "tool_id": tools_call['id']
                    })
            else:
                logger.info("###对话结束###")
                agent_return.response = inner_history[-1]["content"]
                break
        else:
            agent_return.response = default_response
        agent_return.inner_steps = inner_history[offset:]
        return agent_return
