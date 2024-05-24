# -*- coding: utf-8 -*-
import imgui
from tabs import *
from icons import IconsFontAwesome6 as ICON_FA

CURRENT_TAB = 1
TABS = [
    (f"{ICON_FA.ICON_PEOPLE_GROUP} Группы", TAB_groups),
    (f"{ICON_FA.ICON_GEARS} Настройки", TAB_settings)
]


def OnUpdate(fonts):
    drawTabButtons()
    style: imgui.core.GuiStyle = imgui.get_style()
    imgui.push_style_var(imgui.STYLE_CHILD_ROUNDING, 5)
    imgui.set_cursor_pos_y(imgui.get_cursor_pos_y() + 4)
    imgui.begin_child("main_area", 1264, 636, False)

    TABS[CURRENT_TAB][1](fonts)

    imgui.end_child()
    imgui.pop_style_var(1)


def drawTabButtons():
    global CURRENT_TAB
    for k, i in enumerate(TABS):
        if customButton(f"{i[0]}##TAB_BUTTON", (628, 60), i[0] != TABS[len(TABS) - 1][0]):
            CURRENT_TAB = k


def customButton(text, size, same_line):
    dw: imgui.core._DrawList = imgui.get_window_draw_list()
    c_pos = imgui.get_cursor_screen_pos()
    res = imgui.invisible_button(text, size[0], size[1])
    if same_line:
        imgui.same_line()
    save_pos = imgui.get_cursor_pos()

    if imgui.is_item_active():
        dw.add_rect_filled(c_pos[0], c_pos[1], c_pos[0] + size[0], c_pos[1] + size[1], 0xFF4f4f4f, 5)
    elif imgui.is_item_hovered():
        dw.add_rect_filled(c_pos[0], c_pos[1], c_pos[0] + size[0], c_pos[1] + size[1], 0xFF5e5e5e, 5)
    else:
        dw.add_rect_filled(c_pos[0], c_pos[1], c_pos[0] + size[0], c_pos[1] + size[1], 0xFF404040, 5)

    format_text = text.split("##")
    text = "".join(format_text[:len(format_text) - 1])
    text_size = imgui.calc_text_size(text)
    imgui.set_cursor_screen_pos((c_pos[0] + size[0] // 2 - text_size[0] // 2, c_pos[1] + size[1] // 2 - text_size[1] // 2))
    imgui.text(text)

    imgui.set_cursor_pos(save_pos)
    return res


def isTeacherBusy(day, lesson_num, teacher, timetable):
    for k in timetable:
        if k.day == day and k.subject_num == lesson_num and k.teacher == teacher:
            return k
    return False


def isAudienceBusy(day, lesson_num, audience, timetable):
    for k in timetable:
        if k.day == day and k.subject_num == lesson_num and k.audience == audience:
            return k
    return False


def hint(text):
    imgui.push_style_var(imgui.STYLE_WINDOW_ROUNDING, 8)
    if imgui.is_item_hovered():
        imgui.begin_tooltip()
        imgui.push_text_wrap_pos(600)
        imgui.text_unformatted(text)
        imgui.pop_text_wrap_pos()
        imgui.end_tooltip()
    imgui.pop_style_var(1)


def getLessonTime(num: int):
    def_time = [
        "08:30 - 10:00",
        "10:10 - 11:40",
        "12:10 - 13:40",
        "13:50 - 15:20",
        "15:30 - 17:00",
        "17:10 - 18:30",
        "18:40 - 20:10",
        "20:20 - 21:50"
    ]
    return def_time[num] if num < len(def_time) else "08:30 - 10:00"
