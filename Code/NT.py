import pandas as pd
from collections import defaultdict
import sys

def find_duplicates_in_first_column(excel_file):
    """
    检测Excel表格第一列的重复内容
    从第二次出现开始，每出现一次就输出一次
    
    Args:
        excel_file (str): Excel文件路径
    """
    try:
        # 读取Excel文件
        df = pd.read_excel(excel_file)
        
        # 检查文件是否为空
        if df.empty:
            print("Excel文件为空")
            return
        
        # 获取第一列数据
        first_column = df.iloc[:, 0]
        
        # 用于记录每个值出现次数的字典
        value_count = defaultdict(int)
        
        # 用于存储重复值的列表
        duplicates = []
        
        print("开始检测第一列的重复内容...")
        print("=" * 50)
        
        # 遍历第一列的每个单元格
        for index, value in enumerate(first_column):
            # 跳过空值
            if pd.isna(value):
                continue
                
            value_count[value] += 1
            
            # 如果该值出现次数大于1，则记录重复
            if value_count[value] > 1:
                duplicates.append({
                    'value': value,
                    'row': index + 2,  # +2 因为Excel行号从1开始，且第一行是标题
                    'occurrence': value_count[value]
                })
                print(f"第{index + 2}行: '{value}' (第{value_count[value]}次出现)")
        
        print("=" * 50)
        
        # 输出统计信息
        total_duplicates = len(duplicates)
        unique_duplicates = len([v for v in value_count if value_count[v] > 1])
        
        print(f"\n检测完成！")
        print(f"总重复出现次数: {total_duplicates}")
        print(f"有重复的唯一值数量: {unique_duplicates}")
        
        # 如果有重复值，显示详细信息
        if duplicates:
            print(f"\n重复值详细统计:")
            for value, count in value_count.items():
                if count > 1:
                    print(f"'{value}': 共出现{count}次")
        
        return duplicates
        
    except FileNotFoundError:
        print(f"错误: 找不到文件 '{excel_file}'")
        return None
    except Exception as e:
        print(f"读取文件时发生错误: {e}")
        return None

def find_duplicates_advanced(excel_file, sheet_name=0):
    """
    高级版本：支持指定工作表，并提供更详细的输出
    
    Args:
        excel_file (str): Excel文件路径
        sheet_name (str/int): 工作表名称或索引，默认为第一个工作表
    """
    try:
        # 读取Excel文件
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        
        if df.empty:
            print("Excel文件为空")
            return
        
        first_column = df.iloc[:, 0]
        value_positions = defaultdict(list)
        
        print(f"检测文件: {excel_file}")
        print(f"工作表: {sheet_name}")
        print("=" * 50)
        
        found_duplicates = False
        
        # 记录每个值的位置
        for index, value in enumerate(first_column):
            if pd.isna(value):
                continue
            value_positions[value].append(index + 2)  # +2 因为Excel行号从1开始
        
        # 输出重复值
        for value, positions in value_positions.items():
            if len(positions) > 1:
                found_duplicates = True
                print(f"值 '{value}' 在以下行重复出现: {positions}")
                for i, pos in enumerate(positions[1:], 2):  # 从第二次出现开始
                    print(f"  - 第{i}次出现在第{pos}行")
        
        if not found_duplicates:
            print("第一列没有发现重复内容")
            
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    # 使用方法示例
    
    # 方法1: 直接指定文件路径
    excel_file_path = r"C:\Users\lenovo\Desktop\jython\Table\node table.xlsx"  # 请将此处替换为你的Excel文件路径
    
    # 基本用法
    print("=== 基本重复检测 ===")
    duplicates = find_duplicates_in_first_column(excel_file_path)
    
    print("\n" + "="*60 + "\n")
    
    # 高级用法
    print("=== 高级重复检测 ===")
    find_duplicates_advanced(excel_file_path)
    
    # 方法2: 通过命令行参数指定文件
    if len(sys.argv) > 1:
        print("\n" + "="*60 + "\n")
        print("=== 通过命令行参数检测 ===")
        find_duplicates_in_first_column(sys.argv[1])