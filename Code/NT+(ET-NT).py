import pandas as pd
import numpy as np
import os
import shutil
from datetime import datetime
import time

def find_missing_values_from_B(excelA_path, excelB_path, sheetA=0, sheetB=0, has_header=True):
    """
    检测ExcelB前两列中哪些值没有在ExcelA第一列中出现
    """
    try:
        # 读取Excel文件
        if has_header:
            df_A = pd.read_excel(excelA_path, sheet_name=sheetA, header=0, dtype=str)
            df_B = pd.read_excel(excelB_path, sheet_name=sheetB, header=0, dtype=str)
        else:
            df_A = pd.read_excel(excelA_path, sheet_name=sheetA, header=None, dtype=str)
            df_B = pd.read_excel(excelB_path, sheet_name=sheetB, header=None, dtype=str)
        
        print(f"ExcelA 行数: {len(df_A)}")
        print(f"ExcelB 行数: {len(df_B)}")
        
        # 获取ExcelA第一列的值
        if has_header:
            col_A = df_A.iloc[:, 0].dropna()
        else:
            col_A = df_A.iloc[:, 0].dropna()
            
        col_A = col_A.astype(str).str.strip()
        col_A = col_A[col_A != '']
        set_A = set(col_A.unique())
        
        print(f"ExcelA第一列有效值数量: {len(set_A)}")
        
        # 获取ExcelB前两列的值
        if has_header:
            col_B1 = df_B.iloc[:, 0].dropna().astype(str).str.strip()
            col_B2 = df_B.iloc[:, 1].dropna().astype(str).str.strip()
        else:
            col_B1 = df_B.iloc[:, 0].dropna().astype(str).str.strip()
            col_B2 = df_B.iloc[:, 1].dropna().astype(str).str.strip()
        
        # 合并B表前两列的值
        col_B_combined = pd.concat([col_B1, col_B2])
        col_B_combined = col_B_combined[col_B_combined != '']
        set_B = set(col_B_combined.unique())
        
        print(f"ExcelB前两列有效值数量: {len(set_B)}")
        
        # 找出在B中出现但不在A中出现的值
        missing_values = list(set_B - set_A)
        
        print(f"找到需要添加的值数量: {len(missing_values)}")
        return missing_values
        
    except Exception as e:
        print(f"处理过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return []

def add_missing_values_to_first_column(excelA_path, excelB_path, sheetA=0, sheetB=0, has_header=True):
    """
    将ExcelB中出现但未在ExcelA中的值添加到ExcelA的第一列
    始终添加新行，避免覆盖原有数据
    """
    try:
        # 创建备份文件
        backup_path = create_backup(excelA_path)
        print(f"已创建备份文件: {backup_path}")
        
        # 读取Excel文件
        if has_header:
            df_A = pd.read_excel(excelA_path, sheet_name=sheetA, header=0, dtype=str)
            df_B = pd.read_excel(excelB_path, sheet_name=sheetB, header=0, dtype=str)
        else:
            df_A = pd.read_excel(excelA_path, sheet_name=sheetA, header=None, dtype=str)
            df_B = pd.read_excel(excelB_path, sheet_name=sheetB, header=None, dtype=str)
        
        original_rows = len(df_A)
        print(f"原始ExcelA行数: {original_rows}")
        
        # 获取ExcelA第一列的值集合
        if has_header:
            col_A = df_A.iloc[:, 0].dropna().astype(str).str.strip()
        else:
            col_A = df_A.iloc[:, 0].dropna().astype(str).str.strip()
        col_A = col_A[col_A != '']
        set_A = set(col_A.unique())
        
        # 获取ExcelB前两列的值集合
        col_B_values = []
        for col_idx in [0, 1]:  # 前两列
            if has_header:
                col = df_B.iloc[:, col_idx].dropna().astype(str)
            else:
                col = df_B.iloc[:, col_idx].dropna().astype(str)
            col = col.str.strip()
            col = col[col != '']
            col_B_values.extend(col.tolist())
        
        set_B = set(col_B_values)
        print(f"ExcelB前两列有效值数量: {len(set_B)}")
        
        # 找出在B中出现但不在A中出现的值
        missing_values = list(set_B - set_A)
        print(f"需要添加的值数量: {len(missing_values)}")
        
        if missing_values:
            # 为每个缺失值创建新行
            new_rows_data = []
            for value in missing_values:
                # 创建新行数据，第一列为缺失值，其他列为空
                if has_header:
                    new_row = {col: "" for col in df_A.columns}
                    new_row[df_A.columns[0]] = value  # 第一列
                else:
                    new_row = [""] * len(df_A.columns)
                    new_row[0] = value  # 第一列
                new_rows_data.append(new_row)
            
            # 将新行转换为DataFrame
            if has_header:
                new_rows_df = pd.DataFrame(new_rows_data)
            else:
                new_rows_df = pd.DataFrame(new_rows_data, columns=range(len(df_A.columns)))
            
            # 将新行添加到原DataFrame
            df_updated = pd.concat([df_A, new_rows_df], ignore_index=True)
            
            # 尝试保存文件，如果失败则重试
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # 检查文件是否被占用
                    if is_file_locked(excelA_path):
                        print(f"文件被占用，等待重试... (尝试 {attempt+1}/{max_retries})")
                        time.sleep(2)  # 等待2秒
                        continue
                    
                    # 保存处理后的文件
                    if has_header:
                        df_updated.to_excel(excelA_path, index=False, header=True)
                    else:
                        df_updated.to_excel(excelA_path, index=False, header=False)
                    
                    print(f"已成功添加 {len(missing_values)} 个值到ExcelA的第一列")
                    print(f"新增行数: {len(missing_values)}")
                    print(f"处理后总行数: {len(df_updated)}")
                    
                    return df_updated, len(missing_values), missing_values
                    
                except PermissionError:
                    if attempt < max_retries - 1:
                        print(f"权限错误，等待重试... (尝试 {attempt+1}/{max_retries})")
                        time.sleep(2)
                    else:
                        raise  # 最后一次尝试后仍然失败，抛出异常
            
        else:
            print("没有需要添加的值")
            return df_A, 0, []
        
    except Exception as e:
        print(f"处理过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return None, 0, []

def is_file_locked(filepath):
    """
    检查文件是否被占用
    """
    try:
        # 尝试以写入模式打开文件
        with open(filepath, 'a') as f:
            pass
        return False
    except IOError:
        return True

def create_backup(file_path):
    """
    创建文件备份
    """
    try:
        dir_name = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        name, ext = os.path.splitext(file_name)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{name}_backup_{timestamp}{ext}"
        backup_path = os.path.join(dir_name, backup_name)
        
        shutil.copy2(file_path, backup_path)
        return backup_path
    except Exception as e:
        print(f"创建备份失败: {e}")
        return None

def main_add_missing_to_first_column():
    """
    主函数：将缺失值添加到ExcelA的第一列
    """
    # 请修改为您的实际文件路径
    excelA_path = r"C:\Users\lenovo\Desktop\jython\Table\node table.xlsx"  # 修改为您的ExcelA文件路径
    excelB_path = r"C:\Users\lenovo\Desktop\jython\Table\edge table.xlsx"  # 修改为您的ExcelB文件路径
    
    # 确认文件是否有表头
    has_header = True  # 默认有表头，如果您的文件没有表头，请设置为False
    
    print("开始检测需要添加到第一列的值...")
    print(f"ExcelA文件: {excelA_path}")
    print(f"ExcelB文件: {excelB_path}")
    print(f"文件是否有表头: {'是' if has_header else '否'}")
    print("-" * 50)
    
    # 检测需要添加的值
    missing_values = find_missing_values_from_B(excelA_path, excelB_path, has_header=has_header)
    
    # 输出检测结果
    if missing_values:
        print(f"\n以下 {len(missing_values)} 个值在ExcelB中出现但未在ExcelA第一列中出现:")
        print("-" * 50)
        for i, value in enumerate(missing_values, 1):
            print(f"{i}. {value}")
        
        # 询问用户是否要添加这些值
        response = input("\n是否要将这些值添加到ExcelA的第一列？(y/n): ")
        if response.lower() in ['y', 'yes', '是']:
            print("\n开始添加值到ExcelA的第一列...")
            print("-" * 50)
            
            # 添加值到ExcelA的第一列
            df_updated, added_count, added_values = add_missing_values_to_first_column(
                excelA_path, excelB_path, has_header=has_header
            )
            
            if df_updated is not None:
                print(f"\n处理完成！添加了 {added_count} 个值到ExcelA的第一列。")
                print(f"已直接在原文件上修改: {excelA_path}")
                
                # 显示添加的值的详细信息（前20个）
                if added_values:
                    print(f"\n添加的前20个值:")
                    print("-" * 30)
                    for i, value in enumerate(added_values[:20]):
                        print(f"{i+1}. {value}")
                    if len(added_values) > 20:
                        print(f"... 还有 {len(added_values) - 20} 个值被添加")
            else:
                print("处理失败！")
        else:
            print("已取消添加操作。")
    else:
        print("ExcelB中的所有值都已经在ExcelA的第一列中出现了！")

def enhanced_main_add_missing_to_first_column():
    """
    增强版主函数，直接执行添加到第一列的操作
    """
    # 请修改为您的实际文件路径
    excelA_path = r"C:\Users\lenovo\Desktop\jython\Table\node table.xlsx"  # 修改为您的ExcelA文件路径
    excelB_path = r"C:\Users\lenovo\Desktop\jython\Table\edge table.xlsx"  # 修改为您的ExcelB文件路径
    
    # 确认文件是否有表头
    has_header = True  # 默认有表头，如果您的文件没有表头，请设置为False
    
    print("增强版处理开始...")
    print(f"ExcelA文件: {excelA_path}")
    print(f"ExcelB文件: {excelB_path}")
    print(f"文件是否有表头: {'是' if has_header else '否'}")
    print("-" * 50)
    
    # 直接执行添加到第一列的操作
    df_updated, added_count, added_values = add_missing_values_to_first_column(
        excelA_path, excelB_path, has_header=has_header
    )
    
    if df_updated is not None:
        print(f"\n处理完成！添加了 {added_count} 个值到ExcelA的第一列。")
        print(f"已直接在原文件上修改: {excelA_path}")
        
        # 显示添加的值的详细信息
        if added_values:
            print(f"\n添加的值 (前20个):")
            print("-" * 30)
            for i, value in enumerate(added_values[:20]):
                print(f"{i+1}. {value}")
            if len(added_values) > 20:
                print(f"... 还有 {len(added_values) - 20} 个值被添加")
    else:
        print("处理失败！")

if __name__ == "__main__":
    
    print("\n" + "="*60 + "\n")
    print("ExcelB到ExcelA缺失值添加工具 (添加到第一列)")
    print("="*60 + "\n")
    
    # 选择运行模式
    print("请选择运行模式:")
    print("1. 交互模式 (检测需要添加的值并询问是否添加)")
    print("2. 自动模式 (直接添加值到ExcelA的第一列)")
    
    choice = input("请输入选择 (1 或 2): ").strip()
    
    if choice == "1":
        main_add_missing_to_first_column()
    elif choice == "2":
        enhanced_main_add_missing_to_first_column()
    else:
        print("无效选择，使用默认的交互模式。")
        main_add_missing_to_first_column()
    
    print("\n" + "="*60)