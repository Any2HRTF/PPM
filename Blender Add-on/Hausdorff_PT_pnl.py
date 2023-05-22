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
            col.operator("object.visualize_hausdorff", text="Distance visualization")

            # row = layout.row()
            # col=row.column()
            # col.operator("object.reset_colors", text="Reset colors")

            row = layout.row()
            col=row.column()
            col.operator("object.output_hausdorff", text="Output Hausdorff distance")

            # Get the latest hausdorff property item
            hausdorff_items = context.scene.hausdorff
            if hausdorff_items:
                latest_hausdorff_item = hausdorff_items[-1]

                row = layout.row()
                col=row.column()
                layout.label(text='Mean Distance = %.2f' % latest_hausdorff_item.mean)

                row = layout.row()
                col=row.column()
                layout.label(text='Median Distance = %.2f' % latest_hausdorff_item.median)

                row = layout.row()
                col=row.column()
                layout.label(text='Hausdorff Distance = %.2f' % latest_hausdorff_item.max)

                row = layout.row()
                col=row.column()
                layout.label(text='Minimum Distance = %.2f' % latest_hausdorff_item.min)
