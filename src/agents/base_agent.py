'''
Author: Sasha
Date: 2024-06-27 13:32:09
LastEditors: Sasha
LastEditTime: 2024-06-28 15:02:26
Description: 
FilePath: /v2/src/agents/base_agent.py
'''
from src.actions import ActionExecutor
from src.schema import AgentReturn
from src.llms import BaseAPIModel

class BaseAgent:
    """BaseAgent is the base class of all agents.

    Args:
        llm (BaseModel): the language model.
        action_executor (ActionExecutor): the action executor.
        protocol (object): the protocol of the agent, which is used to
            generate the prompt of the agent and parse the response from
            the llm.
    """

    def __init__(self, llm: BaseAPIModel, action_executor: ActionExecutor,
                 protocol: object) -> None:
        self._llm = llm
        self._action_executor = action_executor
        self._protocol = protocol

    def add_action(self, action) -> None:
        """Add an action to the action executor.

        Args:
            action (BaseAction): the action to be added.
        """
        self._action_executor.add_action(action)

    def del_action(self, name: str) -> None:
        """Delete an action from the action executor.

        Args:
            name (str): the name of the action to be deleted.
        """
        self._action_executor.del_action(name)

    def chat(self, message: str, **kwargs) -> AgentReturn:
        raise NotImplementedError
