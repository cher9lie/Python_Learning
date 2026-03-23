import random

answer = random.randint(1, 10)
is_guessed = False
attempts = 0

print("---  猜数字游戏开始（1-10，共 5 次机会） ---")

while attempts < 5:
    user_input = input(f"第 {attempts + 1} 次机会，请猜一个数字：").strip()
    
    try:
        guess = int(user_input)
        if guess < 1 or guess > 10:
            print(" 输入无效！请输入 1 到 10 范围内的数字。\n")
            continue  # 输入越界，不扣除次数
            
        attempts += 1 # 只有输入合法时，才扣除次数
        
        if guess == answer:
            print(" 恭喜你，猜对了！\n")
            is_guessed = True
            break
        elif guess > answer:
            print("猜大了~\n")
        else:
            print("猜小了~\n")
            
    except ValueError:
        print(" 输入无效！请输入一个纯数字。\n")

if not is_guessed:
    print(f" 5 次机会用完啦，正确答案是：{answer}\n")