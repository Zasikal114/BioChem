import py4cytoscape as p4c
import math

def layout_nodes_by_calculation():
    """通过计算设置节点XY坐标"""
    try:
        # 1. 检查 Cytoscape 连接
        p4c.cytoscape_ping()
        print("✓ 成功连接到 Cytoscape")
        
        # 2. 检查是否有网络加载
        network_list = p4c.get_network_list()
        if not network_list:
            print("❌❌ 当前没有加载任何网络")
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
            print("❌❌ 网络中没有节点")
            return False
        
        print(f"✓ 找到 {len(node_table)} 个节点")
        
        # 5. 根据节点属性分类
        # 假设我们根据 "Pathway:glycolysis" 属性来分类
        glycolysis_nodes = node_table[node_table.get('Pathway:glycolysis') == 1.0]
        other_nodes = node_table[~node_table.index.isin(glycolysis_nodes.index)]
        
        print(f"✓ 找到 {len(glycolysis_nodes)} 个 glycolysis 节点")
        print(f"✓ 找到 {len(other_nodes)} 个其他节点")
        
        # 6. 计算布局参数
        # 为 glycolysis 节点创建环形布局
        if not glycolysis_nodes.empty:
            glycolysis_suids = glycolysis_nodes['SUID'].tolist()
            center_x, center_y = 1000, 1000
            radius = 500
            angle_step = 2 * math.pi / len(glycolysis_suids)
            
            print(f"✓ 开始布局 {len(glycolysis_suids)} 个 glycolysis 节点")
            
            for i, suid in enumerate(glycolysis_suids):
                angle = i * angle_step
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                
                # 设置节点位置
                p4c.set_node_property_bypass(
                    node_names=[suid],
                    visual_property='NODE_X_LOCATION',
                    new_values=[x]
                )
                p4c.set_node_property_bypass(
                    node_names=[suid],
                    visual_property='NODE_Y_LOCATION',
                    new_values=[y]
                )
            
            print("✓ glycolysis 节点环形布局完成")
        
        # 7. 为其他节点创建网格布局
        if not other_nodes.empty:
            other_suids = other_nodes['SUID'].tolist()
            
            # 计算网格参数
            grid_size = int(math.ceil(math.sqrt(len(other_suids))))
            cell_width = 200
            cell_height = 200
            start_x, start_y = 2000, 500  # 网格起始位置
            
            print(f"✓ 开始布局 {len(other_suids)} 个其他节点")
            
            for i, suid in enumerate(other_suids):
                row = i // grid_size
                col = i % grid_size
                x = start_x + col * cell_width
                y = start_y + row * cell_height
                
                # 设置节点位置
                p4c.set_node_property_bypass(
                    node_names=[suid],
                    visual_property='NODE_X_LOCATION',
                    new_values=[x]
                )
                p4c.set_node_property_bypass(
                    node_names=[suid],
                    visual_property='NODE_Y_LOCATION',
                    new_values=[y]
                )
            
            print("✓ 其他节点网格布局完成")
        
        # 8. 设置节点颜色以区分不同类型
        if not glycolysis_nodes.empty:
            glycolysis_suids = glycolysis_nodes['SUID'].tolist()
            p4c.set_node_property_bypass(
                node_names=glycolysis_suids,
                visual_property='NODE_FILL_COLOR',
                new_values=['#FF6B6B']  # 红色
            )
            print("✓ 已设置 glycolysis 节点颜色为红色")
        
        if not other_nodes.empty:
            other_suids = other_nodes['SUID'].tolist()
            p4c.set_node_property_bypass(
                node_names=other_suids,
                visual_property='NODE_FILL_COLOR',
                new_values=['#4ECDC4']  # 青色
            )
            print("✓ 已设置其他节点颜色为青色")
        
        # 9. 设置节点大小
        all_suids = node_table['SUID'].tolist()
        p4c.set_node_property_bypass(
            node_names=all_suids,
            visual_property='NODE_SIZE',
            new_values=[50] * len(all_suids)  # 统一大小
        )
        print("✓ 已设置所有节点大小")
        
        # 10. 设置节点标签
        p4c.set_node_property_bypass(
            node_names=all_suids,
            visual_property='NODE_LABEL',
            new_values=node_table['name'].tolist()  # 使用name列作为标签
        )
        print("✓ 已设置节点标签")
        
        # 总结设置结果
        total_nodes = len(glycolysis_nodes) + len(other_nodes)
        print(f"\n✓ 节点布局完成！共处理了 {total_nodes} 个节点")
        if not glycolysis_nodes.empty:
            print(f"  - glycolysis 节点: {len(glycolysis_nodes)} 个 (环形布局)")
        if not other_nodes.empty:
            print(f"  - 其他节点: {len(other_nodes)} 个 (网格布局)")
        
        return True
        
    except Exception as e:
        print(f"❌❌ 执行过程中出现错误: {str(e)}")
        return False

def layout_by_custom_rule():
    """根据自定义规则布局节点"""
    try:
        p4c.cytoscape_ping()
        print("✓ 成功连接到 Cytoscape")
        
        network_list = p4c.get_network_list()
        if not network_list:
            print("❌❌ 当前没有加载任何网络")
            return False
        
        current_network = network_list[0]
        network_name = p4c.get_network_name(current_network)
        print(f"✓ 当前网络: {network_name}")
        
        # 获取节点表
        node_table = p4c.get_table_columns(table='node')
        if node_table.empty:
            print("❌❌ 网络中没有节点")
            return False
        
        print(f"✓ 找到 {len(node_table)} 个节点")
        
        # 根据度中心性布局（假设有degree列）
        if 'degree' in node_table.columns:
            # 按度中心性排序
            sorted_nodes = node_table.sort_values('degree', ascending=False)
            suids = sorted_nodes['SUID'].tolist()
            
            # 创建放射状布局
            center_x, center_y = 1500, 1500
            max_radius = 800
            
            print("✓ 开始按度中心性进行放射状布局")
            
            for i, suid in enumerate(suids):
                # 度越高的节点离中心越近
                radius = max_radius * (i / len(suids))
                angle = 2 * math.pi * (i / len(suids))
                
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                
                p4c.set_node_property_bypass(
                    node_names=[suid],
                    visual_property='NODE_X_LOCATION',
                    new_values=[x]
                )
                p4c.set_node_property_bypass(
                    node_names=[suid],
                    visual_property='NODE_Y_LOCATION',
                    new_values=[y]
                )
            
            print("✓ 放射状布局完成")
        
        return True
        
    except Exception as e:
        print(f"❌❌ 执行过程中出现错误: {str(e)}")
        return False

# 运行函数
if __name__ == "__main__":
    print("=== 节点计算布局 ===")
    success = layout_nodes_by_calculation()
    
    if success:
        print("\n=== 可选：按度中心性布局 ===")
        layout_by_custom_rule()