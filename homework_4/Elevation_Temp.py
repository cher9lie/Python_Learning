# 注意提前 conda activate gis_env
# 注意安装pip install xarray rasterio numpy matplotlib scipy

print("=== 核心引擎启动，代码开始执行 ===")
print("准备引入 xarray...")
import xarray as xr
print("准备引入 rasterio...")
import rasterio
print("准备引入 numpy...")
import numpy as np
print("准备引入 matplotlib...")
import matplotlib
matplotlib.use('Agg') # 强制使用纯净的 Agg 后端，不调用任何弹窗组件
import matplotlib.pyplot as plt
print("准备引入 scipy...")
from scipy.ndimage import zoom

# 解决 Matplotlib 中文显示问题 (Windows 系统默认使用黑体)
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# ================= 1. 读取气温数据 =================
# 注意：假设 monthlyTPR1982-2020 文件夹内的文件名为 download.nc，请根据实际文件名修改
print("1. 开始读取气温数据...")
nc_file = r"D:\260414data\Raster\monthlyTPR1982-2020\download.nc" 
ds = xr.open_dataset(nc_file)

# 提取1982年1月的数据 (time=0)，并将开尔文转换为摄氏度
temp_1982_01 = ds['t2m'].isel(time=0).values - 273.15 
target_shape = temp_1982_01.shape

# ================= 2. 读取DEM数据并重采样 =================
# 指向无后缀的 DEM 文件，rasterio 会自动寻找同名的 .hdr 头文件
print("2. 开始读取并重采样DEM数据 (这步计算量较大，请稍等)...")
dem_file = r"D:\260414data\Raster\DEM" 
with rasterio.open(dem_file) as src:
    dem_data = src.read(1)
    
# 计算缩放比例并进行重采样
zoom_factors = (target_shape[0] / dem_data.shape[0], target_shape[1] / dem_data.shape[1])
dem_resampled = zoom(dem_data, zoom_factors, order=0) 

# ================= 3. 海拔分段与统计 (增加标准差) =================
# 将区间分得更细
bins = [-np.inf, 200, 500, 1000, 1500, 2000, 3000, 4000, np.inf]
bin_labels = ['<200m', '200-500m', '500-1000m', '1000-1500m', '1500-2000m', '2000-3000m', '3000-4000m', '>4000m']

# 将连续高程转化为离散的区间索引
dem_binned = np.digitize(dem_resampled, bins)

avg_temps = {}
std_temps = {}  # 新增：用于存放标准差，构建误差棒

for i, label in enumerate(bin_labels):
    class_val = i + 1 
    mask = (dem_binned == class_val) & (~np.isnan(temp_1982_01))
    
    if np.any(mask):
        avg_temps[label] = np.mean(temp_1982_01[mask])
        std_temps[label] = np.std(temp_1982_01[mask]) # 计算该区间的空间标准差
    else:
        avg_temps[label] = np.nan
        std_temps[label] = np.nan

# ================= 4. 可视化出图 (学术级精调) =================
print("4. 正在生成并保存高精度学术图表...")

labels = list(avg_temps.keys())
values = list(avg_temps.values())
errors = list(std_temps.values())

# 创建更大尺寸的画布，留出足够空间
plt.figure(figsize=(12, 7))

# 画柱状图，加入 yerr 参数生成误差棒，zorder=3 确保柱子和误差棒在网格线之上
bars = plt.bar(labels, values, yerr=errors, capsize=5, 
               color='#4a90e2', edgecolor='black', linewidth=1.2, 
               error_kw={'elinewidth': 1.5, 'ecolor': '#333333'}, zorder=3)

# 设置加粗的坐标轴标签
plt.xlabel("海拔区间 (m)", fontsize=12, fontweight='bold')
plt.ylabel("平均气温 (°C)", fontsize=12, fontweight='bold')
plt.title("不同海拔区间 1982年1月 平均气温", fontsize=15, pad=15)

# 学术风网格：只保留横向虚线，并置于底层 (zorder=0)
plt.grid(axis='y', linestyle='--', alpha=0.6, zorder=0)

# 解决重叠问题一：X轴标签倾斜 45 度，防止区间分细后文字横向拥挤
plt.xticks(rotation=45, ha='right', fontsize=10)

# 解决重叠问题二：动态拓展 Y 轴的上下边界，给顶部/底部的文字留出“呼吸空间”
y_min = min(v - e for v, e in zip(values, errors) if not np.isnan(v))
y_max = max(v + e for v, e in zip(values, errors) if not np.isnan(v))
plt.ylim(y_min - 4, y_max + 4) # 在极端值之外额外增加 4°C 的空白范围

# 重新计算并添加数值标签
for bar, err in zip(bars, errors):
    yval = bar.get_height()
    if not np.isnan(yval):
        # 标签放置在误差棒的最外侧，避免与线条重叠
        offset = err + 0.8 if yval > 0 else -(err + 0.8)
        va = 'bottom' if yval > 0 else 'top'
        
        plt.text(bar.get_x() + bar.get_width()/2, yval + offset, 
                 f'{yval:.1f}', ha='center', va=va, fontsize=10, fontweight='bold', color='#2c3e50')

# 紧凑布局，防止坐标轴标签被裁切
plt.tight_layout()

# 保存高质量图片 (增加 bbox_inches='tight' 完美裁切白边)
plt.savefig(r"D:\260414data\Elevation_Temp_Bar_198201_Pro.png", dpi=300, bbox_inches='tight')

print("5. === 图片保存完毕，请去文件夹查看 Elevation_Temp_Bar_198201_Pro.png ===")