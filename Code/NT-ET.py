import pandas as pd
import numpy as np

def find_missing_values(excelA_path, excelB_path, sheetA=0, sheetB=0):
    """
    检测excelA中第一列的单元格内容是否都在excelB的前两列单元格中出现
    修复了数据比较逻辑，确保准确性
    """
    
    try:
        # 读取Excel文件，确保正确处理空值
        df_A = pd.read_excel(excelA_path, sheet_name=sheetA, header=None, dtype=str)
        df_B = pd.read_excel(excelB_path, sheet_name=sheetB, header=None, dtype=str)
        
        print(f"ExcelA 行数: {len(df_A)}")
        print(f"ExcelB 行数: {len(df_B)}")
        
        # 获取ExcelA第一列的值
        col_A = df_A.iloc[:, 0].dropna()  # 去除NaN值
        col_A = col_A.astype(str).str.strip()
        col_A = col_A[col_A != '']  # 去除空字符串
        col_A = col_A.unique()  # 去重
        
        print(f"ExcelA第一列有效值数量: {len(col_A)}")
        
        # 获取ExcelB前两列的值
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

def enhanced_find_missing_values(excelA_path, excelB_path, sheetA=0, sheetB=0, debug=False):
    """
    增强版本，提供更详细的调试信息
    """
    
    try:
        # 读取Excel文件
        df_A = pd.read_excel(excelA_path, sheet_name=sheetA, header=None, dtype=str)
        df_B = pd.read_excel(excelB_path, sheet_name=sheetB, header=None, dtype=str)
        
        if debug:
            print("=" * 50)
            print("调试信息:")
            print(f"ExcelA 形状: {df_A.shape}")
            print(f"ExcelB 形状: {df_B.shape}")
            print(f"ExcelA 第一列前10个值:")
            print(df_A.iloc[:10, 0].tolist())
            print(f"ExcelB 第一列前10个值:")
            print(df_B.iloc[:10, 0].tolist())
            print(f"ExcelB 第二列前10个值:")
            print(df_B.iloc[:10, 1].tolist())
            print("=" * 50)
        
        # 处理ExcelA第一列
        col_A = df_A.iloc[:, 0].dropna().astype(str)
        col_A = col_A.str.strip()
        col_A = col_A[col_A != '']
        col_A = col_A.unique()
        
        # 处理ExcelB前两列
        col_B_values = []
        for col_idx in [0, 1]:  # 前两列
            col = df_B.iloc[:, col_idx].dropna().astype(str)
            col = col.str.strip()
            col = col[col != '']
            col_B_values.extend(col.tolist())
        
        set_B = set(col_B_values)
        
        if debug:
            print(f"ExcelA唯一值数量: {len(col_A)}")
            print(f"ExcelB前两列唯一值数量: {len(set_B)}")
            print(f"ExcelA示例值: {list(col_A[:10])}")
            print(f"ExcelB示例值: {list(list(set_B)[:10])}")
        
        # 详细比较
        missing_values = []
        found_values = []
        
        for value in col_A:
            if value in set_B:
                found_values.append(value)
            else:
                missing_values.append(value)
        
        if debug:
            print(f"匹配到的值数量: {len(found_values)}")
            print(f"缺失的值数量: {len(missing_values)}")
            if found_values:
                print(f"匹配示例: {found_values[:5]}")
        
        return missing_values
        
    except Exception as e:
        print(f"处理过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return []

def main():
    # 请修改为您的实际文件路径
    excelA_path = r"C:\Users\lenovo\Desktop\jython\Table\node table.xlsx"  # 修改为您的ExcelA文件路径
    excelB_path = r"C:\Users\lenovo\Desktop\jython\Table\edge table.xlsx"  # 修改为您的ExcelB文件路径
    
    print("开始检测缺失值...")
    print(f"ExcelA文件: {excelA_path}")
    print(f"ExcelB文件: {excelB_path}")
    print("-" * 50)
    
    # 使用基本版本
    missing_values = find_missing_values(excelA_path, excelB_path)
    
    # 输出结果
    if missing_values:
        print(f"\n以下 {len(missing_values)} 个值在ExcelB的前两列中未出现:")
        print("-" * 50)
        for i, value in enumerate(missing_values, 1):
            print(f"{i}. {value}")
    else:
        print("ExcelA第一列的所有值都在ExcelB的前两列中出现了！")
    

if __name__ == "__main__":
    
    print("\n" + "="*60 + "\n")
    
    # 然后运行主程序处理您的实际文件
    # 请取消注释下面的行来处理您的实际文件
    
    main()
    
    # 或者使用增强版本（推荐）
    # missing_values = enhanced_find_missing_values(
    #     "excelA.xlsx",  # 修改为您的实际文件路径
    #     "excelB.xlsx",  # 修改为您的实际文件路径
    #     debug=True
    # )