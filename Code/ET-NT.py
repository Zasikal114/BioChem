import pandas as pd
from itertools import chain

def find_unique_cells(file_a_path, file_b_path):
    # 读取文件A的前两列
    try:
        df_a = pd.read_excel(file_a_path, usecols=[0, 1], header=None)
    except Exception as e:
        print(f"读取文件A时出错: {e}")
        return
    
    # 读取文件B的第一列
    try:
        df_b = pd.read_excel(file_b_path, usecols=[0], header=None)
    except Exception as e:
        print(f"读取文件B时出错: {e}")
        return
    
    # 将文件A前两列的数据展平为一维列表，并去除NaN值
    all_cells_a = list(chain.from_iterable(df_a.values.T.tolist()))
    cleaned_cells_a = [str(cell).strip() for cell in all_cells_a if pd.notna(cell)]
    
    # 将文件B第一列的数据转换为集合，用于快速查找，并去除NaN值
    cells_b_set = set(str(cell).strip() for cell in df_b[0].values if pd.notna(cell))
    
    # 使用集合记录已出现的内容
    seen = set()
    unique_cells = []
    
    for cell in cleaned_cells_a:
        # 如果内容不在文件B中且尚未出现过
        if cell not in cells_b_set and cell not in seen:
            seen.add(cell)
            unique_cells.append(cell)
    
    # 输出结果
    print(f"文件A中去重后且不在文件B中的单元格内容（共{len(unique_cells)}个）:")
    for i, cell in enumerate(unique_cells, 1):
        print(f"{cell}")

if __name__ == "__main__":
    # 在这里修改为您的Excel文件路径
    file_a_path = r"C:\Users\lenovo\Desktop\jython\Table\edge table.xlsx"  # 请修改为文件A的实际路径
    file_b_path = r"C:\Users\lenovo\Desktop\jython\Table\node table.xlsx"  # 请修改为文件B的实际路径
    
    find_unique_cells(file_a_path, file_b_path)
    
    # 添加一个暂停，以便在Windows命令行中查看结果
    input("\n按Enter键退出...")