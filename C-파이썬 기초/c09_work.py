hour =int(input("입력하시오: ")) #숫자를 입력받고 그것을 정수로 변환
pay=10000

if hour < 0:
 print("입력수치 오류")
elif hour > 40: # 시간이 40시간 이상이면 급여를 1.5배로 계산합니다.
    money=1.5*pay*(hour-40)+pay*40
    money=int(money)
    print(money, "원")
else:
    money=pay*hour
    print(money, "원")
# 업무시간을 입력하면 급여가 얼마인지 판정합니다.