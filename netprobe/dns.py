from __future__ import annotations

import socket
from typing import Optional


def resolve(host: str) -> tuple[list[str], Optional[str]]:
    """
    도메인 이름을 IP 주소 리스트로 변환합니다.
    """
    try:
        infos = socket.getaddrinfo(host, None, proto=socket.IPPROTO_TCP)
        
        ###########################################################
        # TODO: sockaddr에서 IP 주소만 추출하여 리스트(ips)로 만드세요.
        # HINT: 리스트 컴프리헨션을 사용하여 sockaddr[0] 값을 가져오세요.

        ips = [] # TODO: [이곳에 IP 리스트 생성 코드를 작성하세요]

        ###########################################################

        return ips, None
    except Exception as e:
        return [], str(e)


def pick_ip(ips: list[str], prefer: str = "any") -> Optional[str]:
    """
    prefer 정책에 따라 리스트에서 가장 적절한 IP 하나를 선택합니다.
    """
    if not ips:
        return None

    if prefer == "any":
        return ips[0]

    ###########################################################
    # TODO: prefer 값(ipv4, ipv6)에 따라 적절한 IP를 반환하는 로직을 작성하세요.
    # - 'ipv4': ':'이 없는 주소 우선
    # - 'ipv6': ':'이 있는 주소 우선
    # HINT: Python의 'in' 혹은 'not in' 연산자로 ':' 포함 여부를 확인하세요.

    if prefer == "ipv4":
        pass #TODO

    elif prefer == "ipv6":
        pass #TODO

    ###########################################################

    return ips[0]