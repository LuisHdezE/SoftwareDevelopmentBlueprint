#!/usr/bin/env python3
"""Restricted portable API package preflight; never calls a runtime."""
import argparse
import json
from pathlib import Path
import re
import sys
import yaml

METHODS={"get","post","put","patch","delete","head","options","trace"}
class UniqueLoader(yaml.SafeLoader):
    pass
def unique_pairs(pairs):
    result={}
    for k,v in pairs:
        if k in result:
            raise ValueError("duplicate key: "+str(k))
        result[k]=v
    return result
UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    lambda loader,node:unique_pairs(loader.construct_pairs(node)))
def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"),object_pairs_hook=unique_pairs)
def require(condition,message):
    if not condition:
        raise ValueError(message)
def inventory(path):
    rows={}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip().startswith("|"):
            continue
        cells=[c.strip().strip("`") for c in line.strip().strip("|").split("|")]
        if cells[0]=="operationId" or re.fullmatch(r"[:\-]+",cells[0]):
            continue
        require(len(cells)==5 and all(cells),"invalid endpoint inventory row")
        op,method,url,req,auth=cells
        require(op not in rows,"duplicate inventory operation")
        rows[op]=(method.upper(),url)
    return rows
def requests(items):
    for item in items:
        if "item" in item:
            require("request" not in item,"ambiguous collection item")
            yield from requests(item["item"])
        else:
            yield item
def validate(root):
    doc=yaml.load((root/"openapi.yaml").read_text(encoding="utf-8"),Loader=UniqueLoader)
    require(isinstance(doc.get("openapi"),str) and doc["openapi"].startswith("3."),"OpenAPI 3 required")
    ops={}
    for path,methods in doc["paths"].items():
        require(path.startswith("/"),"invalid OpenAPI path")
        for method,obj in methods.items():
            if method not in METHODS:
                continue
            op=obj.get("operationId")
            require(isinstance(op,str) and op.strip() and op not in ops,"missing or duplicate operationId")
            require(bool(obj.get("responses")),"missing responses: "+op)
            ops[op]=(method.upper(),path)
    require(bool(ops),"empty HTTP API")
    require(inventory(root/"ENDPOINTS.md")==ops,"endpoint inventory drift")
    col=read_json(root/"postman_collection.json")
    require(col["info"]["schema"]=="https://schema.getpostman.com/json/collection/v2.1.0/collection.json","Postman v2.1 required")
    by_name={}
    for item in requests(col["item"]):
        name=item["name"]
        require(isinstance(name,str) and name.strip() and name not in by_name,"duplicate or empty request name")
        request=item["request"]
        raw=request["url"]["raw"] if isinstance(request["url"],dict) else request["url"]
        require(raw.startswith("{{baseUrl}}/"),"request must use environment baseUrl")
        path=raw[len("{{baseUrl}}"):].split("?",1)[0]
        path=re.sub(r"\{\{([A-Za-z_][A-Za-z0-9_]*)\}\}",r"{\1}",path)
        tests=[e for e in item.get("event",[]) if e.get("listen")=="test" and e.get("disabled") is not True]
        require(any("pm.test(" in "\n".join(e.get("script",{}).get("exec",[])) for e in tests),"missing request test: "+name)
        by_name[name]=(request["method"].upper(),path)
    coverage=read_json(root/"operation-coverage.json")
    require(coverage["schema_version"]=="1.0","unsupported coverage version")
    canonical=set()
    mapped=set()
    for row in coverage["operations"]:
        op,name=row["operation_id"],row["request_name"]
        require(op in ops and name in by_name and name not in mapped,"unknown/duplicate request mapping")
        require((row["method"],row["path"])==ops[op]==by_name[name],"method/path drift: "+op)
        require(row["scenario"] in {"canonical","negative","flow"},"invalid scenario")
        if row["scenario"]=="canonical":
            require(op not in canonical,"duplicate canonical coverage")
            canonical.add(op)
        mapped.add(name)
    require(canonical==set(ops),"missing canonical operation coverage")
    require(mapped==set(by_name),"unmapped collection request")
    for env in ("local","staging","production"):
        d=read_json(root/f"postman_environment.{env}.json")
        values={}
        for v in d["values"]:
            key=v["key"]
            require(key not in values,"duplicate environment variable")
            values[key]=v["value"]
            if v.get("type")=="secret" or re.search(r"password|token|secret|api.?key|authorization|credential",key,re.I):
                require(v["value"]=="","nonempty credential template: "+key)
        require("baseUrl" in values,"missing baseUrl")
        if env=="production":
            require(values["baseUrl"]=="","production template must not target a live endpoint")
    return {"status":"PACKAGE_READY_FOR_RUNTIME_QA","api_qa_pass":False,"operations":len(ops),"requests":len(by_name)}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("package",type=Path)
    args=p.parse_args()
    try:
        print(json.dumps(validate(args.package),ensure_ascii=False))
        return 0
    except Exception as exc:
        print(json.dumps({"status":"BLOCKED","api_qa_pass":False,"finding":str(exc)},ensure_ascii=False))
        return 1
if __name__=="__main__":
    sys.exit(main())
