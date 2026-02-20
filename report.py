"""
Formats the grades data into a plain-text and HTML email report.
"""

import datetime
from html import escape

from fetcher import GradeEntry

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
    days: int = 14,
) -> str:
    today = datetime.date.today()
    lines = [
        "Rapport de notes Pronote",
        f"Semaine du {_fmt_date(today - datetime.timedelta(days=days))} au {_fmt_date(today)}",
        "=" * 60,
    ]

    for child_name, grades in grades_by_child.items():
        lines.append(f"\n{'─' * 60}")
        lines.append(f"  {child_name}")
        lines.append(f"{'─' * 60}")

        if not grades:
            lines.append("  Aucune note sur la période.")
            continue

        # Group by subject for a cleaner read
        by_subject: dict[str, list[GradeEntry]] = {}
        for g in grades:
            by_subject.setdefault(g.subject, []).append(g)

        for subject, sg in sorted(by_subject.items()):
            lines.append(f"\n  {subject}")
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


def build_html_report(
    grades_by_child: dict[str, list[GradeEntry]],
    days: int = 14,
) -> str:
    today = datetime.date.today()
    since = today - datetime.timedelta(days=days)

    children_html = ""
    for child_name, grades in grades_by_child.items():
        if not grades:
            child_block = "<p style='color:#888'>Aucune note sur la période.</p>"
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
                    <tr>
                        <td style='padding:6px 12px;color:#555;border-bottom:1px solid #f0f0f0'>{'<b>' + esc_subject + '</b>' if first else ''}</td>
                        <td style='padding:6px 12px;border-bottom:1px solid #f0f0f0'>{_fmt_date(g.date)}</td>
                        <td style='padding:6px 12px;text-align:center;border-bottom:1px solid #f0f0f0;font-weight:bold'>{esc_grade}/{esc_out_of}{bonus}{coeff}</td>
                        <td style='padding:6px 12px;border-bottom:1px solid #f0f0f0;color:#666'>{comment}</td>
                    </tr>"""
                    first = False

            child_block = f"""
            <table style='width:100%;border-collapse:collapse;font-size:14px'>
                <thead>
                    <tr style='background:#f5f5f5;text-align:left'>
                        <th style='padding:8px 12px;font-weight:600'>Matière</th>
                        <th style='padding:8px 12px;font-weight:600'>Date</th>
                        <th style='padding:8px 12px;font-weight:600;text-align:center'>Note</th>
                        <th style='padding:8px 12px;font-weight:600'>Commentaire</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>"""

        children_html += f"""
        <div style='margin-bottom:32px'>
            <h2 style='margin:0 0 12px;color:#2c3e50;border-left:4px solid #3498db;padding-left:10px'>{escape(child_name)}</h2>
            {child_block}
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="fr">
<head><meta charset="UTF-8"></head>
<body style='font-family:Arial,sans-serif;color:#333;max-width:800px;margin:auto;padding:20px'>
    <h1 style='color:#2c3e50'>Notes Pronote</h1>
    <p style='color:#888'>Du {since.strftime('%d/%m/%Y')} au {today.strftime('%d/%m/%Y')}</p>
    <hr style='border:none;border-top:2px solid #eee;margin:20px 0'>
    {children_html}
    <hr style='border:none;border-top:1px solid #eee;margin:20px 0'>
    <p style='color:#aaa;font-size:12px'>Rapport généré automatiquement le {today.strftime('%d/%m/%Y')}</p>
</body>
</html>"""
