import os
import bpy
import uuid
from pandas import read_csv
import numpy as np

from .blender.blender_support_classes import BaseBlenderObject, Bone


class PPM(BaseBlenderObject):
    def __init__(self, name="PPM", from_blender_file=None):
        DIRNAME = os.path.join(os.path.dirname(__file__))

        self.PPM_BLENDER_NAME = 'ARI_PPM_v1'
    
        super().__init__(os.path.join(f'{DIRNAME}/resources/tmp_' + str(uuid.uuid4())), name)

        if from_blender_file is not None:
            super()._load_blender_file(from_blender_file, self.PPM_BLENDER_NAME)

        else:
            # load standard ear
            super()._load_blender_file(f'{DIRNAME}/resources/PPM_modified_v1.blend', self.PPM_BLENDER_NAME)

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

        ppm_params = read_csv(f'{DIRNAME}/resources/PPM_params_default_v1.csv', index_col=0)
        self._params = { self.name: {} }
        for param_name, value in ppm_params.iterrows():
            self._params[self.name][param_name] = value.values[0]

        self._get_ppm_params()
        self.set_ppm_params(self._params[self.name])

    def get_ppm_params(self):

        return self._params
    
    def set_ppm_params(self, params):
        # TODO: check if params are valid
        self._set_ppm_params(params)

    def _shape_key(self, name: str, val: float):
        bpy.data.shape_keys["Key.002"].key_blocks[name].value = val

    def _get_ppm_params(self):
        """Get PPM parameters from Blender"""
        for line, _ in self._params[self.name].items():
            transform = line.split('_')[0]
            line = '_'.join(line.split('_')[1:])
            
            if transform == "Rotation":
                nm = line.split('-')[0]
                pnt = line.split('-')[1].split('_')[0]
                ax = line.split('_')[-1]
                obj = bpy.data.objects["Armature"].pose.bones[nm + "-" + pnt]

                if ax == 'W':
                    self._params[self.name][transform + "_" + nm + "-" + pnt + "_" + ax] = obj.rotation_quaternion.w
                elif ax == 'X':
                    self._params[self.name][transform + "_" + nm + "-" + pnt + "_" + ax] = obj.rotation_quaternion.x
                elif ax == 'Y':
                    self._params[self.name][transform + "_" + nm + "-" + pnt + "_" + ax] = obj.rotation_quaternion.y
                elif ax == 'Z':
                    self._params[self.name][transform + "_" + nm + "-" + pnt + "_" + ax] = obj.rotation_quaternion.z

            elif transform == "Location":
                nm = line.split('-')[0]
                pnt = line.split('-')[1].split('_')[0]
                ax = line.split('_')[-1]
                obj = bpy.data.objects["Armature"].pose.bones[nm + "-" + pnt]

                if ax == 'X':
                    self._params[self.name][transform + "_" + nm + "-" + pnt + "_" + ax] = obj.location.x
                elif ax == 'Y':
                    self._params[self.name][transform + "_" + nm + "-" + pnt + "_" + ax] = obj.location.y
                elif ax == 'Z':
                    self._params[self.name][transform + "_" + nm + "-" + pnt + "_" + ax] = obj.location.z
                else:
                    pass

            elif transform == "Scale":
                nm = line.split('-')[0]
                pnt = line.split('-')[1].split('_')[0]
                ax = line.split('_')[-1]
                obj = bpy.data.objects["Armature"].pose.bones[nm + "-" + pnt]

                if ax == 'X':
                    self._params[self.name][transform + "_" + nm + "-" + pnt + "_" + ax] = obj.scale.x
                elif ax == 'Y':
                    self._params[self.name][transform + "_" + nm + "-" + pnt + "_" + ax] = obj.scale.y
                elif ax == 'Z':
                    self._params[self.name][transform + "_" + nm + "-" + pnt + "_" + ax] = obj.scale.z
                else:
                    pass

            elif transform == "Shape":
                nm = '_'.join(line.split('_')[1:])
                obj = bpy.data.shape_keys["Key.002"].key_blocks[nm]
                self._params[self.name][transform + '_' +line] = obj.value

    def _set_ppm_params(self, params:dict):
        """Set PPM parameters in Blender"""
        for line, value in params.items():

            self._params[self.name][line] = value

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
                self._shape_key('_'.join(line.split('_')[1:]), value)

    def get_image(self, *args, **kwargs):
        """Get image of the ear"""
        path_to_img, _ = super()._render(
                            *args, **kwargs
                            )
        
        return super().get_image(path_to_img, kwargs['resolution'])

    def get_depth(self, *args, **kwargs):
        """Get image of the ear"""
        _, path_to_img = super()._render(
                            *args, **kwargs)

        return super().get_depth(path_to_img, kwargs['resolution'])

    def get_point_cloud(self):
        """Get point cloud of the ear"""
        return super().get_pc(self.PPM_BLENDER_NAME)

    def render(
            self,
            *args, **kwargs) -> tuple:

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

            image[i,...] = super().get_image(path_to_img, kwargs['resolution'])
            depth_image[i,...] = super().get_depth(path_to_depth, kwargs['resolution'])

        return image, depth_image
