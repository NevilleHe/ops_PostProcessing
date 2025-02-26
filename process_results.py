import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import numpy as np

class ResultProcessor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Results处理程序")
        
        # 定义常量数组
        self.array_A = [100, 200, 300, 400, 500, 600, 700]
        self.array_B = [f"{i/10:.1f}g" for i in range(1, 18)]  # 0.1g到1.7g
        self.array_C = [-31, -18.8] + [i for i in range(0, 71, 10)]  # -31, -18.8, 0, 10, ..., 70
        
        # 存储选择的文件
        self.selected_files = {}  # {a_value: file_path}
        
        # 创建主界面
        self.create_main_ui()
        
        # 窗口居中
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # 设置关闭事件处理
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """主窗口关闭事件处理"""
        if messagebox.askokcancel("退出", "确定要退出程序吗？"):
            self.cleanup()
    
    def cleanup(self):
        """清理资源并退出程序"""
        if hasattr(self, 'processing_window'):
            self.processing_window.destroy()
        self.root.destroy()
        os._exit(0)  # 强制结束所有进程

    def create_main_ui(self):
        """创建主界面"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(expand=True, fill="both")
        
        ttk.Label(main_frame, text="请选择功能：").pack(pady=10)
        
        ttk.Button(main_frame, text="功能1：不同ECC高度对应的应变分布",
                  command=self.start_function1).pack(pady=5)
        ttk.Button(main_frame, text="功能2：不同ECC高度对应的最大应变",
                  command=self.start_function2).pack(pady=5)
    
    def create_processing_ui(self):
        """创建处理界面"""
        self.processing_window = tk.Toplevel(self.root)
        self.processing_window.title("文件处理")
        
        # 设置子窗口关闭事件
        self.processing_window.protocol("WM_DELETE_WINDOW", self.on_processing_window_closing)
        
        # 文件选择部分
        file_frame = ttk.LabelFrame(self.processing_window, text="文件选择", padding="5")
        file_frame.pack(fill="x", padx=5, pady=5)
        
        # 选择要使用的A元素
        a_frame = ttk.Frame(file_frame)
        a_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(a_frame, text="选择要使用的A元素：").pack(side="left")
        self.a_vars = []
        for a in self.array_A:
            var = tk.BooleanVar()
            self.a_vars.append(var)
            ttk.Checkbutton(a_frame, text=str(a), variable=var).pack(side="left", padx=5)
        
        self.file_listbox = tk.Listbox(file_frame, height=7)
        self.file_listbox.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(file_frame, text="选择文件", command=self.select_file).pack(pady=5)
        ttk.Button(file_frame, text="重置选择", command=self.reset_selection).pack(pady=5)
        
        # b元素选择部分
        b_frame = ttk.LabelFrame(self.processing_window, text="选择要输出的b元素", padding="5")
        b_frame.pack(fill="x", padx=5, pady=5)
        
        # 创建复选框变量和控件
        self.b_vars = []
        for i in range(0, len(self.array_B), 4):  # 每行4个复选框
            row_frame = ttk.Frame(b_frame)
            row_frame.pack(fill="x", padx=5)
            for j in range(4):
                if i + j < len(self.array_B):
                    var = tk.BooleanVar()
                    self.b_vars.append(var)
                    ttk.Checkbutton(row_frame, text=self.array_B[i + j],
                                  variable=var).pack(side="left", padx=10)
        
        # 输出部分
        output_frame = ttk.Frame(self.processing_window)
        output_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(output_frame, text="选择输出位置并生成文件",
                  command=self.generate_output).pack(pady=10)
        
        # 返回按钮
        ttk.Button(output_frame, text="返回主界面",
                  command=self.return_to_main).pack(pady=5)
        
        self.update_file_list()
    
    def on_processing_window_closing(self):
        """处理窗口关闭事件处理"""
        self.return_to_main()
    
    def return_to_main(self):
        """返回主界面"""
        self.processing_window.destroy()
        self.root.deiconify()  # 显示主窗口
    
    def update_file_list(self):
        """更新文件列表显示"""
        self.file_listbox.delete(0, tk.END)
        selected_a = [a for a, var in zip(self.array_A, self.a_vars) if var.get()]
        for a in selected_a:
            status = "未选择"
            if a in self.selected_files:
                status = os.path.basename(self.selected_files[a])
            self.file_listbox.insert(tk.END, f"{a}: {status}")
    
    def select_file(self):
        """选择一个results文件"""
        # 获取已选择的A元素但还未选择文件的元素
        selected_a = [a for a, var in zip(self.array_A, self.a_vars) if var.get()]
        unselected = [a for a in selected_a if a not in self.selected_files]
        
        if not unselected:
            messagebox.showinfo("提示", "所有选择的元素都已配对文件")
            return
        
        file_path = filedialog.askopenfilename(
            title=f"选择 {unselected[0]} 对应的results文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if file_path:
            self.selected_files[unselected[0]] = file_path
            self.update_file_list()
    
    def reset_selection(self):
        """重置文件选择"""
        self.selected_files.clear()
        self.update_file_list()
    
    def read_results_file(self, file_path):
        """读取results文件内容"""
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
                # 获取表头（B列标题）
                headers = lines[0].strip().split('\t')
                # 获取第一列
                first_column = [line.split('\t')[0] for line in lines[1:]]
                # 获取指定的B列数据
                b_columns = {}
                b_indices = [i for i, h in enumerate(headers) if h.startswith('B')]
                for i, b_val in enumerate(self.array_B):
                    if i < len(b_indices):
                        col_idx = b_indices[i]
                        b_columns[b_val] = [line.strip().split('\t')[col_idx] 
                                          for line in lines[1:]]
                return first_column, b_columns
        except Exception as e:
            messagebox.showerror("错误", f"读取文件 {file_path} 时出错：{str(e)}")
            return None, None

    def process_strain_data(self, X, b, selected_a):
        """处理应变数据，实现功能2的核心逻辑"""
        result_rc = []  # RC行数据
        result_ecc = []  # ECC行数据
        
        # 获取X中的第一列数据（C数组）
        c_values = [float(x) for x in X[0]]  # 假设X[0]是第一列数据
        
        for a in selected_a:
            a_col_idx = selected_a.index(a) + 1  # +1因为第一列是C值
            col_data = [float(x) if x != "error" else float('-inf') for x in X[a_col_idx]]
            
            # 计算y1：c*10 ≤ a的行中最大值
            y1 = float('-inf')
            for c, val in zip(c_values, col_data):
                if c * 10 <= a:
                    y1 = max(y1, val)
            
            # 计算y2：a ≤ c*10的行中最大值
            y2 = float('-inf')
            for c, val in zip(c_values, col_data):
                if a <= c * 10:
                    y2 = max(y2, val)
            
            result_rc.append(str(y1) if y1 != float('-inf') else "error")
            result_ecc.append(str(y2) if y2 != float('-inf') else "error")
        
        return result_rc, result_ecc

    def generate_output(self):
        """生成输出文件"""
        selected_a = [a for a, var in zip(self.array_A, self.a_vars) if var.get()]
        if not selected_a:
            messagebox.showwarning("警告", "请至少选择一个A元素！")
            return
            
        if len(selected_a) != len(self.selected_files):
            messagebox.showwarning("警告", "请为所有选择的A元素选择对应的文件！")
            return
        
        # 获取选中的b元素
        selected_b = [b for b, var in zip(self.array_B, self.b_vars) if var.get()]
        if not selected_b:
            messagebox.showwarning("警告", "请选择至少一个b元素！")
            return
        
        # 选择输出目录
        output_dir = filedialog.askdirectory(title="选择输出目录")
        if not output_dir:
            return
            
        try:
            if hasattr(self, 'current_function') and self.current_function == 2:
                self.generate_function2_output(selected_a, selected_b, output_dir)
            else:
                self.generate_function1_output(selected_a, selected_b, output_dir)
            
            messagebox.showinfo("成功", f"文件已生成到：{output_dir}")
            self.return_to_main()  # 处理完成后返回主界面
            
        except Exception as e:
            messagebox.showerror("错误", f"生成文件时出错：{str(e)}")
    
    def generate_function1_output(self, selected_a, selected_b, output_dir):
        """生成功能1的输出文件"""
        # 读取第一个文件以获取first_column
        first_file = self.selected_files[selected_a[0]]
        first_column, _ = self.read_results_file(first_file)
        if not first_column:
            return
        
        # 为每个选中的b元素生成输出文件
        for b in selected_b:
            output_filename = f"strain_distribution_{b}.txt"
            output_path = os.path.join(output_dir, output_filename)
            
            with open(output_path, 'w') as f:
                # 写入表头
                header = ['b\\a'] + [str(a) for a in selected_a]
                f.write('\t'.join(header) + '\n')
                
                # 获取每个文件中对应b的数据
                for row_idx, row_label in enumerate(first_column):
                    row = [row_label]
                    for a in selected_a:
                        file_path = self.selected_files[a]
                        _, b_data = self.read_results_file(file_path)
                        if b_data and b in b_data:
                            row.append(b_data[b][row_idx])
                        else:
                            row.append("error")
                    f.write('\t'.join(row) + '\n')

    def generate_function2_output(self, selected_a, selected_b, output_dir):
        """生成功能2的输出文件"""
        # 首先获取功能1的数据（但不输出）
        for b in selected_b:
            # 构建数据矩阵X
            X = []
            
            # 读取第一个文件以获取first_column
            first_file = self.selected_files[selected_a[0]]
            first_column, _ = self.read_results_file(first_file)
            if not first_column:
                return
            
            # 添加第一列（C数组值）
            X.append(first_column)
            
            # 获取所有A值对应的数据列
            for a in selected_a:
                file_path = self.selected_files[a]
                _, b_data = self.read_results_file(file_path)
                if b_data and b in b_data:
                    X.append(b_data[b])
                else:
                    X.append(["error"] * len(first_column))
            
            # 处理数据并生成输出
            result_rc, result_ecc = self.process_strain_data(X, b, selected_a)
            
            # 生成输出文件
            output_filename = f"max_strain_{b}.txt"
            output_path = os.path.join(output_dir, output_filename)
            
            with open(output_path, 'w') as f:
                # 写入每个A值一行
                for i, a in enumerate(selected_a):
                    row = [str(a), result_ecc[i], result_rc[i]]  # ECC在前，RC在后
                    f.write('\t'.join(row) + '\n')
    
    def start_function1(self):
        """启动功能1"""
        self.current_function = 1
        self.root.withdraw()  # 隐藏主窗口
        self.create_processing_ui()
    
    def start_function2(self):
        """启动功能2"""
        self.current_function = 2
        self.root.withdraw()  # 隐藏主窗口
        self.create_processing_ui()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ResultProcessor()
    app.run()
