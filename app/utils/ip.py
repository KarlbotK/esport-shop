from fastapi import Request


def get_client_ip(request: Request) -> str:
    """Extract the client IP address from request headers."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    client = request.client
    if client:
        return client.host
    return "0.0.0.0"
