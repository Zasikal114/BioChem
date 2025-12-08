import py4cytoscape as p4c

def set_unified_node_styles():
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
        
        # 4. 获取所有节点和边
        node_table = p4c.get_table_columns('node')
        edge_table = p4c.get_table_columns('edge')
        
        if node_table.empty:
            print("❌❌❌❌❌❌❌❌ 网络中没有节点")
            return False
        
        print(f"✓ 找到 {len(node_table)} 个节点")
        
        if not edge_table.empty:
            print(f"✓ 找到 {len(edge_table)} 条边")
        
        # 5. 获取所有节点的 SUID 和所有边的 SUID
        all_node_suids = node_table['SUID'].tolist()
        all_edge_suids = edge_table['SUID'].tolist() if not edge_table.empty else []
        
        # 6. 统一设置所有节点的样式
        print("正在设置统一节点样式...")
        
        # 设置节点填充颜色为 #F5F5F5 (极浅灰白色)
        p4c.set_node_property_bypass(
            node_names=all_node_suids,
            visual_property='NODE_FILL_COLOR',
            new_values='#F5F5F5'
        )
        print("✓ 设置节点填充色: #F5F5F5")
        
        # 设置节点边框颜色为 #9E9E9E (中度灰色)
        p4c.set_node_property_bypass(
            node_names=all_node_suids,
            visual_property='NODE_BORDER_PAINT',
            new_values='#9E9E9E'
        )
        print("✓ 设置节点边框色: #9E9E9E")
        
        # 设置文字颜色为 #424242 (深灰色)
        p4c.set_node_property_bypass(
            node_names=all_node_suids,
            visual_property='NODE_LABEL_COLOR',
            new_values='#424242'
        )
        print("✓ 设置文字颜色: #424242")
        
        # 设置节点边框宽度
        p4c.set_node_property_bypass(
            node_names=all_node_suids,
            visual_property='NODE_BORDER_WIDTH',
            new_values=2
        )
        print("✓ 设置节点边框宽度: 2")
        
        # 设置节点标签字体大小
        p4c.set_node_property_bypass(
            node_names=all_node_suids,
            visual_property='NODE_LABEL_FONT_SIZE',
            new_values=12
        )
        print("✓ 设置标签字体大小: 12")
        
        # 7. 设置节点大小变大（默认大小的2倍）
        p4c.set_node_property_bypass(
            node_names=all_node_suids,
            visual_property='NODE_SIZE',
            new_values=80  # 默认大小约为40，这里设置为80（2倍大小）
        )
        print("✓ 设置节点大小: 80")
        
        # 8. 如果有边，设置边宽度等比例变宽
        if all_edge_suids:
            p4c.set_edge_property_bypass(
                edge_names=all_edge_suids,
                visual_property='EDGE_WIDTH',
                new_values=4.0  # 默认宽度约为2.0，这里设置为4.0（2倍宽度）
            )
            print("✓ 设置边宽度: 4.0")
            
            
        
        print("\n✓ 统一节点样式设置完成！")
        print("  - 节点填充色: #F5F5F5 (极浅灰白色)")
        print("  - 节点边框色: #9E9E9E (中度灰色)")
        print("  - 文字颜色: #424242 (深灰色)")
        print("  - 边框宽度: 2")
        print("  - 节点大小: 80 (变大)")
        if all_edge_suids:
            print("  - 边宽度: 4.0 (等比例变宽)")
            print("  - 边颜色: #666666")
        
        return True
        
    except Exception as e:
        print(f"❌❌❌❌❌❌❌❌ 执行过程中出现错误: {str(e)}")
        return False

# 运行函数
if __name__ == "__main__":
    set_unified_node_styles()