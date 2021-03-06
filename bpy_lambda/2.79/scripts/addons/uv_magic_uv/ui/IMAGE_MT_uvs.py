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

__author__ = "Nutti <nutti.metro@gmail.com>"
__status__ = "production"
__version__ = "5.2"
__date__ = "17 Nov 2018"

import bpy
from ..op import copy_paste_uv_uvedit
from ..op import align_uv
from ..op import uv_inspection
from ..op import align_uv_cursor
from ..op import select_uv


__all__ = [
    'MenuCopyPasteUVUVEdit',
    'MenuAlignUV',
    'MenuSelectUV',
    'MenuAlignUVCursor',
    'MenuUVInspection',
]


class MenuCopyPasteUVUVEdit(bpy.types.Menu):
    """
    Menu class: Master menu of Copy/Paste UV coordinate on UV/ImageEditor
    """

    bl_idname = "uv.muv_copy_paste_uv_uvedit_menu"
    bl_label = "Copy/Paste UV"
    bl_description = "Copy and Paste UV coordinate among object"

    def draw(self, _):
        layout = self.layout

        layout.operator(copy_paste_uv_uvedit.OperatorCopyUV.bl_idname,
                        text="Copy")
        layout.operator(copy_paste_uv_uvedit.OperatorPasteUV.bl_idname,
                        text="Paste")


class MenuAlignUV(bpy.types.Menu):
    """
    Menu class: Master menu of Align UV
    """

    bl_idname = "uv.muv_align_uv_menu"
    bl_label = "Align UV"
    bl_description = "Align UV"

    def draw(self, context):
        layout = self.layout
        sc = context.scene

        ops = layout.operator(align_uv.OperatorCircle.bl_idname, text="Circle")
        ops.transmission = sc.muv_align_uv_transmission
        ops.select = sc.muv_align_uv_select

        ops = layout.operator(align_uv.OperatorStraighten.bl_idname,
                              text="Straighten")
        ops.transmission = sc.muv_align_uv_transmission
        ops.select = sc.muv_align_uv_select
        ops.vertical = sc.muv_align_uv_vertical
        ops.horizontal = sc.muv_align_uv_horizontal

        ops = layout.operator(align_uv.OperatorAxis.bl_idname,
                              text="XY-axis")
        ops.transmission = sc.muv_align_uv_transmission
        ops.select = sc.muv_align_uv_select
        ops.vertical = sc.muv_align_uv_vertical
        ops.horizontal = sc.muv_align_uv_horizontal
        ops.location = sc.muv_align_uv_location


class MenuSelectUV(bpy.types.Menu):
    """
    Menu class: Master menu of Select UV
    """

    bl_idname = "uv.muv_select_uv_menu"
    bl_label = "Select UV"
    bl_description = "Select UV"

    def draw(self, _):
        layout = self.layout

        layout.operator(select_uv.OperatorSelectOverlapped.bl_idname,
                        text="Overlapped")
        layout.operator(select_uv.OperatorSelectFlipped.bl_idname,
                        text="Flipped")


class MenuAlignUVCursor(bpy.types.Menu):
    """
    Menu class: Master menu of Align UV Cursor
    """

    bl_idname = "uv.muv_align_uv_cursor_menu"
    bl_label = "Align UV Cursor"
    bl_description = "Align UV cursor"

    def draw(self, context):
        layout = self.layout
        sc = context.scene

        ops = layout.operator(align_uv_cursor.Operator.bl_idname,
                              text="Left Top")
        ops.position = 'LEFT_TOP'
        ops.base = sc.muv_align_uv_cursor_align_method

        ops = layout.operator(align_uv_cursor.Operator.bl_idname,
                              text="Middle Top")
        ops.position = 'MIDDLE_TOP'
        ops.base = sc.muv_align_uv_cursor_align_method

        ops = layout.operator(align_uv_cursor.Operator.bl_idname,
                              text="Right Top")
        ops.position = 'RIGHT_TOP'
        ops.base = sc.muv_align_uv_cursor_align_method

        ops = layout.operator(align_uv_cursor.Operator.bl_idname,
                              text="Left Middle")
        ops.position = 'LEFT_MIDDLE'
        ops.base = sc.muv_align_uv_cursor_align_method

        ops = layout.operator(align_uv_cursor.Operator.bl_idname,
                              text="Center")
        ops.position = 'CENTER'
        ops.base = sc.muv_align_uv_cursor_align_method

        ops = layout.operator(align_uv_cursor.Operator.bl_idname,
                              text="Right Middle")
        ops.position = 'RIGHT_MIDDLE'
        ops.base = sc.muv_align_uv_cursor_align_method

        ops = layout.operator(align_uv_cursor.Operator.bl_idname,
                              text="Left Bottom")
        ops.position = 'LEFT_BOTTOM'
        ops.base = sc.muv_align_uv_cursor_align_method

        ops = layout.operator(align_uv_cursor.Operator.bl_idname,
                              text="Middle Bottom")
        ops.position = 'MIDDLE_BOTTOM'
        ops.base = sc.muv_align_uv_cursor_align_method

        ops = layout.operator(align_uv_cursor.Operator.bl_idname,
                              text="Right Bottom")
        ops.position = 'RIGHT_BOTTOM'
        ops.base = sc.muv_align_uv_cursor_align_method


class MenuUVInspection(bpy.types.Menu):
    """
    Menu class: Master menu of UV Inspection
    """

    bl_idname = "uv.muv_uv_inspection_menu"
    bl_label = "UV Inspection"
    bl_description = "UV Inspection"

    def draw(self, context):
        layout = self.layout
        sc = context.scene

        layout.prop(sc, "muv_uv_inspection_show", text="UV Inspection")
        layout.operator(uv_inspection.OperatorUpdate.bl_idname,
                        text="Update")
