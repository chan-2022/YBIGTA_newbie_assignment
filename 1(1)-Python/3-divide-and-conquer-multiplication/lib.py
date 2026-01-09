from __future__ import annotations
import copy


"""
TODO:
- __setitem__ 구현하기
- __pow__ 구현하기 (__matmul__을 활용해봅시다)
- __repr__ 구현하기
"""


class Matrix:
    MOD = 1000

    def __init__(self, matrix: list[list[int]]) -> None:
        self.matrix = matrix

    @staticmethod
    def full(n: int, shape: tuple[int, int]) -> Matrix:
        return Matrix([[n] * shape[1] for _ in range(shape[0])])

    @staticmethod
    def zeros(shape: tuple[int, int]) -> Matrix:
        return Matrix.full(0, shape)

    @staticmethod
    def ones(shape: tuple[int, int]) -> Matrix:
        return Matrix.full(1, shape)

    @staticmethod
    def eye(n: int) -> Matrix:
        matrix = Matrix.zeros((n, n))
        for i in range(n):
            matrix[i, i] = 1
        return matrix

    @property
    def shape(self) -> tuple[int, int]:
        return (len(self.matrix), len(self.matrix[0]))

    def clone(self) -> Matrix:
        return Matrix(copy.deepcopy(self.matrix))

    def __getitem__(self, key: tuple[int, int]) -> int:
        return self.matrix[key[0]][key[1]]

    def __setitem__(self, key: tuple[int, int], value: int) -> None:
        """
        행렬에서 입력한 위치의 값을 설정함
        value를 미리 mod로 나눠줘서 시간복잡도 최소화 
        """
        # 구현하세요!
        self.matrix[key[0]][key[1]]=value%Matrix.MOD

    def __matmul__(self, matrix: Matrix) -> Matrix:
        x, m = self.shape
        m1, y = matrix.shape
        assert m == m1

        result = self.zeros((x, y))

        for i in range(x):
            for j in range(y):
                for k in range(m):
                    result[i, j] += self[i, k] * matrix[k, j]

        return result

    def __pow__(self, n: int) -> Matrix:
        """
        1) matrix의 복제 행렬을 생성
        2) 1)에서 만든 행렬을 1000으로 나눠줌 
        3) 지수의 경우에 따라 재귀적으로 반복하여 행렬 제곱값을 구함
        """
        # 구현하세요!
        row, col = self.shape
        assert row == col 
        mat = self.clone()

        for i in range(row):
            for j in range(col):
                    mat[i,j] %= Matrix.MOD

        if n==0 : 
            return Matrix.eye(row)
        
        elif n==1:
            return mat 
        
        else: 
            tmp = mat ** (n//2)
            if n % 2 ==0: 
                return tmp @ tmp 
            
            else: 
                return (tmp @ tmp) @ mat


    def __repr__(self) -> str:
        """
        1) matrix를 행 단위로 쪼갬
        2) 각 행의 원소를 문자열로 바꾸고 공백 한칸으로 합쳐 줌 
        3) 모든 행을 줄바꿈으로 합쳐 줌
        """
        # 구현하세요!
        return "\n".join(" ".join(map(str,row)) for row in self.matrix)