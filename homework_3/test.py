class City:
    """城市类：表示地图上的点状或面状地理要素"""
    
    def __init__(self, name, population, area):
        self.name = name
        self.population = population  # 单位：万人
        self.area = area              # 单位：平方公里
        
    def displayInfo(self):
        """打印城市的详细信息"""
        print(f"🏙️ [城市信息] 名称: {self.name} | 人口: {self.population} 万 | 面积: {self.area} km²")


class River:
    """河流类：表示地图上的线状地理要素"""
    
    def __init__(self, name, length):
        self.name = name
        self.length = length          # 单位：公里
        self.cities = []              # 提示：初始化一个空的 City 对象列表
        
    def add_city(self, city_obj):
        """稳健性设计：提供专门的方法添加流经城市，并校验类型"""
        if isinstance(city_obj, City):
            self.cities.append(city_obj)
        else:
            print(f"⚠️ 警告：无法添加 '{city_obj}'，它不是一个有效的 City 对象！")

    def displayInfo(self):
        """打印河流详细信息、流经城市及总人口统计"""
        print("-" * 50)
        print(f"🌊 [河流信息] 名称: {self.name} | 长度: {self.length} km")
        
        # 稳健性设计：处理河流没有流经任何城市的情况
        if not self.cities:
            print("   └─ 该河流目前没有记录流经的城市。")
            print("-" * 50)
            return

        # 提取所有城市的名称，并计算总人口
        city_names = [city.name for city in self.cities]
        total_population = sum(city.population for city in self.cities)
        
        print(f"   ├─ 流经的城市 ({len(self.cities)} 个): {', '.join(city_names)}")
        print(f"   └─ 沿线城市总人口统计: {total_population} 万")
        print("-" * 50)


if __name__ == "__main__":
    try:
        # 1. 实例化多个 City 对象
        wuhan = City("武汉", 1373, 8569)
        nanjing = City("南京", 1370, 6587)
        shanghai = City("上海", 948, 6340)
        lanzhou = City("兰州", 441, 13100) # 这里用到了之前实践去过的兰州哦
        
        # 2. 验证 City 的 displayInfo 方法
        wuhan.displayInfo()
        lanzhou.displayInfo()
        
        print("\n" + "="*50 + "\n")
        
        # 3. 实例化 River 对象并添加流经城市
        yangtze_river = River("长江", 6300)
        yellow_river = River("黄河", 5464)
        
        # 长江流经城市组合
        yangtze_river.add_city(wuhan)
        yangtze_river.add_city(nanjing)
        yangtze_river.add_city(shanghai)
        
        # 黄河流经城市组合
        yellow_river.add_city(lanzhou)
        
        # 4. 测试错误的数据录入 (防错机制测试)
        yangtze_river.add_city("一段字符串而不是对象")
        
        # 5. 验证 River 的 displayInfo 综合统计方法
        yangtze_river.displayInfo()
        yellow_river.displayInfo()

    except Exception as e:
        print(f"❌ 程序运行时发生致命错误: {e}")