assistant: Snapshots look right overall. Two fixes needed: the CTA box collides with the last caption, and the "SHOCK" insert doubles the caption text. I'll fix both in the builder and check the WAN batch.

phr = [p for p in phr if not any(a <= p["s"] < b for a, b in SUPPRESS)]  →  phr = [p for p in phr if not any(p["s"] < b and p["e"] > a for a, b in SUPPRESS)]
.cta{position:absolute;left:70px;top:1360px;  →  .cta{position:absolute;left:70px;top:140px;