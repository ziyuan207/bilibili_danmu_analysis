import pandas as pd
import numpy as np
from datetime import datetime

# 定义文件路径
file_path = r'D:\数据分析\数据集\b站视频\加油打工人弹幕.xlsx'

# 读取Excel文件
df = pd.read_excel(file_path)

# 显示原始列名和数据类型
print("原始数据列名:", df.columns.tolist())
print("数据类型:\n", df.dtypes)

# 定义弹幕模式解释字典
MODE_DICT = {
    1: "滚动弹幕",
    2: "滚动弹幕",
    3: "滚动弹幕",
    4: "底端弹幕",
    5: "顶端弹幕",
    6: "逆向弹幕",
    7: "精准定位",
    8: "高级弹幕"
}

# 定义字号解释字典
FONTSIZE_DICT = {
    12: "非常小",
    16: "特小",
    18: "小",
    25: "中",
    36: "大",
    45: "很大",
    64: "特别大"
}


def parse_danmu_info(info):
    """直接按逗号分割解析弹幕信息"""
    if pd.isna(info) or not isinstance(info, str):
        return [np.nan] * 8

    # 1. 移除所有空格
    cleaned = info.replace(" ", "")
    # 3. 按逗号分割字符串
    parts = cleaned.split(',')

    # 4. 确保有足够的部分
    if len(parts) < 8:
        return [np.nan] * 8

    # 5. 解析各个部分
    try:
        time_val = float(parts[0])  # 弹幕时间
        mode_val = int(parts[1])  # 弹幕模式
        fontsize_val = int(parts[2])  # 字号
        color_val = int(parts[3])  # 颜色
        timestamp_val = int(parts[4])  # Unix时间戳
        danmu_pool_val = int(parts[5])  # 弹幕池
        sender_id_val = parts[6]  # 发送者ID
        row_id_val = int(parts[7])  # 弹幕rowID

        return [time_val, mode_val, fontsize_val, color_val, timestamp_val,
                danmu_pool_val, sender_id_val, row_id_val]

    except (ValueError, TypeError, IndexError) as e:
        print(f"解析错误: {e}\n原始数据: {info}")
        return [np.nan] * 8


# 应用解析函数 - 确保使用正确的列名 'danmu_infos'
new_columns = ['time', 'mode', 'fontsize', 'color', 'timestamp', 'danmu_pool', 'sender_id', 'row_id']
df[new_columns] = df['danmu_infos'].apply(lambda x: pd.Series(parse_danmu_info(x)))

# 添加解释性列
df['mode_name'] = df['mode'].map(MODE_DICT)
df['fontsize_name'] = df['fontsize'].map(FONTSIZE_DICT)

# 转换时间戳为可读日期
df['datetime'] = pd.to_datetime(df['timestamp'], unit='s') + pd.Timedelta(hours=8)


# 处理颜色值 - 转换为十六进制
def color_to_hex(color_int):
    try:
        return f"#{color_int:06X}"
    except:
        return None


df['color_hex'] = df['color'].apply(color_to_hex)

# 显示清洗后的数据
print("\n清洗后的数据预览:")
print(df.head())

# 保存清洗后的数据
output_path = r'D:\数据分析\数据集\b站视频\清洗后的弹幕数据.xlsx'
df.to_excel(output_path, index=False)
print(f"\n清洗后的数据已保存至: {output_path}")

# 数据质量报告
print("\n数据质量报告:")
print(f"总弹幕数: {len(df)}")
success_count = df['time'].notnull().sum()
print(f"成功解析数: {success_count} ({success_count / len(df):.1%})")

if success_count < len(df):
    print("\n解析失败的示例:")
    failed_samples = df[df['time'].isnull()]['danmu_infos'].head().tolist()
    for i, sample in enumerate(failed_samples, 1):
        print(f"{i}. {sample}")

# 检查新列是否包含数据
print("\n新列数据检查:")
for col in new_columns:
    print(f"{col}: {df[col].notnull().sum()} 个有效值")