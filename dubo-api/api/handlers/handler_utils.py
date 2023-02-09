import base64


def sql_response_headers(sql: str):
    return {
        "X-Generated-Sql": base64.b64encode(bytes(sql, 'ascii')).decode(),
        "Access-Control-Expose-Headers": "X-Generated-Sql"
    }
