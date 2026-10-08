import math  # 제곱근(sqrt) 같은 수학 함수를 쓰기 위해 불러온다

# ===== 1. 기본 사칙연산 =====
stock = 10
print("시작 재고:", stock)

stock = stock + 5       # 더하기: 10 + 5
print("더하기 후:", stock)

stock = stock - 3       # 빼기: 15 - 3
print("빼기 후:", stock)

stock = stock * 4       # 곱하기: 12 * 4
print("곱하기 후:", stock)

stock = stock / 8       # 나누기: 48 / 8 (결과는 항상 실수 → 6.0)
print("나누기 후:", stock)

stock = int(stock)      # int()로 정수로 바꿔서 소수점 제거 → 6
print("정수로 변환:", stock)

# 몫과 나머지
boxes = stock // 4      # 몫: 6을 4로 나눈 몫 → 1
remain = stock % 4      # 나머지: 6을 4로 나눈 나머지 → 2
print("상자 수(몫):", boxes)
print("남은 개수(나머지):", remain)

# ===== 2. 괄호 연산 (연산 순서) =====
a = 2 + 3 * 4           # 곱하기가 먼저 계산됨: 2 + 12 → 14
b = (2 + 3) * 4         # 괄호 안이 먼저 계산됨: 5 * 4 → 20
print("괄호 없음:", a)
print("괄호 있음:", b)

price = 1000
count = 3
discount = 500
total = (price * count) - discount   # (1000 * 3) - 500 → 2500
print("할인 후 총액:", total)

# ===== 3. 삼항 연산자 =====
# 형식: 참일_때_값 if 조건 else 거짓일_때_값
status = "재고 충분" if stock >= 5 else "재고 부족"
print("재고 상태:", status)

score = 72
result = "합격" if score >= 60 else "불합격"
print("시험 결과:", result)

# ===== 4. 거듭제곱 =====
x = 3
print("3의 제곱:", x ** 2)          # ** 연산자: 3 * 3 → 9
print("3의 세제곱:", x ** 3)        # 3 * 3 * 3 → 27
print("2의 10제곱:", pow(2, 10))    # pow(밑, 지수) 함수 → 1024

# ===== 5. 제곱근 =====
y = 16
print("16의 제곱근(math.sqrt):", math.sqrt(y))   # math.sqrt() → 4.0
print("16의 제곱근(** 0.5):", y ** 0.5)          # 0.5제곱 = 제곱근 → 4.0
print("2의 제곱근:", round(math.sqrt(2), 3))     # round(값, 자릿수)로 소수점 셋째 자리까지 → 1.414
