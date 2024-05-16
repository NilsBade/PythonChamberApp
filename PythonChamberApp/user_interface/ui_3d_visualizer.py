import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl

class VisualizerPyqtGraph:
    """
    This class provides methods that can be used to build frequently needed objects in graphics.
    """

    @staticmethod
    def generate_3d_chamber_print_bed_obj(chamber_max_x: float, chamber_max_y: float, chamber_max_z: float, chamber_z_head_bed_offset: float):
        """
        Given the workspace dimensions this method generates a mesh object to display a print bed with initial z-position at 'chamber_position_z_head_bed_offset'.

        Returns bed object as opengl.GLMeshItem
        """
        # create movable *print bed*
        vertices = np.array([
            [chamber_max_x, chamber_max_y, 0],
            [0, chamber_max_y, 0],
            [0, 0, 0],
            [chamber_max_x, 0, 0]
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
    def generate_3d_chamber_workspace(chamber_max_x: float, chamber_max_y: float, chamber_max_z: float, chamber_z_head_bed_offset: float):
        """
        Given the Workspace dimensions, this method returns an opengl.GLLinePlotItem, that can be used to display the
        chambers workspace in a opengl.GLViewWidget.
        """
        chamber_workspace_plot = gl.GLLinePlotItem()
        vertices_chamber_border = np.array([
            # Draw upper rectangle and vertical lines to bottom at each corner -> Z-level equal to end of probeHead
            [0, 0, chamber_z_head_bed_offset], [0, 0, -chamber_max_z], [0, 0, chamber_z_head_bed_offset],  # draw one vertical line and back ...
            [chamber_max_x, 0, chamber_z_head_bed_offset], [chamber_max_x, 0, -chamber_max_z], [chamber_max_x, 0, chamber_z_head_bed_offset],
            [chamber_max_x, chamber_max_y, chamber_z_head_bed_offset], [chamber_max_x, chamber_max_y, -chamber_max_z],
            [chamber_max_x, chamber_max_y, chamber_z_head_bed_offset],
            [0, chamber_max_y, chamber_z_head_bed_offset], [0, chamber_max_y, -chamber_max_z], [0, chamber_max_y, chamber_z_head_bed_offset],
            [0, 0, chamber_z_head_bed_offset],  # Close the square by connecting back to the first vertex
            # Draw middle rectangle - bed zero coordinate
            [0, 0, 0],
            [chamber_max_x, 0, 0],
            [chamber_max_x, chamber_max_y, 0],
            [0, chamber_max_y, 0],
            [0, 0, 0],
            # Draw the lowest rectangle from total workspace z_distance
            [0, 0, -chamber_max_z],
            [chamber_max_x, 0, -chamber_max_z],
            [chamber_max_x, chamber_max_y, -chamber_max_z],
            [0, chamber_max_y, -chamber_max_z],
            [0, 0, -chamber_max_z]
        ])
        chamber_workspace_plot.setData(pos=vertices_chamber_border, color=(1, 0, 0, 1), width=2.0)
        return chamber_workspace_plot


    @staticmethod
    def generate_3d_antenna_object(antenna_height: float, antenna_width: float, point_up: bool):
        """
        Given an antenna height, this function returns a 3D visualization of an probing antenna for display


        :param antenna_height: Height of antenna dummy in [mm]
        :param antenna_width: Base-length of antenna dummy in [mm]
        :param point_up: True > Antenna points +z direction, False > Antenna points -z direction
        :return: opengl.GLLinePlotItem
        """
        vertices = VisualizerPyqtGraph.generate_3d_antenna_object_vertices(antenna_height, antenna_width, point_up)
        antenna_plot = gl.GLLinePlotItem(pos=vertices, color=(0, 1.0, 1.0, 0.3), width=4.0)
        return antenna_plot

    @staticmethod
    def generate_3d_antenna_object_vertices(antenna_height: float, antenna_width: float, point_up: bool):

        # create cubic antenna dummy
        w = antenna_width / 2
        look_direction = antenna_height

        if point_up is False:  # invert direction when look down
            look_direction *= -1

        points = np.array([
            [-w, -w, 0], [-w, -w, look_direction], [-w, -w, 0],
            [w, -w, 0], [w, -w, look_direction], [w, -w, 0],
            [w, w, 0], [w, w, look_direction], [w, w, 0],
            [-w, w, 0], [-w, w, look_direction], [-w, w, 0],
            [-w, -w, 0],
            [-w, -w, look_direction],[w, -w, look_direction],[w, w, look_direction],[-w, w, look_direction],
            [-w, -w, look_direction],
        ])
        return points

    @staticmethod
    def generate_antenna_object_old(antenna_height: float, antenna_width: float, point_up: bool):
        """
        Given an antenna height, this function returns a 3D visualization of an probing antenna for display


        :param antenna_height: Height of antenna dummy in [mm]
        :param antenna_width: Base-length of antenna dummy in [mm]
        :param point_up: True > Antenna points +z direction, False > Antenna points -z direction
        :return: opengl.GLMeshItem
        """
        # create cubic antenna dummy
        w = antenna_width/2
        look_direction = antenna_height

        if point_up is False:   # invert direction when look down
            look_direction *= -1

        vertices = np.array([
            [-w, -w, 0],
            [w, -w, 0],
            [w, w, 0],
            [-w, w, 0],
            [-w, -w, look_direction],
            [w, -w, look_direction],
            [w, w, look_direction],
            [-w, w, look_direction],
        ])
        # Define vertex indices to form triangles
        faces = np.array([
            [0, 1, 2], [0, 2, 3],
            [0, 5, 1], [0, 4, 5],
            [1, 2, 6], [1, 5, 6],
            [2, 3, 6], [3, 6, 7],
            [0, 4, 3], [3, 4, 7],
            [4, 5, 7], [5, 6, 7]
        ])
        # Create mesh data for probe
        md = gl.MeshData(vertexes=vertices, faces=faces)
        # Create GLMeshItem and return it
        probe_object = gl.GLMeshItem(meshdata=md, smooth=False, color=(0.1, 0.1, 0.1, 1.0))
        return probe_object

    @staticmethod
    def generate_3d_mesh_scatter_plot(x_vec: np.array, y_vec: np.array, z_vec: np.array):
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

    @staticmethod
    def generate_point_list(x_vec: tuple[float, ...], y_vec: tuple[float, ...], z_vec: tuple[float, ...]):
        """
        :param x_vec: vector of x coordinates
        :param y_vec: vectors of y coordinates
        :param z_vec: vectors of z coordinates
        :return: list of points as 3d vectors e.g. list: [ [x1, y1, z1],[x2, y1, z1],... ]
        """
        point_list = []
        for z in z_vec:
            for y in y_vec:
                for x in x_vec:
                    point_list.append([x, y, z])
        return point_list
