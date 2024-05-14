import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl

class VisualizerPyqtGraph:
    """
    This class provides methods that can be used to build frequently needed objects in graphics.
    """

    @staticmethod
    def generate_chamber_print_bed_obj(chamber_max_x: float, chamber_max_y: float, chamber_max_z: float, chamber_z_head_bed_offset: float):
        """
        Given the workspace dimensions this method generates a mesh object to display a print bed with initial z-position at 'chamber_position_z_head_bed_offset'.

        Returns bed object as opengl.GLMeshItem
        """
        # create movable *print bed*
        vertices = np.array([
            [chamber_max_x, chamber_max_y, -chamber_z_head_bed_offset],
            [0, chamber_max_y, -chamber_z_head_bed_offset],
            [0, 0, -chamber_z_head_bed_offset],
            [chamber_max_x, 0, -chamber_z_head_bed_offset]
        ])
        # Define vertex indices to form triangles
        faces = np.array([
            [0, 1, 2],
            [0, 2, 3]
        ])
        # Create mesh data for bed
        md = gl.MeshData(vertexes=vertices, faces=faces)
        # Create GLMeshItem and return it
        bed_object = gl.GLMeshItem(meshdata=md, smooth=False, color=(0.7, 0.7, 1.0, 1.0))
        return bed_object

    @staticmethod
    def generate_chamber_workspace(chamber_max_x: float, chamber_max_y: float, chamber_max_z: float, chamber_z_head_bed_offset: float):
        """
        Given the Workspace dimensions, this method returns an opengl.GLLinePlotItem, that can be used to display the
        chambers workspace in a opengl.GLViewWidget.
        """
        chamber_workspace_plot = gl.GLLinePlotItem()
        z_end_of_workspace = chamber_max_z + chamber_z_head_bed_offset
        vertices_chamber_border = np.array([
            # Draw upper rectangle and vertical lines to bottom at each corner
            [0, 0, 0], [0, 0, -z_end_of_workspace], [0, 0, 0],  # draw one vertical line and back ...
            [chamber_max_x, 0, 0], [chamber_max_x, 0, -z_end_of_workspace], [chamber_max_x, 0, 0],
            [chamber_max_x, chamber_max_y, 0], [chamber_max_x, chamber_max_y, -z_end_of_workspace],
            [chamber_max_x, chamber_max_y, 0],
            [0, chamber_max_y, 0], [0, chamber_max_y, -z_end_of_workspace], [0, chamber_max_y, 0],
            [0, 0, 0],  # Close the square by connecting back to the first vertex
            # Draw middle rectangle from z_head_bed_offset
            [0, 0, -chamber_z_head_bed_offset],
            [chamber_max_x, 0, -chamber_z_head_bed_offset],
            [chamber_max_x, chamber_max_y, -chamber_z_head_bed_offset],
            [0, chamber_max_y, -chamber_z_head_bed_offset],
            [0, 0, -chamber_z_head_bed_offset],
            # Draw the lowest rectangle from total workspace z_distance
            [0, 0, -z_end_of_workspace],
            [chamber_max_x, 0, -z_end_of_workspace],
            [chamber_max_x, chamber_max_y, -z_end_of_workspace],
            [0, chamber_max_y, -z_end_of_workspace],
            [0, 0, -z_end_of_workspace]
        ])
        chamber_workspace_plot.setData(pos=vertices_chamber_border, color=(1, 0, 0, 1), width=2.0)
        return chamber_workspace_plot

    @staticmethod
    def generate_mesh_scatter_plot(x_vec: np.array, y_vec: np.array, z_vec: np.array):
        new_scatter_mesh = gl.GLScatterPlotItem()
        color = (0.5,1,0,1)
        size = 3
        point_list = []
        for z in z_vec:
            for y in y_vec:
                for x in x_vec:
                    point_list.append([x, y, z])
        data = np.array(point_list)
        new_scatter_mesh.setData(pos=data, color=color, size=size)
        return new_scatter_mesh
