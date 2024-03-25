import os
import math

import bpy
import mathutils
import numpy as np

def render(dirpath,
            filename,
            resolution=256,
            depth=False,
            smooth_shading=True,
            image_compression=0,
            image_color_depth='8',
            camera_location=[-0.01, 0.17, 0.005],
            camera_rotation=[90, 0, 180],
            camera_location_reference=None,
            depth_farthest=0.212,
            depth_nearest=0,
            depth_codec_exr='NONE',
            depth_color_depth_exr='16',
            depth_compression_exr=0,
            light_type='Area',
            light_shape='Square',
            light_location=[-0.01, 0.15, 0.1],
            light_rotation=[0, 0, 0],
            light_power=200000):
        
        # transform to mm for use in Blender
        camera_location = [float(i)*1000 for i in camera_location]
        depth_farthest = float(depth_farthest)*1000
        depth_nearest = float(depth_nearest)*1000
        if camera_location_reference is not None:
            camera_location_reference = [float(i)*1000 for i in camera_location_reference]

        # Scene-render settings
        bpy.context.scene.render.engine = 'CYCLES' # CYCLES, BLENDER_EEVEE, WORKBENCH
        bpy.context.view_layer.cycles.denoising_store_passes = True

        camera = bpy.data.objects['Camera']
        camera.rotation_mode = 'XYZ'
        bpy.context.scene.camera = camera

        light = bpy.data.objects[light_type.capitalize()]
        light.data.shape = light_shape
        light.location = light_location
        light.rotation_euler = light_rotation
        light.data.energy = light_power

        # Optionally smooth mesh faces for more pleasing rendering results
        if smooth_shading:
            mesh = bpy.context.object.data
            for polygon in mesh.polygons:
                polygon.use_smooth = True

        camera.location = mathutils.Vector((float(camera_location[0]),
                                            float(camera_location[1]),
                                            float(camera_location[2])))
        bpy.context.view_layer.update()

        camera.rotation_euler = mathutils.Euler((
                                    math.radians(float(camera_rotation[0])),
                                    math.radians(float(camera_rotation[1])),
                                    math.radians(float(camera_rotation[2]))),
                                    camera.rotation_mode
                                )

        if camera_location_reference is not None:

            camera_location_matrix = camera.matrix_world.to_translation()
            camera_rotation = mathutils.Vector((float(camera_location_reference[0]),
                                        float(camera_location_reference[1]),
                                        float(camera_location_reference[2]))) - camera_location_matrix

            camera_rotation_quaternion = camera_rotation.to_track_quat('-Z','Y')

            camera.rotation_euler = camera_rotation_quaternion.to_euler()

        bpy.context.view_layer.update()

        # Render image and depth information, and store as png and exr files
        bpy.context.scene.render.use_compositing = True
        bpy.context.scene.render.filepath = dirpath + '/' + filename 

        bpy.data.scenes["Scene"].render.resolution_x = resolution
        bpy.data.scenes["Scene"].render.resolution_y = resolution
        bpy.data.scenes["Scene"].render.image_settings.color_depth = image_color_depth
        bpy.data.scenes["Scene"].render.image_settings.compression = image_compression
        bpy.data.scenes["Scene"].render.image_settings.color_mode = 'BW'

        # Enable nodes
        bpy.context.scene.use_nodes = True

        tree = bpy.context.scene.node_tree
        links = tree.links

        # Clear default nodes
        for node in tree.nodes:
            tree.nodes.remove(node)

        # Create render-layers node
        render_layer = tree.nodes.new(type='CompositorNodeRLayers')

        # Create denoising node
        denoise = tree.nodes.new(type='CompositorNodeDenoise')

        if depth:
            # Create map-range node
            tree_map = tree.nodes.new(type='CompositorNodeMapRange')
            tree_map.use_clamp = False

            # Set map minimum in Blender units
            tree_map.inputs[1].default_value = float(depth_nearest)

            if depth_nearest=='camera_location': # default
                # Set map maximum to Euclidian distance of camera to origin
                camera = bpy.data.objects['Camera']
                distance_l2 = math.sqrt(camera.location.x**2 + camera.location.y**2 + camera.location.z**2)
                # map maximum in Blender units
                tree_map.inputs[2].default_value = distance_l2
            else:
                # map maximum in Blender units
                tree_map.inputs[2].default_value = float(depth_farthest)

            # Map values between 1 (white) and zero (black) in normalised units (linearly spaced when using OPEN_EXR)
            tree_map.inputs[3].default_value = 1
            tree_map.inputs[4].default_value = 0

            # Link output of render-layers node to input of map node (exr depth)
            links.new(render_layer.outputs['Depth'], tree_map.inputs['Value'])

            # Create a file-output node, set the path, and file format (exr depth)
            file_output_exr = tree.nodes.new(type='CompositorNodeOutputFile')
            file_output_exr.base_path = dirpath
            file_output_exr.format.file_format = "OPEN_EXR"
            file_output_exr.file_slots[0].path = filename +\
            file_output_exr.format.file_format # file name with appended frame idx
            file_output_exr.format.color_depth = depth_color_depth_exr
            file_output_exr.format.compression = depth_compression_exr
            file_output_exr.format.exr_codec = depth_codec_exr

            # Link output of map node to input of compositor-output node (exr depth)
            links.new(tree_map.outputs['Value'], file_output_exr.inputs['Image'])

        links.new(render_layer.outputs['Image'], denoise.inputs['Image'])
        links.new(render_layer.outputs['Denoising Normal'], denoise.inputs['Normal'])
        links.new(render_layer.outputs['Denoising Albedo'], denoise.inputs['Albedo'])

        # Create a file-output node, set the path, and file format (png)
        file_output_png = tree.nodes.new(type='CompositorNodeOutputFile')
        file_output_png.base_path = dirpath
        file_output_png.format.file_format = "PNG"
        file_output_png.file_slots[0].path = filename
        file_output_png.format.color_depth = image_color_depth
        file_output_png.format.compression = int(image_compression)

        # Link denoise-node output with compositor-output node (png)
        links.new(denoise.outputs['Image'], file_output_png.inputs['Image'])

        # Render!
        bpy.ops.render.render()


        if depth:
            for file in os.listdir(dirpath):
                if file.startswith(filename) and file.endswith('.exr'):
                    os.replace(dirpath + f'/{file}', \
                        dirpath + f'/{filename}.exr')
        
        for file in os.listdir(dirpath):
            if file.startswith(filename) and file.endswith('.png'):
                os.replace(dirpath + f'/{file}', \
                    dirpath+ f'/{filename}.png')