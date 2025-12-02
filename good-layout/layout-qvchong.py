import py4cytoscape as p4c
import math
import os

def layout_path_way_nodes_calculated():
    """通过计算只设置path_way节点的XY坐标，不修改其他节点，且跳过已设置过的节点"""
    try:
        # 1. 检查 Cytoscape 连接
        p4c.cytoscape_ping()
        print("✓ 成功连接到 Cytoscape")
        
        # 2. 检查是否有网络加载
        network_list = p4c.get_network_list()
        if not network_list:
            print("❌❌❌❌❌❌❌❌ 当前没有加载任何网络")
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
            print("❌❌❌❌❌❌❌❌ 网络中没有节点")
            return False
        
        print(f"✓ 找到 {len(node_table)} 个节点")
        
        # 5. 获取所有Pathway列
        path_way_columns = [col for col in node_table.columns if col.startswith('Pathway:')]
        if not path_way_columns:
            print("❌❌❌❌❌❌❌❌ 节点表中没有找到任何 'Pathway:' 列")
            print(f"可用列: {list(node_table.columns)}")
            return False
        
        print(f"✓ 找到 {len(path_way_columns)} 个Pathway列: {path_way_columns}")
        
        # 6. 确定当前筛选列
        target_column = 'Pathway:fatty acid synthesis'
        if target_column not in path_way_columns:
            print(f"❌❌❌❌❌❌❌❌ 目标列 '{target_column}' 不存在")
            return False
        
        # 7. 读取已设置坐标的节点记录文件
        record_file = "positioned_nodes.txt"
        positioned_nodes = set()
        
        if os.path.exists(record_file):
            with open(record_file, 'r') as f:
                positioned_nodes = set(line.strip() for line in f if line.strip())
            print(f"✓ 从 {record_file} 中读取到 {len(positioned_nodes)} 个已设置坐标的节点")
        else:
            print(f"✓ 记录文件 {record_file} 不存在，将创建新文件")
        
        # 8. 筛选出目标列值为1的节点
        # 将列转换为字符串类型进行比较，避免数据类型不一致的问题
        path_way_values = node_table[target_column].astype(str)
        
        # 筛选path_way节点（值为字符串"1"）
        target_nodes = node_table[path_way_values == "1"]
        
        if target_nodes.empty:
            print(f"❌❌❌❌❌❌❌❌ 没有找到 {target_column} 值为 1 的节点")
            unique_values = node_table[target_column].unique()
            print(f"{target_column} 列的唯一值: {unique_values}")
            return False
        
        print(f"✓ 找到 {len(target_nodes)} 个 {target_column} 值为 1 的节点")
        
        # 9. 过滤掉已设置过坐标的节点
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
        
        print(f"✓ 过滤结果:")
        print(f"  - 需要设置坐标的节点: {len(nodes_to_layout)}")
        print(f"  - 跳过的节点: {len(skipped_nodes)}")
        
        if skipped_nodes:
            print("  跳过的节点详情:")
            for skipped in skipped_nodes:
                print(f"    - {skipped['name']}: {skipped['skip_reason']}")
        
        if not nodes_to_layout:
            print("❌❌❌❌❌❌❌❌ 没有需要设置坐标的节点")
            return False
        
        # 10. 为需要设置的节点计算环形布局
        center_x, center_y = 2000, -1000  # 环形中心坐标
        radius = 300  # 环形半径
        
        # 计算每个节点的角度
        angle_step = 2 * math.pi / len(nodes_to_layout)
        
        print("✓ 开始计算节点环形布局")
        
        for i, node_info in enumerate(nodes_to_layout):
            angle = i * angle_step
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            
            # 使用节点名称设置节点位置
            p4c.set_node_property_bypass(
                node_names=[node_info['name']],
                visual_property='NODE_X_LOCATION',
                new_values=[x]
            )
            p4c.set_node_property_bypass(
                node_names=[node_info['name']],
                visual_property='NODE_Y_LOCATION',
                new_values=[y]
            )
        
        # 11. 将本次设置的节点添加到记录文件中
        with open(record_file, 'a') as f:
            for node_info in nodes_to_layout:
                f.write(node_info['suid'] + '\n')
        
        # 更新已设置坐标的节点集合
        positioned_nodes.update(node_info['suid'] for node_info in nodes_to_layout)
        
        print(f"✓ 已完成 {len(nodes_to_layout)} 个节点的环形布局")
        print(f"  - 中心位置: ({center_x}, {center_y})")
        print(f"  - 环形半径: {radius}")
        print(f"✓ 已将 {len(nodes_to_layout)} 个节点添加到记录文件 {record_file}")
        
        return True
        
    except Exception as e:
        print(f"❌❌❌❌❌❌❌❌ 执行过程中出现错误: {str(e)}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return False

# 运行函数
if __name__ == "__main__":
    print("=== 智能布局path_way节点 (基于历史记录) ===")
    success = layout_path_way_nodes_calculated()
    
    if success:
        print("\n✓ 布局完成！已跳过已设置过坐标的节点")