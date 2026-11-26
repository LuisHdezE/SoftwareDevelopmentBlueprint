#!/usr/bin/env python3
"""Structural QA evidence review; no release or execution authorization."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROLE_KIND={
 "functional":("qa","test"),"architecture":("qa","architecture_test"),
 "browser":("qa","browser"),"http_api":("qa","newman"),
 "android":("qa","android_runtime"),"ios":("qa","ios_runtime"),
 "desktop":("qa","desktop_runtime"),"security":("security","security_test"),
 "discoverability":("specialist:search-ai-discoverability","discoverability_test"),
 "traceability":("qa","review"),
}
def unique(pairs):
    result={}
    for k,v in pairs:
        if k in result:
            raise ValueError("duplicate JSON key: "+str(k))
        result[k]=v
    return result
def load(path):
    return json.loads(path.read_text(encoding="utf-8"),object_pairs_hook=unique)
def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()).hexdigest()
def require(ok,reason):
    if not ok:
        raise ValueError(reason)
def nonblank(value):
    return isinstance(value,str) and bool(value.strip())
def artifact(root,path,expected):
    require(isinstance(path,str) and path and "\\" not in path and ":" not in path,"invalid artifact path")
    rel=Path(path)
    require(not rel.is_absolute() and all(p not in ("..",".") for p in rel.parts),"artifact traversal")
    current=root
    for part in rel.parts:
        current=current/part
        require(not current.is_symlink(),"artifact symlink forbidden")
    require(current.is_file() and current.resolve().is_relative_to(root.resolve()),"missing or escaped artifact")
    require(current.stat().st_size>0,"empty artifact")
    require(hashlib.sha256(current.read_bytes()).hexdigest()==expected,"artifact digest mismatch")
def evaluate(plan,record,root):
    require(set(plan)=={"repository","candidate","task_id","revision","scope","applicability","review_evidence"},"invalid plan fields")
    require(re.fullmatch(r"[^/\s]+/[^/\s]+",plan["repository"]) is not None,"invalid repository")
    require(re.fullmatch(r"[a-f0-9]{40}",plan["candidate"]) is not None,"full candidate required")
    require(nonblank(plan["task_id"]) and type(plan["revision"]) is int and plan["revision"]>0,"invalid task identity")
    require(nonblank(plan["scope"]) and nonblank(plan["review_evidence"]),"missing reviewed scope")
    app=plan["applicability"]
    require(set(app)==set(ROLE_KIND),"all obligations must be evaluated")
    required=set()
    for key,entry in app.items():
        require(set(entry)=={"required","reason"} and type(entry["required"]) is bool and nonblank(entry["reason"]),"invalid applicability: "+key)
        if entry["required"]:
            required.add(key)
    require({"functional","traceability"}<=required,"mandatory QA and traceability")
    require(set(record)=={"plan_digest","repository","candidate","task_id","revision","evidence"},"invalid evidence record")
    require(record["plan_digest"]==digest(plan),"stale plan binding")
    for key in ("repository","candidate","task_id","revision"):
        require(record[key]==plan[key],"stale or foreign evidence: "+key)
    require(isinstance(record["evidence"],list),"evidence list required")
    seen=set()
    for e in record["evidence"]:
        require(set(e)=={"obligation","producer","kind","runner","version","environment","status","executed","failures","artifact","sha256"},"invalid evidence fields")
        key=e["obligation"]
        require(key in required and key not in seen,"unexpected or duplicate obligation")
        seen.add(key)
        require((e["producer"],e["kind"])==ROLE_KIND[key],"incorrect role or execution kind: "+key)
        require(all(nonblank(e[k]) for k in ("runner","version","environment")),"missing execution metadata")
        require(e["status"]=="PASS" and type(e["executed"]) is int and e["executed"]>0 and type(e["failures"]) is int and e["failures"]==0,"nonpassing or unexecuted evidence")
        artifact(root,e["artifact"],e["sha256"])
    require(seen==required,"missing applicable evidence")
    return {"status":"READY_FOR_INDEPENDENT_QA_REVIEW","release_authorized":False,"obligations":sorted(seen)}
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--plan",type=Path,required=True)
    parser.add_argument("--record",type=Path,required=True)
    parser.add_argument("--artifacts",type=Path,required=True)
    args=parser.parse_args()
    try:
        result=evaluate(load(args.plan),load(args.record),args.artifacts)
    except Exception as exc:
        result={"status":"BLOCKED","release_authorized":False,"finding":str(exc)}
    print(json.dumps(result,ensure_ascii=False))
    return int(result["status"]=="BLOCKED")
if __name__=="__main__":
    sys.exit(main())
