import bpy 

class HausdorffPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Hausdorff Visualization"
    bl_category = "Hausdorff"

    def draw(self, context):
            layout= self.layout

            # 4 Rows with buttons
            row = layout.row()
            col = row.column()
            layout.prop_search(context.scene, "theReferenceObject", context.scene, "objects")

            row = layout.row()
            col = row.column()
            col.operator("object.visualize_hausdorff", text="Hausdorff distance visualization")
