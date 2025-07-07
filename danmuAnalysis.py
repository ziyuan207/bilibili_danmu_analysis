import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 读取清洗后的数据
file_path = r'D:\数据分析\数据集\b站视频\清洗后的弹幕数据.xlsx'
df = pd.read_excel(file_path)

# 1. 弹幕时间分布分析
# 计算弹幕出现时间的基本统计量
time_stats = df['time'].describe()
print("弹幕出现时间统计:")
print(time_stats)

# 2. 时间分段分析
# 将视频时间分为多个区间
bins = np.arange(0, df['time'].max() + 30, 30)  # 每30秒一个区间
labels = [f"{int(i//60)}:{int(i%60):02d}" for i in bins[:-1]]  # 转换为分钟:秒格式

# 计算每个时间段的弹幕数量
df['time_bin'] = pd.cut(df['time'], bins=bins, labels=labels, right=False)
time_bin_counts = df['time_bin'].value_counts().sort_index()

# 3. 弹幕密度分析
# 计算每分钟弹幕数量
time_bin_counts_per_min = time_bin_counts.copy()

# 4. 弹幕累积比例分析
# 计算累积弹幕比例
cumulative_counts = time_bin_counts.cumsum()
cumulative_percentage = cumulative_counts / cumulative_counts.max() * 100

# 5. 可视化
# 创建图表
plt.figure(figsize=(16, 12))

# 图1: 弹幕数量随时间分布 (柱状图)
plt.subplot(3, 1, 1)
bars = plt.bar(time_bin_counts.index, time_bin_counts.values, color='skyblue')
plt.title('弹幕数量随时间分布 (每分钟)', fontsize=14)
plt.xlabel('视频时间 (分钟:秒)', fontsize=12)
plt.ylabel('弹幕数量', fontsize=12)
plt.xticks(rotation=45, ha='right', fontsize=10)

# 标记峰值
max_idx = time_bin_counts.idxmax()
max_val = time_bin_counts.max()
plt.annotate(f'峰值: {max_val}条',
             xy=(max_idx, max_val),
             xytext=(max_idx, max_val + max_val*0.1),
             arrowprops=dict(facecolor='red', shrink=0.05),
             fontsize=12, color='red')

plt.grid(axis='y', linestyle='--', alpha=0.7)

# 图2: 弹幕累积比例
plt.subplot(3, 1, 2)
plt.plot(cumulative_percentage.index, cumulative_percentage.values, 'g-', linewidth=2)
plt.title('弹幕累积比例', fontsize=14)
plt.xlabel('视频时间 (分钟:秒)', fontsize=12)
plt.ylabel('累积弹幕比例 (%)', fontsize=12)
plt.xticks(rotation=45, ha='right', fontsize=10)

# 标记关键点
for percent in [25, 50, 75]:
    # 找到最接近的比例点
    idx = (cumulative_percentage - percent).abs().idxmin()
    value = cumulative_percentage.loc[idx]
    plt.scatter(idx, value, color='red', s=50)
    plt.annotate(f'{percent}% 弹幕\n出现在 {idx} 前',
                 xy=(idx, value),
                 xytext=(idx, value + 5),
                 arrowprops=dict(facecolor='black', shrink=0.05),
                 fontsize=10)

plt.grid(True, linestyle='--', alpha=0.7)

# 图3: 弹幕密度热力图（按分钟）
plt.subplot(3, 1, 3)

# 创建热力图数据
heatmap_data = time_bin_counts_per_min.to_frame().T
sns.heatmap(heatmap_data, cmap='YlGnBu', annot=False, cbar_kws={'label': '弹幕数量'})
plt.title('弹幕密度热力图', fontsize=14)
plt.xlabel('视频时间 (分钟:秒)', fontsize=12)
plt.ylabel('')  # 不需要Y轴标签
plt.xticks(rotation=45, ha='right', fontsize=8)

# 调整布局
plt.tight_layout()

# 保存图表
plt.savefig(r'D:\数据分析\数据集\b站视频\弹幕时间分布分析.png', dpi=300, bbox_inches='tight')
plt.show()

# 6. 关键时间点分析
# 找到弹幕峰值时间点
peak_time = time_bin_counts.idxmax()
peak_count = time_bin_counts.max()

# 计算前50%弹幕出现的时间点
half_percent_time = cumulative_percentage[cumulative_percentage >= 50].index[0]

print("\n关键分析结果:")
print(f"1. 弹幕最密集的时间段: {peak_time} (共 {peak_count} 条弹幕)")
print(f"2. 50%的弹幕出现在 {half_percent_time} 之前")
print(f"3. 视频前半段弹幕比例: {cumulative_percentage.iloc[len(cumulative_percentage)//2]:.1f}%")
print(f"4. 视频最后10%时间段的弹幕比例: {100 - cumulative_percentage.iloc[-len(cumulative_percentage)//10]:.1f}%")

# 7. 弹幕模式与时间的关系
plt.figure(figsize=(12, 8))
sns.boxplot(x='mode_name', y='time', data=df)
plt.title('不同弹幕模式出现的时间分布', fontsize=14)
plt.xlabel('弹幕模式', fontsize=12)
plt.ylabel('出现时间 (秒)', fontsize=12)
plt.xticks(rotation=15)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig(r'D:\数据分析\数据集\b站视频\弹幕模式时间分布.png', dpi=300)
plt.show()

# 8. 高级分析 - 弹幕随时间变化的动态
# 计算滚动平均
window_size = 30  # 30秒窗口
df_sorted = df.sort_values('time')
df_sorted['rolling_count'] = df_sorted['time'].rolling(window=window_size).count()

plt.figure(figsize=(14, 7))
plt.plot(df_sorted['time'], df_sorted['rolling_count'], 'b-', linewidth=1.5)
plt.title(f'弹幕密度动态变化 ({window_size}秒滚动窗口)', fontsize=14)
plt.xlabel('视频时间 (秒)', fontsize=12)
plt.ylabel(f'{window_size}秒窗口弹幕数量', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)

# 标记峰值
max_rolling_idx = df_sorted['rolling_count'].idxmax()
max_rolling_time = df_sorted.loc[max_rolling_idx, 'time']
max_rolling_value = df_sorted.loc[max_rolling_idx, 'rolling_count']
plt.annotate(f'最高密度: {max_rolling_value}条/{window_size}秒\n时间: {max_rolling_time:.1f}秒',
             xy=(max_rolling_time, max_rolling_value),
             xytext=(max_rolling_time, max_rolling_value + 5),
             arrowprops=dict(facecolor='red', shrink=0.05),
             fontsize=12, color='red')

plt.tight_layout()
plt.savefig(r'D:\数据分析\数据集\b站视频\弹幕密度动态变化.png', dpi=300)
plt.show()