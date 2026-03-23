while True:
    password = input("请输入密码（输入 q 退出）：").strip()
    if password.lower() == 'q':
        print("程序已退出。")
        break
        
    if not password:
        print("⚠️ 密码不能为空，请重新输入！\n")
        continue

    has_letter = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)

    if len(password) >= 8 and has_letter and has_digit:
        print(" 密码强度：强\n")
    else:
        print(" 密码强度：弱（提示：密码需包含字母和数字，且长度至少为8位）\n")