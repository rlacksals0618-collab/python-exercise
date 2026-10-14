scores = [90, 25, 67, 45, 80]

for score in scores:
    # score는 리스트 전체가 아니라 이번에 꺼낸 숫자 하나입니다.
    if score >= 60:
        print(score, "합격")
    else:
        print(score, "불합격")
print("판정 끝")           
 # 들여쓰기가 없으므로 반복 종료 후 한 번 실행합니다.
 # 점수를 도출해서 합격과 불합격을 가린다.