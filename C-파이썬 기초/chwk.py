height =int(input("입력하시오: ")) #height는 트리의 높이
wide=2*height-1 #wide는 트리 아랫면의 너비

for number in range(1,height+1):
    vacant=height-number #빈 공간의 숫자 지정
    parts=2*number-1 #중간 트리 부분의 숫자 지정
    print(" "*vacant, end="") #왼쪽 빈 공간 생성
    print("*"*parts, end="") #중앙 트리부분 생성
    print(" "*vacant, end="") #오른쪽 빈 공간 생성
    print("") #줄 띄움

print(" "*(height-1), end="") #줄기 왼쪽 빈 공간 생성
print("I") #줄기 생성
#크리스마스 트리를 입력한 높이에 맞춰서 만든다.