import numpy as np
import pandas as pd
import open3d as o3d
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from matplotlib.colors import Normalize
from mpl_toolkits.mplot3d import Axes3D


class PointCloudAndTrajectoryVisualizer:
    def __init__(self, pcd_file_path, csv_file_paths):
        # The path of the PCD file
        self.pcd_file_path = pcd_file_path
        # The paths of the CSV files
        self.csv_file_paths = csv_file_paths

    def read_pcd_file(self, voxel_size=0.0):
        # Read the point cloud from the PCD file
        pcd = o3d.io.read_point_cloud(self.pcd_file_path)

        # Apply voxel downsampling
        if voxel_size > 0:
            pcd = pcd.voxel_down_sample(voxel_size=voxel_size)

        return np.asarray(pcd.points)

    def read_csv_file(self, csv_file_path, row):
        # Read the CSV file into a DataFrame
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
        # Create an array of indices for the original trajectory points
        t = np.arange(len(trajectory_points))
        # Create interpolation functions for x, y, and z coordinates
        f_x = interp1d(t, trajectory_points[:, 0], kind='cubic')
        f_y = interp1d(t, trajectory_points[:, 1], kind='cubic')
        f_z = interp1d(t, trajectory_points[:, 2], kind='cubic')

        # Create a new array of indices for interpolation
        t_new = np.linspace(0, len(trajectory_points) - 1, num_interpolation_points)
        # Interpolate the trajectory points
        interpolated_trajectory = np.column_stack((f_x(t_new), f_y(t_new), f_z(t_new)))

        return interpolated_trajectory

    def visualize(self, voxel_size=0.0, point_color='height_gradient',
                  point_cloud_alpha=0.5, elev=30, azim=45, zoom=1.0,
                  rows=[6], line_colors=['r'], trajectory_point_colors=['b'],
                  trajectory_point_sizes=[5], line_widths=[2]):
        # Read the point cloud from the PCD file
        point_cloud = self.read_pcd_file(voxel_size)

        # Create a new figure
        fig = plt.figure(figsize=(10, 8))
        # Add a 3D subplot to the figure
        ax = fig.add_subplot(111, projection='3d')

        # Plot the semi-transparent point cloud
        if point_color == 'height_gradient':
            # Normalize the z-coordinates of the point cloud
            norm = Normalize(vmin=np.min(point_cloud[:, 2]), vmax=np.max(point_cloud[:, 2]))
            # Map the normalized z-coordinates to colors using the jet colormap
            colors = plt.cm.jet(norm(point_cloud[:, 2]))
            # Plot the point cloud with color based on height
            ax.scatter(point_cloud[:, 0], point_cloud[:, 1], point_cloud[:, 2],
                       c=colors, alpha=point_cloud_alpha)
        else:
            # Plot the point cloud with a single color
            ax.scatter(point_cloud[:, 0], point_cloud[:, 1], point_cloud[:, 2],
                       c=point_color, alpha=point_cloud_alpha)

        # Plot multiple trajectories
        for csv_file_path, row, line_color, trajectory_point_color, trajectory_point_size, line_width in zip(
                self.csv_file_paths, rows, line_colors, trajectory_point_colors, trajectory_point_sizes, line_widths):
            # Read the trajectory points from the CSV file
            trajectory_points = self.read_csv_file(csv_file_path, row)
            # Interpolate the trajectory points
            interpolated_trajectory = self.interpolate_trajectory(trajectory_points)

            # Plot the original trajectory points
            ax.scatter(trajectory_points[:, 0], trajectory_points[:, 1], trajectory_points[:, 2],
                       c=trajectory_point_color, s=trajectory_point_size, alpha=1.0, zorder=3)

            # Plot the interpolated trajectory line
            ax.plot(interpolated_trajectory[:, 0], interpolated_trajectory[:, 1], interpolated_trajectory[:, 2],
                    c=line_color, linewidth=line_width, alpha=1.0, zorder=4)

        # Set the initial view angle
        ax.view_init(elev=elev, azim=azim)

        # Set the axis ratio to 1:1:1
        self.set_axes_equal(ax)

        # Set the zoom level
        self.set_zoom(ax, zoom)

        # Set the labels for the axes
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        # Set the title of the plot
        ax.set_title(f'Point cloud downsampling rate: {voxel_size}')

        # Display the plot
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
        """Set the zoom level of the 3D plot"""
        # Get the current axis limits
        x_limits = ax.get_xlim3d()
        y_limits = ax.get_ylim3d()
        z_limits = ax.get_zlim3d()

        # Calculate the center point of each axis
        x_middle = np.mean(x_limits)
        y_middle = np.mean(y_limits)
        z_middle = np.mean(z_limits)

        # Calculate the half range of each axis
        x_half_range = abs(x_limits[1] - x_limits[0]) / 2
        y_half_range = abs(y_limits[1] - y_limits[0]) / 2
        z_half_range = abs(z_limits[1] - z_limits[0]) / 2

        # Adjust the range according to the zoom level
        x_half_range /= zoom
        y_half_range /= zoom
        z_half_range /= zoom

        # Set the new axis limits
        ax.set_xlim3d([x_middle - x_half_range, x_middle + x_half_range])
        ax.set_ylim3d([y_middle - y_half_range, y_middle + y_half_range])
        ax.set_zlim3d([z_middle - z_half_range, z_middle + z_half_range])