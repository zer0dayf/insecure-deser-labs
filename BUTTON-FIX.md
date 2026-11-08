# Jackson Run button fix

The HTML template previously generated a literal newline in a JavaScript quoted string, causing a SyntaxError and preventing the click handler from registering. The template now emits the JavaScript escape `\n`.

Rebuild from the new package:

```powershell
docker compose up -d --build --force-recreate java
```

Then refresh `http://127.0.0.1:8081/` with Ctrl+F5. The single Run button sends the textarea content as raw JSON in `POST /api/deserialize` with `Content-Type: application/json`. Burp Repeater still works unchanged.

The embedded script passed `node --check`; container runtime was not tested.
