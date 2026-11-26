#!/usr/bin/env python3
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("validator",ROOT/"scripts/validate-api-qa-package.py")
v=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
source=ROOT/"templates/api-qa.example"
assert v.validate(source)=={"status":"PACKAGE_READY_FOR_RUNTIME_QA","api_qa_pass":False,"operations":4,"requests":12}
print("PASS reference package, not runtime QA")
def change(d,file,fn):
    p=d/file
    data=json.loads(p.read_text(encoding="utf-8"))
    fn(data)
    p.write_text(json.dumps(data),encoding="utf-8")
cases=[
("missing inventory",lambda d:(d/"ENDPOINTS.md").unlink()),
("inventory drift",lambda d:(d/"ENDPOINTS.md").write_text("| health_get | POST | /health | FR-1 | public |",encoding="utf-8")),
("missing operationId",lambda d:change(d,"openapi.yaml",lambda x:x["paths"]["/health"]["get"].pop("operationId"))),
("missing responses",lambda d:change(d,"openapi.yaml",lambda x:x["paths"]["/health"]["get"].pop("responses"))),
("duplicate operationId",lambda d:change(d,"openapi.yaml",lambda x:x["paths"].update({"/other":x["paths"]["/health"]}))),
("method drift",lambda d:change(d,"postman_collection.json",lambda x:x["item"][0]["request"].update(method="POST"))),
("path drift",lambda d:change(d,"postman_collection.json",lambda x:x["item"][0]["request"].update(url="{{baseUrl}}/other"))),
("hardcoded URL",lambda d:change(d,"postman_collection.json",lambda x:x["item"][0]["request"].update(url="https://example.test/health"))),
("missing tests",lambda d:change(d,"postman_collection.json",lambda x:x["item"][0].pop("event"))),
("disabled tests",lambda d:change(d,"postman_collection.json",lambda x:x["item"][0]["event"][0].update(disabled=True))),
("missing coverage",lambda d:change(d,"operation-coverage.json",lambda x:x.update(operations=[]))),
("duplicate mapping",lambda d:change(d,"operation-coverage.json",lambda x:x["operations"].append(x["operations"][0]))),
("noncanonical coverage",lambda d:change(d,"operation-coverage.json",lambda x:x["operations"][0].update(scenario="negative"))),
("unknown operation",lambda d:change(d,"operation-coverage.json",lambda x:x["operations"][0].update(operation_id="other"))),
("credential in template",lambda d:change(d,"postman_environment.local.json",lambda x:x["values"][1].update(value="synthetic-secret"))),
("live production URL",lambda d:change(d,"postman_environment.production.json",lambda x:x["values"][0].update(value="https://example.test"))),
("duplicate YAML",lambda d:(d/"openapi.yaml").write_text("openapi: 3.0.3\nopenapi: 3.0.3\n",encoding="utf-8")),
]
for name,mutate in cases:
    with tempfile.TemporaryDirectory() as tmp:
        d=Path(tmp)/"package"
        shutil.copytree(source,d)
        mutate(d)
        try:
            v.validate(d)
        except (ValueError,FileNotFoundError,KeyError):
            print("PASS negative:",name)
        else:
            raise AssertionError("accepted invalid package: "+name)
print("API QA package: PASS (1 positive, 17 negative)")
