import py4cytoscape as p4c

def set_node_styles():
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
        node_table = p4c.get_table_columns('node')
        if node_table.empty:
            print("❌❌ 网络中没有节点")
            return False
        
        print(f"✓ 找到 {len(node_table)} 个节点")
        
        # 5. 筛选不同 TYPE 类型的节点
        enzyme_nodes = node_table[node_table.get('TYPE') == 'enzyme']
        metabolite_nodes = node_table[node_table.get('TYPE') == 'metabolite']
        
        # 处理 enzyme 节点（红色三角形）
        if not enzyme_nodes.empty:
            enzyme_suids = enzyme_nodes['SUID'].tolist()
            print(f"✓ 找到 {len(enzyme_nodes)} 个 TYPE 为 'enzyme' 的节点")
            
            # 设置节点形状为三角形
            p4c.set_node_property_bypass(
                node_names=enzyme_suids,
                visual_property='NODE_SHAPE',
                new_values='TRIANGLE'
            )
            
            # 设置节点填充颜色为红色
            p4c.set_node_property_bypass(
                node_names=enzyme_suids,
                visual_property='NODE_FILL_COLOR',
                new_values='#FF0000'  # 红色
            )
            
            # 设置节点大小
            p4c.set_node_property_bypass(
                node_names=enzyme_suids,
                visual_property='NODE_SIZE',
                new_values=60
            )
            
            print("✓ 已成功将 enzyme 节点设置为红色三角形")
        else:
            print("⚠ 没有找到 TYPE 为 'enzyme' 的节点")
        
        # 处理 metabolite 节点（蓝色正方形）
        if not metabolite_nodes.empty:
            metabolite_suids = metabolite_nodes['SUID'].tolist()
            print(f"✓ 找到 {len(metabolite_nodes)} 个 TYPE 为 'metabolite' 的节点")
            
            # 设置节点形状为正方形
            p4c.set_node_property_bypass(
                node_names=metabolite_suids,
                visual_property='NODE_SHAPE',
                new_values='RECTANGLE'
            )
            
            # 设置节点填充颜色为蓝色
            p4c.set_node_property_bypass(
                node_names=metabolite_suids,
                visual_property='NODE_FILL_COLOR',
                new_values='#87CEEB'  # 蓝色
            )
            
            # 设置节点大小
            p4c.set_node_property_bypass(
                node_names=metabolite_suids,
                visual_property='NODE_SIZE',
                new_values=40
            )
            
            print("✓ 已成功将 metabolite 节点设置为蓝色正方形")
        else:
            print("⚠ 没有找到 TYPE 为 'metabolite' 的节点")
        
        # 6. 应用布局以更好地显示
        p4c.layout_network('force-directed', network=current_network)
        print("✓ 应用了力导向布局")
        
        # 总结设置结果
        total_processed = len(enzyme_nodes) + len(metabolite_nodes)
        print(f"\n✓ 样式设置完成！共处理了 {total_processed} 个节点")
        if not enzyme_nodes.empty:
            print("  - enzyme 节点: 红色三角形")
        if not metabolite_nodes.empty:
            print("  - metabolite 节点: 蓝色正方形")
        
        return True
        
    except Exception as e:
        print(f"❌❌ 执行过程中出现错误: {str(e)}")
        return False

# 运行函数
if __name__ == "__main__":
    set_node_styles()