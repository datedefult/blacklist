# -*- coding:utf-8 -*-
# @文件       :response.py
# @时间       :2024/9/3 下午3:25
# @作者       :Victoria Steam
# @说明       :通用响应体的封装
import os

from pydantic import BaseModel
from typing import Optional, Any
from fastapi.responses import ORJSONResponse
from fastapi import status



class BaseResponseModel(BaseModel):
    """
    基础响应体

    Attributes:
        code (int): 响应状态码。
        message (str): 响应消息。
        data (Optional[Any]): 响应数据，默认为None。
    """
    code: int
    message: str
    data: Optional[Any] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "code": 200,
                    "message": "成功创建{num}名用户",
                    "data": ['失败详情或成功返回的数据'],
                }
            ]
        }
    }


class ResponseModelSuc(BaseResponseModel):
    """
    成功的响应体,code默认为0

    Attributes:
        code (int): 响应状态码，默认为200。
        message (str): 响应消息，默认为'OK'。
        data (Optional[Any]): 响应数据，默认为None。
    """

    code: int = 200
    message: str = 'OK'


class ResponseModelFail(BaseResponseModel):
    """
    失败的响应体,code默认为-1

    Attributes:
        code (int): 响应状态码，默认为-1。
        message (str): 响应消息，默认为'Bad Request'。
        data (Optional[Any]): 响应数据，默认为None。
    """

    code: int = 400
    message: str = 'Bad Request'

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "code": '400 或者详细code',
                    "message": "错误摘要",
                    "data": ['失败详情或为空'],
                }
            ]
        }
    }


def response_base(content: BaseResponseModel,
                  status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
                  headers: Optional[dict] = None
                  ) -> ORJSONResponse:
    """
    响应体封装返回前端的content, status_code, headers 默认500服务器内部错误

    :param content: 返回的响应内容
    :param status_code: 返回的请求响应码,默认500服务器内部错误
    :param headers: 响应头默认空

    """
    return ORJSONResponse(
        status_code=status_code,
        content=content.dict(),
        headers=headers
    )


def response_suc(
        content: BaseResponseModel = ResponseModelSuc(),
        code: int = None,
        message: str = None,
        data: Optional[Any] = None,
        language: str = "en",
                 ) -> ORJSONResponse:
    """
    响应体封装返回给前端的状态码为200

    :param content: 封装的响应类对象, :instance:
    :param code: 覆盖响应类的定义
    :param message: 覆盖响应类的定义
    :param data: 覆盖响应类的定义
    """


    return ORJSONResponse(
        status_code=status.HTTP_200_OK,
        # 可选参数exclude_none=True可以排除为None的键值对
        content=content.dict(exclude_none=True),
    )


def response_fail(
        content: BaseResponseModel = ResponseModelFail(),
        code: int = None,
        message: str = None,
        data: Optional[Any] = None,
        language: str = "en",
                  ) -> ORJSONResponse:
    """
    响应体封装返回给前端的状态码为400

    :param content: 封装的响应类对象
    :param code: 覆盖响应类的定义
    :param message: 覆盖响应类的定义
    :param data: 覆盖响应类的定义
    """

    return ORJSONResponse(
        status_code=status.HTTP_200_OK,
        content=content.dict(),
    )


base_error_code_dict = {
    422: {
        "description": "Validation error",
        "model": ResponseModelFail
    },
    500: {
        "description": "Internal Server Error",
        "model": ResponseModelFail
    }
}
