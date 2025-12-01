import pandas as pd
from collections import defaultdict
import os

def find_and_remove_duplicate_rows(file_path):
    """
    找出Excel表格中前三列完全相同的行，并删除行号较大的那一行
    注意：会修改原文件，请先备份重要数据
    """
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path)
        
        # 检查数据是否足够
        if len(df) < 2:
            print("数据行数不足，无法进行比较")
            return
        
        # 检查是否有三列数据
        if df.shape[1] < 3:
            print("错误: 数据表至少需要三列数据")
            return
        
        # 创建备份文件
        backup_path = file_path.replace('.xlsx', '_backup.xlsx')
        df.to_excel(backup_path, index=False)
        print(f"已创建备份文件: {backup_path}")
        
        # 用于存储前三列组合及其对应的行索引
        row_dict = defaultdict(list)
        
        # 遍历每一行，以前三列的值作为键
        for idx, row in df.iterrows():
            # 获取前三列的值，转换为元组作为键
            key = tuple(row.iloc[:3])
            row_dict[key].append(idx)
        
        # 找出有重复的行
        duplicate_groups = {k: v for k, v in row_dict.items() if len(v) > 1}
        
        if not duplicate_groups:
            print("未找到前三列完全相同的行，无需删除")
            return
        
        print(f"找到 {len(duplicate_groups)} 组重复行：")
        print("=" * 80)
        
        # 收集需要删除的行索引（每组重复行中行号最大的行）
        rows_to_delete = []
        
        # 输出每组重复行的详细信息
        for group_num, (key, indices) in enumerate(duplicate_groups.items(), 1):
            print(f"第 {group_num} 组重复:")
            print(f"前三列值: '{key[0]}', '{key[1]}', '{key[2]}'")
            
            # 转换为Excel行号（从1开始）
            excel_row_numbers = [i+1 for i in indices]
            print(f"所有重复的行号: {excel_row_numbers}")
            
            # 找出最大行号的行
            max_index = max(indices)
            max_excel_row = max_index + 1
            print(f"将删除的行号: {max_excel_row}")
            
            # 获取要删除的行的数据
            row_to_delete = df.iloc[max_index]
            print("要删除的行的完整数据:")
            for col_idx, value in enumerate(row_to_delete):
                col_name = df.columns[col_idx] if col_idx < len(df.columns) else f"列{col_idx+1}"
                print(f"  {col_name}: {value}")
            
            # 添加到删除列表
            rows_to_delete.append(max_index)
            print("-" * 60)
        
        # 确认删除
        confirm = input(f"\n确认删除以上 {len(rows_to_delete)} 行吗？(y/n): ").strip().lower()
        if confirm != 'y':
            print("操作已取消")
            return
        
        # 创建一个标记列，标记哪些行需要删除
        df['_delete_marker'] = False
        for idx in rows_to_delete:
            df.at[idx, '_delete_marker'] = True
        
        # 保存删除前的行数
        original_row_count = len(df)
        
        # 删除标记为True的行
        df = df[~df['_delete_marker']]
        
        # 删除标记列
        df = df.drop('_delete_marker', axis=1)
        
        # 保存修改后的数据
        df.to_excel(file_path, index=False)
        
        # 输出结果
        deleted_row_count = original_row_count - len(df)
        print(f"删除完成!")
        print(f"原文件行数: {original_row_count}")
        print(f"删除后行数: {len(df)}")
        print(f"共删除 {deleted_row_count} 行")
        print(f"修改已保存到: {file_path}")
        
    except FileNotFoundError:
        print(f"错误: 文件 '{file_path}' 未找到，请检查文件路径是否正确")
    except Exception as e:
        print(f"处理文件时出错: {e}")

def find_duplicate_rows_only(file_path):
    """
    只查找重复行但不删除（预览模式）
    """
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path)
        
        # 检查数据是否足够
        if len(df) < 2:
            print("数据行数不足，无法进行比较")
            return
        
        # 检查是否有三列数据
        if df.shape[1] < 3:
            print("错误: 数据表至少需要三列数据")
            return
        
        # 用于存储前三列组合及其对应的行索引
        row_dict = defaultdict(list)
        
        # 遍历每一行，以前三列的值作为键
        for idx, row in df.iterrows():
            # 获取前三列的值，转换为元组作为键
            key = tuple(row.iloc[:3])
            row_dict[key].append(idx)
        
        # 找出有重复的行
        duplicate_groups = {k: v for k, v in row_dict.items() if len(v) > 1}
        
        if not duplicate_groups:
            print("未找到前三列完全相同的行")
            return
        
        print(f"找到 {len(duplicate_groups)} 组重复行（预览模式，不执行删除）：")
        print("=" * 80)
        
        # 输出每组重复行的详细信息
        for group_num, (key, indices) in enumerate(duplicate_groups.items(), 1):
            print(f"第 {group_num} 组重复:")
            print(f"前三列值: '{key[0]}', '{key[1]}', '{key[2]}'")
            
            # 转换为Excel行号（从1开始）
            excel_row_numbers = [i+1 for i in indices]
            print(f"所有重复的行号: {excel_row_numbers}")
            
            # 找出最大行号的行
            max_index = max(indices)
            max_excel_row = max_index + 1
            print(f"将删除的行号: {max_excel_row}")
            
        
        # 汇总信息
        print("\n汇总信息:")
        print(f"总重复组数: {len(duplicate_groups)}")
        total_duplicates = sum(len(indices) for indices in duplicate_groups.values())
        print(f"总重复行数: {total_duplicates}")
        print(f"将删除的行数: {len(duplicate_groups)}")
        
    except FileNotFoundError:
        print(f"错误: 文件 '{file_path}' 未找到，请检查文件路径是否正确")
    except Exception as e:
        print(f"处理文件时出错: {e}")

# 使用示例
if __name__ == "__main__":
    # 替换为您的Excel文件路径
    file_path = r"C:\Users\lenovo\Desktop\jython\Table\edge table.xlsx"  # 请修改为您的实际文件路径
    
    print("请选择操作模式:")
    print("1. 预览模式 (只查看重复行，不执行删除)")
    print("2. 删除模式 (查找并删除重复行)")
    
    try:
        choice = input("请输入选择 (1 或 2, 默认为1): ").strip()
        
        if choice == "2":
            print("\n=== 删除模式 ===")
            print("警告: 此操作将修改原文件，请确保已备份重要数据!")
            confirm = input("确认继续吗？(y/n): ").strip().lower()
            if confirm == 'y':
                find_and_remove_duplicate_rows(file_path)
            else:
                print("操作已取消")
        else:
            print("\n=== 预览模式 ===")
            find_duplicate_rows_only(file_path)
            
    except KeyboardInterrupt:
        print("\n用户中断操作")
    except Exception as e:
        print(f"发生错误: {e}")