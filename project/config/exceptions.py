from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


def api_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if response is None:
        payload = {
            "code": "server_error",
            "message": "服务器内部错误",
            "errors": {},
        }
        if settings.DEBUG:
            payload["debug"] = str(exc)
        return Response(payload, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    message = _extract_message(response.data)
    return Response(
        {
            "code": response.status_code,
            "message": message,
            "errors": response.data,
        },
        status=response.status_code,
    )


def _extract_message(data):
    if isinstance(data, dict):
        if "detail" in data:
            return str(data["detail"])
        if data:
            first_value = next(iter(data.values()))
            if isinstance(first_value, list) and first_value:
                return str(first_value[0])
            return str(first_value)
    if isinstance(data, list) and data:
        return str(data[0])
    return "请求失败"
