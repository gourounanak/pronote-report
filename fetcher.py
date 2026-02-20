"""
Fetches grades from Pronote for all children linked to a parent account.
"""

import datetime
import pronotepy
from dataclasses import dataclass


@dataclass
class GradeEntry:
    child_name: str
    subject: str
    grade: str
    out_of: str
    coefficient: str
    comment: str
    date: datetime.date
    period: str
    is_bonus: bool
    average: str = ""
    max: str = ""
    min: str = ""


@dataclass
class HomeworkEntry:
    child_name: str
    subject: str
    description: str
    due_date: datetime.date
    done: bool


@dataclass
class TimetableEntry:
    child_name: str
    subject: str
    teacher: str
    start_time: datetime.time
    end_time: datetime.time
    date: datetime.date
    room: str = ""


def fetch_grades(
    pronote_url: str,
    username: str,
    password: str,
    days: int = 14,
) -> dict[str, list[GradeEntry]]:
    """
    Log in as a parent and return grades per child for the last `days` days.

    Args:
        pronote_url: Full URL to the Pronote parent page
                     e.g. "https://YOUR_SCHOOL.index-education.net/pronote/parent.html"
        username: Pronote username
        password: Pronote password
        days: How many days back to look (default: 14)

    Returns:
        dict mapping child full name -> list of GradeEntry sorted by date desc
    """
    client = pronotepy.ParentClient(pronote_url, username=username, password=password)
    if not client.logged_in:
        raise RuntimeError("Pronote login failed — check URL, username, and password")

    cutoff = datetime.date.today() - datetime.timedelta(days=days)
    results: dict[str, list[GradeEntry]] = {}

    for child in client.children:
        client.set_child(child)
        child_name = child.name

        grades: list[GradeEntry] = []
        for period in client.periods:
            for g in period.grades:
                if g.date < cutoff:
                    continue
                grades.append(
                    GradeEntry(
                        child_name=child_name,
                        subject=g.subject.name if g.subject else "—",
                        grade=g.grade,
                        out_of=g.out_of,
                        coefficient=g.coefficient,
                        comment=g.comment or "",
                        date=g.date,
                        period=period.name,
                        is_bonus=g.is_bonus,
                        average=g.average,
                        max=g.max,
                        min=g.min,
                    )
                )

        grades.sort(key=lambda x: x.date, reverse=True)
        results[child_name] = grades

    return results


def fetch_homeworks(
    pronote_url: str,
    username: str,
    password: str,
    days: int = 7,
) -> dict[str, list[HomeworkEntry]]:
    """
    Log in as a parent and return homeworks per child for the next `days` days.

    Args:
        pronote_url: Full URL to the Pronote parent page
        username: Pronote username
        password: Pronote password
        days: How many days ahead to look (default: 7)

    Returns:
        dict mapping child full name -> list of HomeworkEntry sorted by due_date
    """
    client = pronotepy.ParentClient(pronote_url, username=username, password=password)
    if not client.logged_in:
        raise RuntimeError("Pronote login failed — check URL, username, and password")

    today = datetime.date.today()
    cutoff = today + datetime.timedelta(days=days)
    results: dict[str, list[HomeworkEntry]] = {}

    for child in client.children:
        client.set_child(child)
        child_name = child.name

        homeworks: list[HomeworkEntry] = []
        # Try to get homeworks - homework() requires date_from parameter
        try:
            if callable(client.homework):
                hw_list = list(client.homework(date_from=today))
                for hw in hw_list:
                    try:
                        # Homework object uses 'date' for due date
                        due_date = hw.date
                        if due_date is None or due_date < today or due_date > cutoff:
                            continue
                        homeworks.append(
                            HomeworkEntry(
                                child_name=child_name,
                                subject=hw.subject.name if hw.subject else "—",
                                description=hw.description or "",
                                due_date=due_date,
                                done=hw.done,
                            )
                        )
                    except Exception:
                        pass
        except Exception:
            pass  # Silently fail if homework is not available

        homeworks.sort(key=lambda x: x.due_date)
        results[child_name] = homeworks

    return results


def fetch_timetable(
    pronote_url: str,
    username: str,
    password: str,
    days: int = 7,
) -> dict[str, list[TimetableEntry]]:
    """
    Log in as a parent and return timetable per child for the next `days` days.

    Args:
        pronote_url: Full URL to the Pronote parent page
        username: Pronote username
        password: Pronote password
        days: How many days ahead to look (default: 7)

    Returns:
        dict mapping child full name -> list of TimetableEntry sorted by date and time
    """
    client = pronotepy.ParentClient(pronote_url, username=username, password=password)
    if not client.logged_in:
        raise RuntimeError("Pronote login failed — check URL, username, and password")

    today = datetime.date.today()
    cutoff = today + datetime.timedelta(days=days)
    results: dict[str, list[TimetableEntry]] = {}

    for child in client.children:
        client.set_child(child)
        child_name = child.name

        timetable: list[TimetableEntry] = []
        # Try to get timetable - lessons() requires date_from parameter
        try:
            if callable(client.lessons):
                lessons_list = list(client.lessons(date_from=today))
                for lesson in lessons_list:
                    try:
                        if lesson.start is None or lesson.start.date() < today or lesson.start.date() > cutoff:
                            continue
                        # Lesson object may not have teacher attribute
                        teacher_name = ""
                        timetable.append(
                            TimetableEntry(
                                child_name=child_name,
                                subject=lesson.subject.name if lesson.subject else "—",
                                teacher=teacher_name,
                                start_time=lesson.start.time(),
                                end_time=lesson.end.time(),
                                date=lesson.start.date(),
                                room=lesson.classroom or "",
                            )
                        )
                    except Exception:
                        pass
        except Exception:
            pass  # Silently fail if timetable is not available

        timetable.sort(key=lambda x: (x.date, x.start_time))
        results[child_name] = timetable

    return results
