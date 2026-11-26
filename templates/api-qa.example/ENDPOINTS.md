# Synthetic API inventory

| operationId | method | path | requirement | authorization |
|---|---|---|---|---|
| health_get | GET | /health | FR-DEMO-001 | public |
| auth_login | POST | /auth/login | FR-DEMO-002 | public |
| items_create | POST | /items | FR-DEMO-003 | admin |
| items_get | GET | /items/{id} | FR-DEMO-004 | authenticated |
