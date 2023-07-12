
import bpy



class HAUSDORFF_PT_panel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_idname = "HAUSDORFF_PT_panel"
    bl_region_type = "UI"
    bl_label = "Distance Visualization"
    bl_category = "Distance Calculation"
    
    def draw(self, context):

            layout= self.layout
            # 4 Rows with buttons
            row = layout.row()
            col = row.column()
            layout.prop_search(context.scene, "Reference", context.scene, "objects")

            row = layout.row()
            col = row.column()
            #layout.prop(context.scene,"distance_selector")
            
            layout.prop(context.scene.distance_selector,"selector")
            if context.scene.distance_selector.selector == "OP3":
               layout.prop(context.scene.jaccard_resolution,"selector")  


            #layout.prop_search(context.scene, "distance_selector", context.scene, "EnumProperty")
            row = layout.row()
            col = row.column()
            if context.object is not None:
                current_mode = bpy.context.object.mode
                if current_mode == "OBJECT":
                    col.operator("object.visualize_distance", text="Distance visualization")
                else:
                    layout.label(text = "Select an Object and ensure you are in OBJECT Mode!")
            else:
                layout.label(text = "Select an Object and ensure you are in OBJECT Mode!")

            # Get the latest hausdorff property item
            distance_items = context.scene.distances
            if distance_items:
                latest_distance_item = distance_items[-1]
                if latest_distance_item.dist_type == "OP1" or latest_distance_item.dist_type == "OP2":
                    row = layout.row()
                    col=row.column()
                    layout.label(text='Types         | |         From Ref         | |        To Ref')

                    col=row.column()
                    layout.label(text="Mean                        %.3f                        %.3f" 
                                % (latest_distance_item.mean_QP,latest_distance_item.mean_PQ))
                    
                    row = layout.row()
                    col=row.column()
                    layout.label(text="Median                      %.3f                        %.3f" 
                                % (latest_distance_item.median_QP,latest_distance_item.median_PQ))

                    row = layout.row()
                    col=row.column()
                    layout.label(text="Hausdorff                  %.3f                        %.3f" 
                                % (latest_distance_item.max_QP,latest_distance_item.max_PQ))

                    row = layout.row()
                    col=row.column()
                    layout.label(text="Minimum                   %.3f                        %.3f" 
                                % (latest_distance_item.min_QP,latest_distance_item.min_PQ))
                elif latest_distance_item.dist_type == "OP3":
                    row = layout.row()
                    col=row.column()
                    layout.label(text='Types                  | |         Jaccard')

                    col=row.column()
                    layout.label(text="Bool                                  %.3f" 
                                % (latest_distance_item.jaccard_bool))
                    
                    col=row.column()
                    layout.label(text="Point preserve                  %.3f" 
                                % (latest_distance_item.jaccard_point_preserve))
                    
                    col=row.column()
                    layout.label(text="Alternative OR                 %.3f" 
                                % (latest_distance_item.jaccard_altnerative_or))
                """
                pcoll = bpy.utils.previews.new()

                # path to the folder where the icon is
                # the path is calculated relative to this py file inside the addon folder
                my_icons_dir = os.path.join(os.path.dirname(__file__), "icons")

                # load a preview thumbnail of a file and store in the previews collection
                #pcoll.load("my_icon", os.path.join(my_icons_dir, "pic.jpg"), 'IMAGE')
                pcoll.load("my_icon","C:/Program Files/Blender Foundation/Blender 3.6/3.6/scripts/addons/Hausdorff/pic.jpg",'IMAGE')
                preview_collections = pcoll
                pcoll = preview_collections

                row = layout.row()
                my_icon = pcoll["my_icon"]
                #row.operator("render.render", icon_value=my_icon.icon_id)
                #bpy.utils.previews.remove(pcoll)
                
                path = "C:/Program Files/Blender Foundation/Blender 3.6/3.6/scripts/addons/Hausdorff/pic.jpg"
                img = bpy.data.images.load(path, check_existing=True) # load img from disk 
                img = bpy.data.images['pic.jpg'] # load from within blend file
                texture = bpy.data.textures.new(name="previewTexture", type="IMAGE")
                texture.image = img
                tex = bpy.data.textures['previewTexture']
                tex.extension = 'CLIP'  #EXTEND # CLIP # CLIP_CUBE # REPEAT # CHECKE
                
                row = layout.row()
                col=row.column()


                #col.template_preview(self.tex) # if tex is a variable in the same class
                # or
                col.template_preview(bpy.data.textures['previewTexture'])
                
                tex = bpy.data.textures['C:/Program Files/Blender Foundation/Blender 3.6/3.6/scripts/addons/Hausdorff/pic.jpg']
                col=row.column()
                col.template_preview(tex)
                """