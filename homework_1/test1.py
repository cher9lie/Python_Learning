while True:
    user_input = input("请输入一个整数（输入 q 退出）：").strip()
    if user_input.lower() == 'q':
        print("程序已退出。")
        break
        
    try:
        num = int(user_input)
        if num % 2 == 0:
            print(f" {num} 是一个偶数\n")
        else:
            print(f" {num} 是一个奇数\n")
    except ValueError:
        print("输入无效！请确保您输入的是一个纯数字的整数。\n")