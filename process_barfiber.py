import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
from datetime import datetime

def process_file(file_path):
    """处理单个文件，提取最后一列并计算最大绝对值"""
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            last_column = []
            errors = []
            for line_num, line in enumerate(lines, 1):
                parts = line.strip().split()
                if parts:  # 确保行不为空
                    try:
                        value = float(parts[-1])  # 转换最后一列为浮点数
                        last_column.append(value)
                    except (ValueError, IndexError):
                        errors.append((line_num, line.strip()))
                        continue
            if last_column:
                return max(abs(np.array(last_column))), errors
            return None, errors
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {str(e)}")
        return None, []

def extract_numbers(filename):
    """从文件名中提取序号a和序号b"""
    # 分割文件名获取序号a
    parts = filename.split('_')
    if len(parts) >= 2:
        num_a = parts[1]  # 获取B后的数字
    else:
        return None, None
    
    # 提取barfiber后的数字（序号b）
    match = re.search(r'barfiber([-.0-9]+)\.out$', filename)
    if match:
        num_b = float(match.group(1))
        return num_a, num_b
    return None, None

def write_error_log(output_dir, folder_name, errors):
    """写入错误日志"""
    if errors:
        log_filename = f"error_log_{folder_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        log_path = os.path.join(output_dir, log_filename)
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"错误日志 - {folder_name}\n")
            f.write("=" * 50 + "\n\n")
            for file_path, file_errors in errors.items():
                if file_errors:
                    f.write(f"\n文件: {os.path.basename(file_path)}\n")
                    for line_num, line_content in file_errors:
                        f.write(f"行 {line_num}: {line_content}\n")
        return log_path
    return None

def process_folders():
    """主处理函数"""
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    # 用列表存储选择的文件夹
    folder_paths = []
    
    # 循环选择文件夹
    while True:
        folder_path = filedialog.askdirectory(
            title=f"请选择包含barfiber文件的文件夹 ({len(folder_paths) + 1})"
        )
        
        if not folder_path:
            break
            
        folder_paths.append(folder_path)
        
        if not messagebox.askyesno("继续", "是否继续选择其他文件夹？"):
            break
    
    if not folder_paths:
        messagebox.showwarning("警告", "未选择任何文件夹")
        root.destroy()
        return
        
    # 选择输出目录
    output_dir = filedialog.askdirectory(
        title="请选择输出文件夹"
    )
    
    if not output_dir:
        root.destroy()
        return
        
    # 处理每个选择的文件夹
    for folder_path in folder_paths:
        folder_name = os.path.basename(folder_path)
        
        # 存储处理结果
        results = {}  # 格式: {num_b: {num_a: value}}
        all_num_a = set()  # 存储所有的序号a
        all_num_b = set()  # 存储所有的序号b
        all_errors = {}  # 存储所有错误信息
        
        # 遍历文件夹中的文件
        pattern = re.compile(r'S2_B.*_IDA_8\.5MPa_barfiber.*\.out$')
        for filename in os.listdir(folder_path):
            if pattern.match(filename):
                num_a, num_b = extract_numbers(filename)
                if num_a is not None and num_b is not None:
                    file_path = os.path.join(folder_path, filename)
                    max_abs_value, file_errors = process_file(file_path)
                    
                    # 记录错误信息
                    if file_errors:
                        all_errors[file_path] = file_errors
                    
                    if max_abs_value is not None:
                        if num_b not in results:
                            results[num_b] = {}
                        results[num_b][num_a] = max_abs_value * 1000  # 乘以1000
                        all_num_a.add(num_a)
                        all_num_b.add(num_b)
        
        if not results:
            messagebox.showwarning("警告", f"文件夹 {folder_name} 中未找到符合格式的文件或处理失败")
            continue
        
        # 排序序号a（按B后面的数值排序）
        sorted_num_a = sorted(all_num_a, key=lambda x: int(x[1:]))  # 去掉'B'后按数字排序
        sorted_num_b = sorted(all_num_b)  # 序号b按数值排序
        
        # 生成输出文件
        output_filename = f"{folder_name}_results.txt"
        output_path = os.path.join(output_dir, output_filename)
        
        try:
            with open(output_path, 'w') as f:
                # 写入表头
                header = "\t".join(["b\\a"] + sorted_num_a)
                f.write(header + "\n")
                
                # 写入数据行
                for num_b in sorted_num_b:
                    row = [f"{num_b}"]
                    for num_a in sorted_num_a:
                        value = results.get(num_b, {}).get(num_a, "error")
                        row.append(str(value))
                    f.write("\t".join(row) + "\n")
            
            # 写入错误日志
            if all_errors:
                log_path = write_error_log(output_dir, folder_name, all_errors)
                if log_path:
                    print(f"错误日志已保存到：{log_path}")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存结果时出错：{str(e)}")
            continue
    
    messagebox.showinfo("完成", f"处理完成！\n结果文件保存在：{output_dir}")
    root.destroy()

if __name__ == "__main__":
    process_folders()
