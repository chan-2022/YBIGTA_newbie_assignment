# Report

## 1. 개요 및 모델 선정 (Overview & Model Selection)

본 실험은 당초 Llama-3-8B 모델을 타겟으로 기획되었으나, 실험 환경의 변화로 **Llama-3.1-8B-Instant**를 사용하여 진행하였다.

### 1.1. Official Benchmark Comparison (Reference : Meta AI)
아래 표는 Meta AI에서 공개한 공식 벤치마크 데이터 중, 본 실험과 관련된 수학 및 추론 지표를 비교한 것이다.

| Category | Benchmark | Llama 3 8B | **Llama 3.1 8B** | Improvement |
| :--- | :--- | :---: | :---: | :---: |
| **Math** | **GSM-8K (CoT)-8shot** | 80.6 | **84.5** | **+3.9%** |
| | MATH (CoT) | 29.1 | **51.9** | +22.8% |
| **Reasoning** | ARC-C | 82.4 | **83.4** | +1.0% |

> **모델 비교:**
> Llama-3.1은 수학 성능(MATH +22.8%)이 비약적으로 향상된 모델이다. 
---

## 2. 실험 결과 (Experimental Results)

Direct Prompting, CoT(Chain of Thought) Prompting, 그리고 제안하는 **My Prompting** 기법을 0-shot, 3-shot, 5-shot 환경에서 비교 실험한 결과는 다음과 같다.

| Method | 0-shot | 3-shot | 5-shot | Average |
| :--- | :---: | :---: | :---: | :---: |
| **Direct Prompting** | 82.0% | 74.0% | 72.0% | 76.0% |
| **CoT Prompting** | 80.0% | 70.0% | 76.0% | 75.3% |
| **My Prompting** | **84.0%** | **84.0%** | **82.0%** | **83.3%** |

> **요약:** Baseline(Direct/CoT)은 Shot 수가 늘어날수록 오히려 성능이 하락하거나 불안정한 모습을 보였으나, **My Prompting은 전 구간에서 82% 이상을 기록하며 평균 83.3%의 가장 우수한 성능을 달성**하였다.

---

## 3. 이론 vs 실제 : Direct Prompting vs CoT Prompting 

### 3.1 이론적으로 무엇이 더 우수한가? 
이론적으로는 CoT Prompting이 Direct Prompting보다 우수한 것으로 알려져 있다. 그 이유는 다음과 같다. 
1.  **문제 분해:** 복잡한 수학 문제를 "Think step by step" 지시를 통해 작은 논리 단계로 나누어 해결한다.
2.  **오류 수정:** 중간 추론 과정을 통해 논리적 비약을 방지하고 스스로 검증할 기회를 갖는다.


### 3.2 실제 실험 결과 비교 
하지만 표를 참고하면, 0,3shot에서 Direct Prompting의 결과가 더 우수했다. 그 이유를 간접적으로 추론하면 다음과 같다. 
1. **Over-Reasoning** : Direct Prompting의 결과가 이미 좋다. 직관적인 문제 해결 능력이 뛰어나다는 것인데, 여기서 추론과정을 또 추가하는 것이 불필요한 연산 과정을 유발하여 오답률을 높인 것으로 보인다. 
2. **Context Dilution** : 경량 모델이 핵심 지시사항보다 예시의 Noise에 주의를 뺏긴 것으로 보인다. 


---

## 4. 제안 전략: My Prompting

본 실험에서 `My Prompting`은 CoT 대비 압도적인 성능을 기록했다. 이를 달성하기 위해 적용한 핵심 전략은 다음과 같다.

```python
# System Instruction
prompt = (
    "Instruction:\n"
    "You are a math expert. Solve the problem step-by-step logically.\n"
    "The last line of your response MUST be the final answer in double brackets: [[NUMBER]].\n"
    "Do not write anything after the brackets.\n\n"
)

```

### 4.1 정보 밀도 최적화 
기존 CoT에서 성능 하락의 원인을 불필요하게 긴 예시로 인한 주의 분산으로 판단했다. 이를 위해 길이가 짧고 논리 구조가 명확한 예시를 선별하여 사용했다. 이는 모델이 긴 텍스트를 처리하며 발생하는 부하를 줄이고 핵심 논리에 집중하도록 한다. 

### 4.2 답의 포맷 강제
My Prompting은 프롬프트를 통해 답변의 형식을 강제하였다. 이는 채점 시스템이 정답을 정확하게 추출할 수 있도록 한다. 

### 4.3 인지 부하 감소 
앞서 Direct, CoT Prompting을 통해 복잡한 instruction보다 간단하면서도 명료한 Prompting이 효과적이라 판단하였다. 이에 역할을 추가하고, 간단하게 "logically"라는 단어를 추가하여 모델이 논리적으로 생각할 수 있도록 하였다. 


## 5. 결론 
본 실험을 통해 얻은 결론은 다음과 같다. 

1. 모델의 사이즈와 특성을 고려하여 예시의 주입 방식을 설계한다.
2. 출력 포맷을 엄격하게 표준화한다. 

1, 2를 고려하여 만든 My Prompting은 0,3shot 만으로도 Meta의 공식 벤치마크(8shot) 수준인 84%를 달성하여, 효율적인 프롬프트 엔지니어링의 중요성을 확인할 수 있었다. 

