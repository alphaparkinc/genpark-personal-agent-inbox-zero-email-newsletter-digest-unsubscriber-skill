# -*- coding: utf-8 -*-
"""Inbox Zero Newsletter Digest & Unsubscriber Skill for GenPark Personal Productivity Agents."""
import json
from typing import Dict, Any, List

def audit_newsletter_engagement(sender_email: str, received_count_last_90d: int, opened_count_last_90d: int, has_one_click_unsubscribe_header: bool = False, unsubscribe_link_url: str = "") -> Dict[str, Any]:
    if received_count_last_90d <= 0:
        return {"error": "received_count_last_90d must be greater than zero"}

    open_rate = round((opened_count_last_90d / received_count_last_90d) * 100.0, 1)

    if open_rate < 10.0 and received_count_last_90d >= 5:
        action = "AUTO_UNSUBSCRIBE"
        rationale = f"Severe inbox clutter: open rate is only {open_rate}% over {received_count_last_90d} issues."
    elif open_rate < 30.0:
        action = "CONSOLIDATE_INTO_WEEKLY_DIGEST"
        rationale = f"Moderate interest ({open_rate}% open rate); bypass direct inbox to prevent attention fragmentation."
    else:
        action = "WHITELIST_IN_VIP_READ"
        rationale = f"High engagement ({open_rate}% open rate); keep direct priority delivery."

    return {
        "sender_email": sender_email,
        "received_count": received_count_last_90d,
        "opened_count": opened_count_last_90d,
        "open_rate_pct": open_rate,
        "recommended_action": action,
        "rationale": rationale,
        "can_auto_unsubscribe": has_one_click_unsubscribe_header or bool(unsubscribe_link_url),
        "unsubscribe_link_url": unsubscribe_link_url or None,
        "protocol_rfc8058_supported": has_one_click_unsubscribe_header
    }

def compile_daily_newsletter_digest(date_str: str, newsletters: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not newsletters:
        return {"error": "newsletters array is empty"}

    total_articles = len(newsletters)
    original_total_read_time = sum(item.get("read_time_min", 5) for item in newsletters)
    
    curated_items = []
    for item in newsletters:
        curated_items.append({
            "source": item.get("source", "Unknown"),
            "headline": item.get("headline", "No Subject"),
            "bullets": item.get("key_takeaways", [])[:3]
        })

    estimated_digest_time_min = max(1, math.ceil(total_articles * 0.8))
    time_saved_minutes = max(0, original_total_read_time - estimated_digest_time_min)

    return {
        "digest_date": date_str,
        "total_newsletters_compressed": total_articles,
        "original_reading_time_minutes": original_total_read_time,
        "executive_digest_reading_time_minutes": estimated_digest_time_min,
        "saved_productivity_minutes": time_saved_minutes,
        "curated_digest_stream": curated_items,
        "inbox_zero_status": "MAINTAINED"
    }
