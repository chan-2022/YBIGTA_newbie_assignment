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
    try:
        s = _make_socket(ip, timeout)
        start = time.perf_counter()
        s.connect((ip, port))
        ms = (time.perf_counter() - start) * 1000.0
        return s, ms, None
    except Exception as e:
        try:
            s.close()
        except Exception:
            pass
        return None, None, str(e)


def connect_with_fallback(ips: list[str], port: int, timeout: float, prefer: str = "any") -> TCPConnectResult:

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
                local = sock.getsockname()
                peer = sock.getpeername()
                local_addr = (str(local[0]), int(local[1]))
                peer_addr = (str(peer[0]), int(peer[1]))
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
