from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return None

    original_data = response.data

    if isinstance(original_data, dict):
        if "detail" in original_data:
            detail = original_data["detail"]
        else:
            detail = original_data
    else:
        detail = original_data

    response.data = {
        "code": response.status_code,
        "detail": detail,
    }

    return response