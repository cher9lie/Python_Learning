while True:
    user_input = input("请输入一个正整数 n（输入 q 退出）：").strip()
    if user_input.lower() == 'q':
        print("程序已退出。")
        break
        
    try:
        n = int(user_input)
        if n < 1:
            print(" 逻辑错误！请输入大于 0 的正整数。\n")
            continue
            
        total_sum = sum(range(1, n + 1))
        print(f" 1 到 {n} 的和为：{total_sum}\n")
    except ValueError:
        print(" 输入无效！请确保输入的是纯数字。\n")