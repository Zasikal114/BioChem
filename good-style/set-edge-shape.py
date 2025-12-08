import py4cytoscape as p4c

def set_edge_line_types():
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
        
        # 4. 获取所有边
        edge_table = p4c.get_table_columns('edge')
        if edge_table.empty:
            print("❌❌ 网络中没有边")
            return False
        
        print(f"✓ 找到 {len(edge_table)} 条边")
        
        # 5. 定义连接类型映射
        relationship_mapping = {
            'reaction': 'SOLID',
            'reaction(s)': 'SEPARATE_ARROW',
            'transport': 'DOT',
            'activate': 'DASH_DOT',
            'inhibit': 'SOLID',
            'electron flow': 'LONG_DASH',
            'photon flow': 'ZIGZAG'
        }
        
        # 6. 为每种连接类型设置对应的线条类型
        for relationship, line_type in relationship_mapping.items():
            # 筛选特定relationship的边
            relationship_edges = edge_table[edge_table.get('relationship') == relationship]
            
            if relationship_edges.empty:
                print(f"❌ 没有找到 relationship 为 '{relationship}' 的边")
                continue
            
            print(f"✓ 找到 {len(relationship_edges)} 条 relationship 为 '{relationship}' 的边")
            
            # 获取边的SUID列表
            edge_names = relationship_edges['SUID'].tolist()
            
            # 设置线条类型
            p4c.set_edge_property_bypass(
                edge_names=edge_names,
                visual_property='EDGE_LINE_TYPE',
                new_values=line_type
            )
            
            print(f"✓ 已将 '{relationship}' 关系的边线条类型设置为 {line_type}")
        # 7.将所有的箭头设置为单向箭头
        all_edge_suids = edge_table['SUID'].tolist()
        p4c.set_edge_property_bypass(
            edge_names=all_edge_suids,
            visual_property='EDGE_TARGET_ARROW_SHAPE',
            new_values='ARROW'
        )
        p4c.set_edge_property_bypass(
            edge_names=all_edge_suids,
            visual_property='EDGE_SOURCE_ARROW_SHAPE',
            new_values='NONE'
        )
        print("\n✓ 线条类型设置完成！")
        return True
        
    except Exception as e:
        print(f"❌❌ 执行过程中出现错误: {str(e)}")
        return False

# 运行函数
if __name__ == "__main__":
    set_edge_line_types()