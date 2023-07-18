
import bpy



class INTERFACE_PT_panel(bpy.types.Panel):
    """
    A class used to visualize and show the User Interface for the add on
    ...

    Methods
    -------
    draw(cls, context)
        A function used to implement the interface
    
    """
    bl_space_type = "VIEW_3D"
    bl_idname = "INTERFACE_PT_panel"
    bl_region_type = "UI"
    bl_label = "PointCloudCompare"
    bl_category = "PointCloudCompare"
    
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
                    col.operator("object.visualize_distance", text="Calculate")
                else:
                    col.alert = True
                    col.label(text = "Select an Object and Object Mode!")
            else:
                col.alert = True
                col.label(text = "Select an Object and Object Mode!")

            # Get the latest property item
            distance_items = context.scene.distances
            #print( context.scene.distances)
            if distance_items:
                latest_distance_item = distance_items[-1]
                
                
                
                if latest_distance_item.dist_type == "OP1" or latest_distance_item.dist_type == "OP2":               
                    
                    row = layout.row()
                    col=row.column()
                    layout.label(text='   Types             | |            Value')

                    col=row.column()
                    layout.label(text="   Mean                             %.3f" 
                                % (latest_distance_item.mean_pmin))
                    
                    row = layout.row()
                    col=row.column()
                    layout.label(text="   Median                          %.3f" 
                                % (latest_distance_item.median_pmin))

                    row = layout.row()
                    col=row.column()
                    layout.label(text="   Max                               %.3f" 
                                % (latest_distance_item.max_pmin))

                    row = layout.row()
                    col=row.column()
                    layout.label(text="   Min                                %.3f" 
                                % (latest_distance_item.min_pmin))
                    if latest_distance_item.dist_type == "OP1":
                        
                        col=row.column()
                        col=row.column()
                        layout.label(text="\n")
                        col=row.column()
                        layout.label(text=" Theme for Distance visualisation")
                        layout.label(text= "                       Blue    <= 1mm")
                        col=row.column()
                        layout.label(text="   1mm <=    Cyan    < 1.5mm")
                        col=row.column()
                        layout.label(text="1.5mm <=   Green   < 2mm")
                        col=row.column()
                        layout.label(text="   2mm <=   Yellow   < 3mm")
                        col=row.column()
                        layout.label(text="   3mm <=  Orange  < 5mm")
                        col=row.column()
                        layout.label(text="   5mm <=     Red")

                elif latest_distance_item.dist_type == "OP3":
                    
                    
                    col=row.column()
                    layout.label(text='   Types             | |            Value')
                    col=row.column()
                    layout.label(text="   Jaccard                          %.3f" 
                                % (latest_distance_item.jaccard_coef))
                    col=row.column()
                    layout.label(text="   Dice                              %.3f" 
                                % (latest_distance_item.dice_coef))
                row = layout.row()
                col=row.column()
                col.alert = True
                col.label(text=latest_distance_item.ERROR)
 
            
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