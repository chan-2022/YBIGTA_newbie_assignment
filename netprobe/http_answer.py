from __future__ import annotations

from typing import Optional


def build_request(host: str, path: str) -> bytes:

    if not path.startswith("/"):
        path = "/" + path

    req = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    )
    return req.encode("utf-8")


def send_and_recv(sock, request: bytes, max_bytes: int) -> bytes:
    
    sock.sendall(request)

    chunks: list[bytes] = []
    total = 0
    while True:
        data = sock.recv(4096)
        if not data:
            break
        chunks.append(data)
        total += len(data)
        if total > max_bytes:
            break
    return b"".join(chunks)


def parse_status_and_preview(raw: bytes, max_preview: int = 200) -> tuple[Optional[int], str, Optional[str]]:
    """
    - status line에서 status code만 파싱
    - body preview는 max_preview bytes만 decode
    """
    sep = raw.find(b"\r\n\r\n")
    if sep == -1:
        return None, "", "Invalid HTTP response: missing header separator"

    header = raw[:sep].decode("iso-8859-1", errors="replace")
    body = raw[sep + 4:]

    lines = header.split("\r\n")
    if not lines or not lines[0]:
        return None, "", "Invalid HTTP response: empty status line"

    parts = lines[0].split()
    if len(parts) < 2:
        return None, "", "Invalid HTTP status line"

    try:
        status_code = int(parts[1])
    except ValueError:
        return None, "", "Invalid status code"

    preview = body[:max_preview].decode("utf-8", errors="ignore")
    return status_code, preview, None
