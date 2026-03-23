while True:
    # 1. 获取并校验站数
    stops_input = input("请输入乘坐的站数（输入 q 退出）：").strip()
    if stops_input.lower() == 'q':
        print("程序已退出。")
        break
        
    try:
        stops = int(stops_input)
        if stops < 1:
            print(" 站数必须大于等于 1，请重新输入。\n")
            continue
            
        # 2. 获取并校验学生身份
        while True:
            is_student = input("是否为学生？(yes/no)：").strip().lower()
            if is_student in ['yes', 'no']:
                break
            print(" 识别失败！只能输入 yes 或 no，请重新输入。\n")
            
        # 3. 计价逻辑
        if stops <= 3:
            price = 10
        else:
            price = 10 + (stops - 3) * 2
            
        if is_student == "yes":
            price *= 0.8
            
        print(f"您的总金额为：{round(price, 1)} 元\n")
        
    except ValueError:
        print(" 输入无效！站数必须是纯数字整数。\n")