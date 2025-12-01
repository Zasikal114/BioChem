import os
import sys
import subprocess
import time

def run_scripts_in_folder(folder_path, delay=0, exclude_self=True, stop_on_error=False):
    """
    按顺序运行文件夹中的所有Python脚本
    
    参数:
    folder_path: 包含Python脚本的文件夹路径
    delay: 每个脚本运行后的延迟时间（秒）
    exclude_self: 是否排除当前脚本自身
    stop_on_error: 遇到错误时是否停止执行
    """
    
    # 获取当前脚本的文件名（用于排除自身）
    current_script = os.path.abspath(__file__)
    
    # 确保文件夹存在
    if not os.path.exists(folder_path):
        print(f"错误: 文件夹 '{folder_path}' 不存在")
        return False
    
    # 获取文件夹中所有的.py文件
    python_files = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.py'):
            file_path = os.path.abspath(os.path.join(folder_path, filename))
            
            # 如果需要排除自身，且是当前脚本，则跳过
            if exclude_self and file_path == current_script:
                continue
            
            python_files.append(file_path)
    
    # 按文件名排序
    python_files.sort()
    
    if not python_files:
        print(f"在文件夹 '{folder_path}' 中未找到Python脚本")
        return True
    
    print(f"找到 {len(python_files)} 个Python脚本，将按以下顺序运行:")
    for i, script in enumerate(python_files, 1):
        print(f"{i}. {os.path.basename(script)}")
    
    print("\n开始运行脚本...")
    print("=" * 50)
    
    # 按顺序运行每个脚本
    success_count = 0
    for i, script_path in enumerate(python_files, 1):
        script_name = os.path.basename(script_path)
        print(f"\n[{i}/{len(python_files)}] 正在运行: {script_name}")
        print("-" * 30)
        
        try:
            # 使用subprocess运行脚本
            result = subprocess.run([sys.executable, script_path], 
                                  check=False,  # 不自动抛出异常
                                  cwd=folder_path)  # 设置工作目录
            
            if result.returncode == 0:
                print(f"✓ {script_name} 运行成功")
                success_count += 1
            else:
                print(f"✗ {script_name} 运行失败，返回码: {result.returncode}")
                if stop_on_error:
                    print("已启用错误时停止，终止执行")
                    break
            
        except Exception as e:
            print(f"✗ 运行 {script_name} 时发生异常: {e}")
            if stop_on_error:
                print("已启用错误时停止，终止执行")
                break
        
        # 添加延迟
        if delay > 0 and i < len(python_files):
            print(f"等待 {delay} 秒后运行下一个脚本...")
            time.sleep(delay)
    
    print("=" * 50)
    print(f"运行完成: 成功 {success_count}/{len(python_files)}")
    
    return success_count == len(python_files)

def main():
    # ===== 在这里设置你的参数 =====
    
    # 要运行的脚本所在文件夹路径
    folder_path = r"C:\Users\lenovo\Desktop\jython\good-layout"  # 修改为你的文件夹路径
    
    # 每个脚本运行后的延迟时间（秒）
    delay = 1
    
    # 是否包含当前脚本自身（True=排除，False=包含）
    exclude_self = True
    
    # 遇到错误时是否停止执行（True=停止，False=继续）
    stop_on_error = False
    
    # ===== 参数设置结束 =====
    
    print(f"配置信息:")
    print(f"  文件夹路径: {folder_path}")
    print(f"  延迟时间: {delay}秒")
    print(f"  排除自身: {exclude_self}")
    print(f"  错误时停止: {stop_on_error}")
    print()
    
    # 运行脚本
    success = run_scripts_in_folder(
        folder_path=folder_path,
        delay=delay,
        exclude_self=exclude_self,
        stop_on_error=stop_on_error
    )
    
    # 返回适当的退出码
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()