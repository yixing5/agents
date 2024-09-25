'''
Author: Sasha
Date: 2024-06-27 11:59:57
LastEditors: Sasha
LastEditTime: 2024-06-28 16:47:18
Description: 
FilePath: /v2/src/actions/action_executor.py
'''
import json
from src.actions.register import _TOOL_HOOKS
import traceback
from src.actions.register import finish_action,no_action
from src.schema import ActionReturn


class ActionExecutor:
    
    def __init__(self,actions:list) -> None:
        self.actions = actions
        self.finish_action = finish_action
        self.no_action = no_action
        pass
    
    def action_names(self):
        return [action.__name__ for action in self.actions]
    
    def get_actions_info(self):
        return [action.__function_info__.to_dict() for action in self.actions]

    def __call__(self, tool_name: str, code: str, max_retry_time: int = 3):
        print("TOOL CALL!", tool_name, code)
        try:
            tool_params = {} if not code else json.loads(code) if isinstance(code, str) else code
        except json.JSONDecodeError as e:
            err = f"Error decoding JSON: {e}"
            print("system_error", err)
            return err

        if tool_name not in _TOOL_HOOKS:
            err = f"Tool `{tool_name}` not found. Please use a provided tool."
            print("system_error", err)
            return err

        tool_hook = _TOOL_HOOKS[tool_name]
        for k, v in tool_params.items():
            if "Items" in v:
                tool_params[k] = v["Items"]

        for _ in range(max_retry_time):
            try:
                ret = tool_hook(**tool_params)
                return ret if isinstance(ret, ActionReturn) else ActionReturn(
                    args=tool_params,
                    result=ret,
                    name=tool_name,
                )
            except Exception:
                err = traceback.format_exc()
                print("system_error", err)

        return ActionReturn(
            args=tool_params,
            errmsg=err
        )
        
    def __call__(self,tool_name: str, code: str, max_retry_time:int=3):
        print("TOOL CALL! ", tool_name, code)
        try:
            if not code:
                tool_params = {}
            elif type(code) == dict:
                tool_params = code
            else:
                tool_params = json.loads(code)
        except json.JSONDecodeError as e:
            err = f"Error decoding JSON: {e}"
            print("system_error", err)
            return err

        if tool_name not in _TOOL_HOOKS :
            err = f"Tool `{tool_name}` not found. Please use a provided tool."
            print("system_error", err)
            return err

        tool_hook = _TOOL_HOOKS[tool_name] 

        for k, v in tool_params.items():
            if "Items" in v:
                tool_params[k] = v["Items"]

        print("FFFFF", tool_name, tool_params)
        for _ in range(max_retry_time):
            try:
                ret: str = tool_hook(**tool_params)
                # return [ToolObservation(tool_name, str(ret))]
                return ret if isinstance(ret,ActionReturn) else ActionReturn (
                        args = tool_params,
                        result = ret,
                        name = tool_name,
                    ) 
            except Exception:
                err = traceback.format_exc()
                print("system_error", err)
                

        return ActionReturn(
                        args = tool_params,
                        errmsg = err
                    ) 
