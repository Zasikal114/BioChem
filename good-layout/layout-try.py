import py4cytoscape as p4c
import math
import os
import networkx as nx
from collections import deque

def layout_path_way_nodes_calculated():
    """通过计算只设置path_way节点的XY坐标，先布局最大环，再布局连接到环上的节点"""
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
        
        # 4. 获取所有节点和边信息
        node_table = p4c.get_table_columns(table='node')
        edge_table = p4c.get_table_columns(table='edge')
        
        if node_table.empty:
            print("❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌ 网络中没有节点")
            return False
        
        print(f"✓ 找到 {len(node_table)} 个节点, {len(edge_table)} 条边")
        
        # 打印边表的列名以便调试
        print(f"边表列名: {list(edge_table.columns)}")
        
        # 5. 获取所有Pathway列
        path_way_columns = [col for col in node_table.columns if col.startswith('Pathway:')]
        if not path_way_columns:
            print("❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌ 节点表中没有找到任何 'Pathway:' 列")
            print(f"可用列: {list(node_table.columns)}")
            return False
        
        print(f"✓ 找到 {len(path_way_columns)} 个Pathway列: {path_way_columns}")
        
        # 6. 确定当前筛选列
        target_column = 'Pathway:citric acid cycle'
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
        path_way_values = node_table[target_column].astype(str)
        target_nodes = node_table[path_way_values == "1"]
        
        if target_nodes.empty:
            print(f"❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌ 没有找到 {target_column} 值为 1 的节点")
            unique_values = node_table[target_column].unique()
            print(f"{target_column} 列的唯一值: {unique_values}")
            return False
        
        print(f"✓ 找到 {len(target_nodes)} 个 {target_column} 值为 1 的节点")
        
        # 9. 过滤掉已设置过坐标的节点
        nodes_to_layout = []
        skipped_nodes = []
        suid_to_name = {}
        name_to_suid = {}  # 添加名称到SUID的映射
        
        for _, node in target_nodes.iterrows():
            suid = str(node['SUID'])
            node_name = node.get('name', f"SUID_{suid}")
            suid_to_name[suid] = node_name
            name_to_suid[node_name] = suid  # 添加反向映射
            
            if suid in positioned_nodes:
                skipped_nodes.append({
                    'suid': suid,
                    'name': node_name,
                    'skip_reason': "已设置过坐标"
                })
                continue
            
            nodes_to_layout.append({
                'suid': suid,
                'name': node_name
            })
        
        print(f"✓ 过滤结果:")
        print(f"  - 需要设置坐标的节点: {len(nodes_to_layout)}")
        print(f"  - 跳过的节点: {len(skipped_nodes)}")
        
        if not nodes_to_layout:
            print("❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌ 没有需要设置坐标的节点")
            return False
        
        # 10. 构建网络图
        print("✓ 开始构建网络图...")
        G = nx.Graph()
        
        # 添加节点
        for node_info in nodes_to_layout:
            G.add_node(node_info['suid'], name=node_info['name'])
        
        # 添加边（使用正确的列名）
        target_suids = set(node_info['suid'] for node_info in nodes_to_layout)
        target_names = set(node_info['name'] for node_info in nodes_to_layout)
        
        # 检查边表是否有正确的列
        if 'shared name' not in edge_table.columns or 'name' not in edge_table.columns:
            print("❌ 边表中没有找到 'shared name' 或 'name' 列")
            print(f"边表可用列: {list(edge_table.columns)}")
            # 尝试使用其他可能的列名
            source_col = None
            target_col = None
            
            for col in edge_table.columns:
                if 'source' in col.lower() or 'shared' in col.lower():
                    source_col = col
                if 'target' in col.lower() or 'name' in col.lower():
                    target_col = col
            
            if source_col and target_col:
                print(f"使用替代列名: 源节点列='{source_col}', 目标节点列='{target_col}'")
            else:
                print("❌ 无法找到合适的边表列名，将使用简化布局")
                # 使用简化布局（没有边信息）
                layout_simple_circle(nodes_to_layout, suid_to_name)
                # 记录节点
                with open(record_file, 'a') as f:
                    for node_info in nodes_to_layout:
                        f.write(node_info['suid'] + '\n')
                print(f"✓ 已完成 {len(nodes_to_layout)} 个节点的简化环形布局")
                return True
        else:
            source_col = 'shared name'
            target_col = 'name'
            print(f"使用边表列名: 源节点列='{source_col}', 目标节点列='{target_col}'")
        
        # 添加边
        edge_count = 0
        for _, edge in edge_table.iterrows():
            source_name = str(edge[source_col])
            target_name = str(edge[target_col])
            
            # 检查边是否连接目标节点
            if source_name in target_names and target_name in target_names:
                # 通过名称找到SUID
                source_suid = name_to_suid.get(source_name)
                target_suid = name_to_suid.get(target_name)
                
                if source_suid and target_suid:
                    G.add_edge(source_suid, target_suid)
                    edge_count += 1
        
        print(f"✓ 网络图构建完成: {G.number_of_nodes()} 个节点, {G.number_of_edges()} 条边")
        
        # 11. 寻找最大环
        print("✓ 开始寻找最大环...")
        max_cycle = find_max_cycle(G)
        
        if max_cycle:
            print(f"✓ 找到最大环，包含 {len(max_cycle)} 个节点")
        else:
            print("✓ 未找到环，所有节点将按树状结构布局")
        
        # 12. 计算节点布局
        center_x, center_y = 2000, -1000
        main_radius = 300  # 主环半径
        branch_radius = 150  # 分支半径
        
        print("✓ 开始计算节点布局...")
        
        if max_cycle and len(max_cycle) >= 3:  # 确保环至少有3个节点
            # 布局最大环
            layout_cycle_nodes(G, max_cycle, center_x, center_y, main_radius, suid_to_name)
            
            # 布局连接到环上的节点
            layout_branch_nodes(G, max_cycle, center_x, center_y, main_radius, branch_radius, suid_to_name)
        else:
            # 如果没有环或环太小，按树状结构布局
            layout_tree_structure(G, center_x, center_y, main_radius, suid_to_name)
        
        # 13. 将本次设置的节点添加到记录文件中
        with open(record_file, 'a') as f:
            for node_info in nodes_to_layout:
                f.write(node_info['suid'] + '\n')
        
        print(f"✓ 已完成 {len(nodes_to_layout)} 个节点的布局")
        print(f"✓ 已将 {len(nodes_to_layout)} 个节点添加到记录文件 {record_file}")
        
        return True
        
    except Exception as e:
        print(f"❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌ 执行过程中出现错误: {str(e)}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return False

def find_max_cycle(G):
    """寻找图中的最大环"""
    try:
        # 使用简单的环检测算法
        cycles = list(nx.simple_cycles(G.to_directed()))
        if cycles:
            max_cycle = max(cycles, key=len)
            return max_cycle
    except:
        pass
    
    # 如果上述方法失败，使用备用方法
    try:
        # 寻找基础环
        cycles = list(nx.cycle_basis(G))
        if cycles:
            max_cycle = max(cycles, key=len)
            return max_cycle
    except:
        pass
    
    return None

def layout_cycle_nodes(G, cycle, center_x, center_y, radius, suid_to_name):
    """布局环上的节点"""
    angle_step = 2 * math.pi / len(cycle)
    
    for i, node_suid in enumerate(cycle):
        angle = i * angle_step
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        
        node_name = suid_to_name.get(node_suid, f"SUID_{node_suid}")
        set_node_position(node_name, x, y)
        
        
        # 标记为已布局
        G.nodes[node_suid]['positioned'] = True
        G.nodes[node_suid]['x'] = x
        G.nodes[node_suid]['y'] = y

def layout_branch_nodes(G, cycle, center_x, center_y, main_radius, branch_radius, suid_to_name):
    """布局连接到环上的分支节点"""
    # 找到所有未布局且连接到环上的节点
    cycle_set = set(cycle)
    unpositioned_nodes = [node for node in G.nodes() if not G.nodes[node].get('positioned', False)]
    
    if not unpositioned_nodes:
        return
    
    # 按距离环的远近排序
    nodes_by_distance = []
    for node in unpositioned_nodes:
        distance = calculate_distance_to_cycle(G, node, cycle_set)
        nodes_by_distance.append((node, distance))
    
    nodes_by_distance.sort(key=lambda x: x[1])
    
    # 布局分支节点
    for node_suid, distance in nodes_by_distance:
        if distance == float('inf'):
            continue  # 无法连接到环的节点
            
        # 找到最近的环节点
        nearest_cycle_node = find_nearest_cycle_node(G, node_suid, cycle_set)
        if nearest_cycle_node is None:
            continue
            
        cycle_x = G.nodes[nearest_cycle_node]['x']
        cycle_y = G.nodes[nearest_cycle_node]['y']
        
        # 计算分支方向
        dx = cycle_x - center_x
        dy = cycle_y - center_y
        direction_angle = math.atan2(dy, dx)
        
        # 在环节点的外延方向布局
        x = cycle_x + branch_radius * math.cos(direction_angle)
        y = cycle_y + branch_radius * math.sin(direction_angle)
        
        node_name = suid_to_name.get(node_suid, f"SUID_{node_suid}")
        set_node_position(node_name, x, y)
        
        # 标记为已布局
        G.nodes[node_suid]['positioned'] = True

def layout_tree_structure(G, center_x, center_y, radius, suid_to_name):
    """按树状结构布局节点（当没有环时）"""
    if not G.nodes():
        return
        
    # 找到度数最高的节点作为根节点
    if G.nodes():
        root = max(G.nodes(), key=lambda node: G.degree(node))
        
        # 使用BFS进行层次布局
        visited = set()
        queue = deque([(root, 0, 0)])  # (node, level, angle_index)
        level_nodes = {}
        
        while queue:
            node, level, angle_index = queue.popleft()
            if node in visited:
                continue
                
            visited.add(node)
            
            if level not in level_nodes:
                level_nodes[level] = []
            level_nodes[level].append(node)
            
            # 添加邻居节点
            neighbors = [n for n in G.neighbors(node) if n not in visited]
            for i, neighbor in enumerate(neighbors):
                queue.append((neighbor, level + 1, i))
        
        # 布局各层节点
        for level, nodes in level_nodes.items():
            level_radius = radius * (level + 1)
            angle_step = 2 * math.pi / len(nodes)
            
            for i, node_suid in enumerate(nodes):
                angle = i * angle_step
                x = center_x + level_radius * math.cos(angle)
                y = center_y + level_radius * math.sin(angle)
                
                node_name = suid_to_name.get(node_suid, f"SUID_{node_suid}")
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

def layout_simple_circle(nodes_to_layout, suid_to_name):
    """简化环形布局（当无法获取边信息时使用）"""
    center_x, center_y = 2000, -1000
    radius = 300
    
    angle_step = 2 * math.pi / len(nodes_to_layout)
    
    for i, node_info in enumerate(nodes_to_layout):
        angle = i * angle_step
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        
        set_node_position(node_info['name'], x, y)

def calculate_distance_to_cycle(G, node, cycle_set):
    """计算节点到环的最短距离"""
    try:
        min_distance = float('inf')
        for cycle_node in cycle_set:
            try:
                if nx.has_path(G, node, cycle_node):
                    distance = nx.shortest_path_length(G, node, cycle_node)
                    min_distance = min(min_distance, distance)
            except:
                continue
        return min_distance
    except:
        return float('inf')

def find_nearest_cycle_node(G, node, cycle_set):
    """找到距离节点最近的环节点"""
    try:
        nearest_node = None
        min_distance = float('inf')
        
        for cycle_node in cycle_set:
            try:
                if nx.has_path(G, node, cycle_node):
                    distance = nx.shortest_path_length(G, node, cycle_node)
                    if distance < min_distance:
                        min_distance = distance
                        nearest_node = cycle_node
            except:
                continue
                
        return nearest_node
    except:
        return None

def set_node_position(node_name, x, y):
    """设置节点位置"""
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

# 运行函数
if __name__ == "__main__":
    print("=== 智能布局path_way节点 (先布局最大环，再布局分支) ===")
    success = layout_path_way_nodes_calculated()
    
    if success:
        print("\n✓ 布局完成！已按最大环+分支结构进行布局")