import db


def clearExample():
    db_subject: list[db.Subject] = db.Subject.select().where(db.Subject.group == 'Шаблон')
    for k in db_subject:
        k.delete_instance()


def fillExample():
    default_time_monday = [
        "08:30 - 08:45",
        "08:45 - 10:00",
        "10:10 - 11:40",
        "12:10 - 13:40",
        "13:50 - 15:20",
        "15:30 - 17:00"
    ]
    for day in range(6):
        for subj_num in range(6):
            db_subj = db.Subject(group='Шаблон', year=1, week=1, day=day, subject_num=subj_num)
            db_subj.audience = ""
            db_subj.teacher = ""
            db_subj.subject = ""
            if day == 0:
                db_subj.time = default_time_monday[subj_num]
            else:
                if subj_num == 0:
                    continue
                elif subj_num == 1:
                    db_subj.time = "08:30 - 10:00"
                elif subj_num > 1:
                    db_subj.time = default_time_monday[subj_num]
                db_subj.subject_num -= 1
            db_subj.save()


if __name__ == "__main__":
    clearExample()
    fillExample()