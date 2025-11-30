import py4cytoscape as p4c
import math
import pandas as pd

def debug_column_values():
    """调试函数：查看Pathway:glycolysis列的实际值"""
    try:
        p4c.cytoscape_ping()
    except Exception as e:
        print("请确保Cytoscape正在运行并安装了CyREST")
        return
    
    # 获取当前网络
    network_suid = p4c.get_network_suid()
    if network_suid is None:
        print("没有找到当前网络")
        return
    
    # 获取所有节点
    all_nodes = p4c.get_all_nodes()
    if not all_nodes:
        print("网络中没有节点")
        return
    
    print(f"网络中有 {len(all_nodes)} 个节点")
    
    # 获取整个节点表的Pathway:glycolysis列
    try:
        node_table = p4c.get_table_columns(columns=['Pathway:glycolysis'])
        print("Pathway:glycolysis列的值:")
        print(node_table['Pathway:glycolysis'].value_counts())
        
        # 显示前10个节点的值
        print("\n前10个节点的Pathway:glycolysis值:")
        for i, node in enumerate(all_nodes[:10]):
            if node in node_table.index:
                value = node_table.loc[node, 'Pathway:glycolysis']
                print(f"节点 {node}: {value} (类型: {type(value)})")
                
    except Exception as e:
        print(f"获取节点数据时出错: {e}")
        return

def fix_glycolysis_column():
    """修复Pathway:glycolysis列的值"""
    try:
        p4c.cytoscape_ping()
    except Exception as e:
        print("请确保Cytoscape正在运行并安装了CyREST")
        return
    
    # 获取当前网络
    network_suid = p4c.get_network_suid()
    if network_suid is None:
        print("没有找到当前网络")
        return
    
    # 获取所有节点
    all_nodes = p4c.get_all_nodes()
    if not all_nodes:
        print("网络中没有节点")
        return
    
    # 获取整个节点表的Pathway:glycolysis列
    try:
        node_table = p4c.get_table_columns(columns=['Pathway:glycolysis'])
        
        # 修复列的值
        for node in all_nodes:
            if node in node_table.index:
                value = node_table.loc[node, 'Pathway:glycolysis']
                
                # 如果值是节点ID（大数字），则设置为0
                if isinstance(value, (int, float)) and value > 1000:
                    p4c.set_node_property(node, 'Pathway:glycolysis', 0)
                    print(f"已将节点 {node} 的Pathway:glycolysis值从 {value} 修复为 0")
                # 如果值是空值，也设置为0
                elif pd.isna(value):
                    p4c.set_node_property(node, 'Pathway:glycolysis', 0)
                    print(f"已将节点 {node} 的Pathway:glycolysis值从空值修复为 0")
        
        print("Pathway:glycolysis列修复完成")
        
    except Exception as e:
        print(f"修复列时出错: {e}")
        return

def layout_glycolysis_nodes_in_circle():
    """将Pathway:glycolysis值为1.0的节点布局为环形"""
    # 先调试列的值
    print("=== 调试列值 ===")
    debug_column_values()
    
    # 修复列的值
    print("\n=== 修复列值 ===")
    fix_glycolysis_column()
    
    # 重新获取数据
    try:
        p4c.cytoscape_ping()
        network_suid = p4c.get_network_suid()
        all_nodes = p4c.get_all_nodes()
        
        # 获取修复后的节点表
        node_table = p4c.get_table_columns(columns=['Pathway:glycolysis'])
        
        # 筛选出Pathway:glycolysis值为1.0的节点
        glycolysis_nodes = []
        for node in all_nodes:
            if node in node_table.index:
                value = node_table.loc[node, 'Pathway:glycolysis']
                
                # 检查值是否为1.0
                if value is not None:
                    try:
                        float_value = float(value)
                        if abs(float_value - 1.0) < 0.001:
                            glycolysis_nodes.append(node)
                    except (ValueError, TypeError):
                        if str(value).strip() in ['1', '1.0', 'True', 'true']:
                            glycolysis_nodes.append(node)
        
        if not glycolysis_nodes:
            print("没有找到'Pathway:glycolysis'值为1.0的节点")
            return
        
        print(f"找到 {len(glycolysis_nodes)} 个'Pathway:glycolysis'值为1.0的节点")
        
        # 分离glycolysis节点和其他节点
        other_nodes = [node for node in all_nodes if node not in glycolysis_nodes]
        
        # 如果有其他节点，先对它们进行布局
        if other_nodes:
            try:
                p4c.select_nodes(other_nodes, by_col='SUID')
                p4c.layout_network('force-directed', network=network_suid)
                p4c.clear_selection()
                print(f"已对其他 {len(other_nodes)} 个节点进行布局")
            except Exception as e:
                print(f"布局其他节点时出错: {e}")
        
        # 为glycolysis节点创建环形布局
        center_x, center_y = 1000, 1000
        radius = 300
        angle_step = 2 * math.pi / len(glycolysis_nodes)
        
        for i, node in enumerate(glycolysis_nodes):
            angle = i * angle_step
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            p4c.set_node_position(node, x, y)
        
        print(f"已将 {len(glycolysis_nodes)} 个glycolysis节点布局为环形")
        
        # 微调布局以避免重叠
        try:
            p4c.select_nodes(glycolysis_nodes, by_col='SUID')
            p4c.layout_network('force-directed', network=network_suid)
            p4c.clear_selection()
            print("已完成布局微调")
        except Exception as e:
            print(f"布局微调时出错: {e}")
        
        # 设置颜色区分
        try:
            p4c.set_node_color(glycolysis_nodes, '#FF0000')  # 红色
            if other_nodes:
                p4c.set_node_color(other_nodes, '#CCCCCC')  # 灰色
            print("已设置节点颜色区分")
        except Exception as e:
            print(f"设置节点颜色时出错: {e}")
        
        print("环形布局完成！")
        
    except Exception as e:
        print(f"布局过程中出错: {e}")

# 运行函数
if __name__ == "__main__":
    layout_glycolysis_nodes_in_circle()