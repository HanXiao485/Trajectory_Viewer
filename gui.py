import tkinter as tk
from tkinter import filedialog
from map_pcd import PointCloudAndTrajectoryVisualizer


class VisualizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Point Cloud and Trajectory Visualizer")

        # 选择文件
        self.pcd_file_path = tk.StringVar()
        self.csv_files = []
        self.csv_vars = []
        self.row_vars = []
        self.line_color_vars = []
        self.trajectory_point_color_vars = []
        self.trajectory_point_size_vars = []
        self.line_width_vars = []

        # PCD 文件选择部分
        pcd_frame = tk.Frame(root)
        pcd_frame.pack(pady=5)
        tk.Label(pcd_frame, text="PCD文件路径:").pack(side=tk.LEFT)
        tk.Entry(pcd_frame, textvariable=self.pcd_file_path, width=50).pack(side=tk.LEFT, padx=5)
        tk.Button(pcd_frame, text="选择PCD文件", command=self.select_pcd_file).pack(side=tk.LEFT)

        # CSV 文件输入部分
        self.csv_frame = tk.Frame(root)
        self.csv_frame.pack(pady=5)

        # 添加第一个 CSV 文件输入框
        self.add_csv_input(1)

        # 添加和删除 CSV 文件按钮
        button_frame = tk.Frame(root)
        button_frame.pack(pady=5)
        tk.Button(button_frame, text="+", command=self.add_csv_input).pack(side=tk.LEFT)
        tk.Button(button_frame, text="-", command=self.remove_csv_input).pack(side=tk.LEFT, padx=5)

        # 参数设置
        param_frame = tk.Frame(root)
        param_frame.pack(pady=5)

        self.voxel_size = tk.DoubleVar(value=0.05)
        self.point_color = tk.StringVar(value='height_gradient')
        self.point_cloud_alpha = tk.DoubleVar(value=0.3)
        self.elev = tk.IntVar(value=45)
        self.azim = tk.IntVar(value=35)
        self.zoom = tk.DoubleVar(value=1.5)

        tk.Label(param_frame, text="体素大小:").grid(row=0, column=0)
        tk.Entry(param_frame, textvariable=self.voxel_size).grid(row=0, column=1)

        tk.Label(param_frame, text="点云颜色:").grid(row=1, column=0)
        tk.Entry(param_frame, textvariable=self.point_color).grid(row=1, column=1)

        tk.Label(param_frame, text="点云透明度:").grid(row=2, column=0)
        tk.Entry(param_frame, textvariable=self.point_cloud_alpha).grid(row=2, column=1)

        tk.Label(param_frame, text="俯仰角:").grid(row=3, column=0)
        tk.Entry(param_frame, textvariable=self.elev).grid(row=3, column=1)

        tk.Label(param_frame, text="偏航角:").grid(row=4, column=0)
        tk.Entry(param_frame, textvariable=self.azim).grid(row=4, column=1)

        tk.Label(param_frame, text="缩放级别:").grid(row=5, column=0)
        tk.Entry(param_frame, textvariable=self.zoom).grid(row=5, column=1)

        # 可视化按钮
        tk.Button(root, text="可视化", command=self.visualize).pack(pady=10)

    def select_pcd_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("PCD files", "*.pcd")])
        self.pcd_file_path.set(file_path)

    def select_csv_file(self, index):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        self.csv_vars[index].set(file_path)

    def add_csv_input(self, index=None):
        if index is None:
            index = len(self.csv_vars) + 1

        csv_var = tk.StringVar()
        row_var = tk.IntVar(value=6)
        line_color_var = tk.StringVar(value='r')
        trajectory_point_color_var = tk.StringVar(value='g')
        trajectory_point_size_var = tk.IntVar(value=10)
        line_width_var = tk.IntVar(value=3)

        csv_row_frame = tk.Frame(self.csv_frame)
        csv_row_frame.pack(pady=2)

        tk.Label(csv_row_frame, text=f"CSV文件路径 {index}:").pack(side=tk.LEFT)
        tk.Entry(csv_row_frame, textvariable=csv_var, width=30).pack(side=tk.LEFT, padx=5)
        tk.Button(csv_row_frame, text="选择CSV文件", command=lambda i=len(self.csv_vars): self.select_csv_file(i)).pack(side=tk.LEFT, padx=5)

        tk.Label(csv_row_frame, text=f"行数 {index}:").pack(side=tk.LEFT, padx=5)
        tk.Entry(csv_row_frame, textvariable=row_var, width=5).pack(side=tk.LEFT, padx=5)

        tk.Label(csv_row_frame, text=f"线条颜色 {index}:").pack(side=tk.LEFT, padx=5)
        tk.Entry(csv_row_frame, textvariable=line_color_var, width=5).pack(side=tk.LEFT, padx=5)

        tk.Label(csv_row_frame, text=f"轨迹点颜色 {index}:").pack(side=tk.LEFT, padx=5)
        tk.Entry(csv_row_frame, textvariable=trajectory_point_color_var, width=5).pack(side=tk.LEFT, padx=5)

        tk.Label(csv_row_frame, text=f"轨迹点大小 {index}:").pack(side=tk.LEFT, padx=5)
        tk.Entry(csv_row_frame, textvariable=trajectory_point_size_var, width=5).pack(side=tk.LEFT, padx=5)

        tk.Label(csv_row_frame, text=f"线条宽度 {index}:").pack(side=tk.LEFT, padx=5)
        tk.Entry(csv_row_frame, textvariable=line_width_var, width=5).pack(side=tk.LEFT, padx=5)

        self.csv_vars.append(csv_var)
        self.row_vars.append(row_var)
        self.line_color_vars.append(line_color_var)
        self.trajectory_point_color_vars.append(trajectory_point_color_var)
        self.trajectory_point_size_vars.append(trajectory_point_size_var)
        self.line_width_vars.append(line_width_var)

    def remove_csv_input(self):
        if self.csv_vars:
            # 移除最后一个 CSV 文件的输入框和变量
            last_frame = self.csv_frame.winfo_children()[-1]
            last_frame.destroy()

            self.csv_vars.pop()
            self.row_vars.pop()
            self.line_color_vars.pop()
            self.trajectory_point_color_vars.pop()
            self.trajectory_point_size_vars.pop()
            self.line_width_vars.pop()

    def visualize(self):
        pcd_file = self.pcd_file_path.get()
        csv_files = [var.get() for var in self.csv_vars if var.get()]
        rows = [var.get() for var in self.row_vars]
        line_colors = [var.get() for var in self.line_color_vars]
        trajectory_point_colors = [var.get() for var in self.trajectory_point_color_vars]
        trajectory_point_sizes = [var.get() for var in self.trajectory_point_size_vars]
        line_widths = [var.get() for var in self.line_width_vars]

        if pcd_file and csv_files:
            visualizer = PointCloudAndTrajectoryVisualizer(pcd_file, csv_files)
            visualizer.visualize(
                voxel_size=self.voxel_size.get(),
                point_color=self.point_color.get(),
                point_cloud_alpha=self.point_cloud_alpha.get(),
                elev=self.elev.get(),
                azim=self.azim.get(),
                zoom=self.zoom.get(),
                rows=rows,
                line_colors=line_colors,
                trajectory_point_colors=trajectory_point_colors,
                trajectory_point_sizes=trajectory_point_sizes,
                line_widths=line_widths
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = VisualizerGUI(root)
    root.mainloop()