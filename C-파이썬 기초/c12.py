numbers = [4, 5, 7]
total = 0
high_count = 0
for number in numbers:
    total = total + number
    print("현재 합계:", total)
    if number >= 5:
        high_count = high_count + 1
print("5 이상 개수:", high_count)
# total = 0을 반복 안에 두면 이전 합계가 매번 사라집니다.