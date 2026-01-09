# lib.py의 Matrix 클래스를 참조하지 않음
import sys


"""
TODO:
- fast_power 구현하기 
"""


def fast_power(base: int, exp: int, mod: int) -> int:
    """
    - (A*B) mod c = (A mod c) * (B mod c) 이용
    - base를 먼저 mod로 나눠주고 
    - exp를 2로 나눠 가면서 필요한 항만 곱한다. 
    
    """
    # 구현하세요!
    result=1
    base = base % mod
    while exp>0:
        if exp % 2 ==1:
            result = (result * base) % mod
        base = (base*base) % mod
        exp //=2
    return result


def main() -> None:
    A: int
    B: int
    C: int
    A, B, C = map(int, input().split()) # 입력 고정
    
    result: int = fast_power(A, B, C) # 출력 형식
    print(result) 

if __name__ == "__main__":
    main()
