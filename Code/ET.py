import pandas as pd
from collections import defaultdict

def find_duplicate_rows(file_path):
    """
    找出Excel表格中前两列完全相同的行，并输出行号较大的那一行
    所有结果只输出到终端，不修改原文件
    """
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path)
        
        # 检查数据是否足够
        if len(df) < 2:
            print("数据行数不足，无法进行比较")
            return
        
        # 用于存储前两列组合及其对应的行索引
        row_dict = defaultdict(list)
        
        # 遍历每一行，以前两列的值作为键
        for idx, row in df.iterrows():
            # 获取前两列的值，转换为元组作为键
            key = tuple(row.iloc[:2])
            row_dict[key].append(idx)
        
        # 找出有重复的行
        duplicate_groups = {k: v for k, v in row_dict.items() if len(v) > 1}
        
        if not duplicate_groups:
            print("未找到前两列完全相同的行")
            return
        
        print(f"找到 {len(duplicate_groups)} 组重复行：")
        print("=" * 80)
        
        # 输出每组重复行的详细信息
        for group_num, (key, indices) in enumerate(duplicate_groups.items(), 1):
            print(f"第 {group_num} 组重复:")
            print(f"前两列值: '{key[0]}', '{key[1]}'")
            print(f"所有重复的行号 (Excel行号): {[i+1 for i in indices]}")
            print(f"最大行号: {max(indices)+1}")
            print("最大行号的完整数据:")
            
            # 获取最大行号对应的行数据
            max_index = max(indices)
            max_row_data = df.iloc[max_index]
            
            # 打印该行的所有列数据
            for col_idx, value in enumerate(max_row_data):
                col_name = df.columns[col_idx] if col_idx < len(df.columns) else f"列{col_idx+1}"
                print(f"  {col_name}: {value}")
            
            print("-" * 60)
        
        # 汇总信息
        print("\n汇总信息:")
        print(f"总重复组数: {len(duplicate_groups)}")
        total_duplicates = sum(len(indices) for indices in duplicate_groups.values())
        print(f"总重复行数: {total_duplicates}")
        print(f"输出的最大行号行数: {len(duplicate_groups)}")
        
    except FileNotFoundError:
        print(f"错误: 文件 '{file_path}' 未找到，请检查文件路径是否正确")
    except Exception as e:
        print(f"处理文件时出错: {e}")

def find_duplicate_rows_simple(file_path):
    """
    简化版本，只输出最大行号行的基本信息
    """
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path)
        
        if len(df) < 2:
            print("数据行数不足，无法进行比较")
            return
        
        # 用于存储前两列组合及其对应的行索引
        row_dict = defaultdict(list)
        
        for idx, row in df.iterrows():
            key = tuple(row.iloc[:2])
            row_dict[key].append(idx)
        
        # 找出有重复的行
        duplicate_groups = {k: v for k, v in row_dict.items() if len(v) > 1}
        
        if not duplicate_groups:
            print("未找到前两列完全相同的行")
            return
        
        print(f"找到 {len(duplicate_groups)} 组重复行，以下是每组中行号最大的行:")
        print("=" * 60)
        
        # 只输出最大行号行的基本信息
        for group_num, (key, indices) in enumerate(duplicate_groups.items(), 1):
            max_index = max(indices)
            max_row_data = df.iloc[max_index]
            
            print(f"{group_num}. 行号 {max_index+1}: 前两列值 = '{key[0]}', '{key[1]}'")
        
        print("=" * 60)
        
    except FileNotFoundError:
        print(f"错误: 文件 '{file_path}' 未找到，请检查文件路径是否正确")
    except Exception as e:
        print(f"处理文件时出错: {e}")

# 使用示例
if __name__ == "__main__":
    # 替换为您的Excel文件路径
    file_path = r"C:\Users\lenovo\Desktop\jython\Table\edge table.xlsx"  # 请修改为您的实际文件路径
    
    print("请选择输出模式:")
    print("1. 详细模式 (显示所有重复行和完整数据)")
    print("2. 简洁模式 (只显示最大行号行的基本信息)")
    
    try:
        choice = input("请输入选择 (1 或 2, 默认为1): ").strip()
        
        if choice == "2":
            print("\n=== 简洁模式 ===")
            find_duplicate_rows_simple(file_path)
        else:
            print("\n=== 详细模式 ===")
            find_duplicate_rows(file_path)
            
    except KeyboardInterrupt:
        print("\n用户中断操作")
    except Exception as e:
        print(f"发生错误: {e}")