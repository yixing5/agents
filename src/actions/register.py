'''
Author: Sasha
Date: 2024-06-26 10:23:43
LastEditors: Sasha
LastEditTime: 2024-06-28 17:18:23
Description: 
FilePath: /v2/src/actions/register.py
'''
from typing import Any, Dict, Callable, get_type_hints,List,Tuple
from typing import get_origin, get_args, Annotated
import inspect
from enum import Enum
import copy
from src.schema import ActionReturn,ActionValidCode,ActionStatusCode

_TOOL_HOOKS = {}
_TOOL_DESCRIPTIONS = []
class FunctionRegister:
    """
    适用于 autogpt , 工具调用prompt 写在 chat_history 中
    """
    def __init__(self, func: Callable):
        self.func = func
        self.func_name = func.__name__
        self.func_description = func.__doc__ or ""
        self.parameters, self.required = self._parse_parameters()
        self.return_data = self._parse_return_type()

    def _parse_parameters(self) -> Tuple[List[Dict[str, Any]], List[str]]:
        sig = inspect.signature(self.func)
        hints = get_type_hints(self.func)
        params = []
        required = []
        
        for name, param in sig.parameters.items():
            annotation = hints.get(name, param.annotation)
            description = ""
            is_required = True

            if get_origin(param.annotation) is Annotated:
                base_type, description, is_required = get_args(param.annotation)
                annotation = base_type

            param_info = {
                "name": name,
                "type": self._get_type_str(annotation),
                "description": description
            }
            
            if self._is_enum(annotation):
                param_info["enum"] = [e.value for e in annotation]
            elif get_origin(annotation) is list and self._is_enum(get_args(annotation)[0]):
                param_info["enum"] = [e.value for e in get_args(annotation)[0]]
                
            if is_required:
                required.append(name)

            params.append(param_info)
            
        return params, required

    def _parse_return_type(self) -> List[Dict[str, Any]]:
        hints = get_type_hints(self.func)
        return_annotation = hints.get('return', None)
        return_data = []
        if return_annotation:
            return_data.append({
                "name": "content",
                "description": self.func.__doc__.strip().split('\n')[-1],  # Assuming the last line of the docstring describes the return data
                "type": self._get_type_str(return_annotation)
            })
        return return_data

    def _is_enum(self, typ) -> bool:
        return isinstance(typ, type) and issubclass(typ, Enum)

    def _get_type_str(self, typ) -> str:
        origin = get_origin(typ)
        args = get_args(typ)
        
        if origin is list and args:
            item_type = self._get_type_str(args[0])
            return f"LIST[{item_type}]"
        if typ is str:
            return "STRING"
        elif typ is int:
            return "INTEGER"
        elif typ is float:
            return "NUMBER"
        elif typ is bool:
            return "BOOLEAN"
        elif typ is list:
            return "LIST"
        elif typ is dict:
            return "OBJECT"
        elif self._is_enum(typ):
            return typ.__name__
        else:
            return str(typ).upper()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.func_name,
            "description": self.func_description,
            "parameters": self.parameters,
            "required": self.required,
            "return_data": self.return_data,
            'parameter_description': 'If you call this tool, you must pass arguments in the JSON format {key: value}, where the key is the parameter name.'
        }


class ToolRegister:
    """
    适用于 function , 工具描述符合 chatglm 格式
    """
    def __init__(self, func: Callable):
        self.func = func
        self.func_name = func.__name__
        self.func_description = func.__doc__ or ""
        self.parameters = self._parse_parameters()
        
    def _is_enum(self, typ) -> bool:
        return isinstance(typ, type) and issubclass(typ, Enum)
    
    def _parse_parameters(self) -> Dict[str, Any]:
        sig = inspect.signature(self.func)
        hints = get_type_hints(self.func)
        params = {}
        
        for name, param in sig.parameters.items():
            annotation = hints.get(name, param.annotation)
            description = ""
            required = True

            if get_origin(param.annotation) is Annotated:
                base_type, description, required = get_args(param.annotation)
                annotation = base_type

            param_info = {
                "description": description,
                "type": self._get_type_str(annotation),
                "required": required
            }
            if self._is_enum(annotation):
                param_info["enum"] = [e.value for e in annotation]
            elif get_origin(annotation) is list and self._is_enum(get_args(annotation)[0]):
                param_info["enum"] = [e.value for e in get_args(annotation)[0]]
                
            params[name] = param_info
            
        return params

    
    def _get_type_str(self, typ) -> str:
        origin = get_origin(typ)
        args = get_args(typ)
        
        if origin is list and args:
            item_type = self._get_type_str(args[0])
            return f"list"
        if typ is str:
            return "str"
        elif typ is int:
            return "int"
        elif typ is float:
            return "float"
        elif typ is bool:
            return "bool"
        elif typ is list:
            return "list"
        elif typ is dict:
            return "object"
        elif issubclass(typ, Enum):
            return typ.__name__
        else:
            return str(typ)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.func_name,
                "description": self.func_description.strip(),
                "parameters": {
                    "type": "object",
                    "properties": self.parameters
                }
            }
        }
    


def register_tool(func: Callable):
    info = ToolRegister(func)
    func.__function_info__ = info
    _TOOL_HOOKS[info.func_name] = func
    _TOOL_DESCRIPTIONS.append(info.to_dict())
    return func


def register_function(func: Callable):
    info = FunctionRegister(func)
    func.__function_info__ = info
    _TOOL_HOOKS[info.func_name] = func
    _TOOL_DESCRIPTIONS.append(info.to_dict())
    return func

def get_tools() -> list[dict]:
    return copy.deepcopy(_TOOL_DESCRIPTIONS)


@register_function
def finish_action(
                  response: Annotated[str, "The final result", True],
                  ) -> ActionReturn:
    """This is a finish action class, which is used to return the final ,Returns:ActionReturn: The action return.
    result."""

    action_return = ActionReturn(
        url=None,
        args=dict(text=response),
        result=response,
        type='FINISH',
        valid=ActionValidCode.FINISH,
        state=ActionStatusCode.SUCCESS)
    return action_return
finish_action.name = "FINISH"

@register_function
def no_action(                
    err_msg: Annotated[str, "Please follow the format", True],
    description: Annotated[str, "description", True]
    ):
    """This is a no action class, which is used to return error message when
    the response does not follow the format.

    Args:
        err_msg (str): The error message. Defaults to
            'Please follow the format'.
    """
    action_return = ActionReturn(
        url=None,
        args=dict(text=err_msg),
        type="ERROR",
        errmsg="API error no_action" ,
        valid=ActionValidCode.INVALID,
        state=ActionStatusCode.API_ERROR)
    return action_return
no_action.name = "ERROR"



if __name__ == "__main__":
    # import sys
    # sys.path.append("/data1/sasha/project_agent_raw/v2")
    # from src.actions.schema import CompanyInfoEnum, SubCompanyInfoEnum, LegalDocumentEnum, CompanyRegisterEnum

    # @register_tool
    # def search_company_name_by_info(
    #         company_name: Annotated[list, "母公司名称的列表", True],
    #         value: Annotated[str, "公司基本信息字段具体的值", True],
    #         key: Annotated[CompanyInfoEnum, "公司基本信息字段名称", True], # type: ignore
    # ) -> str:
    #     """
    #     根据公司某个基本信息字段是某个值时，查询所有满足条件的公司名称
    #     """
    #     pass
    # # Retrieving function info
    
    # func_info = search_company_name_by_info.__function_info__.to_dict()
    # print(json.dumps(func_info, indent=4, ensure_ascii=False))
    pass
