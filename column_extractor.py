import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox

def extract_column(input_file, output_file, column_num):
    try:
        column_index = column_num - 1  # 转换为从0开始的索引
        with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
            for line_num, line in enumerate(f_in, 1):
                line = line.strip()
                if line:
                    columns = line.split()
                    if len(columns) >= column_num:
                        f_out.write(columns[column_index] + '\n')
                    else:
                        f_out.write("error\n")
        return True
    except Exception as e:
        messagebox.showerror("错误", f"处理过程中发生错误: {str(e)}")
        return False

def gui_mode():
    root = tk.Tk()
    root.withdraw()

    # 创建列号选择对话框
    column_dialog = tk.Toplevel()
    column_dialog.title("列号设置")
    column_dialog.geometry("300x150")
    
    tk.Label(column_dialog, text="请输入要提取的列号（从1开始计数）:").pack(pady=10)
    column_entry = tk.Entry(column_dialog)
    column_entry.pack(pady=5)
    column_entry.insert(0, "2")  # 默认第二列
    
    def validate_column():
        try:
            column_num = int(column_entry.get())
            if column_num < 1:
                raise ValueError
            return column_num
        except ValueError:
            tk.messagebox.showerror("错误", "请输入有效的正整数列号")
            return None
    
    def on_confirm():
        column_num = validate_column()
        if column_num is None:
            return
            
        column_dialog.destroy()
        
        # 先选择输入文件
        input_files = filedialog.askopenfilenames(
            title="请选择多个输入文件 - 需要提取数据的源文件（可多选）",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            initialdir=os.getcwd()
        )
        if not input_files:
            return
            
        # 再选择输出文件夹
        output_dir = filedialog.askdirectory(
            title="请选择输出文件夹 - 保存提取结果的目录",
            initialdir=os.getcwd()
        )
        if not output_dir:
            return
            
        success_count = 0
        error_count = 0
        error_messages = []
        
        for input_file in input_files:
            try:
                input_filename = os.path.basename(input_file)
                # 预检查文件列数
                with open(input_file, 'r') as f:
                    first_line = f.readline().strip()
                    max_columns = len(first_line.split()) if first_line else 0
                if column_num > max_columns:
                    error_count += 1
                    error_messages.append(f"{input_filename}: 最大列数{max_columns}")
                    continue
                    
                # 自动生成输出文件名
                output_filename = f"{os.path.splitext(input_filename)[0]}_column_{column_num}.txt"
                output_path = os.path.join(output_dir, output_filename)
                
                # 检查文件是否已存在
                if os.path.exists(output_path):
                    if not messagebox.askyesno("文件已存在", 
                        f"文件 {output_filename} 已存在，是否覆盖？", parent=root):
                        continue
                        
                if extract_column(input_file, output_path, column_num):
                    success_count += 1
                else:
                    error_count += 1
                    error_messages.append(f"{input_filename}: 处理失败")
            except Exception as e:
                error_count += 1
                error_messages.append(f"{input_filename}: {str(e)}")
        
        # 显示汇总结果
        result_message = f"处理完成！\n成功: {success_count} 个文件\n失败: {error_count} 个文件"
        if error_messages:
            result_message += "\n\n错误详情:\n" + "\n".join(error_messages)
            
        messagebox.showinfo("批量处理结果", result_message)
        root.destroy()  # 明确销毁Tk根窗口
        os._exit(0)     # 强制退出所有线程
            

    tk.Button(column_dialog, text="确认", command=on_confirm).pack(pady=10)
    column_dialog.mainloop()

if __name__ == "__main__":
    if len(sys.argv) == 4:
        # 新版命令行模式
        try:
            column_num = int(sys.argv[1])
            input_file = sys.argv[2]
            output_file = sys.argv[3]
            if column_num < 1:
                raise ValueError
            extract_column(input_file, output_file, column_num)
        except (ValueError, IndexError):
            print("Usage: python column_extractor.py [column_number] [input_file] [output_file]")
            sys.exit(1)
    else:
        # GUI模式
        gui_mode()
