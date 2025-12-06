
#某pathway为1的节点减去common节点，作为被设置的节点，同时已经设置过的节点不进行自动设置。
#在node table中应该有相对X坐标和相对Y坐标列。要求AI给出csv格式，打开并粘贴到相应位置。
#node table中也应该有一个是否已经设置过的列来给AI和人类阅读
#……需要补充想法
import py4cytoscape as p4c
import math
import os
import pandas as pd

p4c.set_node_position_bypass(
    node_names=['glucose'],
    new_x_locations=[0],
    new_y_locations=[0]
)

def layout_path_way_nodes_calculated(refer,pathway):
    """通过计算只设置path_way节点的XY坐标，不修改其他节点，且跳过已设置过的节点"""
    try:
        # 1. 检查 Cytoscape 连接
        p4c.cytoscape_ping()
        print("✓ 成功连接到 Cytoscape")
        
        # 2. 检查是否有网络加载
        network_list = p4c.get_network_list()
        if not network_list:
            print("❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌ 当前没有加载任何网络")
            return False
        
        current_network = network_list[0]
        network_name = p4c.get_network_name(current_network)
        print(f"✓ 当前网络: {network_name} (SUID: {current_network})")
        
        # 3. 明确设置当前网络
        p4c.set_current_network(current_network)
        print("✓ 已设置当前网络")
        
        # 4. 获取所有节点
        node_table = p4c.get_table_columns(table='node')
        if node_table.empty:
            print("❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌ 网络中没有节点")
            return False
        
        print(f"✓ 找到 {len(node_table)} 个节点")
        
        # 5. 获取所有Pathway列
        path_way_columns = [col for col in node_table.columns if col.startswith('Pathway:')]
        if not path_way_columns:
            print("❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌ 节点表中没有找到任何 'Pathway:' 列")
            print(f"可用列: {list(node_table.columns)}")
            return False
        
        print(f"✓ 找到 {len(path_way_columns)} 个Pathway列: {path_way_columns}")
        
        # 6. 确定当前筛选列
        target_column = f'Pathway:{pathway}'
        if target_column not in path_way_columns:
            print(f"❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌ 目标列 '{target_column}' 不存在")
            return False
        
        
        
        # 9. 读取已设置坐标的节点记录文件
        record_file = "positioned_nodes.txt"
        positioned_nodes = set()
        
        if os.path.exists(record_file):
            with open(record_file, 'r') as f:
                positioned_nodes = set(line.strip() for line in f if line.strip())
            print(f"✓ 从 {record_file} 中读取到 {len(positioned_nodes)} 个已设置坐标的节点")
        else:
            print(f"✓ 记录文件 {record_file} 不存在，将创建新文件")
        
        # 10. 筛选出目标列值为1的节点
        path_way_values = node_table[target_column].astype(str)
        target_nodes = node_table[path_way_values == "1"]
        
        if target_nodes.empty:
            print(f"❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌ 没有找到 {target_column} 值为 1 的节点")
            unique_values = node_table[target_column].unique()
            print(f"{target_column} 列的唯一值: {unique_values}")
            return False
        
        print(f"✓ 找到 {len(target_nodes)} 个 {target_column} 值为 1 的节点")
        
        # 11. 过滤掉已设置过坐标的节点
        nodes_to_layout = []
        skipped_nodes = []
        
        for _, node in target_nodes.iterrows():
            suid = str(node['SUID'])
            node_name = node.get('name', f"SUID_{suid}")
            
            # 检查节点是否已设置过坐标
            if suid in positioned_nodes:
                skipped_nodes.append({
                    'suid': suid,
                    'name': node_name,
                    'skip_reason': "已设置过坐标"
                })
                continue
            
            
            # 使用节点名称而不是SUID
            nodes_to_layout.append({
                'suid': suid,
                'name': node_name
            })
            print(node_name)
        
        print(f"✓ 过滤结果:")
        #print(nodes_to_layout['name'])
        print(f"  - 需要设置坐标的节点: {len(nodes_to_layout)}")
        print(f"  - 跳过的节点: {len(skipped_nodes)}")
        
        if skipped_nodes:
            print("  跳过的节点详情:")
            for skipped in skipped_nodes:
                print(f"    - {skipped['name']}: {skipped['skip_reason']}")
        
        if not nodes_to_layout:
            print("❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌ 没有需要设置坐标的节点")
            return False
        
        # 7. 读取Excel文件，获取相对坐标
        excel_file = r'C:\Users\lenovo\Desktop\jython\Table\node table.xlsx'
        try:
            df = pd.read_excel(excel_file)
            print(f"✓ 成功读取Excel文件: {excel_file}")
        
        except Exception as e:
            print(f"❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌ 读取Excel文件失败: {str(e)}")
            return False
        
        # 检查Excel文件是否包含必要的列
        required_columns = ['ID', 'X', 'Y']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌ Excel文件中缺少必要的列: {missing_columns}")
            return False
        
        # 8. 获取参考节点的当前坐标
        refer_node_info = p4c.get_node_property(node_names=refer, visual_property='NODE_X_LOCATION')
        if not refer_node_info or refer not in refer_node_info:
            print(f"❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌ 无法获取参考节点 '{refer}' 的坐标")
            return False
        
        refer_x = refer_node_info[refer]
        refer_y_info = p4c.get_node_property(node_names=refer, visual_property='NODE_Y_LOCATION')
        refer_y = refer_y_info[refer] if refer_y_info and refer in refer_y_info else 0
        
        print(f"✓ 参考节点 '{refer}' 的坐标: X={refer_x}, Y={refer_y}")

        # 12. 为需要设置的节点计算坐标
        print("✓ 开始设置节点坐标")
        
        # 创建副本用于保存绝对坐标
        df_absolute = df.copy()
        
        for i, node_info in enumerate(nodes_to_layout):
            node_name = node_info['name']
            
            # 检查节点是否在Excel文件中
            if node_name not in df['ID'].values:
                skipped_nodes.append({
                    'suid': suid,
                    'name': node_name,
                    'skip_reason': "Excel文件中找不到对应的ID"
                })
                continue

            # 从Excel中获取相对坐标
            node_row = df[df['ID'] == node_name]
            if node_row.empty:
                print(f"❌ 警告: 在Excel中找不到节点 {node_name} 的相对坐标")
                continue
            
            relative_x = node_row['X'].iloc[0]
            relative_y = node_row['Y'].iloc[0]
            
            # 计算绝对坐标
            x = int(refer_x + relative_x)
            y = int(refer_y + relative_y)
            
            print(f"  设置节点 {node_name}: 相对坐标({relative_x}, {relative_y}) -> 绝对坐标({x}, {y})")
            
            # 使用节点名称设置节点位置
            p4c.set_node_property_bypass(
                node_names=[node_name],
                visual_property='NODE_X_LOCATION',
                new_values=[x]
            )
            p4c.set_node_property_bypass(
                node_names=[node_name],
                visual_property='NODE_Y_LOCATION',
                new_values=[y]
            )
            
            # 在副本中更新绝对坐标
            df_absolute.loc[df_absolute['ID'] == node_name, 'X'] = x
            df_absolute.loc[df_absolute['ID'] == node_name, 'Y'] = y
        
        # 13. 将绝对坐标写回Excel文件
        
        try:
            df_absolute.to_excel(excel_file, index=False)
            print(f"✓ 已将绝对坐标写回Excel文件: {excel_file}")
        except Exception as e:
            print(f"❌ 警告: 写回Excel文件失败: {str(e)}")
        
        
        
        # 14. 将本次设置的节点添加到记录文件中
        with open(record_file, 'a') as f:
            for node_info in nodes_to_layout:
                f.write(node_info['suid'] + '\n')
        
        # 更新已设置坐标的节点集合
        positioned_nodes.update(node_info['suid'] for node_info in nodes_to_layout)
        
        print(f"✓ 已完成 {len(nodes_to_layout)} 个节点的布局")
        print(f"✓ 已将 {len(nodes_to_layout)} 个节点添加到记录文件 {record_file}")
        
        return True
        
    except Exception as e:
        print(f"❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌ 执行过程中出现错误: {str(e)}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return False

# 运行函数
if __name__ == "__main__":
    print("=== 智能布局path_way节点 (基于历史记录) ===")
    node_name_refer = "glucose"  # 在这里设置参考节点的名称
    pathway = "glycolysis"  # 在这里设置目标Pathway名称
    success = layout_path_way_nodes_calculated(node_name_refer,pathway)
    
    if success:
        print("\n✓ 布局完成！已跳过已设置过坐标的节点")