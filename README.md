# 🌐 Network Basics Assignment

이 과제는 네트워크 기초 개념 **(DNS → TCP → HTTP)** 을  
**Python 표준 라이브러리만 사용하여 직접 구현**하는 과제입니다.

실습에서 네트워크 요청 흐름을 *관찰*했다면,  
이 과제에서는 그 흐름을 **코드로 재현하고 실행 결과를 기록**합니다.

---

## 🎯 과제 목표

- 도메인 이름이 IP 주소로 변환되는 과정 이해 (DNS)
- TCP 연결 성립 및 실패 처리
- 여러 IP 중 하나를 선택해 연결하는 로직 구현
- HTTP 요청이 TCP 위에서 동작함을 최소 수준으로 확인
- 성공/실패 여부와 관계없이 실행 결과를 JSON으로 저장

---

## 📁 프로젝트 구조

```text
network_assignment/
  README.md
  netprobe/
    __init__.py
    main.py     # 전체 흐름 orchestration
    dns.py      # DNS 해석 (TODO)
    tcp.py      # TCP 연결 + fallback (TODO)
    http.py     # HTTP 최소 구현 (TODO 일부)
    report.py   # 출력/JSON 저장 (제공)
  tests/
    test_dns.py
    test_tcp.py
    test_http.py
```

---

## ▶️ 실행 방법

### 1️⃣ 정상 실행 (성공 케이스)

```bash
python -m netprobe http://google.com --pretty --json results/google.json
```

- DNS → TCP → HTTP 단계가 모두 성공
- `results/google.json` 파일 생성
- JSON의 `stage` 값은 `"ok"`

---

### 2️⃣ 실패 케이스 만들기 (TCP 실패)

아래 명령은 **의도적으로 TCP 연결 실패**를 발생시킵니다.

```bash
python -m netprobe http://google.com:81 --pretty --json results/tcp_fail.json
```

- DNS는 성공
- TCP 단계에서 통신이 정상적으로 이루어지지 않음 (환경에 따라 즉시 실패 또는 timeout)
- 프로그램은 크래시 없이 종료
- `results/tcp_fail.json` 파일 생성
- JSON의 `stage` 값은 `"tcp"`

---

### 3️⃣ 실패 케이스 만들기 (DNS 실패)

```bash
python -m netprobe http://this-domain-should-not-exist.example --pretty --json results/dns_fail.json
```

- DNS 해석 실패
- TCP / HTTP 단계는 실행되지 않음
- `results/dns_fail.json` 파일 생성
- JSON의 `stage` 값은 `"dns"`

---

## 📦 산출물 (제출물)

모든 실행 결과는 **성공/실패 여부와 관계없이 JSON 파일로 저장**해야 합니다.

```text
results/
  google.json      # 성공 케이스
  tcp_fail.json    # TCP 실패 케이스
  dns_fail.json    # DNS 실패 케이스
```

---

## 📝 JSON 저장 규칙

- 실행 결과는 **항상 JSON 파일로 저장**해야 합니다.
- 실패한 경우에도 JSON 파일을 반드시 생성해야 합니다.

### 실패 시 필수 필드

- `stage`: 실패한 단계 (`dns`, `tcp`, `http`)
- `error`: 오류 원인 문자열

### 성공 시

- `stage` 값은 `"ok"`

#### 실패 JSON 예시 (TCP 실패)

```json
{
  "url": "http://google.com:81",
  "stage": "tcp",
  "error": "Connection refused",
  "dns_ips": ["142.250.xxx.xxx"],
  "chosen_ip": "142.250.xxx.xxx"
}
```

---

## 🧪 테스트 실행

```bash
pytest
```

또는

```bash
pytest tests/test_dns.py
pytest tests/test_tcp.py
pytest tests/test_http.py
```

- 모든 테스트는 반드시 통과해야 합니다.

---

## ✅ 과제 통과 요건

아래 조건을 **모두 만족해야 과제로 인정됩니다.**

### 1️⃣ 테스트 통과
- `python -m pytest` 실행 시 **모든 테스트가 성공**해야 함

### 2️⃣ 결과 파일 생성
- `results/` 폴더에 아래 JSON 파일이 **모두 존재**해야 함

```text
results/
  google.json    # stage = "ok"
  tcp_fail.json  # stage = "tcp"
  dns_fail.json  # stage = "dns"
```

### 3️⃣ JSON 내용 검증
- 각 JSON 파일의 `stage` 값은 **실행 결과와 반드시 일치**해야 함
  - 성공 케이스 → `"ok"`
  - DNS 실패 → `"dns"`
  - TCP 실패 → `"tcp"`

---

## 🚫 주의 사항

- `requests`, `http.client` 등 **고수준 네트워크 라이브러리 사용 금지**
- **Python 표준 라이브러리만 사용**
- 네트워크 환경(OS, IPv4/IPv6)에 따라 실행 결과는 달라질 수 있음