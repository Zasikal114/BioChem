import pandas as pd
import numpy as np

def mark_pathways_simple():
    """简化的代谢通路标记函数，直接在原文件上修改"""
    
    # 在这里修改文件路径
    NODE_FILE = r"C:\Users\lenovo\Desktop\jython\Table\node table.xlsx"  # 节点表文件路径
    EDGE_FILE = r"C:\Users\lenovo\Desktop\jython\Table\edge table.xlsx"  # 边表文件路径
    
    print("=" * 50)
    print("开始处理代谢通路数据")
    print("=" * 50)
    
    try:
        # 1. 读取节点表
        print(f"步骤1: 读取节点表 {NODE_FILE}")
        nodes_df = pd.read_excel(NODE_FILE)
        print(f"  ✓ 成功读取节点表，共 {len(nodes_df)} 行，{len(nodes_df.columns)} 列")
        print(f"  ✓ 列名: {list(nodes_df.columns)}")
        print(f"  ✓ 前5个节点ID: {list(nodes_df.iloc[:5, 0])}")
        
        # 2. 读取边表
        print(f"\n步骤2: 读取边表 {EDGE_FILE}")
        edges_df = pd.read_excel(EDGE_FILE)
        print(f"  ✓ 成功读取边表，共 {len(edges_df)} 行，{len(edges_df.columns)} 列")
        print(f"  ✓ 列名: {list(edges_df.columns)}")
        
        # 3. 检查边表格式
        print("\n步骤3: 检查边表格式")
        if len(edges_df.columns) < 4:
            print(f"  ✗ 错误: 边表只有 {len(edges_df.columns)} 列，需要至少4列")
            return False
        
        pathway_col_name = edges_df.columns[3]
        print(f"  ✓ 通路列名: '{pathway_col_name}'")
        print(f"  ✓ 边表前5行通路信息:")
        for i in range(min(5, len(edges_df))):
            print(f"    第{i+1}行: 源={edges_df.iloc[i,0]}, 目标={edges_df.iloc[i,1]}, 通路={edges_df.iloc[i,3]}")
        
        # 4. 提取所有通路名称
        print("\n步骤4: 提取通路名称")
        # 跳过标题行，获取所有不重复的通路名称
        pathway_names = []
        for i in range(1, len(edges_df)):  # 从第2行开始
            pathway = edges_df.iloc[i, 3]
            if pd.notna(pathway) and pathway not in pathway_names and pathway != 'Pathway':
                pathway_names.append(pathway)
        
        print(f"  ✓ 发现 {len(pathway_names)} 个通路: {pathway_names}")
        
        if not pathway_names:
            print("  ✗ 错误: 未发现有效的通路名称")
            return False
        
        # 5. 在节点表中创建通路列
        print("\n步骤5: 在节点表中创建通路列")
        new_columns_added = 0
        for pathway in pathway_names:
            col_name = f'Pathway：{pathway}'
            if col_name not in nodes_df.columns:
                nodes_df[col_name] = 0
                new_columns_added += 1
                print(f"  ✓ 添加列: {col_name}")
            else:
                print(f"  ⓘ 列已存在: {col_name}")
        
        print(f"  ✓ 共添加了 {new_columns_added} 个新列")
        
        # 6. 标记属于通路的节点
        print("\n步骤6: 标记属于通路的节点")
        marked_nodes_count = 0
        
        for i in range(1, len(edges_df)):  # 从第2行开始
            source_node = str(edges_df.iloc[i, 0])
            target_node = str(edges_df.iloc[i, 1])
            pathway = edges_df.iloc[i, 3]
            
            # 跳过无效行
            if pd.isna(pathway) or pathway == 'Pathway':
                continue
            
            col_name = f'Pathway：{pathway}'
            
            # 标记源节点
            source_mask = nodes_df.iloc[:, 0].astype(str) == source_node
            if source_mask.any():
                nodes_df.loc[source_mask, col_name] = 1
                marked_nodes_count += source_mask.sum()
                print(f"  ✓ 标记节点 '{source_node}' 属于通路 '{pathway}'")
            else:
                print(f"  ⚠ 警告: 源节点 '{source_node}' 在节点表中未找到")
            
            # 标记目标节点
            target_mask = nodes_df.iloc[:, 0].astype(str) == target_node
            if target_mask.any():
                nodes_df.loc[target_mask, col_name] = 1
                marked_nodes_count += target_mask.sum()
                print(f"  ✓ 标记节点 '{target_node}' 属于通路 '{pathway}'")
            else:
                print(f"  ⚠ 警告: 目标节点 '{target_node}' 在节点表中未找到")
        
        # 7. 统计标记结果
        print("\n步骤7: 统计标记结果")
        total_marks = 0
        for pathway in pathway_names:
            col_name = f'Pathway：{pathway}'
            if col_name in nodes_df.columns:
                mark_count = nodes_df[col_name].sum()
                total_marks += mark_count
                print(f"  ✓ 通路 '{pathway}': {int(mark_count)} 个节点被标记")
        
        print(f"  ✓ 总共标记了 {total_marks} 个节点-通路关系")
        
        # 8. 保存回原文件
        print(f"\n步骤8: 保存回原文件 {NODE_FILE}")
        nodes_df.to_excel(NODE_FILE, index=False)
        print("  ✓ 文件保存成功！")
        
        # 9. 最终统计
        print("\n" + "=" * 50)
        print("处理完成！")
        print("=" * 50)
        print(f"节点表: {NODE_FILE}")
        print(f"边表: {EDGE_FILE}")
        print(f"处理边数: {len(edges_df)-1}")
        print(f"发现通路数: {len(pathway_names)}")
        print(f"总节点数: {len(nodes_df)}")
        print(f"标记的节点-通路关系数: {total_marks}")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 处理过程中出现错误: {e}")
        import traceback
        print("详细错误信息:")
        print(traceback.format_exc())
        return False

# 运行函数
if __name__ == "__main__":
    # 直接运行函数
    success = mark_pathways_simple()
    
    if success:
        print("\n🎉 程序执行成功！")
    else:
        print("\n💥 程序执行失败，请检查上述错误信息。")
    
    # 暂停以便查看结果（Windows系统）
    input("\n按Enter键退出...")