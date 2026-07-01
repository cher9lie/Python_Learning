import geopandas as gpd
import rasterio
from rasterio.mask import mask
import numpy as np
import pymannkendall as mk
from shapely.geometry import mapping
import matplotlib
import matplotlib.pyplot as plt
import warnings

# 强制使用无头模式，避免 Windows 环境下绘图弹窗崩溃
matplotlib.use('Agg')
warnings.filterwarnings("ignore")
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# ================= 1. 路径设置 =================
shp_path = r"D:\260414data\Vector\World_countries_shp.shp"
# 确保文件名称匹配 2KM 版本的 TIF
tif_path = r"D:\260414data\Global_Annual_LAI_2km_2001_2020.tif"

print("1. 正在加载矢量并聚合大洲边界...")
gdf = gpd.read_file(shp_path)
continents_gdf = gdf.dissolve(by='CONTINENT').reset_index()

years = np.arange(2001, 2021)
continent_lai_ts = {}

# ================= 2. 空间提取 (带内存优化) =================
print("2. 正在读取 2KM 分辨率全球数据集进行裁切...")

with rasterio.open(tif_path) as src:
    for _, row in continents_gdf.iterrows():
        continent_name = row['CONTINENT']
        # 即使下载了全球，对于南极洲这种几乎没有 LAI 数据的区域仍建议跳过计算以节省时间
        if continent_name == 'Antarctica': continue 
        
        geom = [mapping(row['geometry'])]
        ts_means = []
        
        # 逐年(逐波段)读取，避免一次性吞噬内存
        for b in range(1, src.count + 1):
            try:
                # 只读取当前波段的裁切区域
                out_image, _ = mask(src, geom, crop=True, indexes=b)
                band_data = out_image[0]
                
                # LAI 的有效值域一般在 0~10 之间，过滤掉海洋背景的 NoData 和异常值
                valid_mask = (band_data > 0) & (band_data <= 10) & (~np.isnan(band_data))
                valid_data = band_data[valid_mask]
                
                if valid_data.size > 0:
                    ts_means.append(np.mean(valid_data))
                else:
                    ts_means.append(np.nan)
            except:
                ts_means.append(np.nan)
        
        if not np.all(np.isnan(ts_means)):
            continent_lai_ts[continent_name] = np.array(ts_means)
            print(f"   - {continent_name} 计算完成")

# ================= 3. 学术绘图与 MK 检验 =================
print("3. 正在进行时间序列分析与学术出图...")
plt.figure(figsize=(14, 8))
# 生成适配大洲数量的调色盘
colors = plt.cm.tab10(np.linspace(0, 1, len(continent_lai_ts)))

for idx, (continent, ts) in enumerate(continent_lai_ts.items()):
    # 填补可能存在的缺失值（线性插值）
    mask_nan = np.isnan(ts)
    if np.any(mask_nan):
        ts[mask_nan] = np.interp(np.flatnonzero(mask_nan), np.flatnonzero(~mask_nan), ts[~mask_nan])
    
    # Mann-Kendall 趋势检验
    mk_res = mk.original_test(ts)
    
    # 绘制实线和散点
    line, = plt.plot(years, ts, marker='s', markersize=4, label=f"{continent}", color=colors[idx])
    
    # 如果趋势通过显著性检验 (p < 0.05)，则绘制虚线趋势线
    if mk_res.p < 0.05:
        trend_line = mk_res.slope * np.arange(len(years)) + mk_res.intercept
        plt.plot(years, trend_line, linestyle='--', color=line.get_color(), alpha=0.8)
        print(f"   [显著变化] {continent}: MK斜率={mk_res.slope:.4f}, p={mk_res.p:.4f}")

# 图表排版与修饰
plt.xlabel("年份", fontsize=12, fontweight='bold')
plt.ylabel("平均叶面积指数 (LAI)", fontsize=12, fontweight='bold')
plt.title("2001-2020 全球各大洲 2KM 分辨率 LAI 演变趋势 (MK Test)", fontsize=15, pad=15)
plt.xticks(years, rotation=45)
plt.grid(True, linestyle=':', alpha=0.6)

# 将图例放在图表外部，防止遮挡折线
plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
plt.tight_layout()

# 保存高质量图片
save_path = r"D:\260414data\Continent_LAI_2km_Trend_Pro.png"
plt.savefig(save_path, dpi=300, bbox_inches='tight')

print(f"4. === 任务成功完成！请前往文件夹查看：Continent_LAI_2km_Trend_Pro.png ===")