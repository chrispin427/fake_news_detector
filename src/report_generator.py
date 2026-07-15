from datetime import datetime
from io import BytesIO


def _normalise_source(src):
    """
    Normalise an evidence source value to a string.

    SerpAPI and other news APIs sometimes return the source as a dict
    (e.g. {"name": "CNN"}) instead of a plain string. This helper
    extracts the name in that case, returns "Unknown" for None, and
    falls back to str() for anything else.
    """
    if isinstance(src, dict):
        return src.get("name", str(src))
    if src is None:
        return "Unknown"
    return str(src)

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.colors import HexColor
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable
    )
    from reportlab.lib import colors
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


def generate_report(
    article_title,
    verdict_result,
    credibility_score,
    source_info,
    fact_result,
    timeline_result,
    sentiment_result,
    virality_result,
    risk_result,
    source_comparison_result,
    evidence,
    headline_result=None,
    rewrite_result=None
):

    report = {
        "generated_at": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "article_title": article_title,
        "final_verdict": verdict_result.get("verdict", "Mixed Evidence"),
        "verdict_score": verdict_result.get("score", credibility_score),
        "verdict_explanations": verdict_result.get("explanations", []),
        "score_breakdown": verdict_result.get("breakdown", {}),
        "credibility_score": credibility_score,
        "source": source_info,
        "fact_check": fact_result,
        "timeline": timeline_result,
        "sentiment": sentiment_result,
        "virality": virality_result,
        "risk": risk_result,
        "source_comparison": source_comparison_result,
        "headline": headline_result or {},
        "rewrite": rewrite_result or {},
        "evidence": evidence
    }

    return report


def generate_report_text(report):

    text = f"""
==================================================
FAKE NEWS DETECTOR REPORT
==================================================

Title:
{report['article_title']}

Generated:
{report['generated_at']}

--------------------------------------------------
FINAL VERDICT
--------------------------------------------------

Verdict:
{report['final_verdict']}

Score:
{report['verdict_score']}/100

Explanations:
"""

    for expl in report.get("verdict_explanations", []):
        text += f"  - {expl}\n"

    text += """
--------------------------------------------------
SCORE BREAKDOWN
--------------------------------------------------
"""

    breakdown = report.get("score_breakdown", {})
    for metric, data in breakdown.items():
        label = metric.replace("_", " ").title()
        raw = data.get("raw", "N/A")
        weighted = data.get("weighted", "N/A")
        weight = data.get("weight", "N/A")
        text += f"\n{label} (weight: {weight}%):\n"
        text += f"  Raw: {raw} | Weighted: {weighted}\n"

    text += """
--------------------------------------------------
SOURCE
--------------------------------------------------

Domain:
{report['source']['domain']}

Rating:
{report['source']['label']}

--------------------------------------------------
FACT CHECK
--------------------------------------------------

{report['fact_check']['verdict']}

--------------------------------------------------
TIMELINE
--------------------------------------------------

Status:
{report['timeline']['status']}

--------------------------------------------------
SENTIMENT
--------------------------------------------------

Manipulation Risk:
{report['sentiment']['manipulation_risk']}

--------------------------------------------------
VIRALITY
--------------------------------------------------

Spread Level:
{report['virality']['level']}

--------------------------------------------------
RISK
--------------------------------------------------

Risk Level:
{report['risk']['risk_level']}

--------------------------------------------------
SOURCE AGREEMENT
--------------------------------------------------

Agreement:
{report['source_comparison']['agreement']}%
Classification:
{report['source_comparison'].get('classification', 'N/A')}

--------------------------------------------------
HEADLINE ANALYSIS
--------------------------------------------------

Risk:
{report['headline'].get('risk', 'N/A')}
Score:
{report['headline'].get('score', 'N/A')}/100
Reasons:
{'; '.join(report['headline'].get('reasons', ['None']))}

--------------------------------------------------
CONTENT MANIPULATION
--------------------------------------------------

Similarity:
{report['rewrite'].get('similarity', 'N/A')}%
Risk:
{report['rewrite'].get('risk', 'N/A')}

--------------------------------------------------
EVIDENCE
--------------------------------------------------
"""

    for item in report["evidence"]:
        text += (
            f"\n\u2022 {_normalise_source(item.get('source', 'Unknown'))} - "
            f"{item.get('title', '')}"
        )

    return text


def generate_pdf(report):
    """
    Generate a professional PDF report using reportlab.
    Returns bytes of the PDF.
    """

    if not HAS_REPORTLAB:
        raise ImportError(
            "reportlab is required for PDF generation. "
            "Install it with: pip install reportlab"
        )

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch
    )

    styles = getSampleStyleSheet()
    story = []

    # Colors
    PRIMARY = HexColor("#1a1a2e")
    ACCENT = HexColor("#e94560")
    DARK_GRAY = HexColor("#333333")
    MEDIUM_GRAY = HexColor("#666666")
    LIGHT_BG = HexColor("#f0f0f5")
    GREEN = HexColor("#27ae60")
    ORANGE = HexColor("#f39c12")

    # Custom styles
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=22,
        leading=28,
        textColor=PRIMARY,
        spaceAfter=4,
        spaceBefore=0
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=MEDIUM_GRAY,
        spaceAfter=16
    )

    section_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        textColor=PRIMARY,
        spaceBefore=16,
        spaceAfter=8,
        borderWidth=0,
        borderColor=ACCENT,
        borderPadding=0
    )

    label_style = ParagraphStyle(
        "Label",
        parent=styles["Normal"],
        fontSize=10,
        textColor=DARK_GRAY,
        fontName="Helvetica-Bold",
        spaceAfter=2
    )

    value_style = ParagraphStyle(
        "Value",
        parent=styles["Normal"],
        fontSize=11,
        textColor=DARK_GRAY,
        spaceAfter=8,
        leftIndent=12
    )

    verdict_style = ParagraphStyle(
        "Verdict",
        parent=styles["Normal"],
        fontSize=16,
        leading=20,
        textColor=ACCENT,
        fontName="Helvetica-Bold",
        spaceAfter=4
    )

    # --- HEADER ---
    story.append(Paragraph(
        "Fake News Detector Report", title_style
    ))
    story.append(Paragraph(
        "Generated: " + report["generated_at"], subtitle_style
    ))
    story.append(HRFlowable(
        width="100%",
        thickness=2,
        color=ACCENT
    ))
    story.append(Spacer(1, 12))

    # --- ARTICLE TITLE ---
    story.append(Paragraph("Article Title", section_style))
    story.append(Paragraph(
        report["article_title"], value_style
    ))

    # --- FINAL VERDICT ---
    story.append(Paragraph("Final Verdict", section_style))
    story.append(Paragraph(
        report["final_verdict"], verdict_style
    ))
    story.append(Paragraph(
        "Verdict Score: " + str(report["verdict_score"]) + "/100   |   "
        "Credibility Score: " + str(report["credibility_score"]) + "/100",
        value_style
    ))

    # --- EXPLANATIONS ---
    explanations = report.get("verdict_explanations", [])
    if explanations:
        story.append(Paragraph("Why This Verdict", section_style))
        for expl in explanations:
            story.append(Paragraph(
                "\u2022 " + expl,
                ParagraphStyle(
                    "ExplanationItem",
                    parent=styles["Normal"],
                    fontSize=10,
                    textColor=DARK_GRAY,
                    leftIndent=16,
                    spaceAfter=3
                )
            ))

    # --- SCORE BREAKDOWN ---
    breakdown = report.get("score_breakdown", {})
    if breakdown:
        story.append(Paragraph("Score Breakdown", section_style))
        bd_data = [["Signal", "Raw", "Weighted", "Weight"]]
        for metric, data in breakdown.items():
            label = metric.replace("_", " ").title()
            raw_val = data.get("raw", "N/A")
            weighted_val = round(data.get("weighted", 0), 2)
            weight_val = str(data.get("weight", "")) + "%"
            bd_data.append([label, str(raw_val), str(weighted_val), weight_val])
        bd_table = Table(bd_data, colWidths=[1.5 * inch, 1 * inch, 1 * inch, 0.8 * inch])
        bd_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("BACKGROUND", (0, 1), (-1, -1), LIGHT_BG),
        ]))
        story.append(bd_table)
        story.append(Spacer(1, 8))

    # --- SOURCE ---
    story.append(Paragraph("Source Information", section_style))
    source = report["source"]
    source_data = [
        ["Domain", source.get("domain", "N/A")],
        ["Rating", source.get("label", "N/A")],
        ["Trust Score", str(source.get("score", 0)) + "/100"]
    ]
    source_table = Table(
        source_data,
        colWidths=[2 * inch, 3.5 * inch]
    )
    source_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT_BG),
        ("TEXTCOLOR", (0, 0), (-1, -1), DARK_GRAY),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(source_table)
    story.append(Spacer(1, 8))

    # --- FACT CHECK ---
    story.append(Paragraph("Fact Check Result", section_style))
    fact = report["fact_check"]
    fact_color = GREEN if fact.get("verdict") == "Supported" else (
        ORANGE if fact.get("verdict") == "Partially Supported" else ACCENT
    )
    fact_style = ParagraphStyle(
        "FactVerdict",
        parent=styles["Normal"],
        fontSize=12,
        textColor=fact_color,
        fontName="Helvetica-Bold",
        spaceAfter=6
    )
    story.append(Paragraph(
        "Verdict: " + fact.get("verdict", "N/A"), fact_style
    ))
    story.append(Paragraph(
        "Claim: " + fact.get("claim", "N/A"), value_style
    ))

    # --- HEADLINE ANALYSIS ---
    if report["headline"]:
        story.append(Paragraph("Headline Analysis", section_style))
        hl = report["headline"]
        hl_color = GREEN if hl.get("risk") == "Low" else (
            ORANGE if hl.get("risk") == "Medium" else ACCENT
        )
        hl_risk_style = ParagraphStyle(
            "HLRisk",
            parent=styles["Normal"],
            fontSize=11,
            textColor=hl_color,
            fontName="Helvetica-Bold",
            spaceAfter=4
        )
        story.append(Paragraph(
            "Risk: " + hl.get("risk", "N/A") + "   |   "
            "Score: " + str(hl.get("score", 0)) + "/100",
            hl_risk_style
        ))
        reasons = hl.get("reasons", [])
        if reasons:
            for r in reasons[:5]:
                story.append(Paragraph(
                    "\u2022 " + r,
                    ParagraphStyle(
                        "Reason",
                        parent=styles["Normal"],
                        fontSize=9,
                        textColor=MEDIUM_GRAY,
                        leftIndent=16,
                        spaceAfter=2
                    )
                ))

    # --- CONTENT MANIPULATION ---
    if report["rewrite"]:
        story.append(Paragraph("Content Manipulation Detection", section_style))
        rw = report["rewrite"]
        rw_color = GREEN if rw.get("risk") == "Low" else (
            ORANGE if rw.get("risk") == "Medium" else ACCENT
        )
        rw_risk_style = ParagraphStyle(
            "RWRisk",
            parent=styles["Normal"],
            fontSize=11,
            textColor=rw_color,
            fontName="Helvetica-Bold",
            spaceAfter=4
        )
        story.append(Paragraph(
            "Risk: " + rw.get("risk", "N/A") + "   |   "
            "Similarity: " + str(rw.get("similarity", 0)) + "%",
            rw_risk_style
        ))
        story.append(Paragraph(
            rw.get("explanation", ""), value_style
        ))

    # --- TIMELINE ---
    story.append(Paragraph("Timeline Analysis", section_style))
    tl = report["timeline"]
    story.append(Paragraph(
        "Status: " + tl.get("status", "N/A") + "   |   "
        "Old News: " + str(tl.get("is_old_news", "N/A")),
        value_style
    ))

    # --- SENTIMENT ---
    story.append(Paragraph("Sentiment Analysis", section_style))
    se = report["sentiment"]
    story.append(Paragraph(
        "Manipulation Risk: " + se.get("manipulation_risk", "N/A"),
        value_style
    ))

    # --- VIRALITY ---
    story.append(Paragraph("Virality Analysis", section_style))
    vi = report["virality"]
    story.append(Paragraph(
        "Spread Level: " + vi.get("level", "N/A") + "   |   "
        "Mentions: " + str(vi.get("mentions", 0)),
        value_style
    ))

    # --- RISK ---
    story.append(Paragraph("Risk Analysis", section_style))
    ri = report["risk"]
    story.append(Paragraph(
        "Risk Level: " + ri.get("risk_level", "N/A"),
        value_style
    ))
    risk_categories = ri.get("risk_categories", [])
    if risk_categories:
        story.append(Paragraph(
            "Categories: " + ", ".join(risk_categories),
            value_style
        ))

    # --- SOURCE AGREEMENT ---
    story.append(Paragraph("Source Consensus Analysis", section_style))
    sc = report["source_comparison"]
    story.append(Paragraph(
        "Agreement: " + str(sc.get("agreement", 0)) + "%   |   "
        "Classification: " + sc.get("classification", "N/A") + "   |   "
        "Sources Checked: " + str(sc.get("sources_checked", 0)),
        value_style
    ))

    # --- EVIDENCE ---
    evidence = report["evidence"]
    if evidence:
        story.append(Paragraph("Supporting Evidence", section_style))
        for item in evidence[:10]:
            src = _normalise_source(item.get("source", "Unknown"))
            title = item.get("title", "")
            story.append(Paragraph(
                "\u2022 " + src + " - " + title,
                ParagraphStyle(
                    "EvidenceItem",
                    parent=styles["Normal"],
                    fontSize=9,
                    textColor=DARK_GRAY,
                    leftIndent=12,
                    spaceAfter=3
                )
            ))
    else:
        story.append(Paragraph(
            "No supporting evidence available.", value_style
        ))

    # --- FOOTER ---
    story.append(Spacer(1, 20))
    story.append(HRFlowable(
        width="100%",
        thickness=0.5,
        color=colors.grey
    ))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Report generated by Fake News Detector. "
        "This report is for informational purposes only.",
        ParagraphStyle(
            "Footer",
            parent=styles["Normal"],
            fontSize=8,
            textColor=MEDIUM_GRAY,
            alignment=1  # center
        )
    ))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes