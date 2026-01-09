from __future__ import annotations
import copy
from collections import deque
from collections import defaultdict
from typing import DefaultDict, List


"""
TODO:
- __init__ 구현하기
- add_edge 구현하기
- dfs 구현하기 (재귀 또는 스택 방식 선택)
- bfs 구현하기
"""


class Graph:
    def __init__(self, n: int) -> None:
        """
        그래프 초기화
        n: 정점의 개수 (1번부터 n번까지)
        """
        self.n = n
        # 구현하세요!
        self.adj_list: list[list[int]] = [[] for _ in range(n + 1)]

    
    def add_edge(self, u: int, v: int) -> None:
        """
        양방향 간선 추가
        """
        # 구현하세요!
        self.adj_list[u].append(v)
        self.adj_list[v].append(u)
    
    def dfs(self, start: int) -> list[int]:
        """
        깊이 우선 탐색 (DFS)
        
        구현 방법 선택:
        1. 재귀 방식: 함수 내부에서 재귀 함수 정의하여 구현

        - 인접 리스트를 오름차순으로 정렬한 뒤, 번호가 작은 이웃부터 방문합니다.
        - 재귀 방식으로 구현되어 있습니다.
        - 방문 여부는 visited 리스트로 관리합니다.
        """
        # 구현하세요!
        for neighbors in self.adj_list:
            neighbors.sort()

        visited = [False for i in range(self.n + 1)]
        order: list[int] = []
        def doDFS(u: int, visited: list[bool], order: list[int]) -> None:
            visited[u] = True
            order.append(u)
            for v in self.adj_list[u]:
                if not visited[v]:
                    doDFS(v, visited, order)
        doDFS(start, visited, order)
        return order
    
    def bfs(self, start: int) -> list[int]:
        """
        너비 우선 탐색 (BFS)
        큐를 사용하여 구현

        - 인접 리스트를 오름차순으로 정렬한 뒤, 번호가 작은 이웃부터 큐에 넣습니다.
        - deque 큐를 사용한 반복문 방식으로 구현되어 있습니다.
        - 방문 여부는 visited 리스트로 관리합니다.
        """
        # 구현하세요!
        for neighbors in self.adj_list:
            neighbors.sort()
            
        visited = [False for i in range(self.n + 1)]
        order: list[int] = []
        q = deque([start])
        visited[start] = True
        while q:
            u = q.popleft()
            order.append(u)
            for v in self.adj_list[u]:
                if not visited[v]:
                    visited[v] = True
                    q.append(v)
        return order
    
    def search_and_print(self, start: int) -> None:
        """
        DFS와 BFS 결과를 출력
        """
        dfs_result = self.dfs(start)
        bfs_result = self.bfs(start)
        
        print(' '.join(map(str, dfs_result)))
        print(' '.join(map(str, bfs_result)))



from typing import Callable
import sys


"""
-아무것도 수정하지 마세요!
"""


def main() -> None:
    intify: Callable[[str], list[int]] = lambda l: [*map(int, l.split())]

    lines: list[str] = sys.stdin.readlines()

    N, M, V = intify(lines[0])
    
    graph = Graph(N)  # 그래프 생성
    
    for i in range(1, M + 1): # 간선 정보 입력
        u, v = intify(lines[i])
        graph.add_edge(u, v)
    
    graph.search_and_print(V) # DFS와 BFS 수행 및 출력


if __name__ == "__main__":
    main()


