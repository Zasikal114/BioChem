import py4cytoscape as p4c
import logging

def set_enzyme_nodes_to_triangle():
    """
    将 TYPE 属性为 'enzyme' 的节点形状设置为三角形
    """
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
        
        # 4. 检查节点表是否有 TYPE 列
        node_columns = p4c.get_table_column_names('node', network=current_network)
        print(f"✓ 节点表列名: {list(node_columns)}")
        
        if 'TYPE' not in node_columns:
            print("❌ 节点表中没有找到 'TYPE' 列")
            return False
        
        # 5. 获取 TYPE 为 enzyme 的节点
        # 使用表格查询方式选择节点
        node_table = p4c.get_table_columns('node', network=current_network)
        enzyme_nodes = node_table[node_table['TYPE'] == 'enzyme'].index.tolist()
        
        if not enzyme_nodes:
            print("❌ 没有找到 TYPE 为 'enzyme' 的节点")
            unique_types = node_table['TYPE'].dropna().unique()
            print(f"   当前网络中的 TYPE 值: {list(unique_types)}")
            return False
            
        node_count = len(enzyme_nodes)
        print(f"✓ 找到 {node_count} 个 TYPE 为 'enzyme' 的节点")
        
        # 6. 设置节点颜色为红色
        # 使用正确的函数和参数
        try:
            # 方法1: 使用 set_node_fill_color_bypass
            p4c.set_node_color_bypass(
                node_names=enzyme_nodes,
                new_colors='#FF6B6B',
                network=current_network
            )
            print(f"✓ 成功将 {node_count} 个酶节点颜色设置为红色")
        except Exception as e:
            print(f"❌ 设置节点颜色失败: {e}")
        return True
    except Exception as e:
        print(f"❌ 创建高级样式映射失败: {e}")
        return False
if __name__ == "__main__":
    print("=" * 50)
    print("酶节点形状设置工具")
    print("=" * 50)
    
    # 先尝试主方法
    success = set_enzyme_nodes_to_triangle()
    
    if success:
        print("\n" + "="*30)
        print("任务执行成功！")
        print("🎉 酶节点形状已设置为三角形")
        print("提示: 请在 Cytoscape 界面中查看更改效果")
        
        # 验证结果
        try:
            networks = p4c.get_network_list()
            if networks:
                node_table = p4c.get_table_columns('node', network=networks[0])
                enzyme_nodes = node_table[node_table['TYPE'] == 'enzyme'].index.tolist()
                print(f"验证: 找到 {len(enzyme_nodes)} 个酶节点")
                
                # 尝试获取一个酶节点的形状
                if enzyme_nodes:
                    try:
                        shape = p4c.get_node_property(enzyme_nodes[0], 'NODE_SHAPE', network=networks[0])
                        print(f"示例节点形状: {shape}")
                    except:
                        print("无法获取节点形状属性")
        except Exception as e:
            print(f"验证失败: {e}")
            
    else:
        print("\n❌ 所有方法都失败了")
        print("请尝试以下手动方法:")
        print("1. 在 Cytoscape 界面中，选择 'Select' -> 'Select Nodes by Column Value'")
        print("2. 选择列 'TYPE'，值 'enzyme'")
        print("3. 在样式面板中，将节点形状改为三角形")
    
    print("=" * 50)