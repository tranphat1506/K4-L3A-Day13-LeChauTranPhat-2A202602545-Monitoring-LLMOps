from __future__ import annotations

import time

from .incidents import STATE

CORPUS = {
    "refund": ["Refunds are available within 7 days with proof of purchase."],
    "monitoring": ["Metrics detect incidents, logs identify affected requests, traces localize the root cause."],
    "policy": ["Do not expose PII in logs. Use sanitized summaries only."],
}


from app.tracing import observe, get_langfuse_client
from app.pii import scrub_text

@observe(as_type="span", name="retrieval", capture_input=False, capture_output=False)
def retrieve(message: str) -> list[str]:
    get_langfuse_client().update_current_span(input=scrub_text(message))
    
    if STATE["tool_fail"]:
        raise RuntimeError("Vector store timeout")
    if STATE["rag_slow"]:
        time.sleep(2.5)
    lowered = message.lower()
    
    docs = ["No domain document matched. Use general fallback answer."]
    for key, c_docs in CORPUS.items():
        if key in lowered:
            docs = c_docs
            break
            
    get_langfuse_client().update_current_span(output=[scrub_text(d) for d in docs])
    return docs
