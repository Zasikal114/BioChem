import pandas as pd
import numpy as np
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows
import sys
import os

def replace_zeros_with_empty(file_path, sheet_name=None, backup=True):
    """
    将Excel中有内容的行列中的0替换为空单元格，直接覆盖原文件
    
    参数:
    file_path: Excel文件路径
    sheet_name: 工作表名称（默认为所有工作表）
    backup: 是否创建备份文件（默认为True）
    """
    try:
        # 创建备份文件（可选）
        if backup:
            backup_path = file_path.replace('.xlsx', '_backup.xlsx')
            import shutil
            shutil.copy2(file_path, backup_path)
            print(f"已创建备份文件: {backup_path}")
        
        # 读取Excel文件
        if sheet_name:
            # 读取指定工作表
            xl_file = pd.ExcelFile(file_path)
            if sheet_name not in xl_file.sheet_names:
                print(f"错误: 工作表 '{sheet_name}' 不存在")
                return
            
            df_dict = {sheet_name: pd.read_excel(file_path, sheet_name=sheet_name)}
        else:
            # 读取所有工作表
            df_dict = pd.read_excel(file_path, sheet_name=None)
        
        # 创建Excel写入器，直接覆盖原文件
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            for sheet_name, df in df_dict.items():
                print(f"处理工作表: {sheet_name}")
                
                # 找到有数据的行和列的范围
                non_empty_rows = df.notna().any(axis=1)
                non_empty_cols = df.notna().any(axis=0)
                
                if not non_empty_rows.any() or not non_empty_cols.any():
                    print(f"工作表 '{sheet_name}' 没有数据，跳过处理")
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    continue
                
                # 获取有数据的行索引和列索引
                data_rows = df.index[non_empty_rows]
                data_cols = df.columns[non_empty_cols]
                
                # 在有数据的行列范围内，将0替换为空值
                df_replaced = df.copy()
                df_replaced.loc[data_rows, data_cols] = df_replaced.loc[data_rows, data_cols].replace(0, np.nan)
                
                # 写入到原文件
                df_replaced.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # 统计替换的单元格数量
                original_zero_count = (df.loc[data_rows, data_cols] == 0).sum().sum()
                replaced_zero_count = (df_replaced.loc[data_rows, data_cols] == 0).sum().sum()
                replaced_count = original_zero_count - replaced_zero_count
                
                print(f"在工作表 '{sheet_name}' 中替换了 {replaced_count} 个0值为空单元格")
        
        print(f"\n处理完成！原文件已更新: {file_path}")
        
    except FileNotFoundError:
        print(f"错误: 文件 '{file_path}' 不存在")
    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")

def replace_values_with_empty_advanced(file_path, sheet_name=None, values_to_replace=[0], backup=True):
    """
    高级版本：提供更多选项的值替换功能，将指定值替换为空单元格，直接覆盖原文件
    
    参数:
    file_path: Excel文件路径
    sheet_name: 工作表名称
    values_to_replace: 要替换的值列表（默认为[0]）
    backup: 是否创建备份文件（默认为True）
    """
    try:
        # 创建备份文件（可选）
        if backup:
            backup_path = file_path.replace('.xlsx', '_backup.xlsx')
            import shutil
            shutil.copy2(file_path, backup_path)
            print(f"已创建备份文件: {backup_path}")
        
        # 读取Excel文件
        if sheet_name:
            df_dict = {sheet_name: pd.read_excel(file_path, sheet_name=sheet_name)}
        else:
            df_dict = pd.read_excel(file_path, sheet_name=None)
        
        # 创建Excel写入器，直接覆盖原文件
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            for current_sheet, df in df_dict.items():
                print(f"处理工作表: {current_sheet}")
                
                # 找到第一个和最后一个有数据的行和列
                if df.empty:
                    print(f"工作表 '{current_sheet}' 为空，跳过处理")
                    df.to_excel(writer, sheet_name=current_sheet, index=False)
                    continue
                
                # 找到有数据的区域边界
                non_empty_cells = df.notna()
                
                if not non_empty_cells.any().any():
                    print(f"工作表 '{current_sheet}' 没有数据，跳过处理")
                    df.to_excel(writer, sheet_name=current_sheet, index=False)
                    continue
                
                # 获取有数据的行和列索引
                has_data_rows = non_empty_cells.any(axis=1)
                has_data_cols = non_empty_cells.any(axis=0)
                
                data_rows = df.index[has_data_rows]
                data_cols = df.columns[has_data_cols]
                
                if len(data_rows) == 0 or len(data_cols) == 0:
                    df.to_excel(writer, sheet_name=current_sheet, index=False)
                    continue
                
                # 在有数据的区域内替换指定值
                df_replaced = df.copy()
                
                # 对每个要替换的值执行替换操作
                for value in values_to_replace:
                    df_replaced.loc[data_rows.min():data_rows.max(), 
                                  data_cols[0]:data_cols[-1]] = df_replaced.loc[data_rows.min():data_rows.max(), 
                                                                              data_cols[0]:data_cols[-1]].replace(value, np.nan)
                
                # 写入结果
                df_replaced.to_excel(writer, sheet_name=current_sheet, index=False)
                
                # 统计信息
                original_count = 0
                for value in values_to_replace:
                    original_count += (df.loc[data_rows.min():data_rows.max(), 
                                            data_cols[0]:data_cols[-1]] == value).sum().sum()
                
                after_count = 0
                for value in values_to_replace:
                    after_count += (df_replaced.loc[data_rows.min():data_rows.max(), 
                                                 data_cols[0]:data_cols[-1]] == value).sum().sum()
                
                replaced = original_count - after_count
                
                print(f"在工作表 '{current_sheet}' 的数据区域({len(data_rows)}行×{len(data_cols)}列)中替换了 {replaced} 个指定值为空单元格")
        
        print(f"\n高级处理完成！原文件已更新: {file_path}")
        
    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")

# 使用示例
if __name__ == "__main__":
    # 示例1: 基本使用 - 将0替换为空单元格
    file_path = "example.xlsx"  # 替换为您的Excel文件路径
    
    # 处理整个文件的所有工作表，直接覆盖原文件
    replace_zeros_with_empty(r"C:\Users\lenovo\Desktop\jython\Table\node table.xlsx", backup=True)
    
    # 示例2: 指定工作表，不创建备份
    # replace_zeros_with_empty(
    #     file_path="data.xlsx",
    #     sheet_name="Sheet1",
    #     backup=False  # 不创建备份
    # )
    
    # 示例3: 使用高级版本，可以自定义要替换的值
    # replace_values_with_empty_advanced(
    #     file_path="data.xlsx",
    #     values_to_replace=[0, "N/A", ""]  # 可以替换多个值
    # )
    
    # 交互式使用
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        sheet = sys.argv[2] if len(sys.argv) > 2 else None
        backup = sys.argv[3].lower() != 'false' if len(sys.argv) > 3 else True
        
        replace_zeros_with_empty(input_file, sheet, backup)
    '''
    else:
        print("""
使用方法:
1. 修改脚本中的 file_path 变量为您的Excel文件路径
2. 或者通过命令行运行: python script.py <输入文件> [工作表名] [是否备份]

示例:
python excel_replace_zeros.py data.xlsx
python excel_replace_zeros.py data.xlsx Sheet1
python excel_replace_zeros.py data.xlsx Sheet1 false  # 不创建备份
        """)
    '''