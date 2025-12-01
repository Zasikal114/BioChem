import py4cytoscape as p4c

def set_reaction_arrows():
    try:
        # 1. 检查 Cytoscape 连接
        p4c.cytoscape_ping()
        print("✓ 成功连接到 Cytoscape")
        
        # 2. 检查是否有网络加载
        network_list = p4c.get_network_list()
        if not network_list:
            print("❌ 当前没有加载任何网络")
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
            print("❌ 网络中没有边")
            return False
        
        print(f"✓ 找到 {len(edge_table)} 条边")
        
        # 5. 筛选 relationship 为 reaction 的边
        reaction_edges = edge_table[edge_table.get('relationship') == 'reaction']
        
        if reaction_edges.empty:
            print("❌ 没有找到 relationship 为 'reaction' 的边")
            return False
        
        print(f"✓ 找到 {len(reaction_edges)} 条 relationship 为 'reaction' 的边")
        aaa = p4c.get_visual_property_names()
        print(f"类型{aaa}")
        # 6. 设置单向箭头样式
        reaction_names = reaction_edges['SUID'].tolist()
        
        
        # 设置目标箭头为单向箭头
        p4c.set_edge_property_bypass(
            edge_names=reaction_names,
            visual_property='EDGE_TARGET_ARROW_SHAPE',
            new_values='ARROW'
        )
        
        # 设置源箭头为无（确保单向）
        p4c.set_edge_property_bypass(
            edge_names=reaction_names,
            visual_property='EDGE_SOURCE_ARROW_SHAPE',
            new_values='NONE'
        )
        
        # 设置线条为实线
        p4c.set_edge_property_bypass(
            edge_names=reaction_names,
            visual_property='EDGE_LINE_TYPE',
            new_values='SOLID'
        )
        
        print("✓ 已成功将 reaction 关系的边设置为单向箭头")
        print("  - 目标箭头: ARROW")
        print("  - 源箭头: NONE")
        print("  - 线条类型: SOLID")
        
        return True
        
    except Exception as e:
        print(f"❌ 执行过程中出现错误: {str(e)}")
        return False

# 运行函数
if __name__ == "__main__":
    set_reaction_arrows()