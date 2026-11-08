#!/usr/bin/env python3
"""Local-only training UI: report observed evidence, never infer success from exit code alone."""
import base64
import hashlib
import html
import os
import shlex
import subprocess
import threading
import time
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

APP = os.environ['APP_NAME']
CMD = shlex.split(os.environ['LAB_COMMAND'])
MAX_PAYLOAD = 32768
PROOF_PATH = Path('/tmp/cc6-proof') if 'Native Commons' in APP else None
RUN_LOCK = threading.Lock()

def escaped(value):
    return html.escape(str(value), quote=True)

def page(value='', evidence=None):
    section = ''
    if evidence is not None:
        status = evidence['status']
        items = ''.join(f'<tr><th>{escaped(key)}</th><td>{escaped(val)}</td></tr>'
                        for key, val in evidence['facts'])
        section = f'''<section id="evidence"><h2>Observed deserialization output</h2>
<p><strong>Observed status: {escaped(status)}</strong></p>
<p class="muted">These are measurements from this submission, not an assumed exploit result. A nonzero exit code can occur after a gadget side effect.</p>
<table>{items}</table><h3>Application stdout</h3><pre>{escaped(evidence['stdout'])}</pre>
<h3>Application stderr</h3><pre>{escaped(evidence['stderr'])}</pre>
<h3>Gadget / deserialization trace</h3><pre>{escaped(evidence['trace'])}</pre></section>'''
    return f'''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{escaped(APP)} - Deserialization Lab</title>
<style>body{{font:16px/1.5 system-ui;background:#101722;color:#e8eef9;max-width:920px;margin:5vh auto;padding:0 20px}}
textarea{{box-sizing:border-box;width:100%;height:175px;background:#1a2637;color:#f0f4fa;border:1px solid #57697b;border-radius:8px;padding:12px;font:14px monospace}}
button{{background:#7ecbb7;color:#061315;border:0;border-radius:8px;padding:12px 24px;font-weight:700;cursor:pointer}}
pre{{white-space:pre-wrap;overflow-wrap:anywhere;background:#1a2637;border-radius:8px;padding:16px;max-height:300px;overflow:auto}}
small,.muted{{color:#c1c9d1}}table{{border-collapse:collapse;width:100%;table-layout:fixed}}th,td{{padding:8px;border-bottom:1px solid #3b4c60;text-align:left;overflow-wrap:anywhere}}th{{width:36%;color:#b1c6dd}}section{{margin:24px 0 60px}}h3{{font-size:1rem}}</style>
<h1>{escaped(APP)}</h1><p>Deliberately vulnerable training environment. Docker Compose publishes the port on host loopback only.</p>
<form method="POST" action="/submit"><label for="payload">Serialized payload</label>
<textarea id="payload" name="payload" required spellcheck="false">{escaped(value)}</textarea>
<p><button type="submit">Run</button></p></form>
<p class="muted">Paste any payload from payloads.md. Normal and gadget inputs use exactly the same deserialization path. Output and observed side effects are displayed below; absence of a failure does not prove code execution.</p>
<small>Jackson Java (8081) accepts JSON. Java Native (8085), .NET, PHP and Python accept Base64.</small>{section}</html>'''


def jackson_page():
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escaped(APP)} - Burp JSON Lab</title>
<style>body{{font:16px/1.5 system-ui;background:#101722;color:#e8eef9;max-width:920px;margin:5vh auto;padding:0 20px}}textarea{{box-sizing:border-box;width:100%;height:220px;background:#1a2637;color:#f0f4fa;border:1px solid #57697b;border-radius:8px;padding:12px;font:14px monospace}}button{{background:#7ecbb7;color:#061315;border:0;border-radius:8px;padding:12px 24px;font-weight:700;cursor:pointer}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;background:#1a2637;border-radius:8px;padding:16px;max-height:450px;overflow:auto}}small,.muted{{color:#c1c9d1}}code{{color:#8de2c4}}</style></head><body>
<h1>{escaped(APP)}</h1><p>Use this form or intercept the <code>POST /api/deserialize</code> request in Burp. The submitted request body is JSON, not a form field.</p>
<label for="payload">Raw JSON request body</label><textarea id="payload" spellcheck="false">{{
  "@class": "java.util.LinkedHashMap",
  "message": "hello-from-jackson"
}}</textarea><p><button id="run" type="button">Run</button></p>
<p class="muted">Request: <code>POST /api/deserialize</code> · <code>Content-Type: application/json</code>. Response: <code>{{"resp":"..."}}</code>, containing the message or observed command output.</p>
<h2>HTTP response</h2><pre id="output" aria-live="polite">No request sent yet.</pre>
<script>
const btn=document.getElementById('run');const out=document.getElementById('output');
btn.addEventListener('click',async()=>{{btn.disabled=true;out.textContent='Sending raw JSON...';try{{const r=await fetch('/api/deserialize',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:document.getElementById('payload').value}});const t=await r.text();try{{out.textContent=JSON.stringify(JSON.parse(t),null,2)}}catch{{out.textContent=t}}}}catch(e){{out.textContent='Network error: '+e.message}}finally{{btn.disabled=false}}}});
</script></body></html>'''

def inspect_format(payload):
    if 'Jackson' in APP:
        return 'JSON text (direct deserialization)'
    try:
        raw = base64.b64decode(payload, validate=True)
    except (ValueError, base64.binascii.Error):
        return 'Base64 validation failed'
    signature = ' '.join('{:02x}'.format(b) for b in raw[:4])
    suffix = ' [Java serialization magic OK]' if PROOF_PATH and raw.startswith(b'\xac\xed\x00\x05') else ''
    return f'{len(raw)} decoded bytes; first bytes: {signature}{suffix}'

def run_and_capture(payload):
    with RUN_LOCK:  # proof file belongs only to the current request
        old_removed = False
        if PROOF_PATH is not None:
            try:
                
                if PROOF_PATH.exists():
                    PROOF_PATH.unlink()
                old_removed = True
            except OSError:
                pass
        t0 = time.monotonic()
        run_id = uuid.uuid4().hex[:12]
        now = datetime.now(timezone.utc).isoformat(timespec='seconds')
        stdout = stderr = ''
        code = None
        timed_out = False
        try:
            result = subprocess.run(CMD, input=payload+'\n', text=True,
                                    capture_output=True, timeout=8, cwd='/app', errors='replace')
            code, stdout, stderr = result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            stdout = (exc.stdout or b'').decode('utf-8', 'replace') if isinstance(exc.stdout, bytes) else (exc.stdout or '')
            stderr = (exc.stderr or b'').decode('utf-8', 'replace') if isinstance(exc.stderr, bytes) else (exc.stderr or '')
        except OSError as exc:
            stderr = f'Failed to launch lab process: {exc}'
        marker = bool(PROOF_PATH and old_removed and PROOF_PATH.is_file())
        duration = round((time.monotonic() - t0)*1000)
        # Avoid claiming the exploit succeeded just because readObject() returned.
        if marker:
            status = 'OS side effect observed (fresh proof file)'
        elif timed_out:
            status = 'Timed out; OS execution unconfirmed'
        elif code == 0:
            status = 'Deserialization process completed; inspect stdout for effects'
        else:
            status = 'Process error; OS execution unconfirmed'
        facts = [
            ('Request ID', run_id), ('UTC time', now),
            ('SHA-256 of submitted input', hashlib.sha256(payload.encode()).hexdigest()),
            ('Payload format', inspect_format(payload)),
            ('Exit code', 'timeout' if timed_out else (code if code is not None else 'not started')),
            ('Duration', f'{duration} ms'),
        ]
        if PROOF_PATH:
            facts.append(('Fresh OS side-effect proof',
                          'YES: /tmp/cc6-proof created during this request' if marker
                          else ('NOT VERIFIED (cannot clear prior marker)' if not old_removed
                                else 'NO: /tmp/cc6-proof not found')))
        trace = '\n'.join(line for line in (stdout + '\n' + stderr).splitlines()
                          if line.startswith(('[1]', '[2]', '[3]', '[4]', '[5]', '[os stdout]', '[os exit]', '[gadget]')))
        if not trace:
            trace = 'No instrumented gadget trace emitted. See stdout/stderr and side-effect evidence.'
        return {'status':status, 'facts':facts, 'stdout':stdout or '(empty)',
                'stderr':stderr or '(empty)', 'trace':trace}

def jackson_response(evidence):
    """Return only actual application message or OS stdout; never invent success."""
    stdout = evidence['stdout'] if evidence['stdout'] != '(empty)' else ''
    stderr = evidence['stderr'] if evidence['stderr'] != '(empty)' else ''
    os_lines = [line[len('[os stdout] '):] for line in stdout.splitlines()
                if line.startswith('[os stdout] ')]
    if os_lines:
        return '\n'.join(os_lines)
    messages = [line[len('[response] '):] for line in stdout.splitlines()
                if line.startswith('[response] ')]
    if messages:
        return '\n'.join(messages)
    # Deserialization may have failed before any visible result.
    if stderr.strip():
        return 'Error: ' + stderr.strip()[-3000:]
    if evidence['status'].startswith(('Timed out', 'Process error')):
        return 'Error: ' + evidence['status']
    return 'No response value produced by deserialization.'

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/healthz':
            self.respond_json({'status': 'ok', 'service': APP})
            return
        if self.path != '/':
            self.send_error(404); return
        self.respond(jackson_page() if 'Jackson' in APP else page())

    def do_POST(self):
        if 'Jackson' in APP and self.path == '/api/deserialize':
            self.handle_json_submission()
            return
        if self.path != '/submit':
            self.send_error(404); return
        if 'Jackson' in APP:
            self.send_error(415, 'Use POST /api/deserialize with application/json')
            return
        try:
            size = int(self.headers.get('Content-Length','0'))
            if size < 1 or size > MAX_PAYLOAD * 3:
                self.send_error(413); return
            fields = parse_qs(self.rfile.read(size).decode('utf-8'), keep_blank_values=True)
            payload = fields.get('payload', [''])[0].strip()
            if not payload or len(payload) > MAX_PAYLOAD:
                self.send_error(413); return
            self.respond(page(payload, run_and_capture(payload)))
        except (UnicodeError, ValueError) as exc:
            self.send_error(400, str(exc))

    def handle_json_submission(self):
        import json
        if self.headers.get('Content-Type', '').split(';',1)[0].strip().lower() != 'application/json':
            self.respond_json({'resp': 'Error: Content-Type must be application/json'}, 415); return
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if size < 1 or size > MAX_PAYLOAD:
                self.respond_json({'resp': 'Error: JSON body missing or too large'}, 413); return
            raw = self.rfile.read(size)
            payload = raw.decode('utf-8')
            json.loads(payload)  # validate JSON syntax; Java still performs the actual deserialization
        except (UnicodeError, ValueError, json.JSONDecodeError) as exc:
            self.respond_json({'resp': 'Error: Invalid JSON body: ' + str(exc)}, 400); return
        try:
            evidence = run_and_capture(payload)
            self.respond_json({'resp': jackson_response(evidence)})
        except Exception as exc:
            # Application failures should return a response, not an empty connection.
            self.log_error('Uncaught processing exception: %s', repr(exc))
            self.respond_json({'resp': 'Error: Lab execution failed: ' + str(exc)}, 500)

    def respond_json(self, obj, status=200):
        import json
        self.respond_bytes(json.dumps(obj, ensure_ascii=False, indent=2).encode('utf-8'), status, 'application/json; charset=utf-8')

    def respond(self, body):
        self.respond_bytes(body.encode('utf-8'), 200, 'text/html; charset=utf-8')

    def respond_bytes(self, data, status, content_type):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        csp = "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'" if 'Jackson' in APP else "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'"
        self.send_header('Content-Security-Policy', csp)
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', 8080), Handler).serve_forever()
