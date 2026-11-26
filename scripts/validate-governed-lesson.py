#!/usr/bin/env python3
"""Read-only lesson eligibility; declarations are not authenticated approvals."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
CATEGORIES={"pattern","defect","test_strategy","environment","security_control","architecture_observation","process_improvement"}
def unique(pairs):
    out={}
    for k,v in pairs:
        if k in out: raise ValueError("duplicate key: "+str(k))
        out[k]=v
    return out
def load(p):
    return json.loads(p.read_text(encoding="utf-8"),object_pairs_hook=unique)
def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def require(ok,msg):
    if not ok: raise ValueError(msg)
def text(v):
    return isinstance(v,str) and bool(v.strip())
def stamp(v):
    d=datetime.fromisoformat(v.replace("Z","+00:00"))
    require(d.tzinfo is not None,"timezone required")
    return d
def evaluate(lesson,context,now):
    roles={a["id"] for a in load(ROOT/"catalog/agent-policy-registry.proposal.json")["agents"]}
    require(set(lesson)=={"body","status","review","approval"},"invalid record fields")
    b=lesson["body"]
    require(set(b)=={"id","revision","category","author","source_repository","source_commit","source_task","created_at","scope","technologies","title","observation","recommendation","limitations","evidence","policy_override"},"invalid lesson fields")
    require(re.fullmatch(r"LESSON-[A-Z0-9-]+",b["id"]) and type(b["revision"]) is int and b["revision"]>0,"invalid lesson identity")
    require(b["category"] in CATEGORIES and b["author"] in roles,"invalid category or author")
    require(re.fullmatch(r"[^/\s]+/[^/\s]+",b["source_repository"]) and re.fullmatch(r"[a-f0-9]{40}",b["source_commit"]),"invalid source")
    require(all(text(b[k]) for k in ("source_task","title","observation","recommendation","limitations")),"missing lesson content")
    require(isinstance(b["evidence"],list) and b["evidence"] and all(text(x) for x in b["evidence"]),"missing source evidence")
    require(b["policy_override"] is False,"policy override forbidden")
    require(b["scope"] in {"PROJECT_ONLY","PORTABLE"},"invalid distribution scope")
    require(isinstance(b["technologies"],list) and all(text(x) for x in b["technologies"]) and len(set(b["technologies"]))==len(b["technologies"]),"invalid technology scope")
    require(set(context)=={"repository","approved_technologies","owner","requesting_agent"},"invalid retrieval context")
    require(re.fullmatch(r"[^/\s]+/[^/\s]+",context["repository"]) and text(context["owner"]) and context["requesting_agent"] in roles,"invalid consumer identity")
    require(isinstance(context["approved_technologies"],list) and all(text(x) for x in context["approved_technologies"]),"invalid consumer technologies")
    require(set(b["technologies"])<=set(context["approved_technologies"]),"incompatible approved technologies")
    require(lesson["status"]=="APPROVED","lesson not active")
    d=digest(b)
    review=lesson["review"]
    approval=lesson["approval"]
    require(set(review)=={"reviewer","body_digest","status","at","evidence","sanitization"},"invalid review")
    require(review["reviewer"] in {"auditor","security","qa","architect"} and review["reviewer"]!=b["author"],"independent reviewer required")
    require(review["body_digest"]==d and review["status"]=="ACCEPTED" and text(review["evidence"]),"review absent or stale")
    require(set(approval)=={"authority","owner","body_digest","review_digest","at","expires_at","evidence"},"invalid approval")
    require(approval["authority"]=="human_owner" and approval["owner"]==context["owner"],"owner approval required")
    require(approval["body_digest"]==d and approval["review_digest"]==digest(review) and text(approval["evidence"]),"approval absent or stale")
    require(stamp(b["created_at"])<=stamp(review["at"])<=stamp(approval["at"])<=now<stamp(approval["expires_at"]),"invalid or expired approval chronology")
    if b["scope"]=="PROJECT_ONLY":
        require(context["repository"]==b["source_repository"],"project-only lesson cannot cross repositories")
        require(review["sanitization"] in {"NOT_DISTRIBUTED","DECLARED_SANITIZED"},"invalid sanitization declaration")
    else:
        require(review["reviewer"]=="security" and review["sanitization"]=="DECLARED_SANITIZED","portable lesson requires security sanitization review")
    return {"status":"ELIGIBLE_FOR_ADVISORY_REVIEW","lesson_id":b["id"],"revision":b["revision"],"execution_authorized":False,"policy_change_authorized":False}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--lesson",type=Path,required=True)
    p.add_argument("--context",type=Path,required=True)
    args=p.parse_args()
    try:
        result=evaluate(load(args.lesson),load(args.context),datetime.now(timezone.utc))
    except Exception as exc:
        result={"status":"BLOCKED","finding":str(exc),"execution_authorized":False,"policy_change_authorized":False}
    print(json.dumps(result,ensure_ascii=False))
    return int(result["status"]=="BLOCKED")
if __name__=="__main__":
    sys.exit(main())
