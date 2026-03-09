from .models import OperationLog


def log_operation(
    *,
    user,
    module_name: str,
    operation_type: str,
    request=None,
    result: str = OperationLog.RESULT_SUCCESS,
    request_param: str = "",
) -> None:
    OperationLog.objects.create(
        user=user if getattr(user, "is_authenticated", False) else None,
        module_name=module_name,
        operation_type=operation_type,
        request_method=getattr(request, "method", ""),
        request_url=getattr(request, "path", ""),
        request_param=request_param,
        operation_result=result,
        ip_address=_extract_ip(request) if request else "",
    )


def _extract_ip(request) -> str:
    if not request:
        return ""
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")
