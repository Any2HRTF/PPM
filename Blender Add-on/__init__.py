# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


bl_info = {
    "name" : "Calculate several distances between two objects",
    "author" : "Yasen, Jonathan",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}

#With this section it is possible to reload all scripts:
# "blender icon" -> System -> reload scripts
if "bpy" in locals():
    print("\n---------------RELOADD---------------\n")
    import importlib

    importlib.reload(PointCloudCompare_PT_op)
    importlib.reload(PointCloudCompare_PT_pnl)
    print("Succesfully reloaded")

else:        
    print("\n---------------INITIAL---------------\n")
    from . import PointCloudCompare_PT_op
    from . import PointCloudCompare_PT_pnl

import bpy


classes= [PointCloudCompare_PT_op.VisualizeDistance,
          PointCloudCompare_PT_op.DistanceProperty,
          PointCloudCompare_PT_op.DistanceSelector,
          PointCloudCompare_PT_op.JaccardResolutionSelector,
          PointCloudCompare_PT_pnl.INTERFACE_PT_panel]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.Reference = bpy.props.StringProperty()
    bpy.types.Scene.distances = bpy.props.CollectionProperty(type = PointCloudCompare_PT_op.DistanceProperty)
    bpy.types.Scene.distance_selector = bpy.props.PointerProperty(type = PointCloudCompare_PT_op.DistanceSelector)
    bpy.types.Scene.jaccard_resolution = bpy.props.PointerProperty(type = PointCloudCompare_PT_op.JaccardResolutionSelector)
    
    
def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    del bpy.types.Scene.distances
    del bpy.types.Scene.distance_selector
    del bpy.types.Scene.jaccard_resolution
    

if __name__ == "__main__":
    register()



