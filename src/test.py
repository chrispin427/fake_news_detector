from report_generator import (
    generate_report,
    generate_report_text
)

report = generate_report(
    article_title="Europe Heatwave Kills Dozens",

    verdict_result={
        "verdict": "Likely Credible",
        "score": 82
    },

    credibility_score=88,

    source_info={
        "domain": "bbc.com",
        "label": "Trusted",
        "score": 95
    },

    fact_result={
        "verdict": "Supported"
    },

    timeline_result={
        "is_old_news": False
    },

    sentiment_result={
        "manipulation_risk": "Low"
    },

    virality_result={
        "level": "High"
    },

    risk_result={
        "risk_level": "Low"
    },

    source_comparison_result={
        "agreement": 81
    },

    evidence=[
        {
            "source": "BBC",
            "title": "Europe heatwave kills dozens"
        }
    ]
)

print(generate_report_text(report))