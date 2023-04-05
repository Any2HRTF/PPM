import os
import bpy
import uuid
from pandas import read_csv
import numpy as np
os.environ["OPENCV_IO_ENABLE_OPENEXR"]="1"

from .blender.blender_support_classes import BaseBlenderObject, Bone
from .math_helpers import euler_to_quaternion


class PPM(BaseBlenderObject):
    """PPM class

    Parameters:
    -----------
        from_blender_file (str): Path to a blender file to load the PPM from; if None, the standard PPM is loaded
        from_csv_file (str): Path to a csv file to load the PPM parameters from; if None, the standard PPM is loaded
    """
    def __init__(self, from_blender_file=None, from_csv_file=None):

        if from_blender_file and from_csv_file:
            raise ValueError("Please only provide one of the parameters from_blender_file and from_csv_file")

        self.__DIRNAME = os.path.join(os.path.dirname(__file__))
        self.__TEMP_DIR = os.path.join(f'{self.__DIRNAME}/resources/tmp/')

        self.PPM_BLENDER_NAME = 'ARI_PPM_v1'
    
        super().__init__(self.__TEMP_DIR)

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

        ppm_params = read_csv(f'{self.__DIRNAME}/resources/PPM_params_default_v1.csv',  header=None, index_col=0)
        self.__params = {}
        for param_name, value in ppm_params.iterrows():
            self.__params[param_name] = value.values[0]

        if from_blender_file is not None:
            self.__get_ppm_params()

        if from_csv_file is not None:
            ppm_params = read_csv(from_csv_file,  header=None, index_col=0)
            for param_name, value in ppm_params.iterrows():
                self.__params[param_name] = value.values[0]

    def get_parameters(self):
        """Get PPM parameters from Blender
        
        Returns:
        -------
            dict: Dictionary of parameters
        """

        self.__get_ppm_params()

        params = {
            'Location' : {},
            'Rotation' : {},
            'Scale' : {},
            'Shape_key' : {}
        }

        for param_name, value in self.__params.items():
            if 'Location' in param_name:
                param_name = '_'.join(param_name.split('_')[1:])
                nm = param_name.split('-')[0]
                pnt = param_name.split('-')[1].split('_')[0]
                ax = param_name.split('_')[-1]

                if nm in params['Location']:
                    if pnt in params['Location'][nm]:
                        params['Location'][nm][pnt][ax] = value
                    else:
                        params['Location'][nm][pnt] = {
                            ax: value,
                        }
                else:
                    params['Location'][nm] = {
                        pnt:{ax: value},
                    }
            if 'Rotation' in param_name:
                param_name = '_'.join(param_name.split('_')[1:])
                nm = param_name.split('-')[0]
                pnt = param_name.split('-')[1].split('_')[0]
                ax = param_name.split('_')[-1]

                if nm in params['Rotation']:
                    if pnt in params['Rotation'][nm]:
                        params['Rotation'][nm][pnt][ax] = value
                    else:
                        params['Rotation'][nm][pnt] = {
                            ax: value,
                        }
                else:
                    params['Rotation'][nm] = {
                        pnt:{ax: value},
                    }
            if 'Scale' in param_name:
                param_name = '_'.join(param_name.split('_')[1:])
                param_name = param_name.replace('-Bendy', '')
                    
                if 'Size' in param_name:
                    nm = param_name.split('_')[0]
                    ax = param_name.split('_')[-1]

                    if nm in params['Scale']:
                        params['Scale'][nm][ax] = value
                    else:
                        params['Scale'][nm] = {
                            ax: value,
                        }
                else:
                    params['Scale'][param_name] = value

            if 'Shape_key' in param_name:
                param_name = '_'.join(param_name.split('_')[1:])
                nm = '_'.join(param_name.split('_')[1:])
                params['Shape_key'][nm] = value

        return params
    
    def reset_parameters(self):
        """Reset PPM parameters to default"""
        ppm_params = read_csv(f'{self.__DIRNAME}/resources/PPM_params_default_v1.csv',  header=None, index_col=0)
        self.__params = {  }
        for param_name, value in ppm_params.iterrows():
            self.__params[param_name] = value.values[0]

        self.__set_ppm_params(self.__params)

    def set_parameters(self, params):
        """Set PPM parameters in Blender
        
        Parameters:
        ----------
            params (dict): Dictionary of parameters to set
        """

        # TODO: check if params are valid
        for type_of_param, type_params in params.items():
            for name, name_params in type_params.items():
                if type_of_param == 'Location':
                    for point, point_params in name_params.items():
                        for axis, value in point_params.items():
                            self.set_parameter(type_of_param, name, point, **{axis.lower(): value})
                if type_of_param == 'Rotation':
                    for point, point_params in name_params.items():
                        for axis, value in point_params.items():
                            self.set_parameter(type_of_param, name, point, **{axis.lower(): value})
                if type_of_param == 'Scale':
                    if name == 'Size':
                        for axis, value in name_params.items():
                            self.set_parameter(type_of_param, name, **{axis.lower(): value})
                    else:
                        self.set_parameter(type_of_param, name, value=name_params)
                if type_of_param == 'Shape_key':
                    self.set_parameter(type_of_param, name, value=name_params)

    def set_parameter(self, type:str, name:str, point:str=None, w:float=None, x:float=None, y:float=None, z:float=None, sequence=None, value:float=None):
        """Set PPM parameters in Blender
        
        Parameters:
        ----------
            type (str): Type of parameter to set
            name (str): Name of bone to set
            point (str): Point of bone to set
            w (float): W value of quaternion
            x (float): X value of quaternion
            y (float): Y value of quaternion
            z (float): Z value of quaternion
            sequence (str): Rotation sequence (e.g. 'ZYX'). Only applicable for Rotation type with value given as Euler angles
            value (float or np.array()): Value of parameter to set
        """

        if type == 'Location':
            if x is not None:
                self.__params[f'{type}_{name}-{point}_X'] = x
            if y is not None:
                self.__params[f'{type}_{name}-{point}_Y'] = y
            if z is not None:
                self.__params[f'{type}_{name}-{point}_Z'] = z
            self.__set_ppm_params(self.__params)
        elif type == 'Rotation':
            if sequence is not None:
                if value is not None:
                    q = euler_to_quaternion(value, sequence)
                    self.__params[f'{type}_{name}-{point}_W'] = q[0]
                    self.__params[f'{type}_{name}-{point}_X'] = q[1]
                    self.__params[f'{type}_{name}-{point}_Y'] = q[2]
                    self.__params[f'{type}_{name}-{point}_Z'] = q[3]
                else:
                    if w is not None:
                        self.__params[f'{type}_{name}-{point}_W'] = w
                    if x is not None:
                        self.__params[f'{type}_{name}-{point}_X'] = x
                    if y is not None:
                        self.__params[f'{type}_{name}-{point}_Y'] = y
                    if z is not None:
                        self.__params[f'{type}_{name}-{point}_Z'] = z

            else:
                if w is not None:
                    self.__params[f'{type}_{name}-{point}_W'] = w
                if x is not None:
                    self.__params[f'{type}_{name}-{point}_X'] = x
                if y is not None:
                    self.__params[f'{type}_{name}-{point}_Y'] = y
                if z is not None:
                    self.__params[f'{type}_{name}-{point}_Z'] = z
            self.__set_ppm_params(self.__params)
        elif type == 'Scale':
            if name == 'Size':
                if value is not None:
                    self.__params[f'{type}_{name}-Bendy_X'] = value
                    self.__params[f'{type}_{name}-Bendy_Y'] = value
                    self.__params[f'{type}_{name}-Bendy_Z'] = value
                else:
                    if x is not None:
                        self.__params[f'{type}_{name}-Bendy_X'] = x
                    if y is not None:
                        self.__params[f'{type}_{name}-Bendy_Y'] = y
                    if z is not None:
                        self.__params[f'{type}_{name}-Bendy_Z'] = z
            else:
                self.__params[f'{type}_{name}-Bendy'] = value
            self.__set_ppm_params(self.__params)
        elif type == 'Shape_key':
            self.__params[f'{type}_{name}'] = value
            self.__set_ppm_params(self.__params)

    def __shape_key(self, name: str, val: float):
        bpy.data.shape_keys["Key.002"].key_blocks[name].value = val

    def __get_ppm_params(self):
        """Get PPM parameters from Blender"""
        for line, _ in self.__params.items():
            transform = line.split('_')[0]
            line = '_'.join(line.split('_')[1:])
            
            if transform == "Rotation":
                nm = line.split('-')[0]
                pnt = line.split('-')[1].split('_')[0]
                ax = line.split('_')[-1]
                obj = bpy.data.objects["Armature"].pose.bones[nm + "-" + pnt]

                if ax == 'W':
                    self.__params[transform + "_" + nm + "-" + pnt + "_" + ax] = obj.rotation_quaternion.w
                elif ax == 'X':
                    self.__params[transform + "_" + nm + "-" + pnt + "_" + ax] = obj.rotation_quaternion.x
                elif ax == 'Y':
                    self.__params[transform + "_" + nm + "-" + pnt + "_" + ax] = obj.rotation_quaternion.y
                elif ax == 'Z':
                    self.__params[transform + "_" + nm + "-" + pnt + "_" + ax] = obj.rotation_quaternion.z

            elif transform == "Location":
                nm = line.split('-')[0]
                pnt = line.split('-')[1].split('_')[0]
                ax = line.split('_')[-1]
                obj = bpy.data.objects["Armature"].pose.bones[nm + "-" + pnt]

                if ax == 'X':
                    self.__params[transform + "_" + nm + "-" + pnt + "_" + ax] = obj.location.x
                elif ax == 'Y':
                    self.__params[transform + "_" + nm + "-" + pnt + "_" + ax] = obj.location.y
                elif ax == 'Z':
                    self.__params[transform + "_" + nm + "-" + pnt + "_" + ax] = obj.location.z
                else:
                    pass

            elif transform == "Scale":
                nm = line.split('-')[0]
                pnt = line.split('-')[1].split('_')[0]
                ax = line.split('_')[-1]
                obj = bpy.data.objects["Armature"].pose.bones[nm + "-" + pnt]

                if ax == 'X':
                    self.__params[transform + "_" + nm + "-" + pnt + "_" + ax] = obj.scale.x
                elif ax == 'Y':
                    self.__params[transform + "_" + nm + "-" + pnt + "_" + ax] = obj.scale.y
                elif ax == 'Z':
                    self.__params[transform + "_" + nm + "-" + pnt + "_" + ax] = obj.scale.z
                else:
                    pass

            elif transform == "Shape":
                nm = '_'.join(line.split('_')[1:])
                obj = bpy.data.shape_keys["Key.002"].key_blocks[nm]
                self.__params[transform + '_' +line] = obj.value

    def __set_ppm_params(self, params:dict):
        """Set PPM parameters in Blender"""
        for line, value in params.items():

            if line not in self.__params:
                raise Exception(f"Parameter {line} is not valid")

            self.__params[line] = value

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
        self.__set_ppm_params(self.__params)
        path_to_img, _ = super()._render(
                            *args, **kwargs
                            )
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
        self.__set_ppm_params(self.__params)
        _, path_to_img = super()._render(
                            *args, **kwargs)
        return super()._get_depth(path_to_img, kwargs['resolution'])

    def get_point_cloud(self):
        """Get point cloud of the ear
        
        Returns:
        --------
            np.array: (num_points, 3)
        """
        self.__set_ppm_params(self.__params)
        return super()._get_pc(self.PPM_BLENDER_NAME)

    def save_ply(self, path_to_ply, save_as_npy=False):
        """Save point cloud of the ear in .ply format
        
        Parameters:
        -----------
            path_to_ply: str
                path to save .ply file
                *.ply or *.npy is appended to the path if not already specified
        """
        self.__set_ppm_params(self.__params)
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
        self.__set_ppm_params(self.__params)
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
            for key, value in self.__params.items():
                f.write("%s,%s\n"%(key,value))

    def save_png(self, path_to_png, save_as_npy=False, resolution=512, cam_location=None, cam_rotation=None, cam_location_ref=None):
        """Save PNG of the ear
        
        Parameters:
        -----------
            path_to_png: str
                path to save .png file
                *.png or *.npy is appended to the path if not already specified
            resolution: int
                resolution of the image
            cam_location: np.array
                camera location
            cam_rotation: np.array
                camera rotation
            cam_location_ref: np.array
                camera location reference
        """
        self.__set_ppm_params(self.__params)
        if not path_to_png.endswith('.png') and not save_as_npy:
            path_to_png += '.png'
        if save_as_npy:
            if path_to_png.endswith('.png'):
                path_to_png = path_to_png[:-4] + '.npy'
            if not path_to_png.endswith('.npy'):
                path_to_png += '.npy'

        def f(ppm,**kwargs):
            return  ppm._render(**{k:v for k, v in kwargs.items() if v is not None})

        path_to_png_temp, _ = f(self,
                                resolution=resolution,
                                cam_location=cam_location,
                                cam_rotation=cam_rotation,
                                cam_location_ref=cam_location_ref)

        if save_as_npy:
            np.save(path_to_png, path_to_png_temp)
        else:
            super()._get_image(path_to_png_temp, resolution)
            # move file to path_to_png
            os.rename(path_to_png_temp, path_to_png)

    def save_exr(self, path_to_exr, save_as_npy=False, resolution=512, cam_location=None, cam_rotation=None, cam_location_ref=None):
        """Save EXR of the ear
        
        Parameters:
        -----------
            path_to_exr: str
                path to save .exr file
                *.exr or *.npy is appended to the path if not already specified
            resolution: int
                resolution of the image
            cam_location: np.array
                camera location
            cam_rotation: np.array
                camera rotation
            cam_location_ref: np.array
                camera location reference
        """
        self.__set_ppm_params(self.__params)
        if not path_to_exr.endswith('.exr') and not save_as_npy:
            path_to_exr += '.exr'
        if save_as_npy:
            if path_to_exr.endswith('.exr'):
                path_to_exr = path_to_exr[:-4] + '.npy'
            if not path_to_exr.endswith('.npy'):
                path_to_exr += '.npy'

        def f(ppm,**kwargs):
            return  ppm._render(**{k:v for k, v in kwargs.items() if v is not None})

        _, path_to_exr_temp = f(self,
                                resolution=resolution,
                                cam_location=cam_location,
                                cam_rotation=cam_rotation,
                                cam_location_ref=cam_location_ref)

        if save_as_npy:
            np.save(path_to_exr, path_to_exr_temp)
        else:
            super()._get_depth(path_to_exr_temp, resolution)
            # move file to path_to_exr
            os.rename(path_to_exr_temp, path_to_exr)


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

        self.__set_ppm_params(self.__params)

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
