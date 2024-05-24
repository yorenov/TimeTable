# -*- coding: utf-8 -*-
import imgui
from imgui import Vec2

import db
import fill_example
import widgets
from icons import IconsFontAwesome6 as ICON_FA
from word_export import create_word, create_doc, save_doc
from datetime import datetime, date, timedelta

G_FONTS = None
TODAY = date.today()
CURRENT_YEAR, CURRENT_WEEK, DOW = TODAY.isocalendar()
CURRENT_DATE = date.fromisocalendar(CURRENT_YEAR, CURRENT_WEEK, 1)

TEACHER_LIST = None
SUBJECT_LIST = None
AUDIENCE_LIST = None
GROUP_LIST = None
SUBJ_COPY = None
SUBJ_OLD = None

SEARCH_SUBJECT = ""
SEARCH_AUDIENCE = ""
SEARCH_TEACHER = ""
SEARCH_GROUP = ""

SEARCH_TEACHER_ASSOC = ""
SEARCH_SUBJECT_ASSOC = ""

CURRENT_GROUP = None
TIME_TABLE = {
    "GROUP": "",
    "WEEK": "",
    "YEAR": "",
    "DAYS": {}
}

ASSOCIATED = {
    "last_teacher": "",
    "associated_subjects": [],

    "last_subject": "",
    "associated_teachers": []
}

ANOTHER_GROUP_TIME_TABLE = {}

DB_SUBJECTS: list[db.Subject] = db.Subject.select()
MULTILINE_ADD_GROUPS = ""


def TAB_groups(fonts):
    global G_FONTS, MULTILINE_ADD_GROUPS, SEARCH_GROUP
    global CURRENT_GROUP, CURRENT_WEEK, CURRENT_DATE, CURRENT_YEAR
    global GROUP_LIST, AUDIENCE_LIST, TEACHER_LIST, SUBJECT_LIST, DB_SUBJECTS
    global SEARCH_SUBJECT, SEARCH_AUDIENCE, SEARCH_TEACHER
    global TIME_TABLE, ANOTHER_GROUP_TIME_TABLE
    if G_FONTS is None:
        G_FONTS = fonts

    if GROUP_LIST is None or AUDIENCE_LIST is None or TEACHER_LIST is None or SUBJECT_LIST is None:
        updateLists()

    imgui.set_cursor_pos((8, 10))
    imgui.push_font(fonts[22])
    imgui.push_item_width(160)
    imgui.push_style_var(imgui.STYLE_ITEM_SPACING, Vec2(4, 4))
    imgui.push_style_var(imgui.STYLE_FRAME_PADDING, Vec2(2, 2))
    imgui.text("Группа: ")
    imgui.same_line()
    imgui.push_style_var(imgui.STYLE_FRAME_ROUNDING, 5)
    if imgui.button((CURRENT_GROUP if CURRENT_GROUP is not None else "Нет") + "##CURRENT_GROUP", max(imgui.calc_text_size(CURRENT_GROUP if CURRENT_GROUP is not None else "Нет")[0] + 5, 100)):
        imgui.open_popup("choose_group")
    imgui.set_next_window_size(250, 350)
    if imgui.begin_popup("choose_group"):
        imgui.push_item_width(210)
        _, SEARCH_GROUP = imgui.input_text(ICON_FA.ICON_MAGNIFYING_GLASS + "##SEARCH_GROUP", SEARCH_GROUP)
        imgui.separator()
        with imgui.begin_child("SEARCH_SELECT_GROUP", 235, 300, border=True):
            for i, k in enumerate(GROUP_LIST):
                if len(SEARCH_GROUP) == 0 or k.lower().find(SEARCH_GROUP.lower()) != -1:
                    imgui.selectable(k + f"##SELECTABLE_CHOOSE_GROUP{i}")
                    if imgui.is_item_clicked():
                        if CURRENT_GROUP is not None:
                            saveTimeTable()
                        CURRENT_GROUP = k
                        for i in range(6):
                            TIME_TABLE['DAYS'].update({f"{i}": []})
                        if CURRENT_GROUP != 'Шаблон':
                            db_subject: list[db.Subject] = db.Subject.select().where(db.Subject.group == CURRENT_GROUP, db.Subject.week == CURRENT_WEEK, db.Subject.year == CURRENT_YEAR)
                        else:
                            db_subject: list[db.Subject] = db.Subject.select().where(db.Subject.group == CURRENT_GROUP, db.Subject.week == 1, db.Subject.year == 1)
                        for subject in db_subject:
                            TIME_TABLE['DAYS'][str(subject.day)].append(subject)
                            TIME_TABLE['DAYS'][str(subject.day)].sort(key=lambda x: x.subject_num)
                            for i, v in enumerate(TIME_TABLE['DAYS'][str(subject.day)]):
                                v.subject_num = i
                        updateTimeTable()
                        imgui.close_current_popup()
        imgui.end_popup()
    imgui.same_line()
    if CURRENT_GROUP is not None:
        if imgui.button(ICON_FA.ICON_ERASER + " Очистить"):
            imgui.open_popup(ICON_FA.ICON_ERASER + " Очистка таблицы")

    with imgui.begin_popup_modal(ICON_FA.ICON_ERASER + " Очистка таблицы", flags=imgui.WINDOW_NO_RESIZE) as popup_modal:
        if popup_modal.opened:
            imgui.text(f"Вы действительно хотите УДАЛИТЬ расписание недели?")
            imgui.text_colored("Отменить данное действие невозможно", 1, 0.45, 0.45)
            imgui.push_style_color(imgui.COLOR_BUTTON, 0.71, 0.46, 0.46)
            imgui.push_style_color(imgui.COLOR_BUTTON_HOVERED, 0.77, 0.5, 0.5)
            imgui.push_style_color(imgui.COLOR_BUTTON_ACTIVE, 0.61, 0.4, 0.4)
            if imgui.button(ICON_FA.ICON_ERASER + " Да##accept_delete_timetable", imgui.get_window_width() // 2 - 10):
                clearTimeTable()
                updateTimeTable()
                imgui.close_current_popup()
            imgui.pop_style_color(3)
            imgui.same_line()
            if imgui.button(ICON_FA.ICON_XMARK + " Отмена##decline_delete_timetable", imgui.get_window_width() // 2 - 10):
                imgui.close_current_popup()
    if CURRENT_GROUP != 'Шаблон' and CURRENT_GROUP is not None:
        imgui.same_line()
        if imgui.button(ICON_FA.ICON_COPY + " Шаблон"):
            imgui.open_popup(ICON_FA.ICON_COPY + " Скопировать шаблон")
        with imgui.begin_popup_modal(ICON_FA.ICON_COPY + " Скопировать шаблон", flags=imgui.WINDOW_NO_RESIZE) as popup_modal:
            if popup_modal.opened:
                POPUP_restoreTable()
        imgui.same_line()
        imgui.text("| Неделя: ")
        imgui.same_line()
        imgui.push_item_width(100)
        changed, CURRENT_WEEK = imgui.input_int("##Номер недели", CURRENT_WEEK)
        if changed:
            CURRENT_WEEK = min(max(CURRENT_WEEK, 1), 52)
            CURRENT_DATE = date.fromisocalendar(CURRENT_YEAR, CURRENT_WEEK, 1)
            saveTimeTable()
            updateTimeTable()
        imgui.same_line()
        imgui.text("| Год: ")
        imgui.same_line()
        changed, CURRENT_YEAR = imgui.input_int("|##Год", CURRENT_YEAR)
        if changed:
            CURRENT_YEAR = min(max(CURRENT_YEAR, 0), 2999)
            CURRENT_DATE = date.fromisocalendar(CURRENT_YEAR, CURRENT_WEEK, 1)
            saveTimeTable()
            updateTimeTable()
        imgui.same_line()
        if imgui.button(CURRENT_GROUP + " " + ICON_FA.ICON_FILE_EXPORT + "##EXPORT_CURRENT"):
            doc = create_doc()
            date_list = [(CURRENT_DATE + timedelta(days=i)).strftime("%d.%m") for i in range(6)]
            doc = create_word(doc, date_list, group_name=CURRENT_GROUP, timetable=getTimeTable(CURRENT_GROUP, CURRENT_WEEK, CURRENT_YEAR))
            save_doc(doc, f"{CURRENT_WEEK}.{CURRENT_YEAR}_{CURRENT_GROUP}.docx")
        widgets.hint(f'Экспорт расписания для группы {CURRENT_GROUP}')
        imgui.same_line()
        if imgui.button("Все группы" + " " + ICON_FA.ICON_FILE_EXPORT + "##EXPORT_ALL"):
            doc = create_doc()
            date_list = [(CURRENT_DATE + timedelta(days=i)).strftime("%d.%m") for i in range(6)]
            for k in db.Group.select():
                doc = create_word(doc, date_list, group_name=k.name, timetable=getTimeTable(k.name, CURRENT_WEEK, CURRENT_YEAR))
            save_doc(doc, f"{CURRENT_WEEK}.{CURRENT_YEAR}_ВСЕ_ГРУППЫ.docx")
        widgets.hint(f'Экспорт расписания для всех групп')
    elif CURRENT_GROUP is not None:
        imgui.same_line()
        if imgui.button(ICON_FA.ICON_REPEAT + ' Восстановить'):
            imgui.open_popup(ICON_FA.ICON_REPEAT + " Восстановить таблицу")
        with imgui.begin_popup_modal(ICON_FA.ICON_REPEAT + " Восстановить таблицу", flags=imgui.WINDOW_NO_RESIZE) as popup_modal:
            if popup_modal.opened:
                imgui.text(f"Вы действительно хотите ВОССТАНОВИТЬ шаблон?")
                imgui.text_colored("Отменить данное действие невозможно", 1, 0.45, 0.45)
                imgui.push_style_color(imgui.COLOR_BUTTON, 0.71, 0.46, 0.46)
                imgui.push_style_color(imgui.COLOR_BUTTON_HOVERED, 0.77, 0.5, 0.5)
                imgui.push_style_color(imgui.COLOR_BUTTON_ACTIVE, 0.61, 0.4, 0.4)
                if imgui.button(ICON_FA.ICON_ERASER + " Да##accept_restore_example", imgui.get_window_width() // 2 - 10):
                    fill_example.clearExample()
                    fill_example.fillExample()
                    updateTimeTable()
                    imgui.close_current_popup()
                imgui.pop_style_color(3)
                imgui.same_line()
                if imgui.button(ICON_FA.ICON_XMARK + " Отмена##accept_restore_example", imgui.get_window_width() // 2 - 10):
                    imgui.close_current_popup()

    if CURRENT_GROUP is not None:
        setupTable()
        days = [
            'Понедельник',
            'Вторник',
            'Среда',
            'Четверг',
            'Пятница',
            'Суббота'
        ]
        imgui.push_style_var(imgui.STYLE_CELL_PADDING, (5, 5))
        for i, day in enumerate(TIME_TABLE['DAYS'].values()):
            imgui.table_next_row()
            imgui.table_next_column()
            CURRENT_DATE_DAY = CURRENT_DATE + timedelta(days=i)
            imgui.text(CURRENT_DATE_DAY.strftime("%d.%m"))
            imgui.table_next_column()
            imgui.text(days[i])
            imgui.push_font(fonts[18])
            if imgui.button(ICON_FA.ICON_PLUS + f" Добавить##{i}", imgui.get_column_width()):
                TIME_TABLE['DAYS'][str(i)].append(
                    db.Subject(group=CURRENT_GROUP,
                               year=CURRENT_YEAR if CURRENT_GROUP != 'Шаблон' else 1,
                               week=CURRENT_WEEK if CURRENT_GROUP != 'Шаблон' else 1,
                               day=i,
                               subject_num=len(day),
                               time=widgets.getLessonTime(len(day)),
                               subject='',
                               audience='',
                               teacher='')
                )
                saveTimeTable()
                updateTimeTable()
            if imgui.button(ICON_FA.ICON_TRASH_CAN + f" Очистить##{i}{days[i]}", imgui.get_column_width()):
                imgui.open_popup(f"clear_items##{i}{days[i]}")
            imgui.pop_font()
            if imgui.begin_popup(f"clear_items##{i}{days[i]}"):
                imgui.text(ICON_FA.ICON_TRASH_CAN + " Удалить...")
                if imgui.button("Дисциплины##clear_subjects", 150):
                    for v in day:
                        v.subject = ""
                    saveTimeTable()
                    updateTimeTable()
                    imgui.close_current_popup()
                if imgui.button("Преподавателей##clear_teachers", 150):
                    for v in day:
                        v.teacher = ""
                    saveTimeTable()
                    updateTimeTable()
                    imgui.close_current_popup()
                if imgui.button("Аудитории##clear_audience", 150):
                    for v in day:
                        v.audience = ""
                    saveTimeTable()
                    updateTimeTable()
                    imgui.close_current_popup()
                if imgui.button("Время##clear_time", 150):
                    for v in day:
                        v.time = ""
                    saveTimeTable()
                    updateTimeTable()
                    imgui.close_current_popup()
                if imgui.button("Всё кроме времени##clear_all_except_time", 150):
                    for v in day:
                        v.teacher = ""
                        v.subject = ""
                        v.audience = ""
                    saveTimeTable()
                    updateTimeTable()
                    imgui.close_current_popup()
                if imgui.button("Все строки##clear_all_rows", 150):
                    for v in day:
                        v.delete_instance()
                    saveTimeTable()
                    updateTimeTable()
                    imgui.close_current_popup()
                imgui.end_popup()
            imgui.table_next_column()
            draw_table([x.time for x in day], f'TIME:{CURRENT_GROUP}:{CURRENT_YEAR}:{CURRENT_WEEK}:{i}', True)
            imgui.table_next_column()
            draw_table([x.subject for x in day], f'SUBJECT:{CURRENT_GROUP}:{CURRENT_YEAR}:{CURRENT_WEEK}:{i}')
            imgui.table_next_column()
            draw_table([x.teacher for x in day], f'TEACHER:{CURRENT_GROUP}:{CURRENT_YEAR}:{CURRENT_WEEK}:{i}')
            imgui.table_next_column()
            draw_table([x.audience for x in day], f'AUDIENCE:{CURRENT_GROUP}:{CURRENT_YEAR}:{CURRENT_WEEK}:{i}')
        imgui.pop_style_var(1)
        imgui.end_table()
    imgui.pop_style_var(3)
    imgui.pop_font()
    imgui.pop_item_width()


def TAB_teachers(fonts):
    imgui.text("teachers")


def TAB_audience(fonts):
    imgui.text("audience")


def TAB_settings(fonts):
    global SEARCH_SUBJECT, SEARCH_AUDIENCE, SEARCH_TEACHER, SEARCH_GROUP
    global GROUP_LIST, AUDIENCE_LIST, TEACHER_LIST, SUBJECT_LIST, ASSOCIATED
    imgui.push_font(fonts[22])
    if GROUP_LIST is None or AUDIENCE_LIST is None or TEACHER_LIST is None or SUBJECT_LIST is None:
        updateLists()

    imgui.push_style_var(imgui.STYLE_WINDOW_PADDING, Vec2(5, 5))
    imgui.push_style_var(imgui.STYLE_FRAME_PADDING, Vec2(5, 5))
    imgui.push_style_color(imgui.COLOR_CHILD_BACKGROUND, 0.11, 0.11, 0.11, 1.00)
    imgui.set_cursor_pos((5, 5))
    imgui.push_item_width(225)
    _, SEARCH_GROUP = imgui.input_text(ICON_FA.ICON_MAGNIFYING_GLASS + " Группы##SEARCH_GROUP", SEARCH_GROUP)
    imgui.same_line()
    imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + 12)
    imgui.push_item_width(200)
    _, SEARCH_SUBJECT = imgui.input_text(ICON_FA.ICON_MAGNIFYING_GLASS + " Дисциплина##SEARCH_GROUP", SEARCH_SUBJECT)
    imgui.same_line()
    imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + 5)
    imgui.push_item_width(180)
    _, SEARCH_TEACHER = imgui.input_text(ICON_FA.ICON_MAGNIFYING_GLASS + " Преподаватель##SEARCH_GROUP", SEARCH_TEACHER)
    imgui.same_line()
    imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + 8)
    imgui.push_item_width(200)
    _, SEARCH_AUDIENCE = imgui.input_text(ICON_FA.ICON_MAGNIFYING_GLASS + " Аудитория##SEARCH_GROUP", SEARCH_AUDIENCE)

    SIZE_CHILD = 310
    imgui.begin_child("settings_group_list", SIZE_CHILD, 590, border=True, flags=imgui.WINDOW_NO_SCROLLBAR)
    if imgui.button(ICON_FA.ICON_PLUS + " Добавить группы", SIZE_CHILD - 10):
        imgui.open_popup(ICON_FA.ICON_PLUS + " Добавить группы")
    POPUP_addGroups()
    imgui.separator()
    for k in GROUP_LIST[1:]:
        if len(SEARCH_GROUP) == 0 or k.lower().find(SEARCH_GROUP.lower()) != -1:
            imgui.button(k, SIZE_CHILD-45)
            imgui.same_line()
            if imgui.button(ICON_FA.ICON_TRASH_CAN + f"##DELETE_GROUP{k}", 25):
                saveTimeTable()

                db_group = db.Group.get(db.Group.name == k)
                db_group.delete_instance()

                for k in db.Subject.select().where(db.Subject.group == k):
                    k.delete_instance()

                updateLists()
                updateTimeTable()
            widgets.hint("Удалить группу")
    imgui.end_child()
    imgui.same_line()
    imgui.begin_child("settings_subject_list", SIZE_CHILD, 590, border=True, flags=imgui.WINDOW_NO_SCROLLBAR)
    if imgui.button(ICON_FA.ICON_PLUS + " Добавить дисциплины", SIZE_CHILD - 10):
        imgui.open_popup(ICON_FA.ICON_PLUS + " Добавить дисциплины")
    POPUP_addSubjects()
    imgui.separator()
    for k in SUBJECT_LIST:
        if len(SEARCH_SUBJECT) == 0 or k.lower().find(SEARCH_SUBJECT.lower()) != -1:
            if imgui.button(k + "##SELECT_ASSOCIATED_SUBJECTS", SIZE_CHILD-45):
                    # "last_subject": "",
                    # "associated_teachers": []
                if ASSOCIATED['last_subject'] != k:
                    ASSOCIATED['last_subject'] = k
                    ASSOCIATED['associated_teachers'] = [x.teacher for x in db.AssociatedLesson.select().where(db.AssociatedLesson.subject == k)]

                SEARCH_TEACHER = ""
                imgui.open_popup(ICON_FA.ICON_PLUS + " Преподаватели дисциплины")
            imgui.same_line()
            if imgui.button(ICON_FA.ICON_TRASH_CAN + f"##DELETE_SUBJECT_{k}", 25):
                db_lesson = db.Lesson.get(db.Lesson.name == k)
                db_lesson.delete_instance()
                for assoc in db.AssociatedLesson.select().where(db.AssociatedLesson.subject == k):
                    assoc.delete_instance()
                updateLists()
            widgets.hint("Удалить дисциплину")
    POPUP_associatedTeacher()
    imgui.end_child()
    imgui.same_line()
    imgui.begin_child("settings_teacher_list", SIZE_CHILD, 590, border=True, flags=imgui.WINDOW_NO_SCROLLBAR)
    if imgui.button(ICON_FA.ICON_PLUS + " Добавить преподавателей", SIZE_CHILD - 10):
        imgui.open_popup(ICON_FA.ICON_PLUS + " Добавить преподавателей")
    POPUP_addTeachers()
    imgui.separator()
    for k in TEACHER_LIST:
        if len(SEARCH_TEACHER) == 0 or k.lower().find(SEARCH_TEACHER.lower()) != -1:
            if imgui.button(k, SIZE_CHILD-45):
                if ASSOCIATED['last_teacher'] != k:
                    ASSOCIATED['last_teacher'] = k
                    ASSOCIATED['associated_subjects'] = [x.subject for x in db.AssociatedLesson.select().where(db.AssociatedLesson.teacher == k)]
                SEARCH_SUBJECT = ""
                imgui.open_popup(ICON_FA.ICON_PLUS + " Дисциплины преподаваталей")
            imgui.same_line()
            if imgui.button(ICON_FA.ICON_TRASH_CAN + f"##DELETE_TEACHER_{k}", 25):
                db_teacher = db.Teacher.get(db.Teacher.name == k)
                db_teacher.delete_instance()

                for assoc in db.AssociatedLesson.select().where(db.AssociatedLesson.teacher == k):
                    assoc.delete_instance()
                updateLists()
            widgets.hint("Удалить преподавателя")
    POPUP_associatedLessons()
    imgui.end_child()
    imgui.same_line()
    imgui.begin_child("settings_audience_list", SIZE_CHILD, 590, border=True, flags=imgui.WINDOW_NO_SCROLLBAR)
    if imgui.button(ICON_FA.ICON_PLUS + " Добавить аудитории", SIZE_CHILD - 10):
        imgui.open_popup(ICON_FA.ICON_PLUS + " Добавить аудитории")
    POPUP_addAudiences()
    imgui.separator()
    for k in AUDIENCE_LIST:
        if len(SEARCH_AUDIENCE) == 0 or k.lower().find(SEARCH_AUDIENCE.lower()) != -1:
            imgui.button(k, SIZE_CHILD-45)
            imgui.same_line()
            if imgui.button(ICON_FA.ICON_TRASH_CAN + f"##DELETE_AUDIENCE_{k}", 25):
                db_audience = db.Audience.get(db.Audience.name == k)
                db_audience.delete_instance()
                updateLists()
            widgets.hint("Удалить аудиторию")
    imgui.end_child()
    imgui.pop_style_var(2)
    imgui.pop_style_color(1)
    imgui.pop_font()


def draw_table(items, id, draw_tools=False):
    global G_FONTS, SUBJ_COPY, SUBJ_OLD, SEARCH_SUBJECT, SEARCH_AUDIENCE, SEARCH_TEACHER
    global TEACHER_LIST, SUBJECT_LIST, GROUP_LIST, AUDIENCE_LIST
    global TIME_TABLE, ANOTHER_GROUP_TIME_TABLE
    imgui.push_style_var(imgui.STYLE_CELL_PADDING, imgui.Vec2(0, 0))
    imgui.begin_table(f"##draw_table{id}{len(items)}", 1, imgui.TABLE_ROW_BACKGROUND)
    id_s = id.split(":")
    if id_s[0] == "AUDIENCE":
        busy_cell_func = widgets.isAudienceBusy
    elif id_s[0] == "TEACHER":
        busy_cell_func = widgets.isTeacherBusy
    else:
        busy_cell_func = None
    busy_subj = False
    for i, time_lesson in enumerate(items):
        imgui.table_next_row()
        imgui.table_next_column()
        size = imgui.get_column_width()
        if busy_cell_func is not None and len(time_lesson) > 0:
            busy_subj = busy_cell_func(int(id_s[-1]), i, time_lesson, ANOTHER_GROUP_TIME_TABLE)
        imgui.push_style_var(imgui.STYLE_FRAME_ROUNDING, 0)
        imgui.push_style_color(imgui.COLOR_BUTTON, 0, 0, 0, 0)
        if busy_subj:
            imgui.push_style_color(imgui.COLOR_TEXT, 0.99, 1, 0.38)
        icon_btn = (' ' + ICON_FA.ICON_TRIANGLE_EXCLAMATION) if (busy_subj and len(time_lesson) > 0) else ''
        if imgui.button(time_lesson + f"{icon_btn}##{id}{i}", size):
            imgui.open_popup(f"edit_subject_text:{id}:{i}")
            SUBJ_OLD = None
        if busy_subj:
            if len(time_lesson) > 0:
                if id_s[0] == "AUDIENCE":
                    widgets.hint(f"Данная аудитория уже занята группой '{busy_subj.group}'\nПредмет '{busy_subj.subject}' у преподавателя '{busy_subj.teacher}'")
                elif id_s[0] == "TEACHER":
                    widgets.hint(f"Данный преподаватель уже ведёт '{busy_subj.subject}' в аудитории '{busy_subj.audience}' у группы '{busy_subj.group}'")
            imgui.pop_style_color(1)
        imgui.pop_style_var(1)
        imgui.pop_style_color(1)
        if imgui.is_item_clicked(1):
            imgui.open_popup(f"tools_subject:{id}{i}")
        if imgui.begin_popup(f"tools_subject:{id}{i}"):
            if SUBJ_COPY is None:
                imgui.push_style_var(imgui.STYLE_ALPHA, 0.6)
            if imgui.button(ICON_FA.ICON_PASTE + " Вставить", 150) and SUBJ_COPY is not None:
                TIME_TABLE['DAYS'][id.split(":")[4]][i].time = SUBJ_COPY['time']
                TIME_TABLE['DAYS'][id.split(":")[4]][i].teacher = SUBJ_COPY['teacher']
                TIME_TABLE['DAYS'][id.split(":")[4]][i].audience = SUBJ_COPY['audience']
                TIME_TABLE['DAYS'][id.split(":")[4]][i].subject = SUBJ_COPY['subject']
                saveTimeTable()
                updateTimeTable()
                imgui.close_current_popup()

            if SUBJ_COPY is None:
                imgui.pop_style_var(1)
            if imgui.button(ICON_FA.ICON_COPY + " Скопировать", 150):
                item = list(TIME_TABLE['DAYS'].values())[int(id.split(":")[4])][i]
                SUBJ_COPY = {"time": item.time, "subject": item.subject, "teacher": item.teacher, "audience": item.audience}
                imgui.close_current_popup()
            if imgui.button(ICON_FA.ICON_TRASH_CAN + " Удалить", 150):
                list(TIME_TABLE['DAYS'].values())[int(id.split(":")[4])][i].delete_instance()
                saveTimeTable()
                updateTimeTable()
                imgui.close_current_popup()
            imgui.end_popup()
        if imgui.begin_popup(f"edit_subject_text:{id}:{i}"):
            # "last_teacher": "",
            # "associated_subjects": [],
            #
            # "last_subject": "",
            # "associated_teachers": []
            item: db.Subject = list(TIME_TABLE['DAYS'].values())[int(id.split(":")[4])][i]
            if SUBJ_OLD is None:
                SUBJ_OLD = {"time": item.time, "subject": item.subject, "teacher": item.teacher, "audience": item.audience}

            if ASSOCIATED['last_teacher'] != SUBJ_OLD['teacher']:
                ASSOCIATED['last_teacher'] = SUBJ_OLD['teacher']
                ASSOCIATED['associated_subjects'] = [x.subject for x in db.AssociatedLesson.select().where(db.AssociatedLesson.teacher == SUBJ_OLD['teacher'])]

            if ASSOCIATED['last_subject'] != SUBJ_OLD['subject']:
                ASSOCIATED['last_subject'] = SUBJ_OLD['subject']
                ASSOCIATED['associated_teachers'] = [x.teacher for x in db.AssociatedLesson.select().where(db.AssociatedLesson.subject == SUBJ_OLD['subject'])]

            imgui.push_item_width(230)

            _, SUBJ_OLD['time'] = imgui.input_text(f"##Время##input_text_edit_subject_text:{id}:{i}", SUBJ_OLD['time'])
            imgui.same_line()
            if imgui.button(ICON_FA.ICON_MAGNIFYING_GLASS + "##ChooseTimeBind"):
                imgui.open_popup("choose_time_bind")
            imgui.same_line()
            imgui.text("Время")

            _, SUBJ_OLD['subject'] = imgui.input_text(f"##Дисциплина##input_text_edit_subject_text:{id}:{i}", SUBJ_OLD['subject'])
            imgui.same_line()
            if imgui.button(ICON_FA.ICON_MAGNIFYING_GLASS + "##ChooseSubjectBind"):
                SEARCH_SUBJECT = ""
                imgui.open_popup("choose_subject_bind")
            imgui.same_line()
            imgui.text("Дисциплина")

            _, SUBJ_OLD['teacher'] = imgui.input_text(f"##Преподаватель##input_text_edit_subject_text:{id}:{i}", SUBJ_OLD['teacher'])
            imgui.same_line()
            if imgui.button(ICON_FA.ICON_MAGNIFYING_GLASS + "##ChooseTeacherBind"):
                SEARCH_TEACHER = ""
                imgui.open_popup("choose_teacher_bind")
            imgui.same_line()
            imgui.text("Преподаватель")

            _, SUBJ_OLD['audience'] = imgui.input_text(f"##Аудитория##input_text_edit_subject_text:{id}:{i}", SUBJ_OLD['audience'])
            imgui.same_line()
            if imgui.button(ICON_FA.ICON_MAGNIFYING_GLASS + "##ChooseAudienceBind"):
                SEARCH_AUDIENCE = ""
                imgui.open_popup("choose_audience_bind")
            imgui.same_line()
            imgui.text("Аудитория")

            if imgui.begin_popup("choose_time_bind"):
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
                for k in def_time:
                    if imgui.button(k, 150):
                        SUBJ_OLD['time'] = k
                        imgui.close_current_popup()
                imgui.end_popup()

            if imgui.begin_popup("choose_subject_bind"):
                imgui.push_item_width(150)
                _, SEARCH_SUBJECT = imgui.input_text(ICON_FA.ICON_MAGNIFYING_GLASS + "##SEARCH_SUBJECT", SEARCH_SUBJECT)
                imgui.push_style_color(imgui.COLOR_BUTTON, 0.27, 0.46, 0.27)
                imgui.push_style_color(imgui.COLOR_BUTTON_ACTIVE, 0.24, 0.43, 0.24)
                imgui.push_style_color(imgui.COLOR_BUTTON_HOVERED, 0.31, 0.5, 0.31)
                for k in ASSOCIATED['associated_subjects']:
                    if len(SEARCH_SUBJECT) == 0 or k.lower().find(SEARCH_SUBJECT.lower()) != -1:
                        if imgui.button(k, 180):
                            SUBJ_OLD['subject'] = k
                            imgui.close_current_popup()
                imgui.pop_style_color(3)
                imgui.separator()
                for k in SUBJECT_LIST:
                    if len(SEARCH_SUBJECT) == 0 or k.find(SEARCH_SUBJECT) != -1:
                        if k not in ASSOCIATED['associated_subjects']:
                            if imgui.button(k, 180):
                                SUBJ_OLD['subject'] = k
                                imgui.close_current_popup()
                imgui.pop_item_width()
                imgui.end_popup()

            if imgui.begin_popup("choose_teacher_bind"):
                imgui.push_item_width(150)
                _, SEARCH_TEACHER = imgui.input_text(ICON_FA.ICON_MAGNIFYING_GLASS + "##SEARCH_TEACHER", SEARCH_TEACHER)

                imgui.push_style_color(imgui.COLOR_BUTTON, 0.27, 0.46, 0.27)
                imgui.push_style_color(imgui.COLOR_BUTTON_ACTIVE, 0.24, 0.43, 0.24)
                imgui.push_style_color(imgui.COLOR_BUTTON_HOVERED, 0.31, 0.5, 0.31)
                for k in ASSOCIATED['associated_teachers']:
                    if len(SEARCH_SUBJECT) == 0 or k.lower().find(SEARCH_SUBJECT.lower()) != -1:
                        teacher_busy = widgets.isTeacherBusy(int(id.split(":")[4]), i, k, ANOTHER_GROUP_TIME_TABLE)
                        if teacher_busy:
                            imgui.push_style_color(imgui.COLOR_TEXT, 0.99, 1, 0.38)
                        icon_btn = (" " + ICON_FA.ICON_TRIANGLE_EXCLAMATION) if teacher_busy else ''
                        if imgui.button(k + f"{icon_btn}", 180):
                            SUBJ_OLD['teacher'] = k
                            imgui.close_current_popup()
                        if teacher_busy:
                            widgets.hint(f"Данный преподаватель уже ведёт '{teacher_busy.subject}' в аудитории '{teacher_busy.audience}' у группы '{teacher_busy.group}'")
                            imgui.pop_style_color(1)
                imgui.pop_style_color(3)
                imgui.separator()

                for k in TEACHER_LIST:
                    if len(SEARCH_TEACHER) == 0 or k.find(SEARCH_TEACHER) != -1:
                        if k not in ASSOCIATED['associated_teachers']:
                            teacher_busy = widgets.isTeacherBusy(int(id.split(":")[4]), i, k, ANOTHER_GROUP_TIME_TABLE)
                            if teacher_busy:
                                imgui.push_style_color(imgui.COLOR_TEXT, 0.99, 1, 0.38)
                            icon_btn = (" " + ICON_FA.ICON_TRIANGLE_EXCLAMATION) if teacher_busy else ''
                            if imgui.button(k + f"{icon_btn}", 180):
                                SUBJ_OLD['teacher'] = k
                                imgui.close_current_popup()
                            if teacher_busy:
                                widgets.hint(f"Данный преподаватель уже ведёт '{teacher_busy.subject}' в аудитории '{teacher_busy.audience}' у группы '{teacher_busy.group}'")
                                imgui.pop_style_color(1)
                imgui.pop_item_width()
                imgui.end_popup()

            if imgui.begin_popup("choose_audience_bind"):
                imgui.push_item_width(150)
                _, SEARCH_AUDIENCE = imgui.input_text(ICON_FA.ICON_MAGNIFYING_GLASS + "##SEARCH_SUBJECT", SEARCH_AUDIENCE)
                for k in AUDIENCE_LIST:
                    if len(SEARCH_AUDIENCE) == 0 or k.find(SEARCH_AUDIENCE) != -1:
                        audience_busy = widgets.isAudienceBusy(int(id.split(":")[4]), i, k, ANOTHER_GROUP_TIME_TABLE)
                        if audience_busy:
                            imgui.push_style_color(imgui.COLOR_TEXT, 0.99, 1, 0.38)
                        icon_btn = (" " + ICON_FA.ICON_TRIANGLE_EXCLAMATION) if audience_busy else ''
                        if imgui.button(k + f"{icon_btn}", 180):
                            SUBJ_OLD['audience'] = k
                            imgui.close_current_popup()
                        if audience_busy:
                            widgets.hint(f"Данная аудитория уже занята группой '{audience_busy.group}' ({audience_busy.subject} у {audience_busy.teacher})")
                            imgui.pop_style_color(1)
                imgui.pop_item_width()
                imgui.end_popup()
            HAVE_IMPORTANT_F = SUBJ_OLD['subject'][:18] == "Разговор о важном/"
            if HAVE_IMPORTANT_F:
                imgui.push_style_color(imgui.COLOR_BUTTON, 0.27, 0.46, 0.27)
            else:
                imgui.push_style_color(imgui.COLOR_BUTTON, 0.46, 0.27, 0.27)
            if imgui.button(f"{(ICON_FA.ICON_MINUS if HAVE_IMPORTANT_F else ICON_FA.ICON_PLUS)} Разговор о важном" + "##BTN_IMPORTANT", imgui.get_window_width() - 17):
                if HAVE_IMPORTANT_F:
                    SUBJ_OLD['subject'] = SUBJ_OLD['subject'][18:]
                else:
                    SUBJ_OLD['subject'] = "Разговор о важном/" + SUBJ_OLD['subject']
            imgui.pop_style_color(1)
            if imgui.button(ICON_FA.ICON_FLOPPY_DISK + " Сохранить" + "##SAVE_POPUP_EDIT_SUBJECT", imgui.get_window_width() // 2 - 10):
                item.time = SUBJ_OLD['time']
                item.subject = SUBJ_OLD['subject']
                item.teacher = SUBJ_OLD['teacher']
                item.audience = SUBJ_OLD['audience']

                if ((len(item.subject) > 0 and item.subject[:18] != "Разговор о важном/") or (len(item.subject[18:]) > 0)) and item.subject not in SUBJECT_LIST:
                    if item.subject[:18] == "Разговор о важном/":
                        SUBJECT_LIST.append(item.subject)
                    else:
                        SUBJECT_LIST.append(item.subject[18:])

                if len(item.teacher) > 0 and item.teacher not in TEACHER_LIST:
                    TEACHER_LIST.append(item.teacher)

                if len(item.audience) > 0 and item.audience not in AUDIENCE_LIST:
                    AUDIENCE_LIST.append(item.audience)

                item.save()
                SUBJ_OLD = None
                saveTimeTable()
                updateTimeTable()
                imgui.close_current_popup()
            imgui.same_line()

            if imgui.button(ICON_FA.ICON_XMARK + " Отмена##edit_subject_text", imgui.get_window_width() // 2 - 10):
                SUBJ_OLD = None
                saveTimeTable()
                updateTimeTable()
                imgui.close_current_popup()
            imgui.end_popup()
    imgui.end_table()
    imgui.pop_style_var(1)


def setupTable():
    imgui.begin_table(f"##table_time", 6, (
                imgui.TABLE_ROW_BACKGROUND + imgui.TABLE_BORDERS + imgui.TABLE_NO_PAD_INNER_X + imgui.TABLE_NO_PAD_OUTER_X + imgui.TABLE_RESIZABLE))
    imgui.table_setup_column("Дата", imgui.TABLE_COLUMN_WIDTH_STRETCH, 0.2)
    imgui.table_setup_column("День", imgui.TABLE_COLUMN_WIDTH_FIXED)
    imgui.table_setup_column("Время", imgui.TABLE_COLUMN_WIDTH_STRETCH)
    imgui.table_setup_column("Дисциплины", imgui.TABLE_COLUMN_WIDTH_STRETCH)
    imgui.table_setup_column("Преподаватель", imgui.TABLE_COLUMN_WIDTH_STRETCH)
    imgui.table_setup_column("Аудитория", imgui.TABLE_COLUMN_WIDTH_STRETCH)
    imgui.table_headers_row()


def updateTimeTable():
    global CURRENT_GROUP, CURRENT_WEEK, CURRENT_YEAR, TIME_TABLE, ANOTHER_GROUP_TIME_TABLE
    for i in range(6):
        TIME_TABLE['DAYS'].update({f"{i}": []})
    if CURRENT_GROUP != 'Шаблон':
        ANOTHER_GROUP_TIME_TABLE = db.Subject.select().where(db.Subject.group != CURRENT_GROUP, db.Subject.week == CURRENT_WEEK, db.Subject.year == CURRENT_YEAR)
        db_subject: list[db.Subject] = db.Subject.select().where(db.Subject.group == CURRENT_GROUP, db.Subject.week == CURRENT_WEEK, db.Subject.year == CURRENT_YEAR)
    else:
        ANOTHER_GROUP_TIME_TABLE = []
        db_subject: list[db.Subject] = db.Subject.select().where(db.Subject.group == CURRENT_GROUP, db.Subject.week == 1, db.Subject.year == 1)
    for subject in db_subject:
        TIME_TABLE['DAYS'][str(subject.day)].append(subject)
        TIME_TABLE['DAYS'][str(subject.day)].sort(key=lambda x: x.subject_num)
        for i, v in enumerate(TIME_TABLE['DAYS'][str(subject.day)]):
            v.subject_num = i
    updateLists()


def saveTimeTable():
    global TIME_TABLE, ANOTHER_GROUP_TIME_TABLE
    global GROUP_LIST, AUDIENCE_LIST, TEACHER_LIST, SUBJECT_LIST
    for k in TIME_TABLE['DAYS'].values():
        for v in k:
            if len(v.subject) > 0 and v.subject not in SUBJECT_LIST:
                SUBJECT_LIST.append(v.subject)
            if len(v.audience) > 0 and v.audience not in AUDIENCE_LIST:
                AUDIENCE_LIST.append(v.audience)
            if len(v.teacher) > 0 and v.teacher not in TEACHER_LIST:
                TEACHER_LIST.append(v.teacher)
            v.save()
    for AUDIENCE in AUDIENCE_LIST:
        db_Audience, _ = db.Audience.get_or_create(name=AUDIENCE)
        db_Audience.save()
    for SUBJECT in SUBJECT_LIST:
        if (len(SUBJECT) > 0 and SUBJECT[:18] != "Разговор о важном/") or (len(SUBJECT[18:]) > 0):
            if SUBJECT[:18] != "Разговор о важном/":
                db_lesson, _ = db.Lesson.get_or_create(name=SUBJECT)
            else:
                db_lesson, _ = db.Lesson.get_or_create(name=SUBJECT[18:])
            db_lesson.save()
    for TEACHER in TEACHER_LIST:
        db_teacher, _ = db.Teacher.get_or_create(name=TEACHER)
        db_teacher.save()
    updateLists()


def clearTimeTable():
    global TIME_TABLE, ANOTHER_GROUP_TIME_TABLE
    for k in TIME_TABLE['DAYS'].values():
        for v in k:
            v.delete_instance()


def updateLists():
    global GROUP_LIST, AUDIENCE_LIST, TEACHER_LIST, SUBJECT_LIST, ANOTHER_GROUP_TIME_TABLE, TIME_TABLE, ASSOCIATED
    GROUP_LIST = ["Шаблон"]
    AUDIENCE_LIST = []
    TEACHER_LIST = []
    SUBJECT_LIST = []
    for x in db.Group.select():
        if len(x.name) > 0 and x.name not in GROUP_LIST:
            GROUP_LIST.append(x.name)

    for x in db.Teacher.select():
        if len(x.name) > 0 and x.name not in TEACHER_LIST:
            TEACHER_LIST.append(x.name)

    for x in db.Lesson.select():
        if len(x.name) > 0 and x.name not in SUBJECT_LIST:
            SUBJECT_LIST.append(x.name)

    for x in db.Audience.select():
        if len(x.name) > 0 and x.name not in AUDIENCE_LIST:
            AUDIENCE_LIST.append(x.name)

    if len(ASSOCIATED['last_teacher']) > 0:
        ASSOCIATED['associated_subjects'] = [x.subject for x in db.AssociatedLesson.select().where(db.AssociatedLesson.teacher == ASSOCIATED['last_teacher'])]

    if len(ASSOCIATED['last_subject']) > 0:
        ASSOCIATED['associated_teachers'] = [x.teacher for x in db.AssociatedLesson.select().where(db.AssociatedLesson.subject == ASSOCIATED['last_subject'])]


def POPUP_restoreTable():
    global CURRENT_GROUP, CURRENT_WEEK, CURRENT_YEAR

    imgui.text(f"Вы действительно хотите УДАЛИТЬ текущее расписание недели для группы '{CURRENT_GROUP}' и скопировать ШАБЛОН?")
    imgui.text_colored("Отменить данное действие невозможно", 1, 0.45, 0.45)
    imgui.push_style_color(imgui.COLOR_BUTTON, 0.71, 0.46, 0.46)
    imgui.push_style_color(imgui.COLOR_BUTTON_HOVERED, 0.77, 0.5, 0.5)
    imgui.push_style_color(imgui.COLOR_BUTTON_ACTIVE, 0.61, 0.4, 0.4)
    if imgui.button(ICON_FA.ICON_ERASER + " Да##accept_copy_timetable", imgui.get_window_width() // 2 - 10):
        clearTimeTable()
        db_subject_example: list[db.Subject] = db.Subject.select().where(db.Subject.group == 'Шаблон', db.Subject.week == 1, db.Subject.year == 1)
        for subject in db_subject_example:
            subject.id = None
            subject.group = CURRENT_GROUP
            subject.week = CURRENT_WEEK
            subject.year = CURRENT_YEAR
            subject.save()
        updateTimeTable()
        imgui.close_current_popup()
    imgui.pop_style_color(3)
    imgui.same_line()
    if imgui.button(ICON_FA.ICON_XMARK + " Отмена##decline_copy_timetable", imgui.get_window_width() // 2 - 10):
        imgui.close_current_popup()


def POPUP_addGroups():
    global MULTILINE_ADD_GROUPS, TIME_TABLE
    global CURRENT_GROUP, CURRENT_WEEK, CURRENT_YEAR
    imgui.push_style_var(imgui.STYLE_WINDOW_ROUNDING, 8)
    with imgui.begin_popup_modal(ICON_FA.ICON_PLUS + " Добавить группы", flags=imgui.WINDOW_NO_RESIZE) as popup_modal:
        if popup_modal.opened:
            imgui.push_item_width(300)
            imgui.text("Каждая группа с новой строки")
            _, MULTILINE_ADD_GROUPS = imgui.input_text_multiline("##ADD_GROUPS_MULTILINE", MULTILINE_ADD_GROUPS)
            if imgui.button(ICON_FA.ICON_PLUS + " Добавить##add_groups_modal", imgui.get_window_width() // 2 - 10):
                for group_name in MULTILINE_ADD_GROUPS.split("\n"):
                    str_strip = group_name.strip().rstrip()
                    if len(str_strip) > 0 and str_strip != 'Шаблон':
                        db_group, created = db.Group.get_or_create(name=str_strip)
                        db_group.save()
                    updateLists()
                imgui.close_current_popup()
                MULTILINE_ADD_GROUPS = ""
            imgui.same_line()
            if imgui.button(ICON_FA.ICON_XMARK + " Отмена##add_groups_modal", imgui.get_window_width() // 2 - 10):
                imgui.close_current_popup()
            imgui.pop_item_width()
    imgui.pop_style_var(1)


def POPUP_addTeachers():
    global MULTILINE_ADD_GROUPS, TIME_TABLE
    global CURRENT_GROUP, CURRENT_WEEK, CURRENT_YEAR
    imgui.push_style_var(imgui.STYLE_WINDOW_ROUNDING, 8)
    with imgui.begin_popup_modal(ICON_FA.ICON_PLUS + " Добавить преподавателей", flags=imgui.WINDOW_NO_RESIZE) as popup_modal:
        if popup_modal.opened:
            imgui.push_item_width(300)
            imgui.text("Каждый преподаватель с новой строки")
            _, MULTILINE_ADD_GROUPS = imgui.input_text_multiline("##ADD_TEACHER_MULTILINE", MULTILINE_ADD_GROUPS)
            if imgui.button(ICON_FA.ICON_PLUS + " Добавить##add_teacher_modal", imgui.get_window_width() // 2 - 10):
                for group_name in MULTILINE_ADD_GROUPS.split("\n"):
                    str_strip = group_name.strip().rstrip()
                    if len(str_strip) > 0:
                        db_teacher, created = db.Teacher.get_or_create(name=str_strip)
                        db_teacher.save()
                    updateLists()
                imgui.close_current_popup()
                MULTILINE_ADD_GROUPS = ""
            imgui.same_line()
            if imgui.button(ICON_FA.ICON_XMARK + " Отмена##add_teacher_modal", imgui.get_window_width() // 2 - 10):
                imgui.close_current_popup()
            imgui.pop_item_width()
    imgui.pop_style_var(1)


def POPUP_addAudiences():
    global MULTILINE_ADD_GROUPS, TIME_TABLE
    global CURRENT_GROUP, CURRENT_WEEK, CURRENT_YEAR
    imgui.push_style_var(imgui.STYLE_WINDOW_ROUNDING, 8)
    with imgui.begin_popup_modal(ICON_FA.ICON_PLUS + " Добавить аудитории", flags=imgui.WINDOW_NO_RESIZE) as popup_modal:
        if popup_modal.opened:
            imgui.push_item_width(300)
            imgui.text("Каждая аудитория с новой строки")
            _, MULTILINE_ADD_GROUPS = imgui.input_text_multiline("##ADD_AUDIENCES_MULTILINE", MULTILINE_ADD_GROUPS)
            if imgui.button(ICON_FA.ICON_PLUS + " Добавить##add_audiences_modal", imgui.get_window_width() // 2 - 10):
                for group_name in MULTILINE_ADD_GROUPS.split("\n"):
                    str_strip = group_name.strip().rstrip()
                    if len(str_strip) > 0:
                        db_audience, created = db.Audience.get_or_create(name=str_strip)
                        db_audience.save()
                    updateLists()
                imgui.close_current_popup()
                MULTILINE_ADD_GROUPS = ""
            imgui.same_line()
            if imgui.button(ICON_FA.ICON_XMARK + " Отмена##add_audiences_modal", imgui.get_window_width() // 2 - 10):
                imgui.close_current_popup()
            imgui.pop_item_width()
    imgui.pop_style_var(1)


def POPUP_associatedTeacher():
    global ASSOCIATED, TEACHER_LIST, SUBJECT_LIST, SEARCH_TEACHER_ASSOC
    imgui.push_style_var(imgui.STYLE_WINDOW_ROUNDING, 8)
    with imgui.begin_popup(ICON_FA.ICON_PLUS + " Преподаватели дисциплины", flags=imgui.WINDOW_NO_RESIZE) as popup_modal:
        if popup_modal.opened:
            imgui.push_item_width(275)
            imgui.text(f"Преподаватели '{ASSOCIATED['last_subject']}'")
            _, SEARCH_TEACHER_ASSOC = imgui.input_text(ICON_FA.ICON_MAGNIFYING_GLASS + "##SEARCH_TEACHER_ASSOCIATED", SEARCH_TEACHER_ASSOC)
            imgui.separator()
            with imgui.begin_child("SEARCH_TEACHER_ASSOCIATED", 300, 300, border=True):
                imgui.push_style_color(imgui.COLOR_BUTTON, 0.27, 0.46, 0.27)
                imgui.push_style_color(imgui.COLOR_BUTTON_ACTIVE, 0.24, 0.43, 0.24)
                imgui.push_style_color(imgui.COLOR_BUTTON_HOVERED, 0.31, 0.5, 0.31)
                for k in ASSOCIATED['associated_teachers']:
                    if len(SEARCH_TEACHER_ASSOC) == 0 or k.lower().find(SEARCH_TEACHER_ASSOC.lower()) != -1:
                        if imgui.button(k + "##DELETE_ASSOCIATED_BUTTON", 275):
                            db_assoc_lesson = db.AssociatedLesson.get(db.AssociatedLesson.teacher == k, db.AssociatedLesson.subject == ASSOCIATED['last_subject'])
                            db_assoc_lesson.delete_instance()
                            updateLists()
                imgui.pop_style_color(3)
                imgui.separator()
                for k in TEACHER_LIST:
                    if k not in ASSOCIATED['associated_teachers']:
                        if len(SEARCH_TEACHER_ASSOC) == 0 or k.lower().find(SEARCH_TEACHER_ASSOC.lower()) != -1:
                            if imgui.button(k + "##ADD_ASSOCIATED_BUTTON", 275):
                                db_assoc_lesson, _ = db.AssociatedLesson.get_or_create(teacher=k, subject=ASSOCIATED['last_subject'])
                                db_assoc_lesson.save()
                                updateLists()
    imgui.pop_style_var(1)


def POPUP_associatedLessons():
    global ASSOCIATED, TEACHER_LIST, SUBJECT_LIST, SEARCH_SUBJECT_ASSOC
    imgui.push_style_var(imgui.STYLE_WINDOW_ROUNDING, 8)
    with imgui.begin_popup(ICON_FA.ICON_PLUS + " Дисциплины преподаваталей", flags=imgui.WINDOW_NO_RESIZE) as popup_modal:
        if popup_modal.opened:
            imgui.push_item_width(275)
            imgui.text(f"Дисциплины '{ASSOCIATED['last_teacher']}'")
            _, SEARCH_SUBJECT_ASSOC = imgui.input_text(ICON_FA.ICON_MAGNIFYING_GLASS + "##SEARCH_SUBJECT_ASSOCIATED", SEARCH_SUBJECT_ASSOC)
            imgui.separator()
            with imgui.begin_child("SEARCH_SUBJECT_ASSOCIATED", 300, 300, border=True):
                imgui.push_style_color(imgui.COLOR_BUTTON, 0.27, 0.46, 0.27)
                imgui.push_style_color(imgui.COLOR_BUTTON_ACTIVE, 0.24, 0.43, 0.24)
                imgui.push_style_color(imgui.COLOR_BUTTON_HOVERED, 0.31, 0.5, 0.31)
                for k in ASSOCIATED['associated_subjects']:
                    if len(SEARCH_SUBJECT_ASSOC) == 0 or k.lower().find(SEARCH_SUBJECT_ASSOC.lower()) != -1:
                        if imgui.button(k + "##DELETE_ASSOCIATED_BUTTON", 275):
                            db_assoc_lesson = db.AssociatedLesson.get(db.AssociatedLesson.subject == k, db.AssociatedLesson.teacher == ASSOCIATED['last_teacher'])
                            db_assoc_lesson.delete_instance()
                            updateLists()
                imgui.pop_style_color(3)
                imgui.separator()
                for k in SUBJECT_LIST:
                    if k not in ASSOCIATED['associated_subjects']:
                        if len(SEARCH_SUBJECT_ASSOC) == 0 or k.lower().find(SEARCH_SUBJECT_ASSOC.lower()) != -1:
                            if imgui.button(k + "##ADD_ASSOCIATED_BUTTON", 275):
                                db_assoc_lesson, _ = db.AssociatedLesson.get_or_create(subject=k, teacher=ASSOCIATED['last_teacher'])
                                db_assoc_lesson.save()
                                updateLists()
    imgui.pop_style_var(1)


def POPUP_addSubjects():
    global MULTILINE_ADD_GROUPS, TIME_TABLE
    global CURRENT_GROUP, CURRENT_WEEK, CURRENT_YEAR
    imgui.push_style_var(imgui.STYLE_WINDOW_ROUNDING, 8)
    with imgui.begin_popup_modal(ICON_FA.ICON_PLUS + " Добавить дисциплины", flags=imgui.WINDOW_NO_RESIZE) as popup_modal:
        if popup_modal.opened:
            imgui.push_item_width(300)
            imgui.text("Каждый предмет с новой строки")
            _, MULTILINE_ADD_GROUPS = imgui.input_text_multiline("##ADD_SUBJECTS_MULTILINE", MULTILINE_ADD_GROUPS)
            if imgui.button(ICON_FA.ICON_PLUS + " Добавить##add_subjects_modal", imgui.get_window_width() // 2 - 10):
                for group_name in MULTILINE_ADD_GROUPS.split("\n"):
                    str_strip = group_name.strip().rstrip()
                    if len(str_strip) > 0:
                        db_subject, created = db.Lesson.get_or_create(name=str_strip)
                        db_subject.save()
                    updateLists()
                imgui.close_current_popup()
                MULTILINE_ADD_GROUPS = ""
            imgui.same_line()
            if imgui.button(ICON_FA.ICON_XMARK + " Отмена##add_subjects_modal", imgui.get_window_width() // 2 - 10):
                imgui.close_current_popup()
            imgui.pop_item_width()
    imgui.pop_style_var(1)


def getTimeTable(groupname, week, year):
    timetable = {}
    for i in range(6):
        timetable.update({f"{i}": []})
    db_subject: list[db.Subject] = db.Subject.select().where(db.Subject.group == groupname, db.Subject.week == week, db.Subject.year == year)
    for subject in db_subject:
        timetable[str(subject.day)].append(subject)
        timetable[str(subject.day)].sort(key=lambda x: x.subject_num)
        for i, v in enumerate(timetable[str(subject.day)]):
            v.subject_num = i
    return timetable
