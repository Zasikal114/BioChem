import py4cytoscape as p4c

def set_edge_colors_by_pathway_optimized():
    """使用for循环优化的边颜色设置函数"""
    
    print("开始优化设置边颜色...")
    
    # 通路颜色配置列表
    pathway_configs = [
        # 中心碳代谢相关通路(褐色系)
        {"name": "glycolysis", "color": "#8B7355", "description": "褐色"},
        {"name": "gluconeogenesis", "color": "#A1887F", "description": "浅褐色"},
        {"name": "citric acid cycle", "color": "#6D4C41", "description": "深褐色"},
        {"name": "fermentation", "color": "#BCAAA4", "description": "灰褐色"},
        {"name": "pentose phosphate pathway", "color": "#9E9D24", "description": "黄褐色"},
        
        # 能量代谢与穿梭系统(蓝灰色系)
        {"name": "oxidative phosphorylation", "color": "#546E7A", "description": "蓝灰色"},
        {"name": "malate-aspartate shuttle", "color": "#78909C", "description": "浅蓝灰"},
        {"name": "glycerophosphate shuttle", "color": "#90A4AE", "description": "淡蓝灰"},
        
        # 糖原与复杂碳水化合物代谢(米色/卡其色系)
        {"name": "glycogen synthesis", "color": "#D7CCC8", "description": "米色"},
        {"name": "glycogen catabolism", "color": "#BCAAA4", "description": "灰米色"},
        {"name": "other carbohydrate metabolism", "color": "#A1887F", "description": "浅卡其色"},
        
        # 脂质代谢相关通路(绿色系)
        {"name": "fatty acid synthesis", "color": "#81C784", "description": "浅绿色"},
        {"name": "β-oxidation", "color": "#4CAF50", "description": "绿色"},
        {"name": "cholesterol synthesis", "color": "#66BB6A", "description": "草绿色"},
        {"name": "lipid metabolism", "color": "#A5D6A7", "description": "淡绿色"},
        {"name": "glyoxylate cycle", "color": "#C8E6C9", "description": "极淡绿色"},
        {"name": "ketobody metabolism", "color": "#388E3C", "description": "深绿色"},
        
        # 氮代谢与氨基酸循环(蓝色系)
        {"name": "amino acid synthesis", "color": "#64B5F6", "description": "浅蓝色"},
        {"name": "amino acid catabolism", "color": "#2196F3", "description": "蓝色"},
        {"name": "urea cycle", "color": "#1976D2", "description": "深蓝色"},
        {"name": "nitrogen fixation", "color": "#90CAF9", "description": "淡蓝色"},
        
        # 核苷酸代谢(紫色系)
        {"name": "nucleotide synthesis", "color": "#BA68C8", "description": "浅紫色"},
        {"name": "nucleotide catabolism", "color": "#9C27B0", "description": "紫色"},
        
        # 光合作用相关通路(黄色/橙色系)
        {"name": "calvin cycle", "color": "#FFB74D", "description": "橙色", "exclude": "C4"},
        {"name": "calvin cycle（C4）", "color": "#FF9800", "description": "深橙色"},
        {"name": "photophosphorylation", "color": "#FFD54F", "description": "淡黄色"}
    ]
    
    try:
        # 1. 检查 Cytoscape 连接
        p4c.cytoscape_ping()
        print("✓ 成功连接到 Cytoscape")
        
        # 2. 获取当前网络
        network_list = p4c.get_network_list()
        if not network_list:
            print("❌ 当前没有加载任何网络")
            return False
        
        current_network = network_list[0]
        p4c.set_current_network(current_network)
        print(f"✓ 当前网络: {p4c.get_network_name(current_network)}")
        
        # 3. 获取边表
        edge_table = p4c.get_table_columns('edge')
        if edge_table.empty:
            print("❌ 网络中没有边")
            return False
        
        print(f"✓ 找到 {len(edge_table)} 条边")
        
        # 4. 检查边表是否有通路信息
        pathway_column = None
        possible_pathway_columns = ['pathway', 'Pathway', 'PATHWAY', '通路', '代谢通路']
        
        for col in possible_pathway_columns:
            if col in edge_table.columns:
                pathway_column = col
                break
        
        if not pathway_column:
            print("❌ 边表中没有找到通路信息列")
            print(f"  现有列名: {list(edge_table.columns)}")
            return False
        
        print(f"✓ 使用通路列: '{pathway_column}'")
        
        # 5. 使用for循环为每个通路设置颜色
        edges_processed = 0
        
        for config in pathway_configs:
            pathway_name = config["name"]
            color = config["color"]
            description = config["description"]
            
            
            pathway_edges = edge_table[
                edge_table[pathway_column].astype(str).str.lower().str.contains(pathway_name)]
            
            
            if not pathway_edges.empty:
                pathway_suids = pathway_edges.index.tolist()
                
                # 设置目标箭头颜色
                p4c.set_edge_property_bypass(
                    edge_names=pathway_suids,
                    visual_property='EDGE_TARGET_ARROW_UNSELECTED_PAINT',
                    new_values=color
                )
                
                # 设置边颜色
                p4c.set_edge_property_bypass(
                    edge_names=pathway_suids,
                    visual_property='EDGE_STROKE_UNSELECTED_PAINT',
                    new_values=color
                )
                
                edges_processed += len(pathway_suids)
                print(f"✓ {pathway_name}: {len(pathway_suids)}条边 - {description} {color}")
            
        # 6. 输出统计信息
        print(f"\n✓ 边颜色设置完成！")
        print(f"✓ 共处理了 {edges_processed} 条边")
        print(f"✓ 使用了 {len(pathway_configs)} 种通路颜色配置")
        
        return True
        
    except Exception as e:
        print(f"❌ 执行过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

# 运行函数
if __name__ == "__main__":
    print("=" * 50)
    print("优化版代谢通路边颜色设置工具")
    print("=" * 50)
    
    success = set_edge_colors_by_pathway_optimized()
    
    if success:
        print("\n🎉 边颜色设置成功！")
    else:
        print("\n❌ 边颜色设置失败")