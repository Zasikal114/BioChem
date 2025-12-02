import pandas as pd
import numpy as np
import os

def sort_excel_by_rules():
    """
    对Excel文件进行排序，在原文件上直接修改
    排序规则：
    1. 先按TYPE列，值为"common"的行排在前面，其他值视为同等
    2. 对于TYPE列相同的行，按所有以"Pathway："开头的列从左到右排序，1排在0上面
    3. 保持无法确定顺序的行的原始相对顺序
    """
    
    # ========== 在这里修改文件路径 ==========
    file_path = r"C:\Users\lenovo\Desktop\jython\Table\node table.xlsx"  # 请修改为您的Excel文件路径
    # ======================================
    
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"错误: 文件不存在 - {file_path}")
            return
        
        # 读取Excel文件
        print(f"正在读取文件: {file_path}")
        df = pd.read_excel(file_path)
        print(f"原始数据形状: {df.shape} (行数: {len(df)}, 列数: {len(df.columns)})")
        
        # 显示所有列名
        print(f"所有列名: {list(df.columns)}")
        
        # 识别列
        type_column = "TYPE"
        pathway_columns = [col for col in df.columns if col.startswith('Pathway：')]
        
        print(f"找到TYPE列 '{type_column}': {type_column in df.columns}")
        if type_column in df.columns:
            print(f"TYPE列的值分布:\n{df[type_column].value_counts()}")
        
        print(f"找到 {len(pathway_columns)} 个Pathway列: {pathway_columns}")
        
        if type_column not in df.columns:
            print(f"错误: 未找到TYPE列 '{type_column}'")
            print("请检查列名是否正确（注意大小写）")
            return
        
        if len(pathway_columns) == 0:
            print("警告: 未找到以'Pathway：'开头的列")
        
        
        
        # 创建排序键列
        print("\n开始排序...")
        
        # 第一优先级：TYPE列（common在前，其他值视为同等）
        df['_temp_type'] = df[type_column].apply(
            lambda x: 0 if str(x).strip().lower() == 'common' else 1
        )
        
        # 为每个Pathway列创建排序键（1在前，0在后）
        for i, col in enumerate(pathway_columns):
            df[f'_temp_pathway_{i}'] = df[col].apply(
                lambda x: 0 if pd.notna(x) and str(x).strip() == '1' else 
                (1 if pd.notna(x) and str(x).strip() == '0' else 2)
            )
        
        # 构建排序列列表 - 先按TYPE排，然后按所有Pathway列从左到右排
        sort_columns = ['_temp_type'] + [f'_temp_pathway_{i}' for i in range(len(pathway_columns))]
        
        print(f"使用的排序列: {sort_columns}")
        
        # 进行排序
        df_sorted = df.sort_values(by=sort_columns, ascending=True)
        
        # 删除临时列
        df_sorted = df_sorted.drop(columns=sort_columns)
        
        # 保存回原文件（覆盖）
        df_sorted.to_excel(file_path, index=False)
        print(f"排序完成！已覆盖原文件: {file_path}")
        print(f"排序后数据形状: {df_sorted.shape} (行数: {len(df_sorted)}, 列数: {len(df_sorted.columns)})")
        
        
        # 比较排序前后的差异
        if not df.equals(df_sorted):
            print("\n排序已生效 - 文件内容已更改")
        else:
            print("\n警告: 排序前后文件内容相同，可能是所有行已经按正确顺序排列")
            
    except FileNotFoundError:
        print(f"错误: 找不到文件 {file_path}")
        print("请检查文件路径是否正确")
    except Exception as e:
        print(f"发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

# 直接运行函数
if __name__ == "__main__":
    sort_excel_by_rules()