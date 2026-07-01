import xarray as xr
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import zoom

# 解决 Matplotlib 中文显示问题 (Windows 系统默认使用黑体)
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# ================= 1. 读取气温数据 =================
# 注意：假设 monthlyTPR1982-2020 文件夹内的文件名为 download.nc，请根据实际文件名修改
nc_file = r"D:\260414data\Raster\monthlyTPR1982-2020\download.nc" 
ds = xr.open_dataset(nc_file)

# 提取1982年1月的数据 (time=0)，并将开尔文转换为摄氏度
temp_1982_01 = ds['t2m'].isel(time=0).values - 273.15 
target_shape = temp_1982_01.shape

# ================= 2. 读取DEM数据并重采样 =================
# 指向无后缀的 DEM 文件，rasterio 会自动寻找同名的 .hdr 头文件
dem_file = r"D:\260414data\Raster\DEM" 
with rasterio.open(dem_file) as src:
    dem_data = src.read(1)
    
# 计算缩放比例并进行重采样
zoom_factors = (target_shape[0] / dem_data.shape[0], target_shape[1] / dem_data.shape[1])
dem_resampled = zoom(dem_data, zoom_factors, order=0) 

# ================= 3. 海拔分段与统计 =================
# 定义海拔分段区间 (单位：米)
bins = [-np.inf, 500, 1000, 2000, 3000, 4000, np.inf]
bin_labels = ['<500m', '500-1000m', '1000-2000m', '2000-3000m', '3000-4000m', '>4000m']

# 将连续高程转化为离散的区间索引
dem_binned = np.digitize(dem_resampled, bins)

avg_temps = {}
for i, label in enumerate(bin_labels):
    class_val = i + 1 # digitize 返回的索引从 1 开始
    
    # 掩膜提取：要求对应海拔段，且气温数据不为 NaN
    mask = (dem_binned == class_val) & (~np.isnan(temp_1982_01))
    
    if np.any(mask):
        avg_temps[label] = np.mean(temp_1982_01[mask])
    else:
        avg_temps[label] = np.nan

# ================= 4. 可视化出图 =================
labels = list(avg_temps.keys())
values = list(avg_temps.values())

plt.figure(figsize=(10, 6))
bars = plt.bar(labels, values, color='cornflowerblue', edgecolor='black')
plt.xlabel("海拔区间")
plt.ylabel("平均气温 (°C)")
plt.title("不同海拔区间 1982年1月 平均气温")
plt.grid(axis='y', linestyle='--', alpha=0.6)

# 在柱子上添加数值标签
for bar in bars:
    yval = bar.get_height()
    if not np.isnan(yval):
        # 处理正负值标签的位置
        offset = 0.5 if yval > 0 else -1.5
        va = 'bottom' if yval > 0 else 'top'
        plt.text(bar.get_x() + bar.get_width()/2, yval + offset, 
                 f'{yval:.1f}', ha='center', va=va, fontsize=10)

plt.tight_layout()
# 将图片保存在数据根目录下
plt.savefig(r"D:\260414data\Elevation_Temp_Bar_198201.png", dpi=300)
plt.show()