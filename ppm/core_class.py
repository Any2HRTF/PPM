import os
import bpy
import uuid
from pandas import read_csv
import numpy as np
os.environ["OPENCV_IO_ENABLE_OPENEXR"]="1"

from .blender.blender_support_classes import BaseBlenderObject, Bone


class PPM(BaseBlenderObject):
    """PPM class

    Parameters:
    -----------
        name (str): Name of the PPM object
        from_blender_file (str): Path to a blender file to load the PPM from; if None, the standard PPM is loaded
    """
    def __init__(self, name="PPM", from_blender_file=None, from_csv_file=None):
        self.__DIRNAME = os.path.join(os.path.dirname(__file__))

        self.PPM_BLENDER_NAME = 'ARI_PPM_v1'
    
        super().__init__(os.path.join(f'{self.__DIRNAME}/resources/tmp_' + str(uuid.uuid4())), name)

        if from_blender_file is not None:
            super()._load_blender_file(from_blender_file, self.PPM_BLENDER_NAME)

        else:
            # load standard ear
            super()._load_blender_file(f'{self.__DIRNAME}/resources/PPM_modified_v1.blend', self.PPM_BLENDER_NAME)

        self.bones = []
        self.bones_lookup = {}


        Bone("Lobulus", self)
        Bone("Helix_low", self)
        Bone("Helix_middle", self)
        Bone("Helix_up", self)
        Bone("Tragus", self)
        Bone("Antitragus", self)
        Bone("Antihelix", self)
        Bone("Crus_inferius_anthelicis", self)
        Bone("Crus_superius_anthelicis", self)
        Bone("Size", self)

        ppm_params = read_csv(f'{self.__DIRNAME}/resources/PPM_params_default_v1.csv', index_col=0)
        self.__params = { self.name: {} }
        for param_name, value in ppm_params.iterrows():
            self.__params[self.name][param_name] = value.values[0]

        if from_blender_file is not None:
            self.__get_ppm_params()

        if from_csv_file is not None:
            ppm_params = read_csv(from_csv_file, index_col=0)
            for param_name, value in ppm_params.iterrows():
                self.__params[self.name][param_name] = value.values[0]

    def get_ppm_params(self):
        """Get PPM parameters from Blender
        
        Returns:
        -------
            dict: Dictionary of parameters
        """

        return self.__params[self.name]
    
    def reset_parameters(self):
        """Reset PPM parameters to default"""
        ppm_params = read_csv(f'{self.__DIRNAME}/resources/PPM_params_default_v1.csv', index_col=0)
        self.__params = { self.name: {} }
        for param_name, value in ppm_params.iterrows():
            self.__params[self.name][param_name] = value.values[0]

        self.__set_ppm_params(self.get_ppm_params())

    def set_ppm_params(self, params):
        """Set PPM parameters in Blender
        
        Parameters:
        ----------
            params (dict): Dictionary of parameters to set
            
            Example:
                {
                    'Location_Antitragus-End_X':-10,
                    'Location_Antitragus-End_Y':-10,
                    'Location_Antitragus-End_Z':-10
                }
        """

        # TODO: check if params are valid
        self.__set_ppm_params(params)

    def __shape_key(self, name: str, val: float):
        bpy.data.shape_keys["Key.002"].key_blocks[name].value = val

    def __get_ppm_params(self):
        """Get PPM parameters from Blender"""
        for line, _ in self.__params[self.name].items():
            transform = line.split('_')[0]
            line = '_'.join(line.split('_')[1:])
            
            if transform == "Rotation":
                nm = line.split('-')[0]
                pnt = line.split('-')[1].split('_')[0]
                ax = line.split('_')[-1]
                obj = bpy.data.objects["Armature"].pose.bones[nm + "-" + pnt]

                if ax == 'W':
                    self.__params[self.name][transform + "_" + nm + "-" + pnt + "_" + ax] = obj.rotation_quaternion.w
                elif ax == 'X':
                    self.__params[self.name][transform + "_" + nm + "-" + pnt + "_" + ax] = obj.rotation_quaternion.x
                elif ax == 'Y':
                    self.__params[self.name][transform + "_" + nm + "-" + pnt + "_" + ax] = obj.rotation_quaternion.y
                elif ax == 'Z':
                    self.__params[self.name][transform + "_" + nm + "-" + pnt + "_" + ax] = obj.rotation_quaternion.z

            elif transform == "Location":
                nm = line.split('-')[0]
                pnt = line.split('-')[1].split('_')[0]
                ax = line.split('_')[-1]
                obj = bpy.data.objects["Armature"].pose.bones[nm + "-" + pnt]

                if ax == 'X':
                    self.__params[self.name][transform + "_" + nm + "-" + pnt + "_" + ax] = obj.location.x
                elif ax == 'Y':
                    self.__params[self.name][transform + "_" + nm + "-" + pnt + "_" + ax] = obj.location.y
                elif ax == 'Z':
                    self.__params[self.name][transform + "_" + nm + "-" + pnt + "_" + ax] = obj.location.z
                else:
                    pass

            elif transform == "Scale":
                nm = line.split('-')[0]
                pnt = line.split('-')[1].split('_')[0]
                ax = line.split('_')[-1]
                obj = bpy.data.objects["Armature"].pose.bones[nm + "-" + pnt]

                if ax == 'X':
                    self.__params[self.name][transform + "_" + nm + "-" + pnt + "_" + ax] = obj.scale.x
                elif ax == 'Y':
                    self.__params[self.name][transform + "_" + nm + "-" + pnt + "_" + ax] = obj.scale.y
                elif ax == 'Z':
                    self.__params[self.name][transform + "_" + nm + "-" + pnt + "_" + ax] = obj.scale.z
                else:
                    pass

            elif transform == "Shape":
                nm = '_'.join(line.split('_')[1:])
                obj = bpy.data.shape_keys["Key.002"].key_blocks[nm]
                self.__params[self.name][transform + '_' +line] = obj.value

    def __set_ppm_params(self, params:dict):
        """Set PPM parameters in Blender"""
        for line, value in params.items():

            if line not in self.__params[self.name]:
                raise Exception(f"Parameter {line} is not valid")

            self.__params[self.name][line] = value

            transform = line.split('_')[0]
            line = '_'.join(line.split('_')[1:])

            if transform == "Rotation":
                self.bones_lookup[line.split('-')[0]].rotation(
                    line.split('-')[1].split('_')[0],
                    line.split('_')[-1],
                    value
                )
            elif transform == "Location":
                self.bones_lookup[line.split('-')[0]].location(
                    line.split('-')[1].split('_')[0],
                    line.split('_')[-1],
                    value
                )
            elif transform == "Scale":
                if 'Size-Bendy' in line:
                    self.bones_lookup[line.split('-')[0]].scaling(
                        line.split('-')[1].split('_')[0],
                        line.split('_')[-1],
                        value
                    )
                else:
                    self.bones_lookup[line.split('-')[0]].scaling(
                        line.split('-')[1].split('_')[0],
                        'X',
                        value
                    )
                    self.bones_lookup[line.split('-')[0]].scaling(line.split('-')[1].split('_')[0],\
                        'Y', value)
                    self.bones_lookup[line.split('-')[0]].scaling(line.split('-')[1].split('_')[0],\
                        'Z', value)

            elif transform == "Shape":
                self.__shape_key('_'.join(line.split('_')[1:]), value)

    def get_image(self, *args, **kwargs):
        """Get image of the ear

        Parameters:
        -----------
            resolution: int
                resolution of the image
            cam_location: np.array
                camera location
        
        Returns:
        --------
            np.array: (num_cam_location, resolution, resolution)
        """
        path_to_img, _ = super()._render(
                            *args, **kwargs
                            )
        self.__set_ppm_params(self.__params[self.name])
        return super()._get_image(path_to_img, kwargs['resolution'])

    def get_depth(self, *args, **kwargs):
        """Get image of the ear
        
        Parameters:
        -----------
            resolution: int
                resolution of the image
            cam_location: np.array
                camera location
        
        Returns:
        --------
            np.array: (num_cam_location, resolution, resolution)
        """
        _, path_to_img = super()._render(
                            *args, **kwargs)
        self.__set_ppm_params(self.__params[self.name])
        return super()._get_depth(path_to_img, kwargs['resolution'])

    def get_point_cloud(self):
        """Get point cloud of the ear
        
        Returns:
        --------
            np.array: (num_points, 3)
        """
        self.__set_ppm_params(self.__params[self.name])
        return super()._get_pc(self.PPM_BLENDER_NAME)

    def save_ply(self, path_to_ply, save_as_npy=False):
        """Save point cloud of the ear in .ply format
        
        Parameters:
        -----------
            path_to_ply: str
                path to save .ply file
                *.ply or *.npy is appended to the path if not already specified
        """
        self.__set_ppm_params(self.__params[self.name])
        if not path_to_ply.endswith('.ply') and not save_as_npy:
            path_to_ply += '.ply'
        if save_as_npy:
            if path_to_ply.endswith('.ply'):
                path_to_ply = path_to_ply[:-4] + '.npy'
            if not path_to_ply.endswith('.npy'):
                path_to_ply += '.npy'

        if save_as_npy:
            np.save(path_to_ply, super()._get_pc(self.PPM_BLENDER_NAME))
        else:
            super()._export_pc(self.PPM_BLENDER_NAME, path_to_ply)

    def save_stl(self, path_to_stl):
        """Save STL of the ear
        
        Parameters:
        -----------
            path_to_stl: str
                path to save .stl file
                *.stl is appended to the path if not already specified
        """
        self.__set_ppm_params(self.__params[self.name])
        if not path_to_stl.endswith('.stl'):
            path_to_stl += '.stl'
        super()._export_mesh(self.PPM_BLENDER_NAME, path_to_stl)

    def save_parameters(self, path_to_params):
        """Save parameters of the ear
        
        Parameters:
        -----------
            path_to_params: str
                path to save .csv file
                *.csv  is appended to the path if not already specified
        """
        if not path_to_params.endswith('.csv'):
            path_to_params += '.csv'

        with open(path_to_params, 'w', encoding='utf8') as f:
            for key, value in self.__params[self.name].items():
                f.write("%s,%s\n"%(key,value))

    def render(
            self,
            *args, **kwargs) -> tuple:
        """Render image and depth of the ear

        Parameters:
        -----------
            resolution: int
                resolution of the image
            cam_location: np.array
                camera location

        Returns:
        --------
            np.array: (num_cam_location, resolution, resolution)
            np.array: (num_cam_location, resolution, resolution)
        """

        self.__set_ppm_params(self.__params[self.name])

        cam_loc = kwargs['cam_loc']
        # kwargs.pop('cam_loc', None)

        if cam_loc.shape == (3,):
            cam_loc = cam_loc.reshape(3,1)

        image = np.zeros((cam_loc.shape[1], kwargs['resolution'], kwargs['resolution']))
        depth_image = np.zeros((cam_loc.shape[1], kwargs['resolution'], kwargs['resolution']))

        for i in range(cam_loc.shape[1]):
            kwargs['cam_loc'] = cam_loc[:,i]
            path_to_img, path_to_depth = super()._render(
                        *args, **kwargs)

            image[i,...] = super()._get_image(path_to_img, kwargs['resolution'])
            depth_image[i,...] = super()._get_depth(path_to_depth, kwargs['resolution'])

        return image, depth_image
