"""Render synthetic workbook screenshots for Patch Applications and Patch OS.

Reads tests/fixtures/patch_management_synthetic.json (synthetic data only, no live tenant)
and renders high-resolution PNG previews into docs/images/.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = REPO_ROOT / "tests" / "fixtures" / "patch_management_synthetic.json"
OUT_DIR = REPO_ROOT / "docs" / "images"


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNS.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def render_overview(data: dict, out_path: Path) -> None:
    width, height = 1280, 740
    img = Image.new("RGB", (width, height), "#0F172A")
    draw = ImageDraw.Draw(img)

    title_font = _load_font(26, bold=True)
    sub_font = _load_font(15)
    kpi_val_font = _load_font(38, bold=True)
    kpi_lbl_font = _load_font(14)
    sec_font = _load_font(18, bold=True)
    body_font = _load_font(14)

    # Header bar
    draw.rectangle([0, 0, width, 86], fill="#1E293B")
    draw.text((28, 18), "Essential Eight: Patch Applications & Patch Operating Systems", fill="#F8FAFC", font=title_font)
    draw.text(
        (28, 54),
        "Microsoft Sentinel Workbook Preview (Synthetic Fixture Data | Tenant: 00000000-0000-0000-0000-000000000000 | Target: ML2)",
        fill="#94A3B8",
        font=sub_font,
    )

    # Filter pills
    pills = [
        "TimeRange: Last 14 days",
        "DeviceGroup: All (4 groups)",
        "TargetML: ML2",
        "ExposureFilter: All",
    ]
    px = 28
    for pill in pills:
        pw = len(pill) * 8 + 26
        draw.rounded_rectangle([px, 104, px + pw, 134], radius=6, fill="#1E293B", outline="#334155")
        draw.text((px + 12, 111), pill, fill="#CBD5E1", font=body_font)
        px += pw + 12

    # KPI cards
    kpis = [
        ("Overdue Critical / Exploited (>48h)", str(data["summary_kpis"]["overdue_critical_exploited_48h"]), "#EF4444"),
        ("Overdue Core Apps (>14d)", str(data["summary_kpis"]["overdue_core_apps_14d"]), "#F59E0B"),
        ("Overdue Other Apps (ML2 >30d)", str(data["summary_kpis"]["overdue_other_apps_ml2_30d"]), "#F59E0B"),
        ("Overdue OS Patches (ML2)", str(data["summary_kpis"]["overdue_os_ml2"]), "#F59E0B"),
        ("Unsupported Software", str(data["summary_kpis"]["unsupported_software_instances"]), "#E11D48"),
        ("Unsupported OS Devices", str(data["summary_kpis"]["unsupported_os_devices"]), "#E11D48"),
    ]
    card_w = 192
    gap = 14
    for idx, (label, val, accent) in enumerate(kpis):
        x0 = 28 + idx * (card_w + gap)
        y0 = 152
        draw.rounded_rectangle([x0, y0, x0 + card_w, y0 + 118], radius=8, fill="#1E293B", outline="#334155")
        draw.rectangle([x0, y0, x0 + card_w, y0 + 5], fill=accent)
        draw.text((x0 + 16, y0 + 18), val, fill="#F8FAFC", font=kpi_val_font)
        # Wrap label cleanly onto two lines
        words = label.split()
        line1 = " ".join(words[:3])
        line2 = " ".join(words[3:])
        draw.text((x0 + 16, y0 + 70), line1, fill="#94A3B8", font=kpi_lbl_font)
        if line2:
            draw.text((x0 + 16, y0 + 89), line2, fill="#94A3B8", font=kpi_lbl_font)

    # Stacked horizontal bar chart: Vulnerability age distribution by device group
    chart_x0, chart_y0, chart_x1, chart_y1 = 28, 294, 770, 696
    draw.rounded_rectangle([chart_x0, chart_y0, chart_x1, chart_y1], radius=8, fill="#1E293B", outline="#334155")
    draw.text((chart_x0 + 20, chart_y0 + 18), "Vulnerability Age Distribution by Device Group", fill="#F8FAFC", font=sec_font)

    legend = [
        ("0-48h", "#22C55E"),
        ("2-14d", "#3B82F6"),
        ("15-30d", "#F59E0B"),
        (">30d", "#EF4444"),
    ]
    lx = chart_x0 + 20
    for name, colour in legend:
        draw.rectangle([lx, chart_y0 + 52, lx + 14, chart_y0 + 66], fill=colour)
        draw.text((lx + 20, chart_y0 + 50), name, fill="#CBD5E1", font=body_font)
        lx += 95

    bar_y = chart_y0 + 96
    max_total = max(
        row["0_48h"] + row["2_14d"] + row["15_30d"] + row["gt_30d"]
        for row in data["age_distribution_by_group"]
    )
    bar_max_w = 500
    for row in data["age_distribution_by_group"]:
        draw.text((chart_x0 + 20, bar_y + 6), row["group"], fill="#E2E8F0", font=body_font)
        bx = chart_x0 + 210
        for key, colour in [("0_48h", "#22C55E"), ("2_14d", "#3B82F6"), ("15_30d", "#F59E0B"), ("gt_30d", "#EF4444")]:
            val = row[key]
            if val <= 0:
                continue
            seg_w = max(16, int((val / max_total) * bar_max_w))
            draw.rectangle([bx, bar_y, bx + seg_w, bar_y + 32], fill=colour)
            draw.text((bx + 4, bar_y + 8), str(val), fill="#0F172A", font=body_font)
            bx += seg_w + 2
        bar_y += 68

    # Right panel: Unsupported software and OS
    u_x0, u_y0, u_x1, u_y1 = 792, 294, 1252, 696
    draw.rounded_rectangle([u_x0, u_y0, u_x1, u_y1], radius=8, fill="#1E293B", outline="#334155")
    draw.text((u_x0 + 20, u_y0 + 18), "Unsupported Software & OS (ML1)", fill="#F8FAFC", font=sec_font)

    ry = u_y0 + 64
    draw.text((u_x0 + 20, ry), "Type", fill="#94A3B8", font=body_font)
    draw.text((u_x0 + 100, ry), "Product / OS", fill="#94A3B8", font=body_font)
    draw.text((u_x0 + 365, ry), "Devices", fill="#94A3B8", font=body_font)
    draw.line([u_x0 + 16, ry + 24, u_x1 - 16, ry + 24], fill="#334155")
    ry += 36
    for asset in data["unsupported_assets"]:
        badge_colour = "#DC2626" if asset["type"] == "OS" else "#D97706"
        draw.rounded_rectangle([u_x0 + 20, ry, u_x0 + 88, ry + 24], radius=4, fill=badge_colour)
        draw.text((u_x0 + 28, ry + 4), asset["type"], fill="#F8FAFC", font=body_font)
        draw.text((u_x0 + 100, ry + 4), asset["name"], fill="#E2E8F0", font=body_font)
        draw.text((u_x0 + 382, ry + 4), str(asset["devices"]), fill="#F8FAFC", font=body_font)
        draw.text((u_x0 + 100, ry + 26), f"Group: {asset['group']}", fill="#94A3B8", font=kpi_lbl_font)
        ry += 62

    draw.text(
        (28, 712),
        "Synthetic data preview generated from tests/fixtures/patch_management_synthetic.json. Not endorsed by ASD, ACSC or Microsoft.",
        fill="#64748B",
        font=kpi_lbl_font,
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)


def render_exploited(data: dict, out_path: Path) -> None:
    width, height = 1280, 500
    img = Image.new("RGB", (width, height), "#0F172A")
    draw = ImageDraw.Draw(img)

    title_font = _load_font(24, bold=True)
    sub_font = _load_font(14)
    head_font = _load_font(15, bold=True)
    body_font = _load_font(14)

    draw.rectangle([0, 0, width, 78], fill="#1E293B")
    draw.text((28, 16), "Exploited (CISA KEV / Vendor Exploited) & Critical Vulnerabilities (48h SLA)", fill="#F8FAFC", font=title_font)
    draw.text((28, 48), "Synthetic Fixture Data | ASD Essential Eight Maturity Model (November 2023)", fill="#94A3B8", font=sub_font)

    draw.rounded_rectangle([28, 98, width - 28, 444], radius=8, fill="#1E293B", outline="#334155")
    cols = [
        (46, "CVE ID"),
        (195, "Software / OS"),
        (430, "Severity"),
        (540, "Exploit Flag"),
        (710, "Age (Hours)"),
        (835, "Devices"),
        (930, "Device Group"),
        (1110, "48h SLA"),
    ]
    hy = 118
    for cx, title in cols:
        draw.text((cx, hy), title, fill="#94A3B8", font=head_font)
    draw.line([40, hy + 28, width - 40, hy + 28], fill="#334155")

    ry = hy + 46
    for row in data["exploited_vulnerabilities"]:
        breached = row["sla_status"].startswith("Breached")
        status_bg = "#991B1B" if breached else "#166534"
        draw.text((46, ry + 4), row["cve_id"], fill="#38BDF8", font=body_font)
        draw.text((195, ry + 4), row["software"], fill="#F8FAFC", font=body_font)
        draw.text((430, ry + 4), row["severity"], fill="#FCA5A5" if row["severity"] == "Critical" else "#FCD34D", font=body_font)
        draw.text((540, ry + 4), row["tag"], fill="#E2E8F0", font=body_font)
        draw.text((710, ry + 4), f"{row['age_hours']}h", fill="#F8FAFC", font=body_font)
        draw.text((835, ry + 4), str(row["affected_devices"]), fill="#F8FAFC", font=body_font)
        draw.text((930, ry + 4), row["device_group"], fill="#CBD5E1", font=body_font)
        draw.rounded_rectangle([1104, ry, 1236, ry + 26], radius=4, fill=status_bg)
        draw.text((1114, ry + 5), row["sla_status"], fill="#F8FAFC", font=body_font)
        draw.line([40, ry + 44, width - 40, ry + 44], fill="#273449")
        ry += 62

    draw.text(
        (28, 466),
        "Synthetic data preview generated from tests/fixtures/patch_management_synthetic.json. No live tenant data used.",
        fill="#64748B",
        font=sub_font,
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)


def main() -> int:
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    render_overview(data, OUT_DIR / "patch-management-overview.png")
    render_exploited(data, OUT_DIR / "patch-management-exploited.png")
    print("Rendered synthetic screenshots in docs/images/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
