import requests
from typing import  Annotated, List
import sys
sys.path.append("/data1/sasha/project_agent_raw/v2")
from src.actions.register import register_tool
from src.actions.schema import CompanyInfo, SubCompanyInfo, LegalDocument, CompanyRegister
from src.actions.schema import CompanyInfoEnum, SubCompanyInfoEnum, LegalDocumentEnum, CompanyRegisterEnum

class Tool:

    @property
    def name(self):
        return self.__class__.__name__

    def __call__(self, **kwargs) -> str:
        raise NotImplementedError
    
    
api_list = [
    "get_company_info",
    "search_company_name_by_info",
    "get_company_register",
    "search_company_name_by_register",
    "get_sub_company_info",
    "search_company_name_by_sub_info",
    "get_legal_document",
    "search_case_num_by_legal_document"
]


domain = "https://comm.chatglm.cn"

headers = {
    'Content-Type': 'application/json',
    "Authorization": "Bearer 0B6424BEC3D1CD329E09DA41B89AB645006337C4C17C3897"
}


# Tool Definitions
def http_api_call(api_name, data, max_data_len=None):
    url = f"{domain}/law_api/{api_name}"
    
    rsp = requests.post(url, json=data, headers=headers)
    final_rsp = rsp.json()
    final_rsp = [final_rsp] if isinstance(final_rsp, dict) else final_rsp
    
    if max_data_len is None:
        max_data_len = len(final_rsp)
    return {
        "return_items_count": len(final_rsp),
        "return": final_rsp[:max_data_len]
    }


def get_company_name_by_bref(bref):
    company_names = [i["公司名称"] for i in http_api_call("search_company_name_by_info", {"key": "公司简称", "value": bref})["return"]]
    return company_names


def get_company_name_by_en(bref):
    company_names = [i["公司名称"] for i in http_api_call("search_company_name_by_info", {"key": "英文名称", "value": bref})["return"]]
    return company_names


def augment_company_name(company_name):
    company_name = company_name if isinstance(company_name, list) else [company_name]
    for c in company_name[:]:
        company_name += get_company_name_by_bref(c)
        company_name += get_company_name_by_en(c)
        company_name += [c.replace("(", "（").replace(")", "）")]
        company_name += [c.replace("（", "(").replace("）", ")")]

    return list(set(company_name))


@register_tool
def get_company_info(
        company_name: Annotated[list, "公司名称或简称的列表", True],
) -> List[CompanyInfo]:
    """
    根据公司名称获得该公司所有基本信息，可以传入多个公司名称，返回一个列表 ,对应数据表为: CompanyInfo
    """
    company_name = augment_company_name(company_name)
    return http_api_call("get_company_info", {"company_name": company_name})


@register_tool
def get_company_register(
        company_name: Annotated[list, "公司名称或简称的列表", True],
) -> List[CompanyRegister]:
    """
    根据公司名称获得该公司所有注册信息，可以传入多个公司名称，返回一个列表，对应数据表为: CompanyRegister
    """
    company_name = augment_company_name(company_name)
    return http_api_call("get_company_register", {"company_name": company_name})


@register_tool
def get_sub_company_info(
        company_name: Annotated[list, "母公司名称的列表", True],
) -> SubCompanyInfo:
    """
    根据母公司名称获得该母公司所有的关联投资、母公司等信息，可以传入多个母公司名称，返回一个列表，对应数据表为: SubCompanyInfo
    """
    company_name = augment_company_name(company_name)
    all_subs = company_name[:]
    for comp_name in company_name:
        # print("@@@", http_api_call("search_company_name_by_sub_info", {"key": "关联上市公司全称", "value": comp_name})["return"])
        all_subs += [i["公司名称"] for i in http_api_call("search_company_name_by_sub_info", {"key": "关联上市公司全称", "value": comp_name}, max_data_len=None)["return"]]
        # print("!", all_subs)
    print(all_subs)
    return http_api_call("get_sub_company_info", {"company_name": all_subs})

@register_tool
def get_sub_company_info_by_sub_comp(
        company_name: Annotated[list, "子公司名称的列表", True],
) -> SubCompanyInfo:
    """
    根据子公司名称获得该子公司所有的关联投资等信息，可以传入多个子公司名称，返回一个列表，对应数据表为: SubCompanyInfo
    """
    company_name = augment_company_name(company_name)
    return http_api_call("get_sub_company_info", {"company_name": company_name})


@register_tool
def get_legal_document(
        case_num: Annotated[list, "案号", True],
) -> List[LegalDocument]:
    """
    根据案号查询相关法律文书的内容，可以传入多个案号，返回一个列表 ，对应数据表为: LegalDocument
    """
    return http_api_call("get_legal_document", {"case_num": case_num})


@register_tool
def search_company_name_by_info(
        key: Annotated[CompanyInfoEnum, "公司基本信息字段名称", True], # type: ignore
        value: Annotated[str, "公司基本信息字段具体的值", True],
) -> str:
    """
    根据公司某个基本信息字段是某个值时，查询所有满足条件的公司名称
    """
    return http_api_call("search_company_name_by_info", {"key": key, "value": value})


@register_tool
def search_company_name_by_register(
        key: Annotated[CompanyRegisterEnum, "公司注册信息字段名称", True],# type: ignore
        value: Annotated[str, "公司注册信息字段具体的值", True],
) -> str:
    """
    根据公司某个注册信息字段是某个值时，查询所有满足条件的公司名称
    """
    return http_api_call("search_company_name_by_register", {"key": key, "value": value})


@register_tool
def search_company_name_by_sub_info(
        key: Annotated[SubCompanyInfoEnum, "子公司融资信息字段名称", True],# type: ignore
        value: Annotated[str, "子公司融资信息信息字段具体的值", True],
) -> str:
    """
    根据子公司融资信息字段是某个值时，查询所有满足条件的子公司名称
    """
    return http_api_call("search_company_name_by_sub_info", {"key": key, "value": value})


@register_tool
def search_case_num_by_legal_document(
        key: Annotated[LegalDocumentEnum, "法律文书信息字段名称", True],# type: ignore
        value: Annotated[str, "法律文书信息字段具体的值", True],
) -> str:
    """
    根据法律文书信息字段是某个值时，查询所有满足条件的法律文书案号 ，对应数据表为: LegalDocument
    """
    return http_api_call("search_case_num_by_legal_document", {"key": key, "value": value})


if __name__ == "__main__":
    # print(get_sub_company_info(**{"company_name": "北京长久物流股份有限公司"}))
    # print(search_company_name_by_info(**{"key":"所属行业","value":"批发业"}))
    print(search_company_name_by_register(**{"key":"企业类型","value":"医疗生物"}))