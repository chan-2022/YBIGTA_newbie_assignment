from __future__ import annotations

import socket
import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class TCPConnectResult:
    ip: Optional[str]
    port: int
    connect_ms: Optional[float]
    local_addr: Optional[tuple[str, int]]
    peer_addr: Optional[tuple[str, int]]
    error: Optional[str]
    sock: Optional[socket.socket]


def _make_socket(ip: str, timeout: float) -> socket.socket:
    family = socket.AF_INET6 if ":" in ip else socket.AF_INET
    s = socket.socket(family, socket.SOCK_STREAM)
    s.settimeout(timeout)
    return s


def connect_one(ip: str, port: int, timeout: float):
    """
    특정 IP로 TCP 연결을 시도하고 지연 시간을 측정합니다.
    """
    try:
        s = _make_socket(ip, timeout)
        start = time.perf_counter()
        
        ###########################################################
        # TODO: 연결 직전과 직후의 시간을 측정하여 연결에 걸린 시간(ms)을 계산하세요.
        # HINT: time.perf_counter()를 사용하고, 단위가 초(s)이므로 1000을 곱하세요.
        
        s.connect((ip, port))
        ms = 0.0 # TODO: ms 값을 수정하세요

        ###########################################################

        return s, ms, None
    except Exception as e:
        try:
            s.close()
        except Exception:
            pass
        return None, None, str(e)


def connect_with_fallback(ips: list[str], port: int, timeout: float, prefer: str = "any") -> TCPConnectResult:
    """
    연결이 성공할 때까지 IP 후보들을 순회합니다.
    """
    if not ips:
        return TCPConnectResult(
            ip=None, port=port, connect_ms=None,
            local_addr=None, peer_addr=None,
            error="No IPs to connect", sock=None
        )

    v4 = [ip for ip in ips if ":" not in ip]
    v6 = [ip for ip in ips if ":" in ip]

    if prefer == "ipv4":
        ordered = v4 + v6
    elif prefer == "ipv6":
        ordered = v6 + v4
    else:
        ordered = ips[:]

    last_err: Optional[str] = None
    for ip in ordered:
        sock, ms, err = connect_one(ip, port, timeout)
        if sock is not None:
            # local/peer addr 기록
            try:
                ###########################################################
                # TODO: 성공한 소켓에서 내 주소(local)와 서버 주소(peer) 정보를 추출하세요.
                # HINT: sock.getsockname()과 sock.getpeername()을 활용하세요.

                local = None  # TODO
                peer = None   # TODO
                local_addr = (None, None) # TODO
                peer_addr = (None, None)  # TODO
                
                ###########################################################

            except Exception:
                local_addr = None
                peer_addr = None

            return TCPConnectResult(
                ip=ip, port=port, connect_ms=ms,
                local_addr=local_addr, peer_addr=peer_addr,
                error=None, sock=sock
            )
        last_err = err

    return TCPConnectResult(
        ip=ordered[-1] if ordered else None,
        port=port,
        connect_ms=None,
        local_addr=None,
        peer_addr=None,
        error=last_err or "All connections failed",
        sock=None
    )