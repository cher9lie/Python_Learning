# -*- coding: utf-8 -*-
# =============================================================================
# 脚本名称：earthquake_crawler.py
# 功能描述：定向抓取中国地震台网（CENC）最新地震事件公开数据，
#           解析并清洗后导出为 Excel 电子表格。
# 数据来源：https://www.ceic.ac.cn/data/data.json
# 数据字段：发震时刻、经度、纬度、震级、深度、发震位置
# 作者注记：数据仅供个人可视化与规律分析，请勿用于商业用途。
# =============================================================================

# ── 第一部分：导入所需标准库与第三方库 ─────────────────────────────────────────
import sys               # 用于在关键错误时退出程序，以及修复控制台编码

# ── 修复 Windows 控制台 GBK 编码问题 ─────────────────────────────────────────
# Windows 默认控制台编码为 GBK/CP936，无法直接打印部分 UTF-8 中文与特殊符号。
# 此处将标准输出（stdout）和标准错误（stderr）均重新配置为 UTF-8 编码，
# 确保中文注释、Unicode 字符及特殊符号均能在控制台正常显示。
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import requests          # 用于发送 HTTP 网络请求，获取远端数据
import pandas as pd      # 用于将字典列表转换为 DataFrame，并导出 Excel
import urllib3           # 用于禁用不必要的 SSL 证书警告（因官方证书偶发过期）
import json              # 用于在调试时格式化打印 JSON 数据（辅助使用）

# ── 第二部分：全局配置参数 ────────────────────────────────────────────────────

# 目标接口地址：中国地震台网官方网站前端动态加载所使用的 JSON 数据文件
# 经过对 www.ceic.ac.cn 前端 JS 代码逆向分析确认，该接口为官网数据来源
TARGET_URL = "https://www.ceic.ac.cn/data/data.json"

# Excel 文件保存路径（默认保存到 D 盘根目录）
OUTPUT_PATH = "D:/earthquake_data.xlsx"

# 请求超时时间（单位：秒），防止因网络问题导致程序长时间阻塞
REQUEST_TIMEOUT = 20

# 禁用 SSL 证书验证警告
# 原因：中国地震台网官方 SSL 证书曾出现过期情况，为保证程序健壮性，
#       设置 verify=False 时需要同步禁用此类 InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ── 第三部分：HTTP 请求头配置 ─────────────────────────────────────────────────

# 伪装成真实浏览器发送请求，防止被服务端反爬机制（User-Agent 检查）拦截
# 此处模拟 Windows 10 平台下的 Chrome 120 浏览器特征
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    # Referer 字段告知服务器此请求来自官网主页，进一步模拟正常浏览行为
    "Referer": "https://www.ceic.ac.cn/",
    # Accept 字段声明客户端可接受 JSON 格式的响应体
    "Accept": "application/json, text/plain, */*",
    # Accept-Language 字段声明优先接受简体中文响应
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

# ── 第四部分：数据抓取与请求异常处理 ──────────────────────────────────────────

def fetch_earthquake_data():
    """
    发送 HTTP GET 请求，获取地震台网的原始 JSON 数据列表。

    返回值:
        list: 包含若干个地震事件字典的列表，若获取失败则返回 None。
    """
    print("=" * 60)
    print("  中国地震台网 - 地震数据自动抓取脚本")
    print("=" * 60)
    print(f"\n[1/3] 正在连接目标接口：{TARGET_URL}")
    print("      请稍候...\n")

    try:
        # 发送 HTTP GET 请求
        # 参数说明：
        #   url     ── 目标接口地址
        #   headers ── 自定义请求头，用于伪装浏览器
        #   timeout ── 连接与读取超时（秒），防止程序无限等待
        #   verify  ── 设为 False 以跳过 SSL 证书验证，应对证书过期问题
        response = requests.get(
            url=TARGET_URL,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
            verify=False   # 注意：仅在确认目标站点可信时使用此参数
        )

        # 立即调用 raise_for_status()，若服务器返回 4xx/5xx 错误状态码，
        # 则自动抛出 requests.exceptions.HTTPError 异常，保证代码健壮性
        response.raise_for_status()

        print(f"    [OK] 请求成功！HTTP 状态码：{response.status_code}")
        print(f"    [OK] 响应内容长度：{len(response.content):,} 字节\n")

        # 使用 response.json() 方法将响应体直接解析为 Python 列表
        # requests 库内部会根据响应头 Content-Type 的 charset 参数进行解码
        # 该接口返回的是标准 UTF-8 编码的 JSON 数组
        raw_data = response.json()

        print(f"    [OK] JSON 解析成功，共获取 {len(raw_data)} 条地震事件记录。")
        return raw_data

    except requests.exceptions.Timeout:
        # 捕获请求超时异常：连接服务器或等待响应超过 REQUEST_TIMEOUT 秒
        print(f"    [ERR] 错误：请求超时（>{REQUEST_TIMEOUT}s），请检查网络连接后重试。")
        return None

    except requests.exceptions.ConnectionError:
        # 捕获连接错误：通常是 DNS 解析失败或网络不通
        print("    [ERR] 错误：无法连接到目标服务器，请检查网络连接。")
        return None

    except requests.exceptions.HTTPError as e:
        # 捕获 HTTP 协议层错误：由 raise_for_status() 触发，如 403 Forbidden / 404 Not Found
        print(f"    [ERR] 错误：HTTP 请求失败 —— {e}")
        return None

    except requests.exceptions.RequestException as e:
        # 捕获所有其他 requests 相关的底层异常（兜底捕获）
        print(f"    [ERR] 错误：网络请求发生未知异常 —— {e}")
        return None

    except ValueError as e:
        # 捕获 JSON 解析错误：响应体不是有效的 JSON 格式
        print(f"    [ERR] 错误：JSON 数据解析失败 —— {e}")
        print("      （服务器可能返回了非预期的 HTML 或文本内容）")
        return None


# ── 第五部分：数据解析与字段清洗 ─────────────────────────────────────────────

def parse_earthquake_data(raw_data):
    """
    从原始 JSON 列表中提取并清洗所需字段，构建规范化的结构化数据。

    参数:
        raw_data (list): fetch_earthquake_data() 返回的原始字典列表。

    返回值:
        list: 经过清洗与字段映射后的地震事件字典列表，字段为中文列名。
    """
    print("[2/3] 正在解析与清洗数据字段...\n")

    # 初始化结果列表，用于存储清洗后的每一条地震记录
    cleaned_records = []

    # 统计解析失败的记录条数，便于调试与质量评估
    error_count = 0

    # 遍历原始数据列表，逐条提取字段
    for index, item in enumerate(raw_data):
        try:
            # 从字典中提取各字段，并使用 .get() 方法避免 KeyError
            # 若字段缺失则返回默认值 None 或空字符串，保证程序不中断
            record = {
                # 发震时刻：格式为 "YYYY-MM-DD HH:MM:SS"，北京时间（UTC+8）
                "发震时刻": item.get("time", None),

                # 纬度：震中地理坐标纬度值，单位：度（°），浮点数
                "纬度（°）": item.get("latitude", None),

                # 经度：震中地理坐标经度值，单位：度（°），浮点数
                "经度（°）": item.get("longitude", None),

                # 震级：地震能量大小，通常为面波震级（MS）或矩震级（MW）
                "震级（M）": item.get("magnitude", None),

                # 震源深度：地震发生点距地表的垂直深度，单位：千米（km）
                "深度（km）": item.get("depth", None),

                # 发震位置：震中所在的地理位置描述，中文字符串
                "发震位置": item.get("location", ""),

                # 事件编号：地震台网内部编号，用于数据溯源（附加字段）
                "事件编号": item.get("id", ""),
            }

            # 将清洗后的记录追加到结果列表
            cleaned_records.append(record)

        except (AttributeError, TypeError) as e:
            # 捕获单条记录解析异常，跳过该记录并记录错误数，不中断整体流程
            error_count += 1
            print(f"    [WARN] 第 {index + 1} 条记录解析异常（已跳过）：{e}")

    # 汇报解析结果统计
    print(f"    [OK] 数据解析完成！成功处理 {len(cleaned_records)} 条，"
          f"跳过异常 {error_count} 条。\n")

    return cleaned_records


# ── 第六部分：构建 DataFrame 并导出 Excel ──────────────────────────────────────

def save_to_excel(records):
    """
    将清洗后的地震事件列表转换为 pandas DataFrame，并导出为 Excel 文件。

    参数:
        records (list): parse_earthquake_data() 返回的清洗后记录列表。
    """
    print(f"[3/3] 正在写入 Excel 文件：{OUTPUT_PATH}\n")

    # 使用 pandas.DataFrame() 将字典列表一次性转换为二维表格结构
    # 每个字典的键自动成为列名，值成为对应行的单元格数据
    df = pd.DataFrame(records)

    # 指定列的显示顺序，使 Excel 表格结构更直观
    column_order = [
        "发震时刻",
        "纬度（°）",
        "经度（°）",
        "震级（M）",
        "深度（km）",
        "发震位置",
        "事件编号",
    ]

    # 按照指定顺序重新排列 DataFrame 的列
    df = df[column_order]

    # 将"发震时刻"列转换为 datetime 类型，便于后续在 Excel 中排序与筛选
    # 参数 errors='coerce' 表示若解析失败则将该值置为 NaT（Not a Time）
    df["发震时刻"] = pd.to_datetime(df["发震时刻"], errors="coerce")

    # 按发震时刻降序排列（最新记录在最上方）
    df = df.sort_values(by="发震时刻", ascending=False).reset_index(drop=True)

    # 打印前 5 条数据预览，供用户确认数据内容
    print("    数据预览（前 5 条）：")
    print("    " + "-" * 80)
    # 设置 pandas 显示选项，防止列内容被截断
    pd.set_option("display.max_colwidth", 30)
    pd.set_option("display.unicode.east_asian_width", True)
    preview_str = df.head(5).to_string(index=True)
    for line in preview_str.split("\n"):
        print("    " + line)
    print("    " + "-" * 80 + "\n")

    try:
        # 使用 ExcelWriter 上下文管理器，结合 openpyxl 引擎写入 xlsx 格式
        # openpyxl 引擎对中文字符支持良好，且格式兼容 Microsoft Excel
        with pd.ExcelWriter(
            path=OUTPUT_PATH,          # 输出文件路径
            engine="openpyxl",         # 写入引擎，支持 xlsx 格式
            datetime_format="YYYY-MM-DD HH:MM:SS"  # 日期时间格式
        ) as writer:

            # 将 DataFrame 写入名为 "地震事件数据" 的工作表
            # 参数说明：
            #   sheet_name  ── Excel 工作表名称
            #   index       ── 是否写入行索引（False 表示不写入）
            #   freeze_panes── 冻结首行标题行，便于大数据集滚动查看
            df.to_excel(
                excel_writer=writer,
                sheet_name="地震事件数据",
                index=False,
                freeze_panes=(1, 0)    # 冻结第 1 行（列名标题行）
            )

            # 获取当前工作表对象，用于进一步格式化
            worksheet = writer.sheets["地震事件数据"]

            # 自动调整每一列的列宽，使内容完整显示不被遮盖
            # 遍历所有列，根据列名与数据内容的最大字符长度动态设置列宽
            for col_cells in worksheet.columns:
                max_length = 0
                col_letter = col_cells[0].column_letter  # 获取列字母，如 "A"、"B"
                for cell in col_cells:
                    if cell.value is not None:
                        # 计算当前单元格内容的字符长度（中文字符按2个单位计）
                        cell_len = 0
                        for char in str(cell.value):
                            # 判断是否为中文字符（Unicode 范围：0x4e00 ~ 0x9fff）
                            cell_len += 2 if '\u4e00' <= char <= '\u9fff' else 1
                        max_length = max(max_length, cell_len)
                # 设置列宽，额外留 2 个字符的边距，最大不超过 50 字符
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[col_letter].width = adjusted_width

        print(f"    [OK] Excel 文件已成功保存至：{OUTPUT_PATH}")
        print(f"    [OK] 共写入 {len(df)} 条地震事件记录，工作表名称：「地震事件数据」\n")

    except PermissionError:
        # 捕获文件权限错误：通常是目标 Excel 文件正被 Excel 程序打开
        print(f"    [ERR] 错误：无法写入文件 —— 目标文件可能已被 Excel 打开，"
              f"请关闭后重试。")
        sys.exit(1)

    except OSError as e:
        # 捕获操作系统层面的文件 I/O 错误：如路径不存在、磁盘空间不足等
        print(f"    [ERR] 错误：文件写入失败 —— {e}")
        print(f"      请检查路径 {OUTPUT_PATH} 是否存在且具有写入权限。")
        sys.exit(1)


# ── 第七部分：主程序入口 ──────────────────────────────────────────────────────

def main():
    """
    主程序入口，按序调用各功能模块，完成：
    数据抓取 → 字段解析 → 清洗转换 → Excel 导出
    """

    # 第一步：发送请求，抓取原始 JSON 数据
    raw_data = fetch_earthquake_data()

    # 若数据获取失败，退出程序并返回错误状态码
    if raw_data is None:
        print("\n程序终止：数据抓取失败，请检查网络连接或目标接口是否可用。")
        sys.exit(1)

    # 若返回的数据列表为空，给出提示后退出
    if len(raw_data) == 0:
        print("\n程序终止：接口返回的数据列表为空，可能是接口暂时无数据。")
        sys.exit(1)

    # 第二步：解析并清洗每条地震事件的字段
    records = parse_earthquake_data(raw_data)

    # 若解析后无有效记录，退出程序
    if not records:
        print("\n程序终止：数据解析后无有效记录，请检查接口数据格式。")
        sys.exit(1)

    # 第三步：构建 DataFrame 并导出 Excel 电子表格
    save_to_excel(records)

    # 输出成功完成信息
    print("=" * 60)
    print("  [完成] 全部任务执行完成！")
    print(f"  Excel 文件路径：{OUTPUT_PATH}")
    print("=" * 60)


# ── 程序入口保护 ──────────────────────────────────────────────────────────────
# 确保只有直接运行本脚本时才执行 main()，
# 当作为模块被其他脚本 import 时则不自动执行
if __name__ == "__main__":
    main()
