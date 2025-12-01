import pandas as pd
import numpy as np
import os
import shutil
from datetime import datetime

def find_missing_values(excelA_path, excelB_path, sheetA=0, sheetB=0, has_header=True):
    """
    检测excelA中第一列的单元格内容是否都在excelB的前两列单元格中出现
    修复了数据比较逻辑，确保准确性
    """
    
    try:
        # 读取Excel文件，确保正确处理空值
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
            col_A = df_A.iloc[:, 0].dropna()  # 去除NaN值
        else:
            col_A = df_A.iloc[:, 0].dropna()  # 去除NaN值
            
        col_A = col_A.astype(str).str.strip()
        col_A = col_A[col_A != '']  # 去除空字符串
        col_A = col_A.unique()  # 去重
        
        print(f"ExcelA第一列有效值数量: {len(col_A)}")
        
        # 获取ExcelB前两列的值
        if has_header:
            col_B1 = df_B.iloc[:, 0].dropna().astype(str).str.strip()
            col_B2 = df_B.iloc[:, 1].dropna().astype(str).str.strip()
        else:
            col_B1 = df_B.iloc[:, 0].dropna().astype(str).str.strip()
            col_B2 = df_B.iloc[:, 1].dropna().astype(str).str.strip()
        
        # 合并B表前两列的值
        col_B_combined = pd.concat([col_B1, col_B2])
        col_B_combined = col_B_combined[col_B_combined != '']  # 去除空字符串
        set_B = set(col_B_combined.unique())  # 转换为集合并去重
        
        print(f"ExcelB前两列有效值数量: {len(set_B)}")
        
        # 调试信息：显示前几个值
        print(f"ExcelA前5个值: {list(col_A[:5])}")
        print(f"ExcelB前5个值: {list(list(set_B)[:5])}")
        
        # 找出在A中出现但不在B中出现的值
        missing_values = []
        for value in col_A:
            if value not in set_B:
                missing_values.append(value)
        
        print(f"找到缺失值数量: {len(missing_values)}")
        return missing_values
        
    except Exception as e:
        print(f"处理过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return []

def remove_missing_rows_preserve_header(excelA_path, excelB_path, sheetA=0, sheetB=0, has_header=True):
    """
    删除ExcelA中第一列的值在ExcelB前两列中不存在的行
    保留表头，直接在原文件上修改，并创建备份
    """
    try:
        # 创建备份文件
        backup_path = create_backup(excelA_path)
        print(f"已创建备份文件: {backup_path}")
        
        # 读取Excel文件，保留表头
        if has_header:
            df_A = pd.read_excel(excelA_path, sheet_name=sheetA, header=0, dtype=str)
            df_B = pd.read_excel(excelB_path, sheet_name=sheetB, header=0, dtype=str)
        else:
            df_A = pd.read_excel(excelA_path, sheet_name=sheetA, header=None, dtype=str)
            df_B = pd.read_excel(excelB_path, sheet_name=sheetB, header=None, dtype=str)
        
        original_rows = len(df_A)
        print(f"原始ExcelA行数: {original_rows}")
        
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
        
        # 标记需要保留的行（第一列的值在B中出现）
        rows_to_keep = []
        missing_rows = []
        
        for idx, row in df_A.iterrows():
            # 获取第一列的值并处理
            value = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ""
            value = value.strip()
            
            # 如果值是空或者不在B中，则标记为需要删除
            if value == "" or value not in set_B:
                missing_rows.append((idx, value))
            else:
                rows_to_keep.append(idx)
        
        # 保留需要的行
        df_cleaned = df_A.loc[rows_to_keep]
        
        removed_count = original_rows - len(df_cleaned)
        print(f"删除的行数: {removed_count}")
        print(f"处理后行数: {len(df_cleaned)}")
        
        # 保存处理后的文件（覆盖原文件）
        if has_header:
            df_cleaned.to_excel(excelA_path, index=False, header=True)
        else:
            df_cleaned.to_excel(excelA_path, index=False, header=False)
        
        print(f"已直接在原文件上修改: {excelA_path}")
        
        return df_cleaned, removed_count, missing_rows
        
    except Exception as e:
        print(f"处理过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return None, 0, []

def create_backup(file_path):
    """
    创建文件备份
    """
    try:
        # 获取文件目录和文件名
        dir_name = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        name, ext = os.path.splitext(file_name)
        
        # 生成备份文件名（添加时间戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{name}_backup_{timestamp}{ext}"
        backup_path = os.path.join(dir_name, backup_name)
        
        # 复制文件
        shutil.copy2(file_path, backup_path)
        return backup_path
    except Exception as e:
        print(f"创建备份失败: {e}")
        # 如果备份失败，仍然继续处理
        return None

def main():
    # 请修改为您的实际文件路径
    excelA_path = r"C:\Users\lenovo\Desktop\jython\Table\node table.xlsx"  # 修改为您的ExcelA文件路径
    excelB_path = r"C:\Users\lenovo\Desktop\jython\Table\edge table.xlsx"  # 修改为您的ExcelB文件路径
    
    # 确认文件是否有表头
    has_header = True  # 默认有表头，如果您的文件没有表头，请设置为False
    
    print("开始检测缺失值...")
    print(f"ExcelA文件: {excelA_path}")
    print(f"ExcelB文件: {excelB_path}")
    print(f"文件是否有表头: {'是' if has_header else '否'}")
    print("-" * 50)
    
    # 使用基本版本检测缺失值
    missing_values = find_missing_values(excelA_path, excelB_path, has_header=has_header)
    
    # 输出检测结果
    if missing_values:
        print(f"\n以下 {len(missing_values)} 个值在ExcelB的前两列中未出现:")
        print("-" * 50)
        for i, value in enumerate(missing_values, 1):
            print(f"{i}. {value}")
        
        # 询问用户是否要删除这些行
        response = input("\n是否要删除包含这些值的行？(y/n): ")
        if response.lower() in ['y', 'yes', '是']:
            print("\n开始删除缺失值所在的行...")
            print("-" * 50)
            
            # 删除缺失值所在的行
            df_cleaned, removed_count, missing_rows = remove_missing_rows_preserve_header(
                excelA_path, excelB_path, has_header=has_header
            )
            
            if df_cleaned is not None:
                print(f"\n处理完成！删除了 {removed_count} 行。")
                print(f"已直接在原文件上修改: {excelA_path}")
                
                # 显示删除的行的详细信息（前10行）
                if missing_rows:
                    print(f"\n删除的前10行信息:")
                    print("-" * 30)
                    for i, (row_idx, value) in enumerate(missing_rows[:10]):
                        # 调整行号显示（如果有表头，行号从2开始）
                        display_idx = row_idx + 2 if has_header else row_idx + 1
                        print(f"行 {display_idx}: 值='{value}'")
                    if len(missing_rows) > 10:
                        print(f"... 还有 {len(missing_rows) - 10} 行被删除")
            else:
                print("处理失败！")
        else:
            print("已取消删除操作。")
    else:
        print("ExcelA第一列的所有值都在ExcelB的前两列中出现了！")

def enhanced_main():
    """
    增强版主函数，直接执行删除操作
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
    
    # 直接执行删除操作
    df_cleaned, removed_count, missing_rows = remove_missing_rows_preserve_header(
        excelA_path, excelB_path, has_header=has_header
    )
    
    if df_cleaned is not None:
        print(f"\n处理完成！删除了 {removed_count} 行。")
        print(f"已直接在原文件上修改: {excelA_path}")
        
        # 显示删除的行的详细信息
        if missing_rows:
            print(f"\n删除的行信息 (前20行):")
            print("-" * 40)
            for i, (row_idx, value) in enumerate(missing_rows[:20]):
                # 调整行号显示（如果有表头，行号从2开始）
                display_idx = row_idx + 2 if has_header else row_idx + 1
                print(f"行 {display_idx}: 值='{value}'")
            if len(missing_rows) > 20:
                print(f"... 还有 {len(missing_rows) - 20} 行被删除")
    else:
        print("处理失败！")

if __name__ == "__main__":
    
    print("\n" + "="*60 + "\n")
    
    # 选择运行模式
    print("请选择运行模式:")
    print("1. 交互模式 (检测缺失值并询问是否删除)")
    print("2. 自动模式 (直接删除缺失值所在的行)")
    
    choice = input("请输入选择 (1 或 2): ").strip()
    
    if choice == "1":
        main()
    elif choice == "2":
        enhanced_main()
    else:
        print("无效选择，使用默认的交互模式。")
        main()
    
    print("\n" + "="*60)