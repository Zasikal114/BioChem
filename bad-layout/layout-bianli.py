import py4cytoscape as p4c
import math
import os
import pandas as pd
import networkx as nx

def layout_path_way_nodes_calculated(pathway,count):
    """通过计算只设置path_way节点的XY坐标，不修改其他节点，且跳过已设置过的节点"""
    try:
        
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
        target_column = f'{pathway}'
        if target_column not in path_way_columns:
            print(f"❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌ 目标列 '{target_column}' 不存在")
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
        #注释掉"[path_way_values == "1"]"后理论上就会选出所有节点
        if target_nodes.empty:
            print(f"❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌ 没有找到 {target_column} 值为 1 的节点")
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
            print("❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌ 没有需要设置坐标的节点")
            return False
        
        # 10. 读取边信息文件（替换为您的Excel文件路径）
        edge_file_path = r"C:\Users\lenovo\Desktop\jython\Table\edge table.xlsx"  # 请修改为实际路径
        try:
            edge_df = pd.read_excel(edge_file_path)
            # 确保列名正确
            if 'SOURCE' not in edge_df.columns or 'TARGET' not in edge_df.columns:
                # 尝试其他可能的列名
                possible_source_cols = ['source', 'Source', 'FROM', 'from']
                possible_target_cols = ['target', 'Target', 'TO', 'to']
                
                source_col = None
                target_col = None
                
                for col in edge_df.columns:
                    if col in possible_source_cols:
                        source_col = col
                    if col in possible_target_cols:
                        target_col = col
                
                if source_col and target_col:
                    edge_df = edge_df.rename(columns={source_col: 'SOURCE', target_col: 'TARGET'})
                else:
                    raise ValueError("无法找到SOURCE和TARGET列")
                    
            print(f"✓ 成功读取边信息文件，包含 {len(edge_df)} 条边")
        except Exception as e:
            print(f"❌ 读取边文件失败: {e}")
            return False
        #在下边添加一些代码来保证构建图时只用到了需要布局的节点
        # 过滤边，只保留那些目标节点在nodes_to_layout中的节点
        valid_node_names = set(node_info['name'] for node_info in nodes_to_layout)
        edge_df = edge_df[edge_df['TARGET'].isin(valid_node_names)]
        print(f"✓ 过滤后包含 {len(edge_df)} 条边用于布局计算")

        # 11. 构建有向图
        G = nx.DiGraph()
        
        # 添加边
        for _, row in edge_df.iterrows():
            source = str(row['SOURCE']).strip()
            target = str(row['TARGET']).strip()
            if source and target:  # 确保不为空
                G.add_edge(source, target)
        
        # 12. 确定起始节点
        # 寻找根节点（入度为0的节点）
        roots = [node for node in G.nodes() if G.in_degree(node) == 0]
        if roots:
            start_node = roots[0]
        else:
            # 如果没有根节点，选择第一个节点
            start_node = list(G.nodes())[0] if G.nodes() else None
        
        if start_node is None:
            print("图中没有节点")
            return False
        
        print(f"✓ 起始节点: {start_node}")
        

        # 13. 计算层次结构
        levels = {}
        visited = set()
        
        def assign_levels(node, current_level):
            if node in visited:
                return
            
            visited.add(node)
            
            if current_level not in levels:
                levels[current_level] = []
            levels[current_level].append(node)
            
            # 递归处理所有子节点
            for successor in G.successors(node):
                assign_levels(successor, current_level + 1)
        
        assign_levels(start_node, 0)
        
        # 14. 计算坐标
        node_positions = {}
        
        # 布局参数
        level_height = 100  # 每层的高度间隔
        node_width = 100    # 节点水平间隔
        start_x = 0 + 1000*count      # 起始X坐标
        start_y = 0 + 1000*count    # 起始Y坐标
        
        max_level = max(levels.keys()) if levels else 0
        
        for level, nodes in levels.items():
            # 计算当前层的Y坐标
            y = start_y + level * level_height
            
            # 计算当前层节点的X坐标（水平居中分布）
            level_width = len(nodes) * node_width
            level_start_x = start_x - level_width / 2
            
            # 对节点排序以确保一致性
            sorted_nodes = sorted(nodes)
            
            for i, node in enumerate(sorted_nodes):
                x = level_start_x + i * node_width
                node_positions[node] = (x, y)
        
        # 15. 如果有节点没有被访问到
        unvisited_nodes = set(G.nodes()) - visited
        if unvisited_nodes:
            print(f"✓ 检测到环，处理 {len(unvisited_nodes)} 个未访问节点")
            
            # 将节点放在右侧
            ring_start_x = start_x + (max_level + 1) * node_width
            ring_nodes = sorted(list(unvisited_nodes))
            
            # 环形布局节点
            ring_radius = 100
            center_x = ring_start_x
            center_y = start_y
            
            angle_step = 2 * math.pi / len(ring_nodes) if ring_nodes else 0
            
            for i, node in enumerate(ring_nodes):
                angle = i * angle_step
                x = center_x + ring_radius * math.cos(angle)
                y = center_y + ring_radius * math.sin(angle)
                node_positions[node] = (x, y)
        
        # 16. 为需要设置的节点应用树状布局
        print("✓ 开始计算节点树状布局")
        
        positioned_count = 0
        for node_info in nodes_to_layout:
            node_name = node_info['name']
            
            # 检查节点是否在树状布局中
            if node_name in node_positions:
                x, y = node_positions[node_name]
                
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
                
                positioned_count += 1
        
        # 17. 将本次设置的节点添加到记录文件中
        with open(record_file, 'a') as f:
            for node_info in nodes_to_layout:
                f.write(node_info['suid'] + '\n')
        
        # 更新已设置坐标的节点集合
        positioned_nodes.update(node_info['suid'] for node_info in nodes_to_layout)
        
        print(f"✓ 已完成 {positioned_count} 个节点的树状布局")
        print(f"  - 起始位置: ({start_x}, {start_y})")
        print(f"  - 层高: {level_height}, 节点宽度: {node_width}")
        print(f"✓ 已将 {len(nodes_to_layout)} 个节点添加到记录文件 {record_file}")
        
        return True
        
    except Exception as e:
        print(f"❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌ 执行过程中出现错误: {str(e)}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return False

# 运行函数
if __name__ == "__main__":
    print("=== 智能布局path_way节点 (基于历史记录和树状结构) ===")
     # 1. 检查 Cytoscape 连接
    p4c.cytoscape_ping()
    print("✓ 成功连接到 Cytoscape")
        
        # 2. 检查是否有网络加载
    network_list = p4c.get_network_list()
    if not network_list:
        print("❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌ 当前没有加载任何网络")
            
        
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
            
        
    print(f"✓ 找到 {len(node_table)} 个节点")
    pathway_columns = [col for col in node_table.columns if col.startswith('Pathway:')]
    count = 0
    for i in pathway_columns :
        success = layout_path_way_nodes_calculated(i,count)
        count += 1
        if success:
            print(f"=== 完成 Pathway 列 '{i}' 的布局 ===")