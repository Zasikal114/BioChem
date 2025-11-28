import pandas as pd
from itertools import chain

def find_unique_cells(file_path):
    # 读取Excel文件的前两列
    try:
        df = pd.read_excel(file_path, usecols=[0, 1], header=None)
    except Exception as e:
        print(f"读取文件时出错: {e}")
        return
    
    # 将前两列的数据展平为一维列表，并去除NaN值
    all_cells = list(chain.from_iterable(df.values.T.tolist()))
    cleaned_cells = [cell for cell in all_cells if pd.notna(cell)]
    
    # 使用集合记录已出现的内容
    seen = set()
    unique_cells = []
    
    for cell in cleaned_cells:
        # 转换为字符串进行比较，确保类型一致性
        str_cell = str(cell).strip()
        if str_cell not in seen:
            seen.add(str_cell)
            unique_cells.append(cell)
    
    # 输出结果
    print("去重后的单元格内容：")
    for i, cell in enumerate(unique_cells, 1):
        print(f"{i}: {cell}")

if __name__ == "__main__":
    # 在这里修改为您的Excel文件路径
    file_path = r"C:\Users\lenovo\Desktop\Biochem\Table\edge_table_11.23.xlsx"  # 请修改为实际路径
    
    # 如果是Mac或Linux系统，使用类似这样的路径
    # file_path = "/home/username/path/to/excel_file.xlsx"
    
    find_unique_cells(file_path)
    
    # 添加一个暂停，以便在Windows命令行中查看结果
    input("\n按Enter键退出...")