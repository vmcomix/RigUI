import bpy
import bpy.utils.previews
import os

# # Global preview collection
# preview_collection = {}

# class RigUI_OT_GenerateExpressionThumbnails(bpy.types.Operator):
#     bl_idname = "pose.generate_expression_thumbnails"
#     bl_label = "Generate Expression Thumbnails"
#     bl_description = "Generates thumbnails to choose different expressions"
#     bl_options = {"REGISTER"}

#     def execute(self, context):

#         """Update previews based on images in bpy.data.images."""

#         global preview_collection

#         # Create the preview collection if it doesn't exist
#         if not preview_collection:
#             preview_collection = bpy.utils.previews.new()

#         # Get a set of current image names in bpy.data.images
#         current_images = {img.name for img in bpy.data.images if img.type == 'IMAGE'}

#         # Remove any previews for images no longer in bpy.data.images
#         for key in list(preview_collection.keys()):
#             if key not in current_images:
#                 del preview_collection[key]

#         # Add previews for new images
#         for img in bpy.data.images:
#             if "FACE" not in img.name:
#                 continue

#             if bpy.context.active_object.name.split('-')[1] not in img.name:
#                 continue

#             if bpy.context.active_pose_bone.name not in img.name:
#                 continue

#             if img.type == 'IMAGE' and img.name not in preview_collection:
#                 # Ensure the image has a valid filepath or preview
#                 if img.filepath:
#                     preview_collection.load(img.name, bpy.path.abspath(img.filepath), 'IMAGE')

#         return {'FINISHED'}

# Global preview collection
preview_collection = {}

def update_previews():
    """Update previews based on images in bpy.data.images."""
    global preview_collection

    rig_name = bpy.context.active_object.name.split('-')[1]

    # Create the preview collection if it doesn't exist
    if not preview_collection:
        preview_collection = bpy.utils.previews.new()

    # Get a set of current image names in bpy.data.images
    current_images = {img.name for img in bpy.data.images if img.type == 'IMAGE'}

    selected_bone = bpy.context.active_pose_bone.name.replace(".", "_")

    # Remove any previews for images no longer in bpy.data.images
    for key in list(preview_collection.keys()):
        if key not in current_images:
            del preview_collection[key]

        elif selected_bone not in key:
            del preview_collection[key]

    # Add previews for new images
    for img in bpy.data.images:
        if "FACE" not in img.name:
            continue

        if rig_name not in img.name:
            continue

        if selected_bone not in img.name:
            continue

        # if not os.path.exists(bpy.path.abspath(img.filepath)):
        #     for linkedpath in bpy.data.libraries:
        #         if rig_name in linkedpath.name:
        #             path = os.path.join(os.path.dirname(linkedpath), "expressions")
        # else:
        #     path = bpy.path.abspath(img.filepath)
        if img.type == 'IMAGE' and img.name not in preview_collection:
            # Ensure the image has a valid filepath or preview
            if not img.filepath:
                continue

            if not os.path.exists(bpy.path.abspath(img.filepath)):
                for linkedpath in bpy.data.libraries:
                    if rig_name in linkedpath.name:
                        path = os.path.join(os.path.dirname(linkedpath.filepath), "expressions", selected_bone)
                        preview_collection.load(img.name, os.path.join(path, img.name), 'IMAGE')
            else:
                path = bpy.path.abspath(img.filepath)
                preview_collection.load(img.name, path, 'IMAGE')

    # return

def enum_items_callback(self, context):
    """Dynamic callback for EnumProperty items."""
    global preview_collection
    update_previews()  # Dynamically load and clean up previews

    # Create the items list dynamically from the preview collection
    items = []
    for i, (key, preview) in enumerate(preview_collection.items()):
        items.append((key, f"Image {i+1}", f"Preview of {key}", preview.icon_id, i))
    return items

def change_enum(self, context):
    global preview_collection
    bone = context.active_pose_bone
    bone['image_index'] = list(preview_collection.keys()).index(context.preferences.addons['RigUI'].preferences.facial_feature) + 1

    obj = context.active_object

    data_path = f'pose.bones["{bone.name}"]["image_index"]'
    if obj.animation_data and obj.animation_data.action:
        fcurves = obj.animation_data.action.fcurves
        is_animated = any(fc.data_path == data_path for fc in fcurves)

        if is_animated:
            # Insert a keyframe on the specified frame
            context.active_object.keyframe_insert(data_path, frame=context.scene.frame_current)

    # Refresh all drivers
    rig = context.active_object
    for driver in rig.data.animation_data.drivers:
        driver.driver.expression = driver.driver.expression
        for var in driver.driver.variables:
            var.name = var.name
