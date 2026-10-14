raw = "  START  "
# 양끝 공백이 보이도록 출력에서 대괄호를 둘러줍니다.

print(f"원본: [{raw}]")
trimmed = raw.strip()
print(f"공백 제거: [{trimmed}]")
command = trimmed.lower()
print(f"소문자: [{command}]")
#문자열 양옆의 공백을 제거하고 대문자를 소문자로 바꾼다.