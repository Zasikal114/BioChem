import py4cytoscape as p4c
import math

def layout_citric_acid_cycle_nodes_calculated():
    """通过计算只设置citric_acid_cycle节点的XY坐标，不修改其他节点"""
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
        
        # 5. 只筛选出citric_acid_cycle节点
        # 检查是否有Pathway:citric acid cycle列
        if 'Pathway:citric acid cycle' not in node_table.columns:
            print("❌❌ 节点表中没有找到 'Pathway:citric acid cycle' 列")
            print(f"可用列: {list(node_table.columns)}")
            return False 
        
        # 筛选citric_acid_cycle节点（值为1.0）
        citric_acid_cycle_nodes = node_table[node_table['Pathway:citric acid cycle'] == 1.0]
        
        if citric_acid_cycle_nodes.empty:
            print("❌❌ 没有找到 Pathway:citric acid cycle 值为 1.0 的节点")
            # 显示该列的所有唯一值，帮助调试
            unique_values = node_table['Pathway:citric acid cycle'].unique()
            print(f"Pathway:citric acid cycle 列的唯一值: {unique_values}")
            return False
        
        citric_acid_cycle_suids = citric_acid_cycle_nodes['SUID'].tolist()
        print(f"✓ 找到 {len(citric_acid_cycle_suids)} 个 citric_acid_cycle 节点")
        
        # 6. 只为citric_acid_cycle节点计算环形布局
        center_x, center_y = -2000, 1000  # 环形中心坐标
        radius = 300  # 环形半径
        
        # 计算每个节点的角度
        angle_step = 2 * math.pi / len(citric_acid_cycle_suids)
        
        print("✓ 开始计算 citric_acid_cycle 节点的环形布局")
        
        for i, suid in enumerate(citric_acid_cycle_suids):
            angle = i * angle_step
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            
            # 只设置citric_acid_cycle节点的位置
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
        
        print(f"✓ 已完成 {len(citric_acid_cycle_suids)} 个 citric_acid_cycle 节点的环形布局")
        print(f"  - 中心位置: ({center_x}, {center_y})")
        print(f"  - 环形半径: {radius}")
        
        return True
        
    except Exception as e:
        print(f"❌❌ 执行过程中出现错误: {str(e)}")
        return False

# 运行函数
if __name__ == "__main__":
    print("=== 仅布局citric_acid_cycle节点 ===")
    success = layout_citric_acid_cycle_nodes_calculated()
    
    if success:
        print("\n✓ 布局完成！仅修改了citric_acid_cycle节点的位置，其他节点保持不变")