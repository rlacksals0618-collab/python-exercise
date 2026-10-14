score =int(input("입력하시오: ")) #숫자를 입력받고 그것을 정수로 변환

if score < 0 or score > 100:
    print("점수 범위 오류")
elif score == 100:
    print("Excellent!")
elif score >= 90:
    print("A")
elif score >= 80:
    print("B")
elif score >= 70:
    print("C")
elif score >= 60:
    print("D")
else:
    print("F")
# 점수를 입력하면 등급이 얼마인지 판정합니다.