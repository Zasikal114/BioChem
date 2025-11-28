import py4cytoscape as p4c

def create_style_mapping_for_enzyme_and_metabolite():
    """
    使用样式映射为酶节点和代谢物节点设置样式：
    - TYPE为enzyme → 红色三角形
    - TYPE为metabolite → 蓝色正方形
    """
    try:
        # 1. 检查 Cytoscape 连接
        p4c.cytoscape_ping()
        print("✓ 成功连接到 Cytoscape")
        
        # 2. 获取当前网络
        networks = p4c.get_network_list()
        if not networks:
            print("❌ 当前没有加载任何网络")
            return False
            
        current_network = networks[0]
        network_name = p4c.get_network_name(current_network)
        print(f"✓ 当前网络: {network_name}")
        
        # 3. 检查节点表是否有 TYPE 列
        node_columns = p4c.get_table_column_names('node', network=current_network)
        if 'TYPE' not in node_columns:
            print("❌ 节点表中没有找到 'TYPE' 列")
            print(f"   可用的列: {list(node_columns)}")
            return False
        
        # 4. 获取 TYPE 列的唯一值，确认有 enzyme 和 metabolite
        node_table = p4c.get_table_columns('node', network=current_network)
        unique_types = node_table['TYPE'].dropna().unique()
        print(f"✓ 网络中的节点类型: {list(unique_types)}")
        
        # 5. 创建或更新视觉样式
        style_name = "EnzymeMetaboliteStyle"
        existing_styles = p4c.get_visual_style_names()
        
        # 如果样式已存在，先删除
        if style_name in existing_styles:
            p4c.delete_visual_style(style_name)
            print(f"✓ 删除已存在的样式: {style_name}")
        
        # 创建新样式
        p4c.create_visual_style(style_name)
        print(f"✓ 创建新样式: {style_name}")
        
        # 6. 设置默认样式（适用于所有节点）- 使用正确的函数名
        # 注意：使用 set_node_color_default 而不是 set_node_fill_color_default
        p4c.set_node_shape_default('ELLIPSE', style_name=style_name)  # 默认椭圆形
        p4c.set_node_size_default(40, style_name=style_name)  # 默认大小
        p4c.set_node_color_default('#D1D5DB', style_name=style_name)  # 默认颜色（修复的函数名）
        p4c.set_node_border_width_default(2, style_name=style_name)  # 默认边框宽度
        p4c.set_node_border_color_default('#A0AEC0', style_name=style_name)  # 默认边框颜色
        
        # 7. 为酶节点创建样式映射
        print("✓ 设置酶节点样式映射...")
        
        # 酶节点形状映射：TRIANGLE
        p4c.update_style_mapping(
            style_name=style_name,
            visual_property='NODE_SHAPE',
            table_column='TYPE',
            mappings=[{'key': 'enzyme', 'value': 'TRIANGLE'}]
        )
        
        # 酶节点颜色映射：红色
        p4c.update_style_mapping(
            style_name=style_name,
            visual_property='NODE_FILL_COLOR',
            table_column='TYPE',
            mappings=[{'key': 'enzyme', 'value': '#FF6B6B'}]  # 红色
        )
        
        # 酶节点大小映射：稍大一些
        p4c.update_style_mapping(
            style_name=style_name,
            visual_property='NODE_SIZE',
            table_column='TYPE',
            mappings=[{'key': 'enzyme', 'value': 60}]  # 稍大
        )
        
        # 8. 为代谢物节点创建样式映射
        print("✓ 设置代谢物节点样式映射...")
        
        # 代谢物节点形状映射：RECTANGLE（正方形）
        p4c.update_style_mapping(
            style_name=style_name,
            visual_property='NODE_SHAPE',
            table_column='TYPE',
            mappings=[{'key': 'metabolite', 'value': 'RECTANGLE'}]
        )
        
        # 代谢物节点颜色映射：蓝色
        p4c.update_style_mapping(
            style_name=style_name,
            visual_property='NODE_FILL_COLOR',
            table_column='TYPE',
            mappings=[{'key': 'metabolite', 'value': '#4299E1'}]  # 蓝色
        )
        
        # 代谢物节点大小映射：默认大小
        p4c.update_style_mapping(
            style_name=style_name,
            visual_property='NODE_SIZE',
            table_column='TYPE',
            mappings=[{'key': 'metabolite', 'value': 40}]  # 默认大小
        )
        
        # 9. 设置标签显示
        p4c.update_style_mapping(
            style_name=style_name,
            visual_property='NODE_LABEL',
            table_column='name'  # 使用节点名称作为标签
        )
        
        # 10. 应用样式到当前网络
        p4c.set_visual_style(style_name, network=current_network)
        print("✓ 样式已应用到当前网络")
        
        # 11. 应用布局以更好地显示
        p4c.layout_network('force-directed', network=current_network)
        print("✓ 应用了力导向布局")
        
        # 12. 验证映射结果
        enzyme_nodes = node_table[node_table['TYPE'] == 'enzyme'].index.tolist()
        metabolite_nodes = node_table[node_table['TYPE'] == 'metabolite'].index.tolist()
        
        print(f"\n📊 样式映射结果:")
        print(f"   - 酶节点 (TYPE='enzyme'): {len(enzyme_nodes)} 个 → 红色三角形")
        print(f"   - 代谢物节点 (TYPE='metabolite'): {len(metabolite_nodes)} 个 → 蓝色正方形")
        
        # 显示其他类型的节点数量（将使用默认样式）
        other_types = [t for t in unique_types if t not in ['enzyme', 'metabolite']]
        for other_type in other_types:
            other_nodes = node_table[node_table['TYPE'] == other_type].index.tolist()
            print(f"   - {other_type}节点: {len(other_nodes)} 个 → 使用默认样式（灰色椭圆形）")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建样式映射失败: {e}")
        return False

def create_advanced_style_mapping():
    """
    创建更高级的样式映射，包含边框和标签样式
    """
    try:
        networks = p4c.get_network_list()
        if not networks:
            return False
            
        current_network = networks[0]
        
        # 创建高级样式
        style_name = "AdvancedEnzymeMetaboliteStyle"
        existing_styles = p4c.get_visual_style_names()
        
        if style_name in existing_styles:
            p4c.delete_visual_style(style_name)
        
        p4c.create_visual_style(style_name)
        print(f"✓ 创建高级样式: {style_name}")
        
        # 设置默认值 - 使用正确的函数名
        p4c.set_node_shape_default('ELLIPSE', style_name=style_name)
        p4c.set_node_size_default(35, style_name=style_name)
        p4c.set_node_color_default('#E2E8F0', style_name=style_name)  # 修复的函数名
        p4c.set_node_border_width_default(1, style_name=style_name)
        p4c.set_node_border_color_default('#CBD5E0', style_name=style_name)
        p4c.set_node_label_color_default('#2D3748', style_name=style_name)
        p4c.set_node_label_font_size_default(10, style_name=style_name)
        
        # 酶节点的高级映射
        enzyme_mappings = [
            # 形状
            {'property': 'NODE_SHAPE', 'value': 'TRIANGLE'},
            # 填充颜色
            {'property': 'NODE_FILL_COLOR', 'value': '#E53E3E'},  # 更深的红色
            # 大小
            {'property': 'NODE_SIZE', 'value': 65},
            # 边框颜色
            {'property': 'NODE_BORDER_PAINT', 'value': '#C53030'},
            # 边框宽度
            {'property': 'NODE_BORDER_WIDTH', 'value': 3},
            # 标签颜色
            {'property': 'NODE_LABEL_COLOR', 'value': '#742A2A'},
        ]
        
        for mapping in enzyme_mappings:
            p4c.update_style_mapping(
                style_name=style_name,
                visual_property=mapping['property'],
                table_column='TYPE',
                mappings=[{'key': 'enzyme', 'value': mapping['value']}]
            )
        
        # 代谢物节点的高级映射
        metabolite_mappings = [
            # 形状
            {'property': 'NODE_SHAPE', 'value': 'RECTANGLE'},
            # 填充颜色
            {'property': 'NODE_FILL_COLOR', 'value': '#3182CE'},  # 更深的蓝色
            # 大小
            {'property': 'NODE_SIZE', 'value': 45},
            # 边框颜色
            {'property': 'NODE_BORDER_PAINT', 'value': '#2C5AA0'},
            # 边框宽度
            {'property': 'NODE_BORDER_WIDTH', 'value': 2},
            # 标签颜色
            {'property': 'NODE_LABEL_COLOR', 'value': '#2A3C5A'},
        ]
        
        for mapping in metabolite_mappings:
            p4c.update_style_mapping(
                style_name=style_name,
                visual_property=mapping['property'],
                table_column='TYPE',
                mappings=[{'key': 'metabolite', 'value': mapping['value']}]
            )
        
        # 标签映射
        p4c.update_style_mapping(
            style_name=style_name,
            visual_property='NODE_LABEL',
            table_column='name'
        )
        
        # 应用样式
        p4c.set_visual_style(style_name, network=current_network)
        
        print("✓ 高级样式映射创建成功")
        return True
        
    except Exception as e:
        print(f"❌ 创建高级样式映射失败: {e}")
        return False

def alternative_simple_method():
    """
    备选简单方法：使用更基础的函数
    """
    try:
        p4c.cytoscape_ping()
        print("✓ 尝试备选简单方法...")
        
        networks = p4c.get_network_list()
        if not networks:
            return False
            
        current_network = networks[0]
        
        # 使用现有样式或创建新样式
        style_name = "SimpleEnzymeMetaboliteStyle"
        existing_styles = p4c.get_visual_style_names()
        
        if style_name in existing_styles:
            p4c.delete_visual_style(style_name)
        
        # 创建新样式
        p4c.create_visual_style(style_name)
        
        # 使用通用方法设置默认值
        # 注意：这里我们使用更通用的方法，避免使用可能不存在的特定函数
        default_properties = {
            'NODE_SHAPE': 'ELLIPSE',
            'NODE_SIZE': 40,
            'NODE_FILL_COLOR': '#D1D5DB',
            'NODE_BORDER_WIDTH': 2,
            'NODE_BORDER_PAINT': '#A0AEC0'
        }
        
        for prop, value in default_properties.items():
            try:
                # 尝试使用通用函数设置默认值
                p4c.set_visual_property_default(
                    property=prop, 
                    value=value, 
                    style_name=style_name
                )
            except:
                print(f"ℹ️ 无法设置 {prop} 的默认值，继续下一个属性")
        
        # 设置映射
        mappings = [
            # 酶节点映射
            {'type': 'enzyme', 'shape': 'TRIANGLE', 'color': '#FF6B6B', 'size': 60},
            # 代谢物节点映射
            {'type': 'metabolite', 'shape': 'RECTANGLE', 'color': '#4299E1', 'size': 40}
        ]
        
        for mapping in mappings:
            # 形状映射
            p4c.update_style_mapping(
                style_name=style_name,
                visual_property='NODE_SHAPE',
                table_column='TYPE',
                mappings=[{'key': mapping['type'], 'value': mapping['shape']}]
            )
            
            # 颜色映射
            p4c.update_style_mapping(
                style_name=style_name,
                visual_property='NODE_FILL_COLOR',
                table_column='TYPE',
                mappings=[{'key': mapping['type'], 'value': mapping['color']}]
            )
            
            # 大小映射
            p4c.update_style_mapping(
                style_name=style_name,
                visual_property='NODE_SIZE',
                table_column='TYPE',
                mappings=[{'key': mapping['type'], 'value': mapping['size']}]
            )
        
        # 应用样式
        p4c.set_visual_style(style_name, network=current_network)
        p4c.layout_network('force-directed', network=current_network)
        
        print("✓ 备选简单方法成功")
        return True
        
    except Exception as e:
        print(f"❌ 备选简单方法失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("酶节点和代谢物节点样式映射工具")
    print("=" * 60)
    
    # 执行基本样式映射
    success = create_style_mapping_for_enzyme_and_metabolite()
    
    if not success:
        print("\n❌ 主方法失败，尝试备选简单方法...")
        success = alternative_simple_method()
    
    if success:
        print("\n" + "="*40)
        print("🎉 样式映射创建成功！")
        
        # 询问是否应用高级样式
        user_input = input("\n是否应用高级样式映射（包含边框和标签样式）? (y/n): ")
        if user_input.lower() in ['y', 'yes']:
            advanced_success = create_advanced_style_mapping()
            if advanced_success:
                print("✓ 高级样式映射应用成功")
        
        print("\n📋 样式映射规则总结:")
        print("   - TYPE='enzyme' 的节点 → 红色三角形")
        print("   - TYPE='metabolite' 的节点 → 蓝色正方形")
        print("   - 其他类型的节点 → 使用默认样式（灰色椭圆形）")
        print("\n💡 提示: 当网络数据变化时，样式会自动应用！")
        
    else:
        print("\n❌ 样式映射创建失败")
        print("请检查:")
        print("1. Cytoscape 是否正在运行")
        print("2. 网络是否已加载")
        print("3. 节点表是否包含 TYPE 列")
        print("4. TYPE 列是否包含 'enzyme' 和 'metabolite' 值")
        print("5. py4cytoscape 版本是否支持所用函数")
    
    print("=" * 60)