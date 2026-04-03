import numpy as np

#注意 pip install numpy

def process_temperature_data(data):
    """
    处理城市气温数据：按省份分类、计算省份均温、筛选高于全国均温的城市。
    """
    # 校验输入数据是否为有效的列表
    if not isinstance(data, list) or len(data) == 0:
        print("错误：输入数据无效或为空，请检查数据源。")
        return None, None, None, None

    # 1：使用字典按省份分类存储
    province_cities = {}
    all_temps = [] 

    for item in data:
        # 校验单条数据格式是否为长度为3的元组
        if not isinstance(item, tuple) or len(item) != 3:
            print(f" 警告：跳过格式不正确的数据 -> {item}")
            continue
            
        city, province, temp = item
        
        # 如果省份还不在字典中，先初始化一个空列表
        if province not in province_cities:
            province_cities[province] = []
            
        province_cities[province].append((city, temp))
        all_temps.append(temp)

    # 任务 2：计算每个省份的平均气温
    province_avg_temp = {}
    for province, city_list in province_cities.items():
        # 提取该省份下所有城市的气温
        temps = [t for c, t in city_list]
        # 使用 numpy 计算均值，保留1位小数
        province_avg_temp[province] = round(np.mean(temps), 1)

    # 任务 3：找出气温高于全国平均气温的城市，存入集合(set)
    hot_cities = set()
    national_avg = 0
    
    if all_temps:
        national_avg = np.mean(all_temps)
        for item in data:
            if isinstance(item, tuple) and len(item) == 3:
                city, _, temp = item
                if temp > national_avg:
                    hot_cities.add(city) 

    return province_cities, province_avg_temp, hot_cities, national_avg


if __name__ == "__main__":
    # PPT 中提供的原始数据
    temperature_data = [
        ("北京", "北京", 33), ("天津", "天津", 34), ("石家庄", "河北", 38), ("保定", "河北", 36),
        ("唐山", "河北", 35), ("太原", "山西", 31), ("大同", "山西", 29), ("临汾", "山西", 33),
        ("呼和浩特", "内蒙古", 30), ("包头", "内蒙古", 32), ("沈阳", "辽宁", 35), ("大连", "辽宁", 32),
        ("锦州", "辽宁", 34), ("长春", "吉林", 30), ("吉林市", "吉林", 29), ("哈尔滨", "黑龙江", 28)
    ]

    try:
        # 调用核心处理函数
        p_cities, p_avg, h_cities, n_avg = process_temperature_data(temperature_data)

        if p_cities is not None:

            print("按省份分类的城市气温数据 (字典)：")
            for prov, cities in p_cities.items():
                print(f"   {prov}: {cities}")
                
            print("各省份平均气温 (字典)：")
            for prov, avg in p_avg.items():
                print(f"   {prov}: {avg}℃")
                
            print(f"全国平均气温计算结果: {n_avg:.2f}℃")
            print("   气温高于全国均温的城市 (集合 Set)：")
            print(f"   {h_cities}")
     
    except Exception as e:
        # 兜底异常捕获
        print(f"程序运行时发生意外错误: {e}")