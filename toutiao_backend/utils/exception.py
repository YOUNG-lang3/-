import traceback
from typing import Any

from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette import status
from starlette.exceptions import HTTPException as StarletteHTTPException


# 开发模式：返回详细错误信息；生产模式：返回简化错误信息
DEBUG_MODE = True  # 教学项目保持开启


def _error_response(
    status_code: int,
    message: str,
    *,  #*号表示之后所有的参数在这个函数调用时只能通过关键字赋值的方式进行传参
    data: Any = None,
    request: Request | None = None,
    exc: Exception | None = None,
    include_traceback: bool = False,
) -> JSONResponse:
    """统一错误响应结构，与项目 code/message/data 格式保持一致"""
    content: dict[str, Any] = {
        "code": status_code,
        "message": message,
        "data": data,
    }
    if DEBUG_MODE and request is not None:
        content["path"] = request.url.path
    if DEBUG_MODE and include_traceback and exc is not None:
        content["traceback"] = "".join(
            traceback.format_exception(type(exc), exc, exc.__traceback__)
        )
    return JSONResponse(status_code=status_code, content=content)


# 1. HTTPException：业务逻辑主动抛出的异常（400、404 等）
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    处理 HTTPException 异常
    HTTPException 通常是业务逻辑主动抛出的，data 保持 None
    """
    response = _error_response(
        status_code=exc.status_code,
        message=str(exc.detail),
        request=request,
        exc=exc,
    )
    # 保留业务异常上可能携带的自定义响应头（如鉴权的 WWW-Authenticate）
    headers = getattr(exc, "headers", None)
    if headers:
        response.init_headers(headers)
    return response


# 2. RequestValidationError：请求参数/请求体校验失败（422）
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    处理请求参数校验异常，将错误明细整理为可读的字段级信息
    """
    error_details = []
    for err in exc.errors():
        # 过滤掉 body/query/path 这类定位前缀，只保留字段名
        loc = [str(x) for x in err.get("loc", []) if x not in ("body", "query", "path")]
        error_details.append({
            "field": ".".join(loc),
            "message": err.get("msg"),
            "type": err.get("type"),
        })
    return _error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="请求参数校验失败",
        data=error_details,
        request=request,
        exc=exc,
    )


# 3. IntegrityError：唯一约束、外键约束等完整性冲突（400）
async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """
    处理数据库完整性异常：重复注册、外键约束失败等
    """
    # 异常发生后事务已失效，先回滚释放连接
    session = getattr(exc, "session", None)
    if session is not None:
        await session.rollback()

    orig_msg = str(exc.orig) if exc.orig else str(exc)
    if "1062" in orig_msg or "Duplicate entry" in orig_msg:
        message = "数据已存在，请勿重复提交"
    elif "1452" in orig_msg:
        message = "关联数据不存在（外键约束失败）"
    elif "1451" in orig_msg:
        message = "数据被其他记录引用，无法操作"
    else:
        message = "数据完整性约束失败"

    return _error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        message=message,
        data=orig_msg if DEBUG_MODE else None,
        request=request,
        exc=exc,
    )


# 4. SQLAlchemyError：其他数据库错误（500）
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    处理数据库层面的通用异常
    """
    session = getattr(exc, "session", None)
    if session is not None:
        try:
            await session.rollback()
        except Exception:
            pass
    return _error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="数据库操作失败",
        data=str(exc) if DEBUG_MODE else None,
        request=request,
        exc=exc,
        include_traceback=True,
    )


# 5. Exception：兜底处理所有未捕获异常（500）
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    兜底异常处理：开发模式返回详细错误，生产模式返回简化信息
    """
    return _error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message=str(exc) if DEBUG_MODE else "服务器内部错误",
        request=request,
        exc=exc,
        include_traceback=True,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    统一注册所有异常处理器
    """
    # 注册 Starlette 父类 HTTPException：路由未匹配等框架抛出的 404/405 也能被统一捕获
    # （fastapi.HTTPException 是其子类，MRO 匹配，因此注册父类即可覆盖业务抛出的异常）
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
