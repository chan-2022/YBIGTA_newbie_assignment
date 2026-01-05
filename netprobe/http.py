from __future__ import annotations

from typing import Optional


def build_request(host: str, path: str) -> bytes:
    """
    HTTP GET 요청 메시지를 바이트 형태로 생성합니다.
    """
    if not path.startswith("/"):
        path = "/" + path

    ###########################################################
    # TODO: HTTP/1.1 규격에 맞게 요청 문자열(GET, Host, Connection 헤더 포함)을 완성하세요.
    # HINT: 각 줄의 끝은 \r\n이며, 헤더의 끝에는 빈 줄(\r\n)이 하나 더 필요합니다.
    
    req = () # TODO: (이곳에 요청 문자열을 작성하세요)
    
    ###########################################################

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
    ###########################################################
    # TODO: raw 데이터에서 헤더와 바디의 경계인 '\r\n\r\n'의 위치(index)를 찾으세요.
    # HINT: bytes 객체의 .find() 메서드를 사용하세요.

    sep = -1 # TODO: sep 값을 수정하세요

    ###########################################################

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