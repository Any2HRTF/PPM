import csv
import io
import os
import sys
import tempfile
from contextlib import redirect_stdout

import bpy
import bmesh
import mathutils
import numpy as np

from .render_helpers import render

def euler_to_quaternion(euler_matrix: np.array, sequence: str = "ZYX") -> np.array:
    """Transforms a rotation matrix into a quaternion.

    Parameters
    ----------
    euler_matrix : np.array
        Rotation matrix.
    sequence : str
        Rotation sequence.
        "ZYX" (default) | "ZYZ" | "ZXY" | "ZXZ" | "YXY" | "YZX" | "YXZ" | "YZY" | "XYX" | "XYZ" | "XZX" | "XZY"

    Returns
    -------
    np.array
        Quaternion.
    """
    quaternion = np.zeros((4,))

    if sequence.lower() == "zyx":
        c_1 = np.cos(euler_matrix[0] * 0.5)
        s_1 = np.sin(euler_matrix[0] * 0.5)
        c_2 = np.cos(euler_matrix[1] * 0.5)
        s_2 = np.sin(euler_matrix[1] * 0.5)
        c_3 = np.cos(euler_matrix[2] * 0.5)
        s_3 = np.sin(euler_matrix[2] * 0.5)

        quaternion[0] = c_1 * c_2 * c_3 + s_1 * s_2 * s_3
        quaternion[1] = c_1 * c_2 * s_3 - s_1 * s_2 * c_3
        quaternion[2] = c_1 * s_2 * c_3 + s_1 * c_2 * s_3
        quaternion[3] = s_1 * c_2 * c_3 - c_1 * s_2 * s_3

    elif sequence.lower() == "zyz":
        t_1 = euler_matrix[0] * 0.5
        t_2 = euler_matrix[1] * 0.5
        t_3 = euler_matrix[2] * 0.5

        quaternion[0] = np.cos(t_2) * np.cos(t_1 + t_3)
        quaternion[1] = np.sin(t_2) * np.sin(-t_1 + t_3)
        quaternion[2] = np.sin(t_2) * np.cos(-t_1 + t_3)
        quaternion[3] = np.cos(t_2) * np.sin(t_1 + t_3)

    elif sequence.lower() == "zxy":
        # TODO
        raise NotImplementedError("Sequence 'ZXY' not implemented yet.")

    elif sequence.lower() == "zxz":
        # TODO
        raise NotImplementedError("Sequence 'ZXZ' not implemented yet.")

    elif sequence.lower() == "yxy":
        # TODO
        raise NotImplementedError("Sequence 'YXY' not implemented yet.")

    elif sequence.lower() == "yzx":
        # TODO
        raise NotImplementedError("Sequence 'YZX' not implemented yet.")

    elif sequence.lower() == "yxz":
        # TODO
        raise NotImplementedError("Sequence 'YXZ' not implemented yet.")

    elif sequence.lower() == "yzy":
        # TODO
        raise NotImplementedError("Sequence 'YZY' not implemented yet.")

    elif sequence.lower() == "xyx":
        # TODO
        raise NotImplementedError("Sequence 'XYX' not implemented yet.")

    elif sequence.lower() == "xyz":
        # TODO
        raise NotImplementedError("Sequence 'XYZ' not implemented yet.")

    elif sequence.lower() == "xzx":
        # TODO
        raise NotImplementedError("Sequence 'XZX' not implemented yet.")

    elif sequence.lower() == "xzy":
        # TODO
        raise NotImplementedError("Sequence 'XZY' not implemented yet.")

    else:
        raise ValueError(f"Sequence '{sequence}' not supported.")

    return quaternion


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


class BezierPPM:
    """PPM class

    Parameters:
    -----------
        from_blender_file (str): Path to a blender file to load the PPM from; if None, the standard PPM is loaded
        from_csv_file (str): Path to a csv file to load the PPM parameters from; if None, the standard PPM is loaded
        from_dict (dict): Dictionary containing the PPM parameters; if None, the standard PPM is loaded
    """

    def __init__(
        self,
        from_blender_file=None,
        from_csv_file=None,
        from_dict=None,
        backend="blender",
    ):
        self.metadata = {
            "Model": "BezierPPM",
            "Version": "",
            "APIName": "",
            "APIVersion": "",
            "Author": "",
        }
        if from_blender_file != None and from_csv_file != None:
            raise Exception("Either load from blender file or from csv file.")

        if backend != "blender" and from_blender_file != None:
            raise Exception("Blender backend not selected.")

        self.backend = backend

        # load init parameters
        self.__parameters = self.__load_parameters_from_csv()

        if from_blender_file != None:
            self.__load_blender_file(from_blender_file)
            self.__get_parameters_from_blender()

        # rerun fct to load parameters from csv file
        if from_csv_file != None:
            self.__parameters = self.__load_parameters_from_csv(from_csv_file)

        if from_dict != None:
            self.__parameters = self.__load_parameters_from_dict(from_dict)

        self.__reference_point = None
        
        # ugly but if set_parameter arg should be named type needs to be done
        self.type_ = type


    def __load_blender_file(self, filepath):
        logfile = tempfile.mktemp()
        open(logfile, "a").close()
        old = os.dup(sys.stdout.fileno())
        sys.stdout.flush()
        os.close(sys.stdout.fileno())
        fd = os.open(logfile, os.O_WRONLY)
        bpy.ops.wm.open_mainfile(filepath=filepath)
        # disable output redirection
        os.close(fd)
        os.dup(old)
        os.close(old)
        bpy.ops.object.mode_set(mode="OBJECT")

    @property
    def mesh_reference_point(self):
        return self.__reference_point

    @mesh_reference_point.setter
    def mesh_reference_point(self, reference_point):

        self.center_mesh(reference_point=reference_point)

    @property
    def points(self):
        """The point cloud of the PPM"""
        return self.get_point_cloud()

    @property
    def parameters(self):
        """The parameters of the PPM"""
        return self.__parameters

    @parameters.setter
    def parameters(self, parameters):
        for parameter_name, parameter in parameters.items():
            for point_name, point in parameter.items():
                if point_name == "Shape key":
                    self.__parameters[parameter_name][point_name] = point
                else:
                    for type_name, type in point.items():
                        if type_name == "Scale" and parameter_name != "Parent":
                            self.__parameters[parameter_name][point_name][
                                type_name
                            ] = type
                        else:
                            for axis_name, axis in type.items():
                                self.__parameters[parameter_name][point_name][
                                    type_name
                                ][axis_name] = axis

    def get_parameter_dict(self):
        """Returns the PPM parameters as a dictionary.

        Returns
        -------
        dict
            The PPM parameters.
        """
        export_dict = {}

        for parameter_name, parameter in self.__parameters.items():
            # shape keys
            if "Shape key" in parameter.keys():
                export_dict[f"Shape-{parameter_name}-Weight"] = self.__parameters[
                    parameter_name
                ]["Shape key"]
            else:
                for point_name, point in parameter.items():
                    # scale
                    if "Scale" in point.keys():
                        if "Parent" in parameter_name:
                            for axis, axis_value in point["Scale"].items():
                                export_dict[
                                    f"{point_name} bone-{parameter_name}-Scale {axis}"
                                ] = self.__parameters[parameter_name][point_name][
                                    "Scale"
                                ][
                                    axis
                                ]
                        else:
                            export_dict[f"{point_name} bone-{parameter_name}-Scale All"] = (
                                self.__parameters[parameter_name][point_name]["Scale"]
                            )
                    # rotation
                    if "Rotation" in point.keys():
                        for axis, axis_value in point["Rotation"].items():
                            export_dict[
                                f"{point_name} bone-{parameter_name}-Rotation {axis}"
                            ] = self.__parameters[parameter_name][point_name][
                                "Rotation"
                            ][
                                axis
                            ]
                    # location
                    if "Location" in point.keys():
                        for axis, axis_value in point["Location"].items():
                            export_dict[
                                f"{point_name} bone-{parameter_name}-Location {axis}"
                            ] = self.__parameters[parameter_name][point_name][
                                "Location"
                            ][
                                axis
                            ]

        return export_dict

    def __str__(self):

        string = f"Current PPM parameters:\n"
        for parameter_name, parameter in self.__parameters.items():
            string += f"{parameter_name}:\n"
            for point_name, point in parameter.items():
                string += f"  ∟{point_name}:\n"
                if point_name == "Shape key":
                    string += f"    ∟{point}\n"
                else:
                    for type_name, type in point.items():
                        string += f"    ∟{type_name}:\n"
                        if type_name == "Scale" and parameter_name != "Parent":
                            string += f"      ∟{type}\n"
                        else:

                            for axis_name, axis in type.items():
                                string += f"      ∟{axis_name}: {axis}\n"

        # remove last \n
        string = string[:-1]
        return string

    def set_parameter(
        self, name: str, type: str, value: tuple, point=None, axis=None
    ):
        """Set a parameter of the PPM

        Parameters:
        -----------
            name (str): Name of the parameter to set
            type (str): The type of the parameter to set (Shape key, Scale, Rotation, Location)
            point (str): The point to set the parameter to (Start, End, Shape key or None)
            axis (str): The axis to set the parameter to (e.g. X, Y, Z, XY, XYZ, WXYZ, ... or None)
            value (tuple): The value to set the parameter to
        """
        if self.type_(value) is list:
            value = tuple(value)
        elif self.type_(value) is not tuple:
            value = (value,)

        type = type.lower().capitalize()
        axis = axis.upper() if axis != None else None
        point = point.lower().capitalize() if point != None else None

        if type not in ["Shape key", "Scale", "Rotation", "Location"]:
            raise Exception(
                "type must be one of Shape key, Scale, Rotation, Location"
            )

        if point == "Shape key":
            if len(value) > 1:
                raise Exception("value must be a single float value")
            self.__parameters[name][type] = value
        elif type == "Scale":
            if point in ["Start", "End"]:
                raise Exception("Cannot scale points of bone.")
            if name.lower() == "parent":
                if axis is None:
                    axis = "XYZ"
                for a in axis:
                    if a not in ["X", "Y", "Z"]:
                        raise Exception("axis must be X, Y, Z")
                for i in range(len(value)):
                    self.__parameters[name]["Bendy"][type][axis[i]] = (
                        value[i]
                    )
            else:
                if len(value) > 1:
                    raise Exception("value must be a single float value")
                self.__parameters[name]["Bendy"][type] = value[0]
        else:
            if point not in ["Start", "End"] and name != "Parent":
                raise Exception("point must be one of Start, End")
            elif name == "Parent":
                point = "Bendy"

            if len(value) != len(axis):
                raise Exception("value and axis must have the same number of elements")

            if type == "Location":
                for a in axis:
                    if a not in ["X", "Y", "Z"]:
                        raise Exception("axis must be X, Y, Z")
                for i in range(len(value)):
                    self.__parameters[name][point][type][axis[i]] = (
                        value[i]
                    )

            elif type == "Rotation":
                # rotation defined in euler angles
                if len(axis) == 3:
                    for a in axis:
                        if a not in ["X", "Y", "Z"]:
                            raise Exception("axis must be X, Y, Z")

                    quaternion = euler_to_quaternion(value, sequence=axis)

                    self.__parameters[name][point][type]["W"] = (
                        quaternion[0]
                    )
                    self.__parameters[name][point][type]["X"] = (
                        quaternion[1]
                    )
                    self.__parameters[name][point][type]["Y"] = (
                        quaternion[2]
                    )
                    self.__parameters[name][point][type]["Z"] = (
                        quaternion[3]
                    )

                elif len(axis) == 4:
                    if not all(elem in axis for elem in ["W", "X", "Y", "Z"]):
                        raise Exception("axis must contain W, X, Y, Z")

                    for i in range(len(value)):
                        self.__parameters[name][point][type][axis[i]] = (
                            value[i]
                        )

    def __load_parameters_from_dict(self, parameter_dict: dict) -> dict:
        parameters = {}
        for key, value in parameter_dict.items():
            if len(key) == key:
                continue
            elif "Shape" in key:
                type = "Shape key"
                name = '-'.join(key.split('-')[1:-1])
                point = None
                axis = None
            elif "Rotation" in key or "Location" in key or "Scale" in key:
                object, name, function = key.split('-')
                type, axis = function.split(' ')
                point =  object.split(' ')[0]
                if not name == "Parent" and type == "Scale":
                    axis = None
            value = float(value)

            if type == "Scale":
                pass

            if name not in parameters:
                parameters[name] = {}
            if point != None:
                if point not in parameters[name]:
                    parameters[name][point] = {}
                if axis != None:
                    if type not in parameters[name][point]:
                        parameters[name][point][type] = {}
                    parameters[name][point][type][axis] = value
                else:
                    parameters[name][point][type] = value
            else:
                if axis != None:
                    if type not in parameters[name]:
                        parameters[name][type] = {}
                    parameters[name][type][axis] = value
                else:
                    parameters[name][type] = value

        return parameters

    def __load_parameters_from_csv(self, csv_file=None) -> dict:

        if csv_file is None:
            csv_file = f"{CURRENT_DIR}/resources/PPM.csv"

        with open(csv_file, newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            parameters = {}

            for key, value in reader:
                if len(key) == key:
                    continue
                elif "Shape" in key:
                    type = "Shape key"
                    name = '-'.join(key.split('-')[1:-1])
                    point = None
                    axis = None
                elif "Rotation" in key or "Location" in key or "Scale" in key:
                    object, name, function = key.split('-')
                    type, axis = function.split(' ')
                    point =  object.split(' ')[0]
                    if not name == "Parent" and type == "Scale":
                        axis = None
                else:
                    # TODO: implement checks
                    if key == "General-APIVersion":
                        self.metadata["APIVersion"] = value
                    elif key == "General-Version":
                        self.metadata["Version"] = value
                    elif key == "General-Author":
                        self.metadata["Author"] = value
                    elif key == "General-APIName":
                        self.metadata["APIName"] = value
                    continue
                value = float(value)

                if type == "Scale":
                    pass

                if name not in parameters:
                    parameters[name] = {}
                if point != None:
                    if point not in parameters[name]:
                        parameters[name][point] = {}
                    if axis != None:
                        if type not in parameters[name][point]:
                            parameters[name][point][type] = {}
                        parameters[name][point][type][axis] = value
                    else:
                        parameters[name][point][type] = value
                else:
                    if axis != None:
                        if type not in parameters[name]:
                            parameters[name][type] = {}
                        parameters[name][type][axis] = value
                    else:
                        parameters[name][type] = value
        return parameters

    def reset_parameters(self):
        """Resets the PPM parameters to the default parameters."""
        self.__parameters = self.__load_parameters_from_csv()

    def __set_parameters_in_blender(self):
        self.__load_blender_file(f"{CURRENT_DIR}/resources/PPM.blend")

        if self.__reference_point is not None:
            self.__center_mesh_blender(reference_point=self.__reference_point)

        obj = bpy.data.objects["Armature"]
        for parameter_name, parameter in self.__parameters.items():
            # shape keys
            if "Shape key" in parameter.keys():
                bpy.data.shape_keys["Key"].key_blocks[parameter_name].value = (
                    self.__parameters[parameter_name]["Shape key"]
                )
            else:
                for point_name, point in parameter.items():
                    # scale
                    if "Scale" in point.keys():
                        if "Parent" in parameter_name:
                            for axis, axis_value in point["Scale"].items():
                                obj.pose.bones[parameter_name + "-" + point_name].scale[
                                    (
                                        0
                                        if axis == "X"
                                        else (
                                            1
                                            if axis == "Y"
                                            else 2 if axis == "Z" else None
                                        )
                                    )
                                ] = axis_value

                        else:
                            obj.pose.bones[parameter_name + "-" + point_name].scale[
                                0
                            ] = self.__parameters[parameter_name][point_name]["Scale"]
                            obj.pose.bones[parameter_name + "-" + point_name].scale[
                                1
                            ] = self.__parameters[parameter_name][point_name]["Scale"]
                            obj.pose.bones[parameter_name + "-" + point_name].scale[
                                2
                            ] = self.__parameters[parameter_name][point_name]["Scale"]
                    # rotation
                    if "Rotation" in point.keys():
                        for axis, axis_value in point["Rotation"].items():
                            obj.pose.bones[
                                parameter_name + "-" + point_name
                            ].rotation_quaternion[
                                (
                                    0
                                    if axis == "W"
                                    else (
                                        1
                                        if axis == "X"
                                        else (
                                            2
                                            if axis == "Y"
                                            else 3 if axis == "Z" else None
                                        )
                                    )
                                )
                            ] = axis_value
                    # location
                    if "Location" in point.keys():
                        for axis, axis_value in point["Location"].items():
                            obj.pose.bones[parameter_name + "-" + point_name].location[
                                (
                                    0
                                    if axis == "X"
                                    else (
                                        1 if axis == "Y" else 2 if axis == "Z" else None
                                    )
                                )
                            ] = (1000 * axis_value)

    def __get_parameters_from_blender(self):

        obj = bpy.data.objects["Armature"]

        for parameter_name, parameter in self.__parameters.items():
            # shape keys
            if "Shape key" in parameter.keys():
                self.__parameters[parameter_name]["Shape key"] = (
                    bpy.data.shape_keys["Key"].key_blocks[parameter_name].value
                )
            else:
                for point_name, point in parameter.items():
                    # scale
                    if "Scale" in point.keys():
                        if "Parent" in parameter_name:
                            for axis, axis_value in point["Scale"].items():
                                self.__parameters[parameter_name][point_name]["Scale"][
                                    axis
                                ] = obj.pose.bones[
                                    parameter_name + "-" + point_name
                                ].scale[
                                    (
                                        0
                                        if axis == "X"
                                        else (
                                            1
                                            if axis == "Y"
                                            else 2 if axis == "Z" else None
                                        )
                                    )
                                ]
                        else:
                            self.__parameters[parameter_name][point_name]["Scale"] = (
                                obj.pose.bones[parameter_name + "-" + point_name].scale[
                                    0
                                ]
                            )
                    # rotation
                    if "Rotation" in point.keys():
                        for axis, axis_value in point["Rotation"].items():
                            self.__parameters[parameter_name][point_name]["Rotation"][
                                axis
                            ] = obj.pose.bones[
                                parameter_name + "-" + point_name
                            ].rotation_quaternion[
                                (
                                    0
                                    if axis == "W"
                                    else (
                                        1
                                        if axis == "X"
                                        else (
                                            2
                                            if axis == "Y"
                                            else 3 if axis == "Z" else None
                                        )
                                    )
                                )
                            ]
                    # location
                    if "Location" in point.keys():
                        for axis, axis_value in point["Location"].items():
                            self.__parameters[parameter_name][point_name]["Location"][
                                axis
                            ] = (
                                1
                                / 1000
                                * obj.pose.bones[
                                    parameter_name + "-" + point_name
                                ].location[
                                    (
                                        0
                                        if axis == "X"
                                        else (
                                            1
                                            if axis == "Y"
                                            else 2 if axis == "Z" else None
                                        )
                                    )
                                ]
                            )

    def __get_point_cloud_blender(self):

        obj = bpy.data.objects["Mesh"]

        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode="OBJECT")

        depsgraph = bpy.context.evaluated_depsgraph_get()
        obj_eval = obj.evaluated_get(depsgraph)
        bm = bmesh.new()
        me = obj_eval.to_mesh()
        me.transform(obj.matrix_world)
        bm.from_mesh(me)
        obj.to_mesh_clear()

        verts = [v.co for v in bm.verts]

        return np.array(verts)

    def get_point_cloud(self) -> np.array:
        """Returns the point cloud of the PPM.

        Returns
        -------
        np.array
            Point cloud of the PPM.
        """
        if self.backend == "blender":
            self.__set_parameters_in_blender()
            return self.__get_point_cloud_blender()
        else:
            raise NotImplementedError

    def __export_ply_blender(self, file):

        bpy.ops.object.select_all(action="DESELECT")
        bpy.data.objects["Mesh"].select_set(True)
        # bpy.context.view_layer.objects.active = bpy.data.objects['Mesh']

        with redirect_stdout(io.StringIO()):
#             bpy.ops.export_mesh.ply(filepath=file, use_selection=True)
            bpy.ops.export_mesh.stl(filepath=file,filter_glob='*.ply', use_selection=True)

    def export_ply(self, file):
        """Exports the PPM as a PLY file.

        Parameters
        ----------
        file : str
            Path to the PLY file.
        """
        if file[-4:] != ".ply":
            file += ".ply"
        if self.backend == "blender":
            self.__set_parameters_in_blender()
            self.__export_ply_blender(file)
        else:
            raise NotImplementedError

    def __export_stl_blender(self, file):

        bpy.ops.object.select_all(action="DESELECT")
        bpy.data.objects["Mesh"].select_set(True)

        with redirect_stdout(io.StringIO()):
            bpy.ops.export_mesh.stl(filepath=file, use_selection=True)

    def export_stl(self, file):
        """Exports the PPM as a STL file.

        Parameters
        ----------
        file : str
            Path to the STL file.
        """
        if file[-4:] != ".stl":
            file += ".stl"
        if self.backend == "blender":
            self.__set_parameters_in_blender()
            self.__export_stl_blender(file)
        else:
            raise NotImplementedError

    def __export_blend_blender(self, file):

        bpy.ops.wm.save_as_mainfile(filepath=file)

    def export_blend(self, file: str):
        """Exports the PPM as a blend file.

        Parameters
        ----------
        file : str
            Path to the blend file.(NOTE: has to be an absolute path)
        """

        if self.backend != "blender":
            raise NotImplementedError

        self.__set_parameters_in_blender()
        self.__export_blend_blender(file=file)

    def export_csv(self, file):
        """Exports the PPM as a CSV file.

        Parameters
        ----------
        file : str
            Path to the CSV file.
        """

        export_dict = self.get_parameter_dict()

        with open(file, "w", newline="") as csvfile:
            for key, value in self.metadata.items():
                csvfile.write(f"General-{key},{value}\n")
            for key, value in export_dict.items():
                csvfile.write(f"{key},{value:e}\n")

    def render(self, *args, **kwargs):
        """Renders the PPM.

        Parameters
        ----------
        file : str
            Path to the rendered image.
        camera_location : list
            Location of the camera. Default: [-10, 170, 5]
            If str not given the unit will be infered from the unit of the PPM.
        camera_rotation : list
            Rotation of the camera. Default: [90, 0, 180]
        camera_location_reference : list or None
            Location of the reference camera.
        light_location : list
            Location of the light source in global coordinates. Default: [-0.01, 0.15, 0.1]
        light_rotation : list
            Rotation of the light source in Euler angles ('XYZ'). Default: [0, 0, 0]
        light_power : float
            Power of the light source in Watts. Default: 200000
        light_type : str
            Type of the light source. Default: 'AREA'.
            Currently, only 'AREA' is supported.
        light_shape : str
            Shape of the light source. Can be one of 'SQUARE', 'RECTANGLE', 'DISC' or 'ELLIPSE'. Default: 'SQUARE'
        light_size : list
            Dimensions for the SQUARE or RECTANGLE. Default: [0.1, 0.1]
        depth_farthest : float
            Farthest depth value. Default is 1.25 times the radius of the camera.
        depth_nearest : float
            Farthest depth value. Default 0.
        resolution : int
            Resolution of the rendered image. Default: 256
        depth : bool
            Whether to render the depth map. Default: False
        smooth_shading : bool
            Whether to render the image with smooth shading. Default: True
        image_compression : int
            Compression of the rendered image. Default: 0
        image_color_depth : str
            Color depth of the rendered image. Default: '8'
        depth_codec_exr : str
            Codec of the depth map. Default: 'NONE'
        depth_color_depth_exr : str
            Color depth of the depth map. Default: '16'
        depth_compression_exr : int
            Compression of the depth map. Default: 0
        """
        if self.backend == "blender":
            self.__set_parameters_in_blender()
            # redirect output to temporary file
            logfile = tempfile.mktemp()
            open(logfile, "a").close()
            old = os.dup(sys.stdout.fileno())
            sys.stdout.flush()
            os.close(sys.stdout.fileno())
            fd = os.open(logfile, os.O_WRONLY)

            if "camera_location" not in kwargs.keys():
                kwargs["camera_location"] = [-0.010, 0.170, 0.005]

            if "camera_location_reference" not in kwargs.keys():
                kwargs["camera_location_reference"] = None

            if "depth_farthest" not in kwargs.keys():
                kwargs["depth_farthest"] = 1.25 * np.sqrt(
                    kwargs["camera_location"][0] ** 2
                    + kwargs["camera_location"][1] ** 2
                    + kwargs["camera_location"][2] ** 2
                )

            if "depth_nearest" not in kwargs.keys():
                kwargs["depth_nearest"] = 0

            if "camera_rotation" not in kwargs.keys():
                kwargs["camera_rotation"] = [90, 0, 180]

            if "light_type" not in kwargs.keys():
                kwargs["light_type"] = "AREA"

            if kwargs["light_type"] != "AREA":
                raise NotImplementedError

            if "light_shape" not in kwargs.keys():
                kwargs["light_shape"] = "SQUARE"

            if "light_location" not in kwargs.keys():
                kwargs["light_location"] = np.array([-0.01, 0.15, 0.1]) * 1000
            else:
                kwargs["light_location"] = np.array(kwargs["light_location"]) * 1000

            if "light_rotation" not in kwargs.keys():
                kwargs["light_rotation"] = [0, 0, 0]

            if "light_power" not in kwargs.keys():
                kwargs["light_power"] = 200000
            
            render(
                dirpath="/".join(kwargs["file"].split("/")[:-1]),
                filename=kwargs["file"].split("/")[-1],
                resolution=kwargs["resolution"] if "resolution" in kwargs else 256,
                depth=kwargs["depth"] if "depth" in kwargs else False,
                smooth_shading=(
                    kwargs["smooth_shading"] if "smooth_shading" in kwargs else True
                ),
                image_compression=(
                    kwargs["image_compression"] if "image_compression" in kwargs else 0
                ),
                image_color_depth=(
                    kwargs["image_color_depth"]
                    if "image_color_depth" in kwargs
                    else "8"
                ),
                camera_location=kwargs["camera_location"],
                camera_rotation=kwargs["camera_rotation"],
                camera_location_reference=kwargs["camera_location_reference"],
                light_location=kwargs["light_location"],
                light_rotation=kwargs["light_rotation"],
                light_power=kwargs["light_power"],
                light_type=kwargs["light_type"],
                light_shape=kwargs["light_shape"],
                depth_farthest=kwargs["depth_farthest"],
                depth_nearest=(
                    kwargs["depth_nearest"]
                    if "depth_nearest" in kwargs
                    else "camera_location"
                ),
                depth_codec_exr=(
                    kwargs["depth_codec_exr"] if "depth_codec_exr" in kwargs else "NONE"
                ),
                depth_color_depth_exr=(
                    kwargs["depth_color_depth_exr"]
                    if "depth_color_depth_exr" in kwargs
                    else "16"
                ),
                depth_compression_exr=(
                    kwargs["depth_compression_exr"]
                    if "depth_compression_exr" in kwargs
                    else 0
                ),
            )

            # disable output redirection
            os.close(fd)
            os.dup(old)
            os.close(old)
        else:
            raise NotImplementedError

    def center_mesh(self, reference_point="ear_canal_entrance"):

        self.__reference_point = reference_point

    def __center_mesh_blender(self, reference_point):
        # get reference point
        if reference_point == "ear_canal_entrance":
            reference_point = self.__get_ear_canal_entrance_blender()
        elif reference_point == "center_of_mass":
            reference_point = self.__get_center_of_mass_blender()
        else:
            raise ValueError(
                "reference_point must be either 'ear_canal_entrance' or 'center_of_mass'."
            )

        # move object so that the reference point coincides with the center of the global coordinate system
        obj = bpy.data.objects["Armature"]
        obj.matrix_world = (
            mathutils.Matrix.Translation(-reference_point) @ obj.matrix_world
        )

    def __get_ear_canal_entrance_blender(self):

        vs = [
            vert
            for vert in bpy.context.object.data.vertices
            if bpy.context.object.vertex_groups["Ear_canal_entrance_center"].index
            in [i.group for i in vert.groups]
        ]
        local_ear_canal_entrance = vs[0].co

        obj = bpy.data.objects["Mesh"]
        ear_canal_entrance = obj.matrix_world @ local_ear_canal_entrance

        return ear_canal_entrance

    def __get_center_of_mass_blender(self):

        # get center of mass of PPM template mesh bounding box
        obj = bpy.data.objects["Mesh"]
        local_bounding_box_center = (
            1
            / 8
            * sum((mathutils.Vector(b) for b in obj.bound_box), mathutils.Vector())
        )

        # convert to world coordinates
        center_of_mass = obj.matrix_world @ local_bounding_box_center

        return center_of_mass


if __name__ == "__main__":

    p = BezierPPM()
    import os
    filedir = os.getcwd()
    
    p.metadata["Author"] = "James Bond"
    
    p.export_csv(file=filedir+"/parameters.csv")
#     parameter_dict = p.get_parameter_dict()
#     p = BezierPPM(from_dict=parameter_dict)
#     p.export_csv(file=filedir+"/parameters copy.csv")
#     p.set_parameter(name='Parent', type='Scale', value=(0.75, 1.5, 0.9), axis='ZXY')
#     p.export_ply(file=filedir+"/test")
#     p.set_parameter(name='Helix up', point='Start', type='Location', value=(0.01,0.006), axis='ZX')
#     p.export_stl(file=filedir+"/test2")
#     q = (np.sqrt(2)/2, np.sqrt(2)/2, 0, 0)
#     p.set_parameter(name='Parent', point='Bendy', type='Rotation', value=q, axis='WXYZ')    
#     p.export_stl(file=filedir+"/test3")
#     
#     p.render(file=filedir+"/test4", depth=True)
