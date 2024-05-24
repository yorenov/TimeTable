import imgui


def load_style():
    style = imgui.get_style()
    imgui.style_colors_dark(style)

    style.popup_rounding = 8
    style.frame_rounding = 8

    style.colors[imgui.COLOR_TEXT] = (0.95, 0.96, 0.98, 1.00)
    style.colors[imgui.COLOR_TEXT_DISABLED] = (0.29, 0.29, 0.29, 1.00)
    style.colors[imgui.COLOR_WINDOW_BACKGROUND] = (0.08, 0.08, 0.08, 1.00)
    style.colors[imgui.COLOR_CHILD_BACKGROUND] = (0.14, 0.14, 0.14, 1.00)
    style.colors[imgui.COLOR_POPUP_BACKGROUND] = (0.08, 0.08, 0.08, 1.00)

    style.colors[imgui.COLOR_BORDER] = (0.14, 0.14, 0.14, 1.00)
    style.colors[imgui.COLOR_BORDER_SHADOW] = (1.00, 1.00, 1.00, 0.10)
    style.colors[imgui.COLOR_FRAME_BACKGROUND] = (0.22, 0.22, 0.22, 1.00)
    style.colors[imgui.COLOR_FRAME_BACKGROUND_HOVERED] = (0.18, 0.18, 0.18, 1.00)
    style.colors[imgui.COLOR_FRAME_BACKGROUND_ACTIVE] = (0.09, 0.12, 0.14, 1.00)

    style.colors[imgui.COLOR_TITLE_BACKGROUND] = (0.14, 0.14, 0.14, 0.81)
    style.colors[imgui.COLOR_TITLE_BACKGROUND_ACTIVE] = (0.14, 0.14, 0.14, 1.00)
    style.colors[imgui.COLOR_TITLE_BACKGROUND_COLLAPSED] = (0.00, 0.00, 0.00, 0.51)
    style.colors[imgui.COLOR_MENUBAR_BACKGROUND] = (0.20, 0.20, 0.20, 1.00)

    style.colors[imgui.COLOR_SCROLLBAR_BACKGROUND] = (0.02, 0.02, 0.02, 0.39)
    style.colors[imgui.COLOR_SCROLLBAR_GRAB] = (0.36, 0.36, 0.36, 1.00)
    style.colors[imgui.COLOR_SCROLLBAR_GRAB_HOVERED] = (0.18, 0.22, 0.25, 1.00)
    style.colors[imgui.COLOR_SCROLLBAR_GRAB_ACTIVE] = (0.24, 0.24, 0.24, 1.00)
    style.colors[imgui.COLOR_CHECK_MARK] = (0.28, 0.28, 0.28, 1.00)

    style.colors[imgui.COLOR_SLIDER_GRAB] = (0.28, 0.28, 0.28, 1.00)
    style.colors[imgui.COLOR_SLIDER_GRAB_ACTIVE] = (0.28, 0.28, 0.28, 1.00)

    style.colors[imgui.COLOR_BUTTON] = (0.28, 0.28, 0.28, 1.00)
    style.colors[imgui.COLOR_BUTTON_ACTIVE] = (0.21, 0.21, 0.21, 1.00)
    style.colors[imgui.COLOR_BUTTON_HOVERED] = (0.39, 0.39, 0.39, 1.00)

    style.colors[imgui.COLOR_HEADER] = (0.28, 0.28, 0.28, 1.00)
    style.colors[imgui.COLOR_HEADER_HOVERED] = (0.39, 0.39, 0.39, 1.00)
    style.colors[imgui.COLOR_HEADER_ACTIVE] = (0.21, 0.21, 0.21, 1.00)

    style.colors[imgui.COLOR_RESIZE_GRIP] = (0.28, 0.28, 0.28, 1.00)
    style.colors[imgui.COLOR_RESIZE_GRIP_HOVERED] = (0.39, 0.39, 0.39, 1.00)
    style.colors[imgui.COLOR_RESIZE_GRIP_ACTIVE] = (0.19, 0.19, 0.19, 1.00)

    style.colors[imgui.COLOR_PLOT_LINES] = (0.61, 0.61, 0.61, 1.00)
    style.colors[imgui.COLOR_PLOT_LINES_HOVERED] = (0.43, 0.43, 0.35, 1.00)
    style.colors[imgui.COLOR_PLOT_HISTOGRAM] = (0.21, 0.21, 0.21, 1.00)
    style.colors[imgui.COLOR_PLOT_HISTOGRAM_HOVERED] = (0.18, 0.18, 0.18, 0.60)
    style.colors[imgui.COLOR_TEXT_SELECTED_BACKGROUND] = (0.32, 0.32, 0.32, 1.00)
    style.colors[imgui.COLOR_MODAL_WINDOW_DIM_BACKGROUND] = (0.26, 0.26, 0.26, 0.60)

