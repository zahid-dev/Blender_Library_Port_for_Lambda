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
from ..op import copy_paste_uv_object


__all__ = [
    'MenuCopyPasteUVObject',
]


class MenuCopyPasteUVObject(bpy.types.Menu):
    """
    Menu class: Master menu of Copy/Paste UV coordinate among object
    """

    bl_idname = "uv.muv_copy_paste_uv_object_menu"
    bl_label = "Copy/Paste UV"
    bl_description = "Copy and Paste UV coordinate among object"

    def draw(self, _):
        layout = self.layout

        layout.menu(copy_paste_uv_object.MenuCopyUV.bl_idname,
                    text="Copy")
        layout.menu(copy_paste_uv_object.MenuPasteUV.bl_idname,
                    text="Paste")
