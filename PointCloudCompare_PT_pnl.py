
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
            
            #select obj1
            layout.prop(context.scene.distance_selector,"fix_obj1")
            if context.scene.distance_selector.fix_obj1:
                layout.prop_search(context.scene, "fix_obj1", context.scene, "objects")
            #Dropdown menu for distance selection
            row = layout.row()
            col = row.column()
            layout.prop_search(context.scene, "Reference", context.scene, "objects")
            row = layout.row()
            col = row.column()
            layout.prop(context.scene.distance_selector,"selector")


            #subselection in case of jaccard/dice
            if context.scene.distance_selector.selector == "jaccard_dice":
               layout.prop(context.scene.jaccard_resolution,"selector") 
               layout.prop(context.scene.jaccard_resolution,"vis_grid")
               layout.prop(context.scene.jaccard_resolution,"vis_grid_type")


            row = layout.row()
            col = row.column()


            #Check if Object Mode and an Object are selected
            if context.object is not None:
                current_mode = bpy.context.object.mode
                if current_mode == "OBJECT":
                    col.operator("object.visualize_distance", text="Calculate")
                    if 'Grid_visualization' in bpy.context.scene.objects.keys():
                        bpy.data.objects.remove(context.scene.objects['Grid_visualization'], do_unlink=True)
                    if 'Grid_object1' in bpy.context.scene.objects.keys():
                        bpy.data.objects.remove(context.scene.objects['Grid_object1'], do_unlink=True)
                    if 'Grid_object2' in bpy.context.scene.objects.keys():
                        bpy.data.objects.remove(context.scene.objects['Grid_object2'], do_unlink=True)
                else:
                    col.alert = True
                    col.label(text = "Select an Object and Object Mode!")
            else:
                col.alert = True
                col.label(text = "Select an Object and Object Mode!")


            # Get the latest property item
            distance_items = context.scene.distances
            
            #Display statistics of selected measurement
            if distance_items:
                latest_distance_item = distance_items[-1]
                prev_distance_item = get_previous_items(distance_items)
                
                    
                #Minimal pointwise distance
                if latest_distance_item.dist_type == "min_p_dist_to" or latest_distance_item.dist_type == "min_p_dist_from": 

                    if prev_distance_item is not None:
                        row = layout.row()
                        col=row.column()
                        layout.label(text='   Types             | |            Value                | |          Change')
                        col=row.column()
                        layout.label(text="   Mean                         %.3fmm                       %.3fmm" 
                                    % (latest_distance_item.mean_pmin, latest_distance_item.mean_pmin-prev_distance_item.mean_pmin))
                        row = layout.row()
                        col=row.column()
                        layout.label(text="   Median                      %.3fmm                       %.3fmm" 
                                    % (latest_distance_item.median_pmin, latest_distance_item.median_pmin-prev_distance_item.median_pmin))
                        row = layout.row()
                        col=row.column()
                        layout.label(text="   Max                           %.3fmm                       %.3fmm" 
                                    % (latest_distance_item.max_pmin, latest_distance_item.max_pmin-prev_distance_item.max_pmin))
                        row = layout.row()
                        col=row.column()
                        layout.label(text="   Min                            %.3fmm                       %.3fmm" 
                                    % (latest_distance_item.min_pmin, latest_distance_item.min_pmin-prev_distance_item.min_pmin))
                    else:
                        row = layout.row()
                        col=row.column()
                        layout.label(text='   Types             | |            Value                | |        Change')
                        col=row.column()
                        layout.label(text="   Mean                         %.3fmm                           --" 
                                    % (latest_distance_item.mean_pmin))
                        row = layout.row()
                        col=row.column()
                        layout.label(text="   Median                      %.3fmm                           --" 
                                    % (latest_distance_item.median_pmin))
                        row = layout.row()
                        col=row.column()
                        layout.label(text="   Max                           %.3fmm                           --" 
                                    % (latest_distance_item.max_pmin))
                        row = layout.row()
                        col=row.column()
                        layout.label(text="   Min                            %.3fmm                           --" 
                                    % (latest_distance_item.min_pmin))
                        
                    #Specify color scheme
                    if latest_distance_item.dist_type == "min_p_dist_to":
                        col=row.column()
                        col=row.column()
                        layout.label(text="\n")
                        col=row.column()
                        layout.label(text="                    Theme for Distance visualisation")
                        layout.label(text= "                                         Blue    <= 1mm")
                        col=row.column()
                        layout.label(text="                     1mm <=    Cyan    < 1.5mm")
                        col=row.column()
                        layout.label(text="                  1.5mm <=   Green   < 2mm")
                        col=row.column()
                        layout.label(text="                     2mm <=   Yellow   < 3mm")
                        col=row.column()
                        layout.label(text="                     3mm <=  Orange  < 5mm")
                        col=row.column()
                        layout.label(text="                     5mm <=     Red")

                #Jaccard/Dice
                elif latest_distance_item.dist_type == "jaccard_dice":
                    if prev_distance_item is not None:
                        col=row.column()
                        layout.label(text='   Types             | |            Value                | |        Change')
                        col=row.column()
                        layout.label(text="   Jaccard                          %.3f                           %.3f" 
                                    % (latest_distance_item.jaccard_coef,latest_distance_item.jaccard_coef-prev_distance_item.jaccard_coef))
                        col=row.column()
                        layout.label(text="   Dice                               %.3f                           %.3f" 
                                    % (latest_distance_item.dice_coef,latest_distance_item.dice_coef-prev_distance_item.dice_coef))
                        

                        #BETA

                        #col=row.column()
                        #layout.label(text="   Avg Jaccard                   %.3f" 
                        #            % (latest_distance_item.avg_jaccard_coef))
                        #
                    else:
                        col=row.column()
                        layout.label(text='   Types             | |            Value                | |        Change')
                        col=row.column()
                        layout.label(text="   Jaccard                          %.3f                           --" 
                                    % (latest_distance_item.jaccard_coef))
                        col=row.column()
                        layout.label(text="   Dice                               %.3f                           --" 
                                    % (latest_distance_item.dice_coef))
                        

                        #BETA

                        #col=row.column()
                        #layout.label(text="   Avg Jaccard                   %.3f" 
                        #            % (latest_distance_item.avg_jaccard_coef))
                        #


                        
                    #Visualize Grid
                    if context.scene.jaccard_resolution.vis_grid:
                        col=row.column()
                        col=row.column()
                        layout.label(text="\n")
                        col=row.column()
                        layout.label(text="                       Theme for Voxel visualisation")
                        col=row.column()

                        #Specify color scheme
                        if context.scene.jaccard_resolution.vis_grid_type == "quantized_meshes":
                            layout.label(text="                                    Object 1: red")
                            col=row.column()
                            layout.label(text="                                  Reference: green")
                            col=row.column()
                            layout.label(text="              Note: Only the active object is colored!")
                        else:
                            layout.label(text="                                      Union: red")
                            col=row.column()
                            layout.label(text="                               Intersection: green")

                #Display potential Error messages
                row = layout.row()
                col=row.column()
                col.alert = True
                col.label(text=latest_distance_item.ERROR)#


def get_previous_items(distance_items):
    latest_item = distance_items[-1]

    #loop through all stored values
    for item in reversed(distance_items[0:-1]):
        
        #check whether an error occured
        if item.ERROR != "":
            continue

        #check if the same distance was calculated
        if latest_item.dist_type != item.dist_type:
            continue
        
        #Jaccard selected
        if item.dist_type == "jaccard_dice":
            if item.jaccard_res != latest_item.jaccard_res:
                continue
            if item.obj1 == latest_item.obj1 and item.obj2 == latest_item.obj2:
                return item
            if item.obj1 == latest_item.obj2 and item.obj2 == latest_item.obj1:
                return item
            continue
            
            
        
        #min pointwise distance
        if item.dist_type == "min_p_dist_to" or item.dist_type == "min_p_dist_from":
            if item.obj1 != latest_item.obj1:
                continue
            if item.obj2 != latest_item.obj2:
                continue
            
            return item
    return None