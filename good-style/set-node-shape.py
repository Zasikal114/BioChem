import py4cytoscape as p4c

def set_node_shapes():
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
        
        # 4. 获取所有节点
        node_table = p4c.get_table_columns('node')
        if node_table.empty:
            print("❌ 网络中没有节点")
            return False
        
        print(f"✓ 找到 {len(node_table)} 个节点")
        
        # 5. 根据节点类型设置形状
        # 节点类型映射字典
        type_to_shape = {
            'metabolite': 'RECTANGLE',
            'state': 'RECTANGLE',
            'enzyme': 'ROUND_RECTANGLE',
            'hormone': 'OCTAGON',
            'drug': 'HEXAGON',
            'inhibitor': 'PARALLELOGRAM',
            'photon': 'ELLIPSE',
            'condition': 'ELLIPSE',
            'cofactor': 'DIAMOND',
            'reaction': 'VEE'
        }
        
        # 处理每种节点类型
        processed_count = 0
        for node_type, shape in type_to_shape.items():
            # 筛选对应类型的节点
            type_nodes = node_table[node_table.get('TYPE') == node_type]
            
            if not type_nodes.empty:
                type_suids = type_nodes['SUID'].tolist()
                print(f"✓ 找到 {len(type_nodes)} 个 TYPE 为 '{node_type}' 的节点")
                
                # 设置节点形状
                p4c.set_node_property_bypass(
                    node_names=type_suids,
                    visual_property='NODE_SHAPE',
                    new_values=shape
                )
                
                processed_count += len(type_nodes)
                print(f"✓ 已将 {node_type} 节点设置为 {shape} 形状")
        
        print(f"\n✓ 形状设置完成！共处理了 {processed_count} 个节点")
        

        # 将所有节点的高度设置为50，宽度设置为120，文本最大宽度为100
        all_node_suids = node_table['SUID'].tolist()
        p4c.set_node_property_bypass(
            node_names=all_node_suids,
            visual_property='NODE_HEIGHT',
            new_values=50
        )
        print(f"✓ 已将所有节点高度设置为 50")
        p4c.set_node_property_bypass(
            node_names=all_node_suids,
            visual_property='NODE_WIDTH',
            new_values=120
        )
        print(f"✓ 已将所有节点宽度设置为 120")
        p4c.set_node_property_bypass(
            node_names=all_node_suids,
            visual_property='NODE_LABEL_WIDTH',
            new_values=100
        )
        print(f"✓ 已将所有节点文本最大宽度设置为 100")

        # 将enzyme节点大小设置为40，高度设置为40，宽度设置为60，文本最大宽度为70
        enzyme_nodes = node_table[node_table.get('TYPE') == 'enzyme']
        if not enzyme_nodes.empty:
            enzyme_suids = enzyme_nodes['SUID'].tolist()
            p4c.set_node_property_bypass(
                node_names=enzyme_suids,
                visual_property='NODE_SIZE',
                new_values=40
            )
            print(f"✓ 已将 enzyme 节点大小设置为 40")
            p4c.set_node_property_bypass(
                node_names=enzyme_suids,
                visual_property='NODE_HEIGHT',
                new_values=80
            )
            print(f"✓ 已将 enzyme 节点高度设置为 80")
            p4c.set_node_property_bypass(
                node_names=enzyme_suids,
                visual_property='NODE_WIDTH',
                new_values=80
            )
            print(f"✓ 已将 enzyme 节点宽度设置为 80")
            p4c.set_node_property_bypass(
                node_names=enzyme_suids,
                visual_property='NODE_LABEL_WIDTH',
                new_values=70
            )
            print(f"✓ 已将 enzyme 节点文本最大宽度设置为 70")

        

        return True
    
    except Exception as e:
        print(f"❌ 执行过程中出现错误: {str(e)}")
        return False

# 运行函数
if __name__ == "__main__":
    set_node_shapes()