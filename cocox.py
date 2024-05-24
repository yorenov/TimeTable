#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from pyglet import gl
import pyglet
import imgui
import sys
from widgets import *
from icons import IconsFontAwesome6 as ICON_FA
from style import load_style
fonts = {}


# Note that we could explicitly choose to use PygletFixedPipelineRenderer
# or PygletProgrammablePipelineRenderer, but create_renderer handles the
# version checking for us.
from imgui.integrations.pyglet import create_renderer


def main():
    global fonts

    window = pyglet.window.Window(width=1280, height=720, resizable=False)
    window.set_caption('TimeTableCreator')
    gl.glClearColor(0, 0, 0, 0)
    imgui.create_context()
    load_style()
    impl = create_renderer(window)

    io = imgui.get_io()
    io.ini_file_name = None
    io.fonts.clear()
    io.fonts.add_font_from_file_ttf("./fonts/main.otf", 32.0, glyph_ranges=io.fonts.get_glyph_ranges_cyrillic())
    config = imgui.core.FontConfig(merge_mode=True, pixel_snap_h=True)
    b = imgui.core.GlyphRanges([ICON_FA.ICON_MIN, ICON_FA.ICON_MAX, 0])
    io.fonts.add_font_from_file_ttf("./fonts/icons.ttf", 25.0, font_config=config, glyph_ranges=b)
    for i in range(14, 40, 4):
        fonts[i] = io.fonts.add_font_from_file_ttf("./fonts/main.otf", i, glyph_ranges=io.fonts.get_glyph_ranges_cyrillic())
        io.fonts.add_font_from_file_ttf("./fonts/icons.ttf", i - 4, font_config=config, glyph_ranges=b)
    impl.refresh_font_texture()

    def update(dt):
        impl.process_inputs()
        imgui.new_frame()

        imgui.begin("TimeTableCreator", False, imgui.WINDOW_NO_COLLAPSE + imgui.WINDOW_NO_RESIZE + imgui.WINDOW_NO_TITLE_BAR + imgui.WINDOW_NO_MOVE)
        imgui.set_window_size(1280, 720)
        imgui.set_window_position(0, 0)
        OnUpdate(fonts)
        imgui.end()

    def draw(dt):
        update(dt)
        window.clear()
        imgui.render()
        impl.render(imgui.get_draw_data())

    pyglet.clock.schedule_interval(draw, 1 / 120.0)
    pyglet.app.run()
    impl.shutdown()


if __name__ == "__main__":
    main()