# <pep8-80 compliant>

# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

__author__ = "imdjs, Nutti <nutti.metro@gmail.com>"
__status__ = "production"
__version__ = "5.2"
__date__ = "17 Nov 2018"


import bpy
import bmesh
from bpy.props import (
    StringProperty,
    BoolProperty,
    IntProperty,
    EnumProperty,
)

from .. import common


__all__ = [
    'Properties',
    'OpeartorCopyUV',
    'MenuCopyUV',
    'OperatorPasteUV',
    'MenuPasteUV',
    'OperatorSelSeqCopyUV',
    'MenuSelSeqCopyUV',
    'OperatorSelSeqPasteUV',
    'MenuSelSeqPasteUV',
]


def is_valid_context(context):
    obj = context.object

    # only edit mode is allowed to execute
    if obj is None:
        return False
    if obj.type != 'MESH':
        return False
    if context.object.mode != 'EDIT':
        return False

    # only 'VIEW_3D' space is allowed to execute
    for space in context.area.spaces:
        if space.type == 'VIEW_3D':
            break
    else:
        return False

    return True


def get_copy_uv_layers(ops_obj, bm):
    uv_layers = []
    if ops_obj.uv_map == "__default":
        if not bm.loops.layers.uv:
            ops_obj.report(
                {'WARNING'}, "Object must have more than one UV map")
            return None
        uv_layers.append(bm.loops.layers.uv.verify())
        ops_obj.report({'INFO'}, "Copy UV coordinate")
    elif ops_obj.uv_map == "__all":
        for uv in bm.loops.layers.uv.keys():
            uv_layers.append(bm.loops.layers.uv[uv])
        ops_obj.report({'INFO'}, "Copy UV coordinate (UV map: ALL)")
    else:
        uv_layers.append(bm.loops.layers.uv[ops_obj.uv_map])
        ops_obj.report(
            {'INFO'}, "Copy UV coordinate (UV map:{})".format(ops_obj.uv_map))

    return uv_layers


def get_paste_uv_layers(ops_obj, obj, bm, src_info):
    uv_layers = []
    if ops_obj.uv_map == "__default":
        if not bm.loops.layers.uv:
            ops_obj.report(
                {'WARNING'}, "Object must have more than one UV map")
            return None
        uv_layers.append(bm.loops.layers.uv.verify())
        ops_obj.report({'INFO'}, "Paste UV coordinate")
    elif ops_obj.uv_map == "__new":
        new_uv_map = common.create_new_uv_map(obj)
        if not new_uv_map:
            ops_obj.report({'WARNING'},
                           "Reached to the maximum number of UV map")
            return None
        uv_layers.append(bm.loops.layers.uv[new_uv_map.name])
        ops_obj.report(
            {'INFO'}, "Paste UV coordinate (UV map:{})".format(new_uv_map))
    elif ops_obj.uv_map == "__all":
        for src_layer in src_info.keys():
            if src_layer not in bm.loops.layers.uv.keys():
                new_uv_map = common.create_new_uv_map(obj, src_layer)
                if not new_uv_map:
                    ops_obj.report({'WARNING'},
                                   "Reached to the maximum number of UV map")
                    return None
            uv_layers.append(bm.loops.layers.uv[src_layer])
        ops_obj.report({'INFO'}, "Paste UV coordinate (UV map: ALL)")
    else:
        uv_layers.append(bm.loops.layers.uv[ops_obj.uv_map])
        ops_obj.report(
            {'INFO'}, "Paste UV coordinate (UV map:{})".format(ops_obj.uv_map))

    return uv_layers


def paste_uv(ops_obj, bm, src_info, dest_info, uv_layers, strategy, flip,
             rotate, copy_seams):
    for slayer_name, dlayer in zip(src_info.keys(), uv_layers):
        src_faces = src_info[slayer_name]
        dest_faces = dest_info[dlayer.name]

        for idx, dinfo in enumerate(dest_faces):
            sinfo = None
            if strategy == 'N_N':
                sinfo = src_faces[idx]
            elif strategy == 'N_M':
                sinfo = src_faces[idx % len(src_faces)]

            suv = sinfo["uvs"]
            spuv = sinfo["pin_uvs"]
            ss = sinfo["seams"]
            if len(sinfo["uvs"]) != len(dinfo["uvs"]):
                ops_obj.report({'WARNING'}, "Some faces are different size")
                return -1

            suvs_fr = [uv for uv in suv]
            spuvs_fr = [pin_uv for pin_uv in spuv]
            ss_fr = [s for s in ss]

            # flip UVs
            if flip is True:
                suvs_fr.reverse()
                spuvs_fr.reverse()
                ss_fr.reverse()

            # rotate UVs
            for _ in range(rotate):
                uv = suvs_fr.pop()
                pin_uv = spuvs_fr.pop()
                s = ss_fr.pop()
                suvs_fr.insert(0, uv)
                spuvs_fr.insert(0, pin_uv)
                ss_fr.insert(0, s)

            # paste UVs
            for l, suv, spuv, ss in zip(bm.faces[idx].loops, suvs_fr,
                                        spuvs_fr, ss_fr):
                l[dlayer].uv = suv
                l[dlayer].pin_uv = spuv
                if copy_seams is True:
                    l.edge.seam = ss

    return 0


class Properties:
    @classmethod
    def init_props(cls, scene):
        class Props():
            src_info = None

        scene.muv_props.copy_paste_uv = Props()
        scene.muv_props.copy_paste_uv_selseq = Props()

        scene.muv_copy_paste_uv_enabled = BoolProperty(
            name="Copy/Paste UV Enabled",
            description="Copy/Paste UV is enabled",
            default=False
        )
        scene.muv_copy_paste_uv_copy_seams = BoolProperty(
            name="Seams",
            description="Copy Seams",
            default=True
        )
        scene.muv_copy_paste_uv_mode = EnumProperty(
            items=[
                ('DEFAULT', "Default", "Default Mode"),
                ('SEL_SEQ', "Selection Sequence", "Selection Sequence Mode")
            ],
            name="Copy/Paste UV Mode",
            description="Copy/Paste UV Mode",
            default='DEFAULT'
        )
        scene.muv_copy_paste_uv_strategy = EnumProperty(
            name="Strategy",
            description="Paste Strategy",
            items=[
                ('N_N', 'N:N', 'Number of faces must be equal to source'),
                ('N_M', 'N:M', 'Number of faces must not be equal to source')
            ],
            default='N_M'
        )

    @classmethod
    def del_props(cls, scene):
        del scene.muv_props.copy_paste_uv
        del scene.muv_props.copy_paste_uv_selseq
        del scene.muv_copy_paste_uv_enabled
        del scene.muv_copy_paste_uv_copy_seams
        del scene.muv_copy_paste_uv_mode
        del scene.muv_copy_paste_uv_strategy


class OpeartorCopyUV(bpy.types.Operator):
    """
    Operation class: Copy UV coordinate
    """

    bl_idname = "uv.muv_copy_paste_uv_operator_copy_uv"
    bl_label = "Copy UV"
    bl_description = "Copy UV coordinate"
    bl_options = {'REGISTER', 'UNDO'}

    uv_map = StringProperty(default="__default", options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        # we can not get area/space/region from console
        if common.is_console_mode():
            return True
        return is_valid_context(context)

    def execute(self, context):
        props = context.scene.muv_props.copy_paste_uv
        obj = context.active_object
        bm = common.create_bmesh(obj)

        # get UV layer
        uv_layers = get_copy_uv_layers(self, bm)
        if not uv_layers:
            return {'CANCELLED'}

        # get selected face
        props.src_info = {}
        for layer in uv_layers:
            face_info = []
            for face in bm.faces:
                if face.select:
                    info = {
                        "uvs": [l[layer].uv.copy() for l in face.loops],
                        "pin_uvs": [l[layer].pin_uv for l in face.loops],
                        "seams": [l.edge.seam for l in face.loops],
                    }
                    face_info.append(info)
            if not face_info:
                self.report({'WARNING'}, "No faces are selected")
                return {'CANCELLED'}
            props.src_info[layer.name] = face_info

        face_count = len([f for f in bm.faces if f.select])
        self.report({'INFO'}, "{} face(s) are copied".format(face_count))

        return {'FINISHED'}


class MenuCopyUV(bpy.types.Menu):
    """
    Menu class: Copy UV coordinate
    """

    bl_idname = "uv.muv_copy_paste_uv_menu_copy_uv"
    bl_label = "Copy UV (Menu)"
    bl_description = "Menu of Copy UV coordinate"

    @classmethod
    def poll(cls, context):
        return is_valid_context(context)

    def draw(self, context):
        layout = self.layout
        # create sub menu
        obj = context.active_object
        bm = common.create_bmesh(obj)
        uv_maps = bm.loops.layers.uv.keys()

        ops = layout.operator(OpeartorCopyUV.bl_idname, text="[Default]")
        ops.uv_map = "__default"

        ops = layout.operator(OpeartorCopyUV.bl_idname, text="[All]")
        ops.uv_map = "__all"

        for m in uv_maps:
            ops = layout.operator(OpeartorCopyUV.bl_idname, text=m)
            ops.uv_map = m


class OperatorPasteUV(bpy.types.Operator):
    """
    Operation class: Paste UV coordinate
    """

    bl_idname = "uv.muv_copy_paste_uv_operator_paste_uv"
    bl_label = "Paste UV"
    bl_description = "Paste UV coordinate"
    bl_options = {'REGISTER', 'UNDO'}

    uv_map = StringProperty(default="__default", options={'HIDDEN'})
    strategy = EnumProperty(
        name="Strategy",
        description="Paste Strategy",
        items=[
            ('N_N', 'N:N', 'Number of faces must be equal to source'),
            ('N_M', 'N:M', 'Number of faces must not be equal to source')
        ],
        default="N_M"
    )
    flip_copied_uv = BoolProperty(
        name="Flip Copied UV",
        description="Flip Copied UV...",
        default=False
    )
    rotate_copied_uv = IntProperty(
        default=0,
        name="Rotate Copied UV",
        min=0,
        max=30
    )
    copy_seams = BoolProperty(
        name="Seams",
        description="Copy Seams",
        default=True
    )

    @classmethod
    def poll(cls, context):
        # we can not get area/space/region from console
        if common.is_console_mode():
            return True
        sc = context.scene
        props = sc.muv_props.copy_paste_uv
        if not props.src_info:
            return False
        return is_valid_context(context)

    def execute(self, context):
        props = context.scene.muv_props.copy_paste_uv
        if not props.src_info:
            self.report({'WARNING'}, "Need copy UV at first")
            return {'CANCELLED'}
        obj = context.active_object
        bm = common.create_bmesh(obj)

        # get UV layer
        uv_layers = get_paste_uv_layers(self, obj, bm, props.src_info)
        if not uv_layers:
            return {'CANCELLED'}

        # get selected face
        dest_face_count = 0
        dest_info = {}
        for layer in uv_layers:
            face_info = []
            for face in bm.faces:
                if face.select:
                    info = {
                        "uvs": [l[layer].uv.copy() for l in face.loops],
                    }
                    face_info.append(info)
            if not face_info:
                self.report({'WARNING'}, "No faces are selected")
                return {'CANCELLED'}
            key = list(props.src_info.keys())[0]
            src_face_count = len(props.src_info[key])
            dest_face_count = len(face_info)
            if self.strategy == 'N_N' and src_face_count != dest_face_count:
                self.report(
                    {'WARNING'},
                    "Number of selected faces is different from copied" +
                    "(src:{}, dest:{})"
                    .format(src_face_count, dest_face_count))
                return {'CANCELLED'}
            dest_info[layer.name] = face_info

        # paste
        ret = paste_uv(self, bm, props.src_info, dest_info, uv_layers,
                       self.strategy, self.flip_copied_uv,
                       self.rotate_copied_uv, self.copy_seams)
        if ret:
            return {'CANCELLED'}

        self.report({'INFO'}, "{} face(s) are pasted".format(dest_face_count))

        bmesh.update_edit_mesh(obj.data)
        if self.copy_seams is True:
            obj.data.show_edge_seams = True

        return {'FINISHED'}


class MenuPasteUV(bpy.types.Menu):
    """
    Menu class: Paste UV coordinate
    """

    bl_idname = "uv.muv_copy_paste_uv_menu_paste_uv"
    bl_label = "Paste UV (Menu)"
    bl_description = "Menu of Paste UV coordinate"

    @classmethod
    def poll(cls, context):
        sc = context.scene
        props = sc.muv_props.copy_paste_uv
        if not props.src_info:
            return False
        return is_valid_context(context)

    def draw(self, context):
        sc = context.scene
        layout = self.layout
        # create sub menu
        obj = context.active_object
        bm = common.create_bmesh(obj)
        uv_maps = bm.loops.layers.uv.keys()

        ops = layout.operator(OperatorPasteUV.bl_idname, text="[Default]")
        ops.uv_map = "__default"
        ops.copy_seams = sc.muv_copy_paste_uv_copy_seams
        ops.strategy = sc.muv_copy_paste_uv_strategy

        ops = layout.operator(OperatorPasteUV.bl_idname, text="[New]")
        ops.uv_map = "__new"
        ops.copy_seams = sc.muv_copy_paste_uv_copy_seams
        ops.strategy = sc.muv_copy_paste_uv_strategy

        ops = layout.operator(OperatorPasteUV.bl_idname, text="[All]")
        ops.uv_map = "__all"
        ops.copy_seams = sc.muv_copy_paste_uv_copy_seams
        ops.strategy = sc.muv_copy_paste_uv_strategy

        for m in uv_maps:
            ops = layout.operator(OperatorPasteUV.bl_idname, text=m)
            ops.uv_map = m
            ops.copy_seams = sc.muv_copy_paste_uv_copy_seams
            ops.strategy = sc.muv_copy_paste_uv_strategy


class OperatorSelSeqCopyUV(bpy.types.Operator):
    """
    Operation class: Copy UV coordinate by selection sequence
    """

    bl_idname = "uv.muv_copy_paste_uv_operator_selseq_copy_uv"
    bl_label = "Copy UV (Selection Sequence)"
    bl_description = "Copy UV data by selection sequence"
    bl_options = {'REGISTER', 'UNDO'}

    uv_map = StringProperty(default="__default", options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        # we can not get area/space/region from console
        if common.is_console_mode():
            return True
        return is_valid_context(context)

    def execute(self, context):
        props = context.scene.muv_props.copy_paste_uv_selseq
        obj = context.active_object
        bm = common.create_bmesh(obj)

        # get UV layer
        uv_layers = get_copy_uv_layers(self, bm)
        if not uv_layers:
            return {'CANCELLED'}

        # get selected face
        props.src_info = {}
        for layer in uv_layers:
            face_info = []
            for hist in bm.select_history:
                if isinstance(hist, bmesh.types.BMFace) and hist.select:
                    info = {
                        "uvs": [l[layer].uv.copy() for l in hist.loops],
                        "pin_uvs": [l[layer].pin_uv for l in hist.loops],
                        "seams": [l.edge.seam for l in hist.loops],
                    }
                    face_info.append(info)
            if not face_info:
                self.report({'WARNING'}, "No faces are selected")
                return {'CANCELLED'}
            props.src_info[layer.name] = face_info

        face_count = len([f for f in bm.faces if f.select])
        self.report({'INFO'}, "{} face(s) are selected".format(face_count))

        return {'FINISHED'}


class MenuSelSeqCopyUV(bpy.types.Menu):
    """
    Menu class: Copy UV coordinate by selection sequence
    """

    bl_idname = "uv.muv_copy_paste_uv_menu_selseq_copy_uv"
    bl_label = "Copy UV (Selection Sequence) (Menu)"
    bl_description = "Menu of Copy UV coordinate by selection sequence"

    @classmethod
    def poll(cls, context):
        return is_valid_context(context)

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        bm = common.create_bmesh(obj)
        uv_maps = bm.loops.layers.uv.keys()

        ops = layout.operator(OperatorSelSeqCopyUV.bl_idname, text="[Default]")
        ops.uv_map = "__default"

        ops = layout.operator(OperatorSelSeqCopyUV.bl_idname, text="[All]")
        ops.uv_map = "__all"

        for m in uv_maps:
            ops = layout.operator(OperatorSelSeqCopyUV.bl_idname, text=m)
            ops.uv_map = m


class OperatorSelSeqPasteUV(bpy.types.Operator):
    """
    Operation class: Paste UV coordinate by selection sequence
    """

    bl_idname = "uv.muv_copy_paste_uv_operator_selseq_paste_uv"
    bl_label = "Paste UV (Selection Sequence)"
    bl_description = "Paste UV coordinate by selection sequence"
    bl_options = {'REGISTER', 'UNDO'}

    uv_map = StringProperty(default="__default", options={'HIDDEN'})
    strategy = EnumProperty(
        name="Strategy",
        description="Paste Strategy",
        items=[
            ('N_N', 'N:N', 'Number of faces must be equal to source'),
            ('N_M', 'N:M', 'Number of faces must not be equal to source')
        ],
        default="N_M"
    )
    flip_copied_uv = BoolProperty(
        name="Flip Copied UV",
        description="Flip Copied UV...",
        default=False
    )
    rotate_copied_uv = IntProperty(
        default=0,
        name="Rotate Copied UV",
        min=0,
        max=30
    )
    copy_seams = BoolProperty(
        name="Seams",
        description="Copy Seams",
        default=True
    )

    @classmethod
    def poll(cls, context):
        # we can not get area/space/region from console
        if common.is_console_mode():
            return True
        sc = context.scene
        props = sc.muv_props.copy_paste_uv_selseq
        if not props.src_info:
            return False
        return is_valid_context(context)

    def execute(self, context):
        props = context.scene.muv_props.copy_paste_uv_selseq
        if not props.src_info:
            self.report({'WARNING'}, "Need copy UV at first")
            return {'CANCELLED'}
        obj = context.active_object
        bm = common.create_bmesh(obj)

        # get UV layer
        uv_layers = get_paste_uv_layers(self, obj, bm, props.src_info)
        if not uv_layers:
            return {'CANCELLED'}

        # get selected face
        dest_face_count = 0
        dest_info = {}
        for layer in uv_layers:
            face_info = []
            for hist in bm.select_history:
                if isinstance(hist, bmesh.types.BMFace) and hist.select:
                    info = {
                        "uvs": [l[layer].uv.copy() for l in hist.loops],
                    }
                    face_info.append(info)
            if not face_info:
                self.report({'WARNING'}, "No faces are selected")
                return {'CANCELLED'}
            key = list(props.src_info.keys())[0]
            src_face_count = len(props.src_info[key])
            dest_face_count = len(face_info)
            if self.strategy == 'N_N' and src_face_count != dest_face_count:
                self.report(
                    {'WARNING'},
                    "Number of selected faces is different from copied" +
                    "(src:{}, dest:{})"
                    .format(src_face_count, dest_face_count))
                return {'CANCELLED'}
            dest_info[layer.name] = face_info

        # paste
        ret = paste_uv(self, bm, props.src_info, dest_info, uv_layers,
                       self.strategy, self.flip_copied_uv,
                       self.rotate_copied_uv, self.copy_seams)
        if ret:
            return {'CANCELLED'}

        self.report({'INFO'}, "{} face(s) are pasted".format(dest_face_count))

        bmesh.update_edit_mesh(obj.data)
        if self.copy_seams is True:
            obj.data.show_edge_seams = True

        return {'FINISHED'}


class MenuSelSeqPasteUV(bpy.types.Menu):
    """
    Menu class: Paste UV coordinate by selection sequence
    """

    bl_idname = "uv.muv_copy_paste_uv_menu_selseq_paste_uv"
    bl_label = "Paste UV (Selection Sequence) (Menu)"
    bl_description = "Menu of Paste UV coordinate by selection sequence"

    @classmethod
    def poll(cls, context):
        sc = context.scene
        props = sc.muv_props.copy_paste_uv_selseq
        if not props.src_uvs or not props.src_pin_uvs:
            return False
        return is_valid_context(context)

    def draw(self, context):
        sc = context.scene
        layout = self.layout
        # create sub menu
        obj = context.active_object
        bm = common.create_bmesh(obj)
        uv_maps = bm.loops.layers.uv.keys()

        ops = layout.operator(OperatorSelSeqPasteUV.bl_idname,
                              text="[Default]")
        ops.uv_map = "__default"
        ops.copy_seams = sc.muv_copy_paste_uv_copy_seams
        ops.strategy = sc.muv_copy_paste_uv_strategy

        ops = layout.operator(OperatorSelSeqPasteUV.bl_idname, text="[New]")
        ops.uv_map = "__new"
        ops.copy_seams = sc.muv_copy_paste_uv_copy_seams
        ops.strategy = sc.muv_copy_paste_uv_strategy

        ops = layout.operator(OperatorSelSeqPasteUV.bl_idname, text="[All]")
        ops.uv_map = "__all"
        ops.copy_seams = sc.muv_copy_paste_uv_copy_seams
        ops.strategy = sc.muv_copy_paste_uv_strategy

        for m in uv_maps:
            ops = layout.operator(OperatorSelSeqPasteUV.bl_idname, text=m)
            ops.uv_map = m
            ops.copy_seams = sc.muv_copy_paste_uv_copy_seams
            ops.strategy = sc.muv_copy_paste_uv_strategy
