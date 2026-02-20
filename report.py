"""
Formats the grades data into a plain-text and HTML email report.
"""

import datetime
from html import escape

from fetcher import GradeEntry, HomeworkEntry, TimetableEntry

_WEEKDAYS_FR = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]


def _fmt_date(d: datetime.date) -> str:
    return f"{_WEEKDAYS_FR[d.weekday()]} {d.day:02d}/{d.month:02d}"


def _fmt_date_whatsapp(d: datetime.date) -> str:
    """Format date for WhatsApp without day abbreviation."""
    return f"{d.day:02d}/{d.month:02d}"


def _grade_line(g: GradeEntry) -> str:
    bonus_tag = " [BONUS]" if g.is_bonus else ""
    comment = f" — {g.comment}" if g.comment else ""
    coeff = f" (coeff {g.coefficient})" if g.coefficient and g.coefficient != "1" else ""
    return (
        f"  {_fmt_date(g.date)}  {g.subject:<25} {g.grade}/{g.out_of}{coeff}{bonus_tag}{comment}"
    )


def _grade_line_whatsapp(g: GradeEntry) -> str:
    """Format grade line for WhatsApp with subject at start, no day abbreviation, and colon separator."""
    bonus_tag = " [BONUS]" if g.is_bonus else ""
    comment = f" — {g.comment}" if g.comment else ""
    coeff = f" (coeff {g.coefficient})" if g.coefficient and g.coefficient != "1" else ""
    return (
        f"{g.subject:<25} {_fmt_date_whatsapp(g.date)}: {g.grade}/{g.out_of}{coeff}{bonus_tag}{comment}"
    )


def build_text_report(
    grades_by_child: dict[str, list[GradeEntry]],
    homeworks_by_child: dict[str, list[HomeworkEntry]] | None = None,
    timetable_by_child: dict[str, list[TimetableEntry]] | None = None,
    days: int = 14,
) -> str:
    today = datetime.date.today()
    lines = [
        "Rapport Pronote",
        f"Du {_fmt_date(today - datetime.timedelta(days=days))} au {_fmt_date(today)}",
        "=" * 60,
    ]

    for child_name, grades in grades_by_child.items():
        lines.append(f"\n{'─' * 60}")
        lines.append(f"  {child_name}")
        lines.append(f"{'─' * 60}")

        # Add timetable first
        if timetable_by_child and child_name in timetable_by_child:
            timetable = timetable_by_child[child_name]
            if timetable:
                lines.append("\n  EMPLOI DU TEMPS")
                current_date = None
                for lesson in timetable:
                    if lesson.date != current_date:
                        current_date = lesson.date
                        lines.append(f"\n    {_fmt_date(lesson.date)}")
                    time_str = f"{lesson.start_time.strftime('%H:%M')}-{lesson.end_time.strftime('%H:%M')}"
                    room_str = f" ({lesson.room})" if lesson.room else ""
                    lines.append(f"      {time_str:<11} {lesson.subject:<25}{room_str}")

        # Add homeworks second
        if homeworks_by_child and child_name in homeworks_by_child:
            homeworks = homeworks_by_child[child_name]
            if homeworks:
                lines.append("\n  DEVOIRS")
                for hw in homeworks:
                    status = "✓" if hw.done else "○"
                    lines.append(f"    {status} {hw.subject:<25} {_fmt_date(hw.due_date)}")
                    if hw.description:
                        lines.append(f"       {hw.description}")

        # Add grades last
        if not grades:
            lines.append("\n  NOTES")
            lines.append("  Aucune note sur la période.")
        else:
            lines.append("\n  NOTES")
            # Group by subject for a cleaner read
            by_subject: dict[str, list[GradeEntry]] = {}
            for g in grades:
                by_subject.setdefault(g.subject, []).append(g)

            for subject, sg in sorted(by_subject.items()):
                lines.append(f"\n    {subject}")
                for g in sg:
                    lines.append(_grade_line(g))

    lines.append(f"\n{'=' * 60}")
    lines.append(f"Généré le {today.strftime('%d/%m/%Y')}")
    return "\n".join(lines)


def build_whatsapp_report(
    grades_by_child: dict[str, list[GradeEntry]],
    days: int = 14,
) -> str:
    """Build a WhatsApp-friendly report with emoji and bold child names, no subject grouping."""
    today = datetime.date.today()
    lines = [
        "📊 Rapport de notes Pronote",
        f"Semaine du {_fmt_date_whatsapp(today - datetime.timedelta(days=days))} au {_fmt_date_whatsapp(today)}",
        "=" * 50,
    ]

    for child_name, grades in grades_by_child.items():
        lines.append(f"\n👧🏻 **{child_name}**")
        lines.append("─" * 30)

        if not grades:
            lines.append("  Aucune note sur la période.")
            continue

        # Sort grades by date (most recent first) without grouping by subject
        sorted_grades = sorted(grades, key=lambda g: g.date, reverse=True)

        for g in sorted_grades:
            lines.append(_grade_line_whatsapp(g))

    lines.append(f"\n{'=' * 50}")
    lines.append(f"Généré le {today.strftime('%d/%m/%Y')}")
    return "\n".join(lines)


# Color palette for timetable - various pastel colors for different subjects
_TIMETABLE_COLORS = [
    '#FFD6E7',  # Pink
    '#E7F3FF',  # Light blue
    '#E7FFE7',  # Light green
    '#FFFFE7',  # Light yellow
    '#FFE7D6',  # Light orange
    '#F0E7FF',  # Light purple
    '#E7FFFF',  # Cyan
    '#FFE7F3',  # Magenta
]

def _get_subject_color(subject: str, subject_index: int = 0) -> str:
    """Get a consistent color for a subject based on its name hash."""
    return _TIMETABLE_COLORS[hash(subject) % len(_TIMETABLE_COLORS)]


def build_html_report(
    grades_by_child: dict[str, list[GradeEntry]],
    homeworks_by_child: dict[str, list[HomeworkEntry]] | None = None,
    timetable_by_child: dict[str, list[TimetableEntry]] | None = None,
    days: int = 14,
) -> str:
    today = datetime.date.today()
    since = today - datetime.timedelta(days=days)

    children_html = ""
    for child_name, grades in grades_by_child.items():
        child_sections = ""

        # Timetable section FIRST
        if timetable_by_child and child_name in timetable_by_child:
            timetable = timetable_by_child[child_name]
            if timetable:
                child_sections += f"""
        <h3 style='margin:20px 0 16px;color:#2c3e50;font-size:18px'>📅 Emploi du temps</h3>"""
                
                # Group lessons by date
                lessons_by_date: dict[datetime.date, list[TimetableEntry]] = {}
                for lesson in timetable:
                    lessons_by_date.setdefault(lesson.date, []).append(lesson)
                
                if lessons_by_date:
                    sorted_dates = sorted(lessons_by_date.keys())
                    
                    # Display as simple list, grouped by date
                    for lesson_date in sorted_dates:
                        date_lessons = sorted(lessons_by_date[lesson_date], key=lambda x: x.start_time)
                        date_str = _fmt_date(lesson_date)
                        
                        child_sections += f"""
        <div style='margin-bottom:16px;border:1px solid #ddd;border-radius:4px;overflow:hidden;background:#f9f9f9'>
            <div style='background:#2c3e50;color:white;padding:10px 12px;font-weight:600'>{date_str}</div>
            <div style='padding:8px 12px'>"""
                        
                        for lesson in date_lessons:
                            time_str = f"{lesson.start_time.strftime('%H:%M')} - {lesson.end_time.strftime('%H:%M')}"
                            esc_subject = escape(lesson.subject)
                            room_str = f" • {escape(lesson.room)}" if lesson.room else ""
                            color = _get_subject_color(lesson.subject)
                            
                            child_sections += f"""
                <div style='padding:8px;margin-bottom:6px;background:{color};border-left:4px solid #666;border-radius:2px'>
                    <strong>{esc_subject}</strong>{room_str}
                    <div style='font-size:12px;color:#666;margin-top:2px'>{time_str}</div>
                </div>"""
                        
                        child_sections += """
            </div>
        </div>"""

        # Homeworks section SECOND
        if homeworks_by_child and child_name in homeworks_by_child:
            homeworks = homeworks_by_child[child_name]
            if homeworks:
                hw_rows = ""
                for hw in homeworks:
                    status_icon = "✓" if hw.done else "⭕"
                    status_color = "#27ae60" if hw.done else "#e74c3c"
                    status_bg = "#f0f8f0" if hw.done else "#fff5f5"
                    esc_subject = escape(hw.subject)
                    esc_desc = escape(hw.description) if hw.description else ""
                    desc_row = f"<tr style='background:#fafafa'><td colspan='3' style='padding:6px 12px;border-bottom:1px solid #f0f0f0;color:#666;font-size:12px'><em>{esc_desc}</em></td></tr>" if esc_desc else ""
                    hw_rows += f"""
                <tr style='background:{status_bg};border-bottom:1px solid #f0f0f0'>
                    <td style='padding:8px 12px;color:{status_color};font-weight:bold;width:30px;text-align:center'>{status_icon}</td>
                    <td style='padding:8px 12px'>{esc_subject}</td>
                    <td style='padding:8px 12px;text-align:right'>{_fmt_date(hw.due_date)}</td>
                </tr>{desc_row}"""

                child_sections += f"""
        <h3 style='margin:20px 0 16px;color:#2c3e50;font-size:18px'>📝 Devoirs</h3>
        <table style='width:100%;border-collapse:collapse;font-size:14px;border:1px solid #ddd;border-radius:4px;overflow:hidden'>
            <thead>
                <tr style='background:#34495e;color:white'>
                    <th style='padding:10px 12px;font-weight:600;text-align:center;width:40px'></th>
                    <th style='padding:10px 12px;font-weight:600;text-align:left'>Matière</th>
                    <th style='padding:10px 12px;font-weight:600;text-align:right'>À faire pour le</th>
                </tr>
            </thead>
            <tbody>{hw_rows}</tbody>
        </table>"""

        # Grades section LAST
        if not grades:
            grades_block = "<p style='color:#888'>Aucune note sur la période.</p>"
        else:
            by_subject: dict[str, list[GradeEntry]] = {}
            for g in grades:
                by_subject.setdefault(g.subject, []).append(g)

            rows = ""
            for subject, sg in sorted(by_subject.items()):
                first = True
                for g in sg:
                    esc_subject = escape(subject)
                    esc_grade = escape(g.grade)
                    esc_out_of = escape(g.out_of)
                    bonus = " <span style='color:#e67e22;font-size:11px'>[BONUS]</span>" if g.is_bonus else ""
                    coeff = f"<br><small style='color:#888'>coeff {escape(g.coefficient)}</small>" if g.coefficient and g.coefficient != "1" else ""
                    comment = f"<br><small style='color:#888;font-style:italic'>{escape(g.comment)}</small>" if g.comment else ""
                    rows += f"""
                <tr style='border-bottom:1px solid #f0f0f0'>
                    <td style='padding:8px 12px;color:#555'>{'<b>' + esc_subject + '</b>' if first else ''}</td>
                    <td style='padding:8px 12px'>{_fmt_date(g.date)}</td>
                    <td style='padding:8px 12px;text-align:center;font-weight:bold'>{esc_grade}/{esc_out_of}{bonus}{coeff}</td>
                    <td style='padding:8px 12px;color:#666'>{comment}</td>
                </tr>"""
                    first = False

            grades_block = f"""
            <table style='width:100%;border-collapse:collapse;font-size:14px;border:1px solid #ddd;border-radius:4px;overflow:hidden'>
                <thead>
                    <tr style='background:#34495e;color:white'>
                        <th style='padding:10px 12px;font-weight:600;text-align:left'>Matière</th>
                        <th style='padding:10px 12px;font-weight:600;text-align:left'>Date</th>
                        <th style='padding:10px 12px;font-weight:600;text-align:center'>Note</th>
                        <th style='padding:10px 12px;font-weight:600;text-align:left'>Commentaire</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>"""

        child_sections += f"""
        <h3 style='margin:20px 0 16px;color:#2c3e50;font-size:18px'>📊 Notes</h3>
        {grades_block}"""

        children_html += f"""
        <div style='margin-bottom:32px'>
            <h2 style='margin:0 0 12px;color:#2c3e50;border-left:4px solid #3498db;padding-left:10px'>{escape(child_name)}</h2>
            {child_sections}
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="fr">
<head><meta charset="UTF-8"></head>
<body style='font-family:Arial,sans-serif;color:#333;max-width:900px;margin:auto;padding:20px;background:#f9f9f9'>
    <h1 style='color:#2c3e50;border-bottom:3px solid #3498db;padding-bottom:10px'>📚 Rapport Pronote</h1>
    <p style='color:#888;margin-top:0'>Du {since.strftime('%d/%m/%Y')} au {today.strftime('%d/%m/%Y')}</p>
    <hr style='border:none;border-top:2px solid #eee;margin:20px 0'>
    {children_html}
    <hr style='border:none;border-top:1px solid #eee;margin:20px 0'>
    <p style='color:#aaa;font-size:12px'>Rapport généré automatiquement le {today.strftime('%d/%m/%Y')}</p>
</body>
</html>"""
