import numpy as np
import pandas as pd
import open3d as o3d
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from matplotlib.colors import Normalize
from mpl_toolkits.mplot3d import Axes3D


class PointCloudAndTrajectoryVisualizer:
    def __init__(self, pcd_file_path, csv_file_paths):
        self.pcd_file_path = pcd_file_path
        self.csv_file_paths = csv_file_paths

    def read_pcd_file(self, voxel_size=0.0):
        pcd = o3d.io.read_point_cloud(self.pcd_file_path)

        # Apply voxel downsampling
        if voxel_size > 0:
            pcd = pcd.voxel_down_sample(voxel_size=voxel_size)

        return np.asarray(pcd.points)

    def read_csv_file(self, csv_file_path, row):
        df = pd.read_csv(csv_file_path)
        # Find all column names ending with '.x', '.y', '.z'
        x_cols = [col for col in df.columns if col.endswith('.x')]
        y_cols = [col for col in df.columns if col.endswith('.y')]
        z_cols = [col for col in df.columns if col.endswith('.z')]

        num_points = len(x_cols)
        trajectory_points = []
        for i in range(num_points):
            x = df.at[row, x_cols[i]]
            y = df.at[row, y_cols[i]]
            z = df.at[row, z_cols[i]]
            trajectory_points.append([x, y, z])

        return np.array(trajectory_points)

    def interpolate_trajectory(self, trajectory_points, num_interpolation_points=100):
        t = np.arange(len(trajectory_points))
        f_x = interp1d(t, trajectory_points[:, 0], kind='cubic')
        f_y = interp1d(t, trajectory_points[:, 1], kind='cubic')
        f_z = interp1d(t, trajectory_points[:, 2], kind='cubic')

        t_new = np.linspace(0, len(trajectory_points) - 1, num_interpolation_points)
        interpolated_trajectory = np.column_stack((f_x(t_new), f_y(t_new), f_z(t_new)))

        return interpolated_trajectory

    def visualize(self, voxel_size=0.0, point_color='height_gradient',
                  point_cloud_alpha=0.5, elev=30, azim=45, zoom=1.0,
                  rows=[6], line_colors=['r'], trajectory_point_colors=['b'],
                  trajectory_point_sizes=[5], line_widths=[2]):
        point_cloud = self.read_pcd_file(voxel_size)

        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')

        # plot the semi-transparent point cloud
        if point_color == 'height_gradient':
            norm = Normalize(vmin=np.min(point_cloud[:, 2]), vmax=np.max(point_cloud[:, 2]))
            colors = plt.cm.jet(norm(point_cloud[:, 2]))
            ax.scatter(point_cloud[:, 0], point_cloud[:, 1], point_cloud[:, 2],
                       c=colors, alpha=point_cloud_alpha)
        else:
            ax.scatter(point_cloud[:, 0], point_cloud[:, 1], point_cloud[:, 2],
                       c=point_color, alpha=point_cloud_alpha)

        # Plot multiple trajectories
        for csv_file_path, row, line_color, trajectory_point_color, trajectory_point_size, line_width in zip(
                self.csv_file_paths, rows, line_colors, trajectory_point_colors, trajectory_point_sizes, line_widths):
            trajectory_points = self.read_csv_file(csv_file_path, row)
            interpolated_trajectory = self.interpolate_trajectory(trajectory_points)

            ax.scatter(trajectory_points[:, 0], trajectory_points[:, 1], trajectory_points[:, 2],
                       c=trajectory_point_color, s=trajectory_point_size, alpha=1.0, zorder=3)

            ax.plot(interpolated_trajectory[:, 0], interpolated_trajectory[:, 1], interpolated_trajectory[:, 2],
                    c=line_color, linewidth=line_width, alpha=1.0, zorder=4)

        # Set the initial view angle
        ax.view_init(elev=elev, azim=azim)

        # Set the axis ratio to 1:1:1
        self.set_axes_equal(ax)

        # Set the zoom level
        self.set_zoom(ax, zoom)

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title(f'Point cloud downsampling rate: {voxel_size}')

        plt.show()

    def set_axes_equal(self, ax):
        """Set the axis ratio in 3D plotting to 1:1:1"""
        # Get the current axis limits
        x_limits = ax.get_xlim3d()
        y_limits = ax.get_ylim3d()
        z_limits = ax.get_zlim3d()

        # Calculate the range and center point of each axis
        x_range = abs(x_limits[1] - x_limits[0])
        x_middle = np.mean(x_limits)
        y_range = abs(y_limits[1] - y_limits[0])
        y_middle = np.mean(y_limits)
        z_range = abs(z_limits[1] - z_limits[0])
        z_middle = np.mean(z_limits)

        # Adjust the axis range to make them equal
        plot_radius = 0.5 * max([x_range, y_range, z_range])

        ax.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
        ax.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])
        ax.set_zlim3d([z_middle - plot_radius, z_middle + plot_radius])

    def set_zoom(self, ax, zoom):
        """设置3D绘图的缩放比例"""
        # 获取当前坐标轴的限制范围
        x_limits = ax.get_xlim3d()
        y_limits = ax.get_ylim3d()
        z_limits = ax.get_zlim3d()

        # 计算每个坐标轴的中心点
        x_middle = np.mean(x_limits)
        y_middle = np.mean(y_limits)
        z_middle = np.mean(z_limits)

        # 计算每个坐标轴的半范围
        x_half_range = abs(x_limits[1] - x_limits[0]) / 2
        y_half_range = abs(y_limits[1] - y_limits[0]) / 2
        z_half_range = abs(z_limits[1] - z_limits[0]) / 2

        # 根据缩放比例调整范围
        x_half_range /= zoom
        y_half_range /= zoom
        z_half_range /= zoom

        # 设置新的坐标轴限制
        ax.set_xlim3d([x_middle - x_half_range, x_middle + x_half_range])
        ax.set_ylim3d([y_middle - y_half_range, y_middle + y_half_range])
        ax.set_zlim3d([z_middle - z_half_range, z_middle + z_half_range])