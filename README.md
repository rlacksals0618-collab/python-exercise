# Python Exercise

파이썬 기초 문법을 연습한 예제 모음입니다.

## 실행 방법

```bash
cd intro
python intro.py
python operators.py
```

## 파일 설명

### [intro/intro.py](intro/intro.py)
변수와 `print` 출력을 연습합니다.

- `name`, `age` 변수에 값을 저장
- 변수 출력과 문자열 출력(`"name"`)의 차이
- f-string으로 변수를 문장 안에 넣기

```python
print(f"안녕하세요, {age}세 {name}")   # 안녕하세요, 30세 민수
```

### [intro/operators.py](intro/operators.py)
파이썬의 기본 연산자를 연습합니다. 줄마다 주석으로 계산 과정과 결과를 적어 두었습니다.

| 구분 | 연산 | 예시 |
|---|---|---|
| 사칙연산 | `+` `-` `*` `/` | `48 / 8` → `6.0` |
| 몫과 나머지 | `//` `%` | `6 // 4` → `1`, `6 % 4` → `2` |
| 괄호 연산 | `( )` | `2 + 3 * 4` → `14`, `(2 + 3) * 4` → `20` |
| 삼항 연산자 | `A if 조건 else B` | `"합격" if score >= 60 else "불합격"` |
| 거듭제곱 | `**`, `pow()` | `3 ** 2` → `9`, `pow(2, 10)` → `1024` |
| 제곱근 | `math.sqrt()`, `** 0.5` | `math.sqrt(16)` → `4.0` |

참고:
- `/`로 나누면 결과는 항상 실수입니다. 정수가 필요하면 `int()`나 `//`를 사용합니다.
- `math.sqrt()`를 쓰려면 `import math`가 필요합니다.
