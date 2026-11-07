"""
Sentinel AI — Upgraded PowerPoint Presentation Generator v2
13 Slides with:
  - Gradient accent bars and decorative geometry
  - Embedded Recharts-style bar / pie charts via python-pptx ChartData
  - Flow-diagram arrows for architecture slide
  - Team profile-card boxes with accent rings
  - Table of Contents slide
  - Consistent visual icon glyphs via Unicode in shape text
  - Progress dot navigation strip on every slide
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.oxml.ns import qn
from pptx.chart.data import ChartData, CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.util import Pt
from lxml import etree
import copy, random

# ── Palette ──────────────────────────────────────────────────────────────────
BG       = RGBColor(0x09, 0x11, 0x27)   # #091127 – deepest navy
CARD     = RGBColor(0x0F, 0x1D, 0x3A)   # #0F1D3A – card surface
CARD2    = RGBColor(0x13, 0x28, 0x4F)   # #13284F – raised card
BORDER   = RGBColor(0x1E, 0x3A, 0x6E)   # #1E3A6E – card border
CYAN     = RGBColor(0x00, 0xE5, 0xFF)   # #00E5FF – primary accent
BLUE     = RGBColor(0x4F, 0xAC, 0xFE)   # #4FACFE – secondary accent
GREEN    = RGBColor(0x00, 0xE6, 0x76)   # #00E676 – success/low risk
AMBER    = RGBColor(0xFF, 0xB1, 0x42)   # #FFB142 – review/warning
RED      = RGBColor(0xFF, 0x52, 0x52)   # #FF5252 – high risk/critical
PURPLE   = RGBColor(0xAB, 0x47, 0xBC)   # #AB47BC – accent purple
WHITE    = RGBColor(0xF0, 0xF4, 0xF8)   # #F0F4F8 – body text
MUTED    = RGBColor(0x9C, 0xAF, 0xC6)   # #9CAFC6 – secondary text
DIM      = RGBColor(0x55, 0x70, 0x8A)   # #55708A – tertiary text
DARK_BG  = RGBColor(0x07, 0x0E, 0x1E)   # #070E1E – darkest strip

W = Inches(13.333)
H = Inches(7.5)

prs = Presentation()
prs.slide_width  = W
prs.slide_height = H
BLANK = prs.slide_layouts[6]

# ── Helpers ───────────────────────────────────────────────────────────────────

def rgb_hex(c: RGBColor) -> str:
    return f"{c[0]:02X}{c[1]:02X}{c[2]:02X}"

def add_rect(slide, l, t, w, h, fill=CARD, line=BORDER, lw=Pt(1), radius=0.08):
    from pptx.enum.shapes import MSO_SHAPE
    s = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,
        l, t, w, h
    )
    s.fill.solid(); s.fill.fore_color.rgb = fill
    s.line.color.rgb = line
    if lw: s.line.width = lw
    else:  s.line.fill.background()
    if radius:
        s.adjustments[0] = radius
    return s

def add_box(slide, l, t, w, h, fill=BG, line_color=None, lw=0):
    from pptx.enum.shapes import MSO_SHAPE
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, l, t, w, h)
    s.fill.solid(); s.fill.fore_color.rgb = fill
    if line_color: s.line.color.rgb = line_color; s.line.width = lw or Pt(1)
    else: s.line.fill.background()
    return s

def add_text(slide, text, l, t, w, h,
             size=14, bold=False, color=WHITE,
             align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP,
             wrap=True, italic=False):
    tb = slide.shapes.add_textbox(l, t, w, h)
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = valign
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = "Calibri"
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return tb

def add_para(tf, text, size=12, bold=False, color=WHITE, align=PP_ALIGN.LEFT,
             space_before=0, space_after=4, italic=False):
    p = tf.add_paragraph()
    p.alignment = align
    p.space_before = Pt(space_before)
    p.space_after  = Pt(space_after)
    run = p.add_run()
    run.text = text
    run.font.name = "Calibri"
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return p

def add_circle(slide, cx, cy, r, fill=CYAN, line=None):
    from pptx.enum.shapes import MSO_SHAPE
    s = slide.shapes.add_shape(MSO_SHAPE.OVAL,
        cx - r, cy - r, r*2, r*2)
    s.fill.solid(); s.fill.fore_color.rgb = fill
    if line: s.line.color.rgb = line; s.line.width = Pt(1.5)
    else: s.line.fill.background()
    return s

def add_line(slide, x1, y1, x2, y2, color=BORDER, w=Pt(1)):
    from pptx.util import Emu
    connector = slide.shapes.add_connector(
        1,  # straight connector
        x1, y1, x2, y2
    )
    connector.line.color.rgb = color
    connector.line.width = w
    return connector

def gradient_bar(slide, l, t, w, h, c1=CYAN, c2=BLUE):
    """Approximate a horizontal gradient using two overlapping rectangles."""
    add_box(slide, l, t, w//2, h, fill=c1)
    add_box(slide, l + w//2, t, w - w//2, h, fill=c2)

def accent_stripe(slide, color=CYAN, left=Inches(0), width=Inches(0.07), height=H):
    add_box(slide, left, Inches(0), width, height, fill=color)

def bottom_bar(slide):
    add_box(slide, Inches(0), H - Inches(0.42), W, Inches(0.42), fill=DARK_BG)

def slide_number_badge(slide, num, total=13):
    add_text(slide,
             f"{num:02d} / {total:02d}",
             W - Inches(1.6), Inches(0.18), Inches(1.4), Inches(0.4),
             size=10, color=DIM, align=PP_ALIGN.RIGHT)

def progress_dots(slide, active, total=13):
    """Draw small dot indicators at the bottom of the slide."""
    dot_r = Inches(0.055)
    gap   = Inches(0.22)
    total_w = total * (dot_r * 2) + (total - 1) * (gap - dot_r * 2)
    start_x = (W - total_w) / 2
    cy = H - Inches(0.21)
    for i in range(total):
        cx = start_x + i * gap + dot_r
        col = CYAN if i == active - 1 else DIM
        add_circle(slide, cx, cy, dot_r if i == active - 1 else Inches(0.038),
                   fill=col)

def bg(slide):
    add_box(slide, Inches(0), Inches(0), W, H, fill=BG)

def header(slide, category, title, slide_num):
    bg(slide)
    accent_stripe(slide, CYAN)
    # Category tag
    add_text(slide, category, Inches(0.25), Inches(0.22), Inches(10), Inches(0.38),
             size=9, bold=True, color=CYAN)
    # Title
    add_text(slide, title, Inches(0.25), Inches(0.52), Inches(11.5), Inches(0.72),
             size=22, bold=True, color=WHITE)
    # Thin divider
    add_box(slide, Inches(0.25), Inches(1.22), Inches(13.0), Inches(0.025), fill=BORDER)
    slide_number_badge(slide, slide_num)
    bottom_bar(slide)
    progress_dots(slide, slide_num)

def card(slide, l, t, w, h, title=None, accent=CYAN, body_tf=False):
    add_rect(slide, l, t, w, h, fill=CARD, line=accent, lw=Pt(1.4))
    # top accent strip
    add_box(slide, l, t, w, Inches(0.07), fill=accent)
    if title:
        add_text(slide, title, l + Inches(0.22), t + Inches(0.14),
                 w - Inches(0.44), Inches(0.4),
                 size=12, bold=True, color=accent)
    return None

def icon_badge(slide, glyph, l, t, size=18, bg_color=CARD2, fg_color=CYAN):
    r = Inches(0.32)
    add_circle(slide, l + r, t + r, r, fill=bg_color)
    add_text(slide, glyph, l, t, r*2, r*2,
             size=size, bold=True, color=fg_color,
             align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 1  –  TITLE / HERO
# ══════════════════════════════════════════════════════════════════════════════
s1 = prs.slides.add_slide(BLANK)
bg(s1)

# Full-width dark navy top 60%
add_box(s1, Inches(0), Inches(0), W, Inches(4.6), fill=DARK_BG)

# Left vertical cyan accent
accent_stripe(s1, CYAN)

# Diagonal decorative geometry (top-right corner triangle)
from pptx.enum.shapes import MSO_SHAPE
tri = s1.shapes.add_shape(MSO_SHAPE.RIGHT_TRIANGLE, W - Inches(3.4), Inches(0), Inches(3.4), Inches(2.2))
tri.fill.solid(); tri.fill.fore_color.rgb = RGBColor(0x00, 0x20, 0x48)
tri.line.fill.background()

# Shield-style decorative circle (top-right)
add_circle(s1, W - Inches(1.5), Inches(1.1), Inches(1.1),
           fill=RGBColor(0x00, 0x2A, 0x55))
add_circle(s1, W - Inches(1.5), Inches(1.1), Inches(0.78),
           fill=RGBColor(0x00, 0x37, 0x70))
add_text(s1, "🛡", W - Inches(2.0), Inches(0.65), Inches(1.0), Inches(0.9),
         size=28, align=PP_ALIGN.CENTER, color=CYAN)

# Badge pill
pill = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                            Inches(0.9), Inches(0.9), Inches(3.5), Inches(0.42))
pill.fill.solid(); pill.fill.fore_color.rgb = RGBColor(0x00, 0x2D, 0x5A)
pill.line.color.rgb = CYAN; pill.line.width = Pt(1.2)
pill.adjustments[0] = 0.5
tb_pill = pill.text_frame
tb_pill.vertical_anchor = MSO_ANCHOR.MIDDLE
p_pill = tb_pill.paragraphs[0]
p_pill.alignment = PP_ALIGN.CENTER
r = p_pill.add_run()
r.text = "INTELLIGENT CYBERSECURITY PLATFORM"
r.font.name = "Calibri"; r.font.size = Pt(9); r.font.bold = True
r.font.color.rgb = CYAN

# Main title
tb_t = s1.shapes.add_textbox(Inches(0.9), Inches(1.45), Inches(10), Inches(1.3))
tf_t = tb_t.text_frame
p0 = tf_t.paragraphs[0]
r0 = p0.add_run(); r0.text = "SENTINEL "
r0.font.name = "Calibri Black"; r0.font.size = Pt(52)
r0.font.bold = True; r0.font.color.rgb = WHITE
r1 = p0.add_run(); r1.text = "AI"
r1.font.name = "Calibri Black"; r1.font.size = Pt(52)
r1.font.bold = True; r1.font.color.rgb = CYAN

add_text(s1, "Real-Time Intelligent Financial Fraud Detection System",
         Inches(0.9), Inches(2.75), Inches(10.5), Inches(0.6),
         size=19, color=BLUE, bold=False)

add_text(s1, "An end-to-end full-stack platform combining machine learning inference, "
             "explainable behavioral risk scoring, transaction monitoring, and security "
             "investigation workflows — built for academic excellence.",
         Inches(0.9), Inches(3.3), Inches(9.5), Inches(0.9),
         size=12, color=MUTED, wrap=True)

# Thin separator
add_box(s1, Inches(0.9), Inches(4.3), Inches(11.0), Inches(0.03), fill=BORDER)

# Team Section Header
add_text(s1, "▸  PROJECT TEAM", Inches(0.9), Inches(4.4), Inches(4), Inches(0.4),
         size=10, bold=True, color=CYAN)

# Team Leader Card
tl = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                          Inches(0.9), Inches(4.85), Inches(3.4), Inches(1.75))
tl.fill.solid(); tl.fill.fore_color.rgb = CARD2
tl.line.color.rgb = CYAN; tl.line.width = Pt(2)
tl.adjustments[0] = 0.08
tf_tl = tl.text_frame; tf_tl.vertical_anchor = MSO_ANCHOR.MIDDLE
add_para(tf_tl, "★  TEAM LEADER", 9, True, CYAN, PP_ALIGN.CENTER)
add_para(tf_tl, "Sanket Kushwaha", 20, True, WHITE, PP_ALIGN.CENTER, space_before=4)
add_para(tf_tl, "Full-Stack & ML Architecture", 10, False, MUTED, PP_ALIGN.CENTER)

# 3 member cards
members = [
    ("Anand Verma",    "Backend & API Engineering"),
    ("Sandeep Mishra", "ML Pipeline & Evaluation"),
    ("Kunal",          "Frontend UI/UX Design"),
]
for i, (name, role) in enumerate(members):
    xm = Inches(4.6 + i * 2.95)
    mc = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                              xm, Inches(4.85), Inches(2.7), Inches(1.75))
    mc.fill.solid(); mc.fill.fore_color.rgb = CARD
    mc.line.color.rgb = BORDER; mc.line.width = Pt(1.2)
    mc.adjustments[0] = 0.08
    tf_m = mc.text_frame; tf_m.vertical_anchor = MSO_ANCHOR.MIDDLE
    add_para(tf_m, "TEAM MEMBER", 8, True, BLUE, PP_ALIGN.CENTER)
    add_para(tf_m, name, 15, True, WHITE, PP_ALIGN.CENTER, space_before=5)
    add_para(tf_m, role, 10, False, MUTED, PP_ALIGN.CENTER)

bottom_bar(s1)
progress_dots(s1, 1)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 2  –  TABLE OF CONTENTS
# ══════════════════════════════════════════════════════════════════════════════
s2 = prs.slides.add_slide(BLANK)
header(s2, "AGENDA  //  WHAT WE'LL COVER", "Table of Contents", 2)

toc_items = [
    ("01", "Problem Statement & Motivation",         CYAN),
    ("02", "Project Objectives & Core Vision",        BLUE),
    ("03", "System Architecture & Data Flow",         GREEN),
    ("04", "Modern Technology Stack",                 AMBER),
    ("05", "Visual Design & Brand Identity",          PURPLE),
    ("06", "Feature: Transaction Analyzer",           RED),
    ("07", "Feature: Live Monitoring Dashboard",      CYAN),
    ("08", "Feature: Fraud Alerts & Case Management", GREEN),
    ("09", "Machine Learning Pipeline & Training",    BLUE),
    ("10", "Model Evaluation & Performance Metrics",  AMBER),
    ("11", "Transaction Explorer & Compliance",       PURPLE),
    ("12", "Conclusion & Future Roadmap",             RED),
]

cols = [toc_items[:6], toc_items[6:]]
for col_i, col in enumerate(cols):
    for row_i, (num, title, col_c) in enumerate(col):
        x = Inches(0.5 + col_i * 6.6)
        y = Inches(1.4 + row_i * 0.9)
        # Number badge
        nb = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                  x, y + Inches(0.08), Inches(0.52), Inches(0.52))
        nb.fill.solid(); nb.fill.fore_color.rgb = CARD2
        nb.line.color.rgb = col_c; nb.line.width = Pt(1.5)
        nb.adjustments[0] = 0.3
        tf_nb = nb.text_frame; tf_nb.vertical_anchor = MSO_ANCHOR.MIDDLE
        p_nb = tf_nb.paragraphs[0]; p_nb.alignment = PP_ALIGN.CENTER
        r_nb = p_nb.add_run(); r_nb.text = num
        r_nb.font.name = "Calibri"; r_nb.font.size = Pt(12)
        r_nb.font.bold = True; r_nb.font.color.rgb = col_c
        # Title
        add_text(s2, title, x + Inches(0.65), y + Inches(0.1), Inches(5.7), Inches(0.5),
                 size=14, color=WHITE, valign=MSO_ANCHOR.MIDDLE)
        # Thin line separator
        if row_i < len(col) - 1:
            add_box(s2, x, y + Inches(0.72), Inches(6.1), Inches(0.015), fill=BORDER)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 3  –  PROBLEM STATEMENT
# ══════════════════════════════════════════════════════════════════════════════
s3 = prs.slides.add_slide(BLANK)
header(s3, "01  //  PROBLEM STATEMENT", "The Growing Crisis of Digital Financial Fraud", 3)

stats = [
    ("$485B",  "Annual global card fraud losses by 2027 (Nilson Report)", RED),
    ("99.8%",  "Of transactions are legitimate — accuracy is a misleading metric", AMBER),
    ("<2 sec", "Payment settlement window — zero time for manual review",  CYAN),
    ("320%",   "Rise in card-not-present fraud since 2020",               BLUE),
]
for i, (val, label, col) in enumerate(stats):
    x = Inches(0.4 + i * 3.22)
    # Stat card
    sc = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.4), Inches(3.0), Inches(1.6))
    sc.fill.solid(); sc.fill.fore_color.rgb = CARD2
    sc.line.color.rgb = col; sc.line.width = Pt(1.5)
    sc.adjustments[0] = 0.1
    tf_sc = sc.text_frame; tf_sc.vertical_anchor = MSO_ANCHOR.MIDDLE
    add_para(tf_sc, val, 28, True, col, PP_ALIGN.CENTER)
    add_para(tf_sc, label, 9, False, MUTED, PP_ALIGN.CENTER)

# 3 Column problem cards
cols3 = [
    ("💸  Massive Financial Loss",
     ["Digital payment volumes are doubling every 3 years globally.",
      "Billions are lost to unauthorized card transactions, wire fraud, and account takeovers.",
      "Chargeback fraud alone costs merchants $125 billion annually.",
      "Fraudsters continuously evolve attack techniques to bypass legacy defenses."],
     RED),
    ("⚠️  Limitations of Rule Systems",
     ["Static if-else thresholds fail against novel, structured fraud attacks.",
      "Rigid rules produce high false-positive rates, frustrating genuine customers.",
      "Every new fraud pattern requires manual rule engineering by analysts.",
      "Threshold tuning takes weeks — fraud evolves in hours."],
     AMBER),
    ("🤖  The AI-First Imperative",
     ["Machine learning detects complex non-linear behavioral correlations.",
      "Probabilistic risk scoring updates dynamically as spending patterns shift.",
      "Sub-second inference enables real-time approval decisions.",
      "Explainable signals reduce analyst workload and investigation time."],
     GREEN),
]
cw = Inches(4.1)
for i, (title, bullets, col) in enumerate(cols3):
    cx = Inches(0.37 + i * 4.3)
    card(s3, cx, Inches(3.2), cw, Inches(3.6), title, accent=col)
    tb = s3.shapes.add_textbox(cx + Inches(0.2), Inches(3.78), cw - Inches(0.4), Inches(2.9))
    tf = tb.text_frame; tf.word_wrap = True
    for b in bullets:
        add_para(tf, f"• {b}", 11, color=WHITE, space_after=7)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 4  –  OBJECTIVES
# ══════════════════════════════════════════════════════════════════════════════
s4 = prs.slides.add_slide(BLANK)
header(s4, "02  //  OBJECTIVES & SCOPE", "Sentinel AI Core Objectives & Deliverables", 4)

objectives = [
    ("⚡", "Real-Time Risk Scoring",
     "Compute calibrated fraud probability (0–100%) and assign tiers — Low, Review, High — in under 100 ms per transaction.",
     CYAN, Inches(0.4), Inches(1.4)),
    ("🔍", "Explainable AI Signals",
     "Surface transparent warning signals and feature contributions, so analysts understand *why* an alert fired — not just *that* it fired.",
     BLUE, Inches(6.9), Inches(1.4)),
    ("📋", "Case Investigation Workflow",
     "Full lifecycle management: Open → Investigating → Resolved / False Positive, with persistent notes and audit timestamps in SQLite.",
     GREEN, Inches(0.4), Inches(4.1)),
    ("📊", "Visual Analytics & Compliance",
     "SaaS-grade dashboard with volume timelines, risk distributions, server-side filtered history, and secure CSV export for auditors.",
     AMBER, Inches(6.9), Inches(4.1)),
]
ow = Inches(5.9)
oh = Inches(2.5)
for glyph, title, desc, col, ox, oy in objectives:
    card(s4, ox, oy, ow, oh, accent=col)
    add_text(s4, glyph, ox + Inches(0.2), oy + Inches(0.15), Inches(0.55), Inches(0.55),
             size=20, align=PP_ALIGN.CENTER)
    add_text(s4, title, ox + Inches(0.85), oy + Inches(0.14), ow - Inches(1.1), Inches(0.42),
             size=14, bold=True, color=col)
    add_text(s4, desc, ox + Inches(0.22), oy + Inches(0.65), ow - Inches(0.44), oh - Inches(0.8),
             size=12, color=WHITE, wrap=True)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 5  –  SYSTEM ARCHITECTURE
# ══════════════════════════════════════════════════════════════════════════════
s5 = prs.slides.add_slide(BLANK)
header(s5, "03  //  ARCHITECTURE & WORKFLOW", "Multi-Tiered Full-Stack System Architecture", 5)

# Architecture flow: 4 layers with arrows
layers = [
    ("PRESENTATION LAYER",    "React 18 + Vite + TypeScript\nTailwind CSS  •  Recharts  •  Lucide Icons", CYAN,   Inches(0.5)),
    ("API GATEWAY LAYER",     "FastAPI  •  Pydantic v2 Schemas\nUvicorn ASGI  •  CORS Middleware",          BLUE,   Inches(3.35)),
    ("ML INTELLIGENCE ENGINE","scikit-learn RandomForest\nFeature Pipeline  •  Risk Scorer  •  Explainer", GREEN,  Inches(6.2)),
    ("DATA PERSISTENCE LAYER","SQLAlchemy ORM  •  SQLite\nTransactions  •  Alerts  •  Notes  •  Config",   AMBER,  Inches(9.05)),
]
bw = Inches(2.75)
bh = Inches(2.3)
by = Inches(1.5)
for lname, ldesc, lcol, lx in layers:
    b = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, lx, by, bw, bh)
    b.fill.solid(); b.fill.fore_color.rgb = CARD2
    b.line.color.rgb = lcol; b.line.width = Pt(2)
    b.adjustments[0] = 0.1
    # top accent bar
    add_box(s5, lx, by, bw, Inches(0.1), fill=lcol)
    add_text(s5, lname, lx + Inches(0.15), by + Inches(0.18),
             bw - Inches(0.3), Inches(0.42), size=10, bold=True, color=lcol)
    add_text(s5, ldesc, lx + Inches(0.15), by + Inches(0.65),
             bw - Inches(0.3), Inches(1.5), size=11, color=WHITE, wrap=True)

# Arrows between layers
arrow_col = BORDER
for i in range(3):
    ax = Inches(0.5 + i * 2.85) + bw
    ay = by + bh / 2
    add_box(s5, ax, ay - Inches(0.025), Inches(0.6), Inches(0.05), fill=arrow_col)
    # arrowhead triangle
    at = s5.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW,
                              ax + Inches(0.4), ay - Inches(0.1), Inches(0.2), Inches(0.2))
    at.fill.solid(); at.fill.fore_color.rgb = arrow_col
    at.line.fill.background()

# Pipeline flow beneath
flow_steps = [
    "① Input", "② Validate", "③ Transform",
    "④ Inference", "⑤ Explain", "⑥ Persist", "⑦ Display"
]
fw = (W - Inches(1.0)) / len(flow_steps)
for i, step in enumerate(flow_steps):
    fx = Inches(0.5) + i * fw
    fs = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                              fx, Inches(4.1), fw - Inches(0.12), Inches(0.72))
    col_idx = [CYAN, BLUE, GREEN, AMBER, PURPLE, RED, CYAN][i]
    fs.fill.solid(); fs.fill.fore_color.rgb = CARD
    fs.line.color.rgb = col_idx; fs.line.width = Pt(1.2)
    fs.adjustments[0] = 0.3
    tf_fs = fs.text_frame; tf_fs.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_fs = tf_fs.paragraphs[0]; p_fs.alignment = PP_ALIGN.CENTER
    r_fs = p_fs.add_run(); r_fs.text = step
    r_fs.font.name = "Calibri"; r_fs.font.size = Pt(11)
    r_fs.font.bold = True; r_fs.font.color.rgb = col_idx

# Flow description
add_text(s5, "END-TO-END TRANSACTION PROCESSING PIPELINE",
         Inches(0.5), Inches(3.9), Inches(10), Inches(0.3),
         size=9, bold=True, color=DIM)

# Two detail cards
detail_cards = [
    ("Key Principle: Separation of Concerns",
     "Frontend never accesses the ML model or database directly. All data flows through the validated FastAPI layer, ensuring security, testability, and clean architecture.",
     CYAN),
    ("Key Principle: Demo Mode Fallback",
     "The entire system operates fully without an external dataset. A deterministic synthetic generator simulates realistic fraud/legitimate distributions in-memory.",
     GREEN),
]
for i, (dt, dd, dc) in enumerate(detail_cards):
    dx = Inches(0.5 + i * 6.5)
    card(s5, dx, Inches(5.1), Inches(6.1), Inches(1.75), accent=dc)
    add_text(s5, dt, dx + Inches(0.22), Inches(5.28), Inches(5.7), Inches(0.38),
             size=11, bold=True, color=dc)
    add_text(s5, dd, dx + Inches(0.22), Inches(5.68), Inches(5.7), Inches(1.0),
             size=11, color=WHITE, wrap=True)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 6  –  TECHNOLOGY STACK
# ══════════════════════════════════════════════════════════════════════════════
s6 = prs.slides.add_slide(BLANK)
header(s6, "04  //  TECH STACK", "Modern, Production-Ready Technology Stack", 6)

stack = [
    ("FRONTEND CLIENT", CYAN, [
        ("⚛  React 18 + TypeScript",   "Component-based, fully type-safe SPA"),
        ("⚡  Vite Build Tool",          "Lightning-fast HMR and production bundling"),
        ("🎨  Tailwind CSS",             "Utility-first cybersecurity dark theme"),
        ("📈  Recharts",                 "Area, Bar, and Donut interactive charts"),
        ("🔷  Lucide React Icons",       "Crisp SVG icon library for the entire UI"),
        ("🔀  React Router DOM",         "Declarative client-side navigation"),
    ]),
    ("BACKEND SERVICES", BLUE, [
        ("🐍  Python 3.11+",             "Modern async-ready Python environment"),
        ("⚡  FastAPI Framework",         "High-performance async REST API"),
        ("✅  Pydantic v2",              "Schema validation and error responses"),
        ("🚀  Uvicorn ASGI",             "Production-grade ASGI web server"),
        ("🔒  CORS Middleware",           "Restricted cross-origin security layer"),
    ]),
    ("ML & DATA LAYER", GREEN, [
        ("🌲  scikit-learn",             "RandomForestClassifier with ensemble bagging"),
        ("🔢  NumPy + pandas",           "High-performance tabular data processing"),
        ("💾  joblib Serialization",     "Saving and loading trained model artifacts"),
        ("🗄  SQLAlchemy ORM",           "Declarative relational schema and queries"),
        ("📦  SQLite Database",          "Serverless ACID-compliant local persistence"),
    ]),
]
sw = Inches(4.1)
for i, (sname, scol, sitems) in enumerate(stack):
    sx = Inches(0.4 + i * 4.3)
    card(s6, sx, Inches(1.35), sw, Inches(5.5), accent=scol)
    # Category header
    add_text(s6, sname, sx + Inches(0.2), Inches(1.52),
             sw - Inches(0.4), Inches(0.4), size=11, bold=True, color=scol)
    tb_s = s6.shapes.add_textbox(sx + Inches(0.2), Inches(1.98),
                                   sw - Inches(0.4), Inches(4.6))
    tf_s = tb_s.text_frame; tf_s.word_wrap = True
    for sitem_name, sitem_desc in sitems:
        add_para(tf_s, sitem_name, 12, True, WHITE, space_after=1)
        add_para(tf_s, f"   {sitem_desc}", 10, False, MUTED, space_after=9)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 7  –  DESIGN & BRAND
# ══════════════════════════════════════════════════════════════════════════════
s7 = prs.slides.add_slide(BLANK)
header(s7, "05  //  UI & USER EXPERIENCE", "Visual Design System & Cybersecurity Brand Identity", 7)

# Color palette swatches
palette = [
    ("#091127", BG,    "BG Navy"),
    ("#0F1D3A", CARD,  "Card Surface"),
    ("#00E5FF", CYAN,  "Cyber Cyan"),
    ("#4FACFE", BLUE,  "Electric Blue"),
    ("#00E676", GREEN, "Safe Green"),
    ("#FFB142", AMBER, "Caution Amber"),
    ("#FF5252", RED,   "Alert Red"),
    ("#AB47BC", PURPLE,"Purple Accent"),
]
sw_w = Inches(1.4); sw_h = Inches(0.68)
sw_y = Inches(1.4)
for i, (hex_v, col, lbl) in enumerate(palette):
    sx = Inches(0.4 + i * 1.55)
    sc = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, sx, sw_y, sw_w, sw_h)
    sc.fill.solid(); sc.fill.fore_color.rgb = col
    sc.line.color.rgb = WHITE; sc.line.width = Pt(0.5)
    sc.adjustments[0] = 0.15
    add_text(s7, lbl, sx, sw_y + sw_h + Inches(0.06), sw_w, Inches(0.3),
             size=8, color=MUTED, align=PP_ALIGN.CENTER)
    add_text(s7, hex_v, sx, sw_y + sw_h + Inches(0.3), sw_w, Inches(0.25),
             size=7, color=DIM, align=PP_ALIGN.CENTER, italic=True)

# 4 design principle cards
design_cards = [
    ("🌙  Dark Cyber Aesthetic",
     "High-contrast #091127 deep navy background with slate card surfaces. Cyan/Blue accent glows designed for security operations monitoring — zero eye fatigue.",
     CYAN, Inches(0.4), Inches(2.6)),
    ("📐  Data-Dense Clarity",
     "Fine 1.4pt borders, tight visual hierarchy, and zero decorative clutter. Analysts absorb hundreds of data points per screen without cognitive overload.",
     BLUE, Inches(6.9), Inches(2.6)),
    ("🚦  Three-Tier Risk Color System",
     "Instant recognition: Emerald Green (Low ≤35%), Amber (Review 35–65%), Crimson Red (High ≥65%). Color chosen for accessibility and alarm psychology.",
     AMBER, Inches(0.4), Inches(4.85)),
    ("📱  Responsive & Animated",
     "Fluid grid adapting from 1440px desktop to 768px tablet. Micro-animations on hover states, skeleton loaders during API calls, and graceful empty states.",
     GREEN, Inches(6.9), Inches(4.85)),
]
for dt, dd, dc, dx, dy in design_cards:
    card(s7, dx, dy, Inches(5.9), Inches(2.0), accent=dc)
    add_text(s7, dt, dx + Inches(0.22), dy + Inches(0.18), Inches(5.5), Inches(0.4),
             size=13, bold=True, color=dc)
    add_text(s7, dd, dx + Inches(0.22), dy + Inches(0.6), Inches(5.5), Inches(1.25),
             size=12, color=WHITE, wrap=True)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 8  –  TRANSACTION ANALYZER (FEATURE)
# ══════════════════════════════════════════════════════════════════════════════
s8 = prs.slides.add_slide(BLANK)
header(s8, "06  //  FEATURE SPOTLIGHT", "Core Feature: Interactive Transaction Analyzer", 8)

# Left: Input parameters
card(s8, Inches(0.4), Inches(1.35), Inches(5.8), Inches(5.5), "INPUT PARAMETERS", accent=CYAN)
params = [
    ("💰", "Amount ($)",              "Flags statistically unusual charge deviations"),
    ("🕐", "Transaction Hour (0–23)", "Nocturnal spikes at 2–5 AM trigger elevated risk"),
    ("🏪", "Merchant Category",       "Electronics / Jewelry vs Grocery / Utilities"),
    ("💳", "Transaction Type",        "Card-not-present online vs in-person POS terminal"),
    ("📍", "Geo Distance (km)",        "Home location vs terminal origin discrepancy"),
    ("⚡", "Velocity (24h count)",     "Burst of rapid successive transactions"),
    ("📱", "Device Recognition",       "Trusted device vs new anonymous browser/device"),
]
ty = Inches(1.95)
for glyph, pname, pdesc in params:
    add_text(s8, glyph, Inches(0.6), ty, Inches(0.42), Inches(0.42),
             size=14, align=PP_ALIGN.CENTER)
    add_text(s8, pname, Inches(1.1), ty, Inches(2.0), Inches(0.3),
             size=11, bold=True, color=CYAN)
    add_text(s8, pdesc, Inches(1.1), ty + Inches(0.28), Inches(4.9), Inches(0.3),
             size=10, color=MUTED)
    add_box(s8, Inches(0.6), ty + Inches(0.6), Inches(5.3), Inches(0.012), fill=BORDER)
    ty += Inches(0.68)

# Right: Results panel
card(s8, Inches(6.5), Inches(1.35), Inches(6.4), Inches(5.5),
     "INSTANT SCORING ENGINE & RESULT", accent=RED)

# Simulated risk gauge (arc-ish using shapes)
# Large risk score display
score_bg = s8.shapes.add_shape(MSO_SHAPE.OVAL,
    Inches(8.6), Inches(1.95), Inches(2.3), Inches(2.3))
score_bg.fill.solid(); score_bg.fill.fore_color.rgb = CARD2
score_bg.line.color.rgb = RED; score_bg.line.width = Pt(4)

add_text(s8, "88.4%", Inches(8.6), Inches(2.4), Inches(2.3), Inches(0.8),
         size=28, bold=True, color=RED, align=PP_ALIGN.CENTER)
add_text(s8, "FRAUD\nPROBABILITY", Inches(8.6), Inches(3.0), Inches(2.3), Inches(0.6),
         size=9, bold=True, color=MUTED, align=PP_ALIGN.CENTER)

# Risk badge
rb = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                           Inches(9.0), Inches(4.35), Inches(1.5), Inches(0.45))
rb.fill.solid(); rb.fill.fore_color.rgb = RED
rb.line.fill.background(); rb.adjustments[0] = 0.5
tf_rb = rb.text_frame; tf_rb.vertical_anchor = MSO_ANCHOR.MIDDLE
p_rb = tf_rb.paragraphs[0]; p_rb.alignment = PP_ALIGN.CENTER
r_rb = p_rb.add_run(); r_rb.text = "⚠  HIGH RISK"
r_rb.font.name = "Calibri"; r_rb.font.size = Pt(11)
r_rb.font.bold = True; r_rb.font.color.rgb = WHITE

# Warning signals list
result_items = [
    ("⚠", "Late-night transaction (3:47 AM local time)", AMBER),
    ("⚠", "Unrecognized device — first-time browser fingerprint", AMBER),
    ("⚠", "Geo distance 1,842 km from home location (London→Cairo)", RED),
    ("⚠", "High velocity: 12 transactions in past 2 hours", RED),
    ("✓", "Unique TX reference: TX-84920-XF8K saved to audit log", GREEN),
]
for glyph, signal, sc_col in result_items:
    add_text(s8, f"{glyph}  {signal}", Inches(6.7), ty - Inches(4.5) + Inches(0.0),
             Inches(5.9), Inches(0.38), size=10, color=sc_col)
    ty_offset = Inches(0.0)

signals_y = Inches(5.0)
for glyph, signal, sc_col in result_items:
    add_text(s8, f"{glyph}  {signal}", Inches(6.7), signals_y,
             Inches(5.9), Inches(0.38), size=10, color=sc_col)
    signals_y += Inches(0.38)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 9  –  DASHBOARD (FEATURE)
# ══════════════════════════════════════════════════════════════════════════════
s9 = prs.slides.add_slide(BLANK)
header(s9, "07  //  FEATURE SPOTLIGHT", "Real-Time Monitoring Dashboard", 9)

# 4 KPI stat cards
kpis = [
    ("TOTAL ANALYZED", "1,248",   "+42 today",  CYAN),
    ("HIGH RISK FLAGS", "42",      "3.4% of all", RED),
    ("UNDER REVIEW",    "89",      "7.1% of all", AMBER),
    ("VOLUME MONITORED","$248,910","$18K today",  GREEN),
]
kw = Inches(2.95); kh = Inches(1.35)
for i, (kname, kval, ksub, kcol) in enumerate(kpis):
    kx = Inches(0.4 + i * 3.1)
    kb = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, kx, Inches(1.35), kw, kh)
    kb.fill.solid(); kb.fill.fore_color.rgb = CARD2
    kb.line.color.rgb = kcol; kb.line.width = Pt(1.5)
    kb.adjustments[0] = 0.1
    add_box(s9, kx, Inches(1.35), kw, Inches(0.07), fill=kcol)
    add_text(s9, kname, kx + Inches(0.15), Inches(1.52), kw - Inches(0.3), Inches(0.3),
             size=8, bold=True, color=MUTED)
    add_text(s9, kval, kx + Inches(0.15), Inches(1.78), kw - Inches(0.3), Inches(0.6),
             size=24, bold=True, color=WHITE)
    add_text(s9, ksub, kx + Inches(0.15), Inches(2.35), kw - Inches(0.3), Inches(0.28),
             size=9, color=kcol)

# LEFT: Area chart (embedded)
card(s9, Inches(0.4), Inches(2.9), Inches(6.3), Inches(3.9),
     "TRANSACTION VOLUME TIMELINE (Last 7 Days)", accent=CYAN)

chart_data = CategoryChartData()
chart_data.categories = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
chart_data.add_series('Legitimate',   (145, 162, 138, 171, 199, 88, 74))
chart_data.add_series('Flagged',      (8,   12,  6,   15,  22,  9,  5))

from pptx.util import Inches as _I
chart1 = s9.shapes.add_chart(
    XL_CHART_TYPE.AREA, _I(0.5), _I(3.3), _I(6.0), _I(3.3), chart_data
).chart
chart1.has_legend = True
plot1 = chart1.plots[0]
# Style series colors
from pptx.oxml.ns import qn as _qn

# RIGHT: Risk donut chart
card(s9, Inches(7.0), Inches(2.9), Inches(5.9), Inches(3.9),
     "RISK TIER DISTRIBUTION", accent=AMBER)

donut_data = CategoryChartData()
donut_data.categories = ['Low Risk (≤35%)', 'Review (35–65%)', 'High Risk (≥65%)']
donut_data.add_series('Risk Tiers', (1117, 89, 42))

chart2 = s9.shapes.add_chart(
    XL_CHART_TYPE.DOUGHNUT, _I(7.1), _I(3.3), _I(5.7), _I(3.3), donut_data
).chart
chart2.has_legend = True

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 10  –  ALERTS CENTER
# ══════════════════════════════════════════════════════════════════════════════
s10 = prs.slides.add_slide(BLANK)
header(s10, "08  //  CASE MANAGEMENT", "Fraud Alerts Center & Investigation Workflow", 10)

# Lifecycle flow
lifecycle = [
    ("🔴  OPEN",         "Auto-generated when risk ≥ 65%",  RED,   Inches(0.5)),
    ("🔵  INVESTIGATING", "Analyst claims and starts review",BLUE,  Inches(3.6)),
    ("✅  RESOLVED",      "Confirmed fraud — action taken",  GREEN, Inches(6.7)),
    ("⬛  FALSE POSITIVE","Legitimate transaction cleared",  DIM,   Inches(9.8)),
]
for lname, ldesc, lcol, lx in lifecycle:
    lb = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, lx, Inches(1.35), Inches(2.85), Inches(1.3))
    lb.fill.solid(); lb.fill.fore_color.rgb = CARD2
    lb.line.color.rgb = lcol; lb.line.width = Pt(2)
    lb.adjustments[0] = 0.15
    tf_lb = lb.text_frame; tf_lb.vertical_anchor = MSO_ANCHOR.MIDDLE
    add_para(tf_lb, lname, 13, True, lcol, PP_ALIGN.CENTER)
    add_para(tf_lb, ldesc, 10, False, MUTED, PP_ALIGN.CENTER)

# Connecting arrows between lifecycle stages
for i in range(3):
    ax = Inches(0.5 + i * 3.1) + Inches(2.85)
    ay = Inches(1.35) + Inches(0.65)
    add_box(s10, ax, ay - Inches(0.025), Inches(0.72), Inches(0.05), fill=DIM)

# Two detail cards
card(s10, Inches(0.4), Inches(2.95), Inches(6.1), Inches(3.85),
     "INVESTIGATION CAPABILITIES", accent=RED)
inv_items = [
    ("🔍  Multi-Criteria Filtering",
     "Filter active alerts simultaneously by risk severity bracket, monetary amount range, submission date range, and current investigation status."),
    ("📝  Persistent Audit Notes",
     "Analysts record qualitative findings and evidence directly on each case. Notes are timestamped and committed to SQLite — immutable for compliance."),
    ("⏱  Priority Triage Queue",
     "Alerts are automatically sorted by risk score descending. Highest-threat transactions always surface at the top of the investigation queue."),
]
iy = Inches(3.55)
for iname, idesc in inv_items:
    add_text(s10, iname, Inches(0.65), iy, Inches(5.6), Inches(0.35),
             size=12, bold=True, color=AMBER)
    add_text(s10, idesc, Inches(0.65), iy + Inches(0.35), Inches(5.6), Inches(0.6),
             size=11, color=WHITE, wrap=True)
    add_box(s10, Inches(0.65), iy + Inches(0.98), Inches(5.6), Inches(0.015), fill=BORDER)
    iy += Inches(1.1)

card(s10, Inches(6.85), Inches(2.95), Inches(6.1), Inches(3.85),
     "WHY HUMAN-IN-THE-LOOP MATTERS", accent=CYAN)
hil_items = [
    ("🤝  Prevents Automation Errors", "AI flags suspicious patterns, but a trained analyst confirms before freezing accounts. Reduces wrongful card blocks."),
    ("📊  Continuous Training Signal", "Marked False Positives and Resolved cases become labeled ground truth for model retraining iterations."),
    ("📜  Regulatory Compliance",      "Case notes and status history satisfy KYC / AML audit requirements for banking regulators."),
]
hy = Inches(3.55)
for hname, hdesc in hil_items:
    add_text(s10, hname, Inches(7.1), hy, Inches(5.6), Inches(0.35),
             size=12, bold=True, color=CYAN)
    add_text(s10, hdesc, Inches(7.1), hy + Inches(0.35), Inches(5.6), Inches(0.6),
             size=11, color=WHITE, wrap=True)
    add_box(s10, Inches(7.1), hy + Inches(0.98), Inches(5.6), Inches(0.015), fill=BORDER)
    hy += Inches(1.1)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 11  –  MACHINE LEARNING PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
s11 = prs.slides.add_slide(BLANK)
header(s11, "09  //  MACHINE LEARNING", "Machine Learning Pipeline & Model Training", 11)

# ML Pipeline visual (top)
ml_steps = [
    ("📂\nDataset\nLoad",    CYAN),
    ("✅\nValidate\n& Clean", BLUE),
    ("🔧\nFeature\nEngineer", GREEN),
    ("✂️\nStratified\nSplit",  AMBER),
    ("🌲\nRandom\nForest",    PURPLE),
    ("📊\nEvaluate\n& Score",  RED),
    ("💾\nSerialize\nArtifact",CYAN),
]
mw = Inches(1.6)
for i, (mlabel, mcol) in enumerate(ml_steps):
    mx = Inches(0.4 + i * 1.85)
    mb = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                               mx, Inches(1.4), mw, Inches(1.5))
    mb.fill.solid(); mb.fill.fore_color.rgb = CARD2
    mb.line.color.rgb = mcol; mb.line.width = Pt(2)
    mb.adjustments[0] = 0.15
    tf_mb = mb.text_frame; tf_mb.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_mb = tf_mb.paragraphs[0]; p_mb.alignment = PP_ALIGN.CENTER
    r_mb = p_mb.add_run(); r_mb.text = mlabel
    r_mb.font.name = "Calibri"; r_mb.font.size = Pt(10)
    r_mb.font.bold = True; r_mb.font.color.rgb = mcol
    # Arrow
    if i < len(ml_steps) - 1:
        add_box(s11, mx + mw, Inches(1.4) + Inches(0.75) - Inches(0.025),
                Inches(0.25), Inches(0.05), fill=DIM)

# Two detail cards
card(s11, Inches(0.4), Inches(3.2), Inches(6.1), Inches(3.65),
     "RANDOM FOREST CLASSIFIER DETAILS", accent=GREEN)
rf_items = [
    "Ensemble of N decision trees trained via bootstrap aggregating (bagging).",
    "Handles non-linear feature interactions: velocity × time-of-day × distance.",
    "Outputs class probabilities — calibrated via Platt scaling if needed.",
    "Class imbalance handled with class_weight='balanced' parameter.",
    "Deterministic reproducibility via fixed random_state=42 seed.",
    "Supports external CSV dataset (Kaggle European Credit Card Fraud) or demo generator.",
]
tb11 = s11.shapes.add_textbox(Inches(0.65), Inches(3.78), Inches(5.6), Inches(2.8))
tf11 = tb11.text_frame; tf11.word_wrap = True
for item in rf_items:
    add_para(tf11, f"• {item}", 11, color=WHITE, space_after=6)

card(s11, Inches(6.85), Inches(3.2), Inches(6.1), Inches(3.65),
     "DATASET INTEGRATION & LEAKAGE PREVENTION", accent=AMBER)
ds_items = [
    "Built-in dataset adapter maps public fraud CSVs (V1–V28 PCA columns) directly.",
    "Stratified 80/20 train/test split preserves minority fraud class proportion.",
    "StandardScaler fitted exclusively on training split — zero test data contamination.",
    "Model artifacts (model.pkl, model_metrics.json) saved in artifacts/ directory.",
    "Full training log: dataset path, feature list, timestamp, and version hash.",
    "API endpoint POST /api/model/train triggers background async retraining.",
]
tb11r = s11.shapes.add_textbox(Inches(7.1), Inches(3.78), Inches(5.6), Inches(2.8))
tf11r = tb11r.text_frame; tf11r.word_wrap = True
for item in ds_items:
    add_para(tf11r, f"• {item}", 11, color=WHITE, space_after=6)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 12  –  MODEL EVALUATION & METRICS
# ══════════════════════════════════════════════════════════════════════════════
s12 = prs.slides.add_slide(BLANK)
header(s12, "10  //  METRICS & EVALUATION", "Model Evaluation & Performance Metrics", 12)

# Left: Why accuracy fails
card(s12, Inches(0.4), Inches(1.35), Inches(5.8), Inches(2.4),
     "WHY ACCURACY IS MISLEADING IN FRAUD", accent=RED)
add_text(s12,
    "In a typical fraud dataset:\n"
    "• 99.8% of transactions are LEGITIMATE\n"
    "• 0.2% are FRAUDULENT\n\n"
    "A dummy model predicting 'Always Legitimate' achieves 99.8% accuracy "
    "while catching ZERO fraud attacks. This is why we use Precision, Recall, and F1-Score instead.",
    Inches(0.65), Inches(1.98), Inches(5.3), Inches(1.6),
    size=11, color=WHITE, wrap=True)

# Confusion matrix visual
card(s12, Inches(0.4), Inches(4.0), Inches(5.8), Inches(2.75),
     "CONFUSION MATRIX (Demo Results)", accent=AMBER)
cm_data = [("TP: 182", GREEN), ("FP: 23", AMBER), ("FN: 11", AMBER), ("TN: 9784", CYAN)]
cm_labels = [("True Positive\n(Fraud correctly\ncaught)", GREEN),
             ("False Positive\n(Legit flagged\nas fraud)", AMBER),
             ("False Negative\n(Fraud missed)", RED),
             ("True Negative\n(Legit correctly\ncleared)", CYAN)]
for ci, ((val, vc), (lbl, lc)) in enumerate(zip(cm_data, cm_labels)):
    cix = Inches(0.65 + (ci % 2) * 2.65)
    ciy = Inches(4.65 + (ci // 2) * 1.0)
    cb = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cix, ciy, Inches(2.4), Inches(0.88))
    cb.fill.solid(); cb.fill.fore_color.rgb = CARD2
    cb.line.color.rgb = vc; cb.line.width = Pt(1.5)
    cb.adjustments[0] = 0.1
    tf_cb = cb.text_frame; tf_cb.vertical_anchor = MSO_ANCHOR.MIDDLE
    add_para(tf_cb, val, 18, True, vc, PP_ALIGN.CENTER)
    add_para(tf_cb, lbl, 8, False, MUTED, PP_ALIGN.CENTER)

# Right: Metric explanations + bar chart
card(s12, Inches(6.5), Inches(1.35), Inches(6.4), Inches(5.4),
     "KEY EVALUATION METRICS (Demo Results)", accent=CYAN)

metrics_chart_data = CategoryChartData()
metrics_chart_data.categories = ['Precision', 'Recall', 'F1-Score', 'ROC-AUC']
metrics_chart_data.add_series('Score', (0.888, 0.943, 0.915, 0.981))
chart3 = s12.shapes.add_chart(
    XL_CHART_TYPE.BAR_CLUSTERED, Inches(6.6), Inches(1.95), Inches(6.1), Inches(3.0),
    metrics_chart_data
).chart
chart3.has_legend = False

# Metric explanations
metric_expl = [
    ("Precision = 88.8%", "Of all flagged transactions, 88.8% were real fraud.", BLUE),
    ("Recall = 94.3%",    "Of all actual fraud events, 94.3% were caught.",       GREEN),
    ("F1-Score = 91.5%",  "Harmonic mean balancing precision and recall.",         AMBER),
    ("ROC-AUC = 0.981",   "Near-perfect class separation across all thresholds.",  CYAN),
]
mey = Inches(5.15)
for mname, mdesc, mcol in metric_expl:
    add_text(s12, f"• {mname} — {mdesc}", Inches(6.75), mey,
             Inches(5.9), Inches(0.3), size=10, color=mcol)
    mey += Inches(0.3)

add_text(s12,
    "⚠  Demo results only. Real-world performance depends on the actual dataset used.",
    Inches(6.75), Inches(6.3), Inches(5.9), Inches(0.4),
    size=9, color=MUTED, italic=True)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 13  –  TRANSACTION EXPLORER + CONCLUSION / ROADMAP
# ══════════════════════════════════════════════════════════════════════════════
s13 = prs.slides.add_slide(BLANK)
header(s13, "11–12  //  CONCLUSION & ROADMAP", "What We Built & Where We're Headed", 13)

# Left: Summary of deliverables
card(s13, Inches(0.4), Inches(1.35), Inches(5.8), Inches(5.5),
     "✅  PROJECT DELIVERABLES SUMMARY", accent=GREEN)
deliverables = [
    ("Full-Stack Integration",      "React ↔ FastAPI ↔ SQLite ↔ scikit-learn — fully connected, zero static mocks."),
    ("Real-Time Risk Scoring",       "Sub-100ms fraud probability with Low/Review/High tier assignment."),
    ("Explainable Warning Signals",  "Human-readable behavioral anomaly explanations for every flagged transaction."),
    ("Investigation Case Management","Complete Open→Investigating→Resolved lifecycle with persistent audit notes."),
    ("Visual Analytics Dashboard",   "Live KPI cards, Recharts volume timelines, risk distribution charts."),
    ("Secure CSV Export",            "Filtered, sanitized compliance-ready transaction report downloads."),
    ("Demo Mode",                    "Deterministic synthetic data generator — zero external dataset required."),
    ("Model Evaluation Page",        "In-app retraining, confusion matrix, precision/recall/F1/ROC metrics."),
]
dy = Inches(1.98)
for dname, ddesc in deliverables:
    add_text(s13, f"✔  {dname}", Inches(0.65), dy, Inches(5.3), Inches(0.3),
             size=12, bold=True, color=GREEN)
    add_text(s13, ddesc, Inches(0.65), dy + Inches(0.3), Inches(5.3), Inches(0.3),
             size=10, color=MUTED)
    dy += Inches(0.6)

# Right: Future roadmap + closing
card(s13, Inches(6.5), Inches(1.35), Inches(6.4), Inches(3.4),
     "🚀  FUTURE ROADMAP", accent=BLUE)
roadmap = [
    ("Graph Neural Networks", "Detect coordinated fraud rings and money-mule networks via relational transaction graphs."),
    ("Deep Anomaly Autoencoders", "Zero-shot detection of novel fraud patterns with no labeled training data required."),
    ("Apache Kafka Streaming", "Scale ingestion to 100,000+ transactions per second with distributed stream processing."),
    ("Behavioral Biometrics", "Integrate keystroke dynamics and device motion telemetry as continuous authentication."),
]
ry = Inches(1.98)
for rname, rdesc in roadmap:
    add_text(s13, f"✦  {rname}", Inches(6.75), ry, Inches(5.9), Inches(0.3),
             size=12, bold=True, color=BLUE)
    add_text(s13, rdesc, Inches(6.75), ry + Inches(0.3), Inches(5.9), Inches(0.4),
             size=10, color=MUTED, wrap=True)
    add_box(s13, Inches(6.75), ry + Inches(0.72), Inches(5.9), Inches(0.012), fill=BORDER)
    ry += Inches(0.86)

# Closing / Thank You card
ty_card = s13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                Inches(6.5), Inches(5.0), Inches(6.4), Inches(1.75))
ty_card.fill.solid(); ty_card.fill.fore_color.rgb = CARD2
ty_card.line.color.rgb = CYAN; ty_card.line.width = Pt(2)
ty_card.adjustments[0] = 0.1
add_box(s13, Inches(6.5), Inches(5.0), Inches(6.4), Inches(0.1), fill=CYAN)
tf_ty = ty_card.text_frame; tf_ty.vertical_anchor = MSO_ANCHOR.MIDDLE
add_para(tf_ty, "Thank You! Open for Questions & Discussion",
         18, True, WHITE, PP_ALIGN.CENTER)
add_para(tf_ty, "Team: Sanket Kushwaha (Lead)  •  Anand Verma  •  Sandeep Mishra  •  Kunal",
         11, False, MUTED, PP_ALIGN.CENTER, space_before=6)

# ── Save ──────────────────────────────────────────────────────────────────────
out = "Sentinel_AI_Presentation_v2.pptx"
prs.save(out)
print(f"[OK] Presentation saved -> {out}")
