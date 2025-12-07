import py4cytoscape as p4c

def set_unified_node_styles():
    try:
        # 1. 检查 Cytoscape 连接
        p4c.cytoscape_ping()
        print("✓ 成功连接到 Cytoscape")
        
        # 2. 检查是否有网络加载
        network_list = p4c.get_network_list()
        if not network_list:
            print("❌❌❌❌ 当前没有加载任何网络")
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
            print("❌❌❌❌ 网络中没有节点")
            return False
        
        print(f"✓ 找到 {len(node_table)} 个节点")
        
        # 5. 获取所有节点的 SUID
        all_node_suids = node_table['SUID'].tolist()
        
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
        
        # 7. 可选：设置边框宽度为统一值（默认为1，可根据需要调整）
        p4c.set_node_property_bypass(
            node_names=all_node_suids,
            visual_property='NODE_BORDER_WIDTH',
            new_values=2
        )
        print("✓ 设置节点边框宽度: 2")
        
        # 8. 可选：确保节点标签可见
        p4c.set_node_property_bypass(
            node_names=all_node_suids,
            visual_property='NODE_LABEL_FONT_SIZE',
            new_values=12
        )
        print("✓ 设置标签字体大小: 12")
        
        print("\n✓ 统一节点样式设置完成！")
        print("  - 节点填充色: #F5F5F5 (极浅灰白色)")
        print("  - 节点边框色: #9E9E9E (中度灰色)")
        print("  - 文字颜色: #424242 (深灰色)")
        print("  - 边框宽度: 2")
        
        return True
        
    except Exception as e:
        print(f"❌❌❌❌ 执行过程中出现错误: {str(e)}")
        return False

# 运行函数
if __name__ == "__main__":
    set_unified_node_styles()