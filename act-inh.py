import py4cytoscape as p4c

def set_edge_styles():
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
        
        # 5. 筛选不同 relationship 类型的边
        activate_edges = edge_table[edge_table.get('relationship') == 'activate']
        inhibit_edges = edge_table[edge_table.get('relationship') == 'inhibit']
        
        # 处理 activate 边（绿色箭头）
        if not activate_edges.empty:
            activate_suids = activate_edges['SUID'].tolist()
            print(f"✓ 找到 {len(activate_edges)} 条 relationship 为 'activate' 的边")
            
            # 设置目标箭头为单向箭头
            p4c.set_edge_property_bypass(
                edge_names=activate_suids,
                visual_property='EDGE_TARGET_ARROW_SHAPE',
                new_values='ARROW'
            )
            
            # 设置源箭头为无
            p4c.set_edge_property_bypass(
                edge_names=activate_suids,
                visual_property='EDGE_SOURCE_ARROW_SHAPE',
                new_values='NONE'
            )
            p4c.set_edge_property_bypass(
                edge_names=activate_suids,
                visual_property='EDGE_TARGET_ARROW_UNSELECTED_PAINT',
                new_values='#00FF00'
            )
            
            # 设置边颜色为绿色
            p4c.set_edge_property_bypass(
                edge_names=activate_suids,
                visual_property='EDGE_STROKE_UNSELECTED_PAINT',
                new_values='#00FF00'  # 绿色
            )
            
            # 设置线条为实线
            p4c.set_edge_property_bypass(
                edge_names=activate_suids,
                visual_property='EDGE_LINE_TYPE',
                new_values='SOLID'
            )
            
            print("✓ 已成功将 activate 关系的边设置为绿色单向箭头")
        else:
            print("⚠ 没有找到 relationship 为 'activate' 的边")
        
        # 处理 inhibit 边（红色平头箭头）
        if not inhibit_edges.empty:
            inhibit_suids = inhibit_edges['SUID'].tolist()
            print(f"✓ 找到 {len(inhibit_edges)} 条 relationship 为 'inhibit' 的边")
            
            # 设置目标箭头为平头箭头（T型）
            p4c.set_edge_property_bypass(
                edge_names=inhibit_suids,
                visual_property='EDGE_TARGET_ARROW_SHAPE',
                new_values='T'
            )
            p4c.set_edge_property_bypass(
                edge_names=inhibit_suids,
                visual_property='EDGE_TARGET_ARROW_UNSELECTED_PAINT',
                new_values='#FF0000'  # 红色
            )
            
            # 设置源箭头为无
            p4c.set_edge_property_bypass(
                edge_names=inhibit_suids,
                visual_property='EDGE_SOURCE_ARROW_SHAPE',
                new_values='NONE'
            )
            
            # 设置边颜色为红色
            p4c.set_edge_property_bypass(
                edge_names=inhibit_suids,
                visual_property='EDGE_STROKE_UNSELECTED_PAINT',
                new_values='#FF0000'  # 红色
            )
            
            # 设置线条为实线
            p4c.set_edge_property_bypass(
                edge_names=inhibit_suids,
                visual_property='EDGE_LINE_TYPE',
                new_values='SOLID'
            )
            
            print("✓ 已成功将 inhibit 关系的边设置为红色平头箭头")
        else:
            print("⚠ 没有找到 relationship 为 'inhibit' 的边")
        
        # 总结设置结果
        total_processed = len(activate_edges) + len(inhibit_edges)
        print(f"\n✓ 样式设置完成！共处理了 {total_processed} 条边")
        if not activate_edges.empty:
            print("  - activate 边: 绿色单向箭头 →")
        if not inhibit_edges.empty:
            print("  - inhibit 边: 红色平头箭头 —|")
        
        return True
        
    except Exception as e:
        print(f"❌ 执行过程中出现错误: {str(e)}")
        return False

# 运行函数
if __name__ == "__main__":
    set_edge_styles()