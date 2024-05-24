#!/usr/bin/env python
# -*- coding: utf-8 -*-

from imgui.integrations.glfw import GlfwRenderer
import OpenGL.GL as gl
import glfw
import imgui
import sys
from widgets import *
from icons import IconsFontAwesome6 as ICON_FA
from style import load_style
fonts = {}


def main():
    global fonts
    imgui.create_context()
    load_style()
    window = impl_glfw_init()
    impl = GlfwRenderer(window)

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

    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()

        if glfw.get_window_attrib(window, glfw.ICONIFIED) == 0:
            imgui.new_frame()
            imgui.begin("TimeTableCreator", False, imgui.WINDOW_NO_COLLAPSE + imgui.WINDOW_NO_RESIZE + imgui.WINDOW_NO_TITLE_BAR + imgui.WINDOW_NO_MOVE)
            imgui.set_window_size(1280, 720)
            imgui.set_window_position(0, 0)

            OnUpdate(fonts)

            imgui.end()

        gl.glClearColor(1.0, 1.0, 1.0, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        if glfw.get_window_attrib(window, glfw.ICONIFIED) == 0:
            imgui.render()
            impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)

    impl.shutdown()
    glfw.terminate()


def impl_glfw_init():
    width, height = 1280, 720
    window_name = "TimeTable creator"

    if not glfw.init():
        print("Could not initialize OpenGL context")
        sys.exit(1)

    # OS X supports only forward-compatible core profiles from 3.2
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(int(width), int(height), window_name, None, None)
    glfw.make_context_current(window)
    glfw.set_window_attrib(window, glfw.RESIZABLE, False)

    if not window:
        glfw.terminate()
        print("Could not initialize Window")
        sys.exit(1)

    return window


if __name__ == "__main__":
    main()