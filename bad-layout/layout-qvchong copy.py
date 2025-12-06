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
        
        # 计算节点布局的核心逻辑
        # 这部分代码插入在第15步和第16步之间
        
        # 构建只包含需要布局节点的子图
        node_names = [node_info['name'] for node_info in nodes_to_layout]
        G_sub = G.subgraph(node_names).copy()
        
        # 如果子图为空，使用简单布局
        if len(G_sub.nodes) == 0:
            print("⚠️ 子图中没有节点，使用简单网格布局")
            
        else:
            # 寻找最大的环
            largest_cycle = find_largest_cycle(G_sub)
            # 但是如果最大的环大小小于等于6，就不认为是有效环
            if largest_cycle and len(largest_cycle) <= 6:
                largest_cycle = None
            if largest_cycle:
                print(f"✓ 找到最大环，包含 {len(largest_cycle)} 个节点")
                # 对环应用环形布局
                cycle_positions = circular_layout(largest_cycle, radius=20*len(largest_cycle) , center_x=1000+1000*count, center_y=1000+1000*count)
                
                # 对非环节点应用最小夹角布局
                node_positions = layout_non_cycle_nodes(G_sub, largest_cycle, cycle_positions)
            else:
                print("⚠️ 未找到环，使用树状布局")
                # 如果没有环，使用树状布局
                node_positions = tree_layout(G_sub)

        # 计算布局结束
        
        # 16. 为需要设置的节点应用布局
        print("✓ 开始应用节点布局")
        
        positioned_count = 0
        for node_info in nodes_to_layout:
            node_name = node_info['name']
            
            # 检查节点是否在布局中
            if node_name in node_positions:
                x, y = node_positions[node_name]
                
                # 使用节点名称设置节点位置
                p4c.set_node_position_bypass(
                    node_names=[node_name],
                    new_x_locations=[x],
                    new_y_locations=[y]
                )
                
        
        # 17. 将本次设置的节点添加到记录文件中
        with open(record_file, 'a') as f:
            for node_info in nodes_to_layout:
                f.write(node_info['suid'] + '\n')
        
        # 更新已设置坐标的节点集合
        positioned_nodes.update(node_info['suid'] for node_info in nodes_to_layout)
        
        print(f"✓ 已完成 {positioned_count} 个节点的布局")
        print(f"✓ 已将 {len(nodes_to_layout)} 个节点添加到记录文件 {record_file}")
        
        return True
        
    except Exception as e:
        print(f"❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌ 执行过程中出现错误: {str(e)}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return False

def find_largest_cycle(G):
    """寻找图中最大的环"""
    try:
        # 使用强连通分量寻找环
        sccs = list(nx.strongly_connected_components(G))
        largest_scc = max(sccs, key=len) if sccs else set()
        
        if len(largest_scc) < 2:
            return None
            
        # 在最大的强连通分量中寻找环
        subgraph = G.subgraph(largest_scc)
        cycles = []
        
        # 尝试从每个节点开始寻找简单环
        for node in list(subgraph.nodes())[:10]:  # 限制数量避免性能问题
            try:
                for cycle in nx.simple_cycles(subgraph):
                    if len(cycle) > 2:  # 至少3个节点才认为是有效的环
                        cycles.append(cycle)
                    if len(cycles) > 20:  # 限制循环数量
                        break
            except:
                continue
                
        if cycles:
            largest_cycle = max(cycles, key=len)
            return largest_cycle
        return None
        
    except Exception as e:
        print(f"⚠️ 寻找环时出错: {e}")
        return None

def circular_layout(nodes, radius=300, center_x=0, center_y=0):
    """对节点应用环形布局"""
    positions = {}
    n = len(nodes)
    for i, node in enumerate(nodes):
        angle = 2 * math.pi * i / n
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        positions[node] = (x, y)
    return positions

def layout_non_cycle_nodes(G, cycle_nodes, cycle_positions):
    """对非环节点应用最小夹角布局算法"""
    all_positions = cycle_positions.copy()
    non_cycle_nodes = set(G.nodes()) - set(cycle_nodes)
    
    # 为每个环节点创建子节点列表
    children_map = {}
    for node in cycle_nodes:
        children_map[node] = []
    
    # 将非环节点分配到相连的环节点
    for node in non_cycle_nodes:
        connected_cycle_nodes = []
        
        # 查找所有与当前节点相连的环节点
        for cycle_node in cycle_nodes:
            if G.has_edge(node, cycle_node) or G.has_edge(cycle_node, node):
                connected_cycle_nodes.append(cycle_node)
        
        if connected_cycle_nodes:
            # 选择连接数最多的环节点作为父节点
            parent = max(connected_cycle_nodes, 
                        key=lambda x: len([n for n in G.predecessors(x) if n in non_cycle_nodes] + 
                                         [n for n in G.successors(x) if n in non_cycle_nodes]))
            children_map[parent].append(node)
    
    # 为每个环节点的子节点布局
    for parent, children in children_map.items():
        if children:
            parent_x, parent_y = cycle_positions[parent]
            child_radius = 150  # 子节点布局半径
            
            # 计算最优夹角
            n_children = len(children)
            if n_children == 1:
                angles = [0]  # 单个子节点直接放在上方
            else:
                # 均匀分布角度
                angles = [2 * math.pi * i / n_children for i in range(n_children)]
            
            for i, child in enumerate(children):
                angle = angles[i]
                x = parent_x + child_radius * math.cos(angle)
                y = parent_y + child_radius * math.sin(angle)
                all_positions[child] = (x, y)
    
    # 处理剩余未分配的非环节点（使用网格布局）
    remaining_nodes = non_cycle_nodes - set(all_positions.keys())
    if remaining_nodes:
        grid_size = int(math.sqrt(len(remaining_nodes))) + 1
        for i, node in enumerate(remaining_nodes):
            row = i // grid_size
            col = i % grid_size
            all_positions[node] = (col * 200 - 1000, row * 200 - 1000)  # 放在左下角
    
    return all_positions

def tree_layout(G):
    """树状布局作为备用方案"""
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
        
    if True:
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
        start_x = 1000 + 1000*count      # 起始X坐标
        start_y = 1000 + 1000*count    # 起始Y坐标
        
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
        return node_positions
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