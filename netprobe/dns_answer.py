from __future__ import annotations

import socket
from typing import Optional


def resolve(host: str) -> tuple[list[str], Optional[str]]:

    try:
        infos = socket.getaddrinfo(host, None, proto=socket.IPPROTO_TCP)
        ips: list[str] = [sockaddr[0] for _, _, _, _, sockaddr in infos]
        return ips, None
    except Exception as e:
        return [], str(e)


def pick_ip(ips: list[str], prefer: str = "any") -> Optional[str]:

    if not ips:
        return None

    if prefer == "any":
        return ips[0]

    if prefer == "ipv4":
        for ip in ips:
            if ":" not in ip:
                return ip
        return ips[0]

    if prefer == "ipv6":
        for ip in ips:
            if ":" in ip:
                return ip
        return ips[0]

    return ips[0]
