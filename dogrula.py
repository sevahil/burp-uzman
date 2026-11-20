import hashlib
import json
import fnmatch
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
MANIFEST_NAME = "manifest.sha256"
MANIFEST_DIRS = ("bchecks", "configs", "auth", "kapsam")
MANIFEST_FILES = ("bapps.md", "kabul-windows.md")
MAX_BYTES = 65536
FORBIDDEN = re.compile(r"\b(claude|anthropic|opus|sonnet|fable)\b|generated with", re.I)
RESERVED = {"base", "latest", "response", "request", "user_agent", "insertion_point_base_value"}
SEVERITIES = ("info", "low", "medium", "high")
CONFIDENCES = ("certain", "firm", "tentative")
PROP_ORDER = ("name", "severity", "confidence", "remediation", "detail")
META_KEYS = ("language", "name", "description", "author", "tags")
SECRET_KEY = re.compile(
    r"(^|[_\-. ])(password|passwd|pwd|secret|token|api[_-]?key|cookie|authorization|credentials?)($|[_\-. ])",
    re.I,
)
REQUIRED_IGNORE = ("*.burp", "*.har", "*.token", "*.env", "auth/private/", "configs/private/", "raporlar/")

GIVEN = re.compile(
    r"^given\s+(response|request|host|path"
    r"|(?:any\s+)?insertion\s+point"
    r"|(?:query|header|body|cookie)(?:\s+or\s+(?:query|header|body|cookie))*\s+insertion\s+point)\s+then$"
)
DEFINE = re.compile(r"^define\s*:\s*(\w+)\s*=")
RUN_EACH = re.compile(r"^run\s+for\s+each\s*:\s*(\w+)\s*=")
IF = re.compile(r"^if\s+(.+?)\s+then$")
ELIF = re.compile(r"^else\s+if\s+(.+?)\s+then$")
ELSE = re.compile(r"^else\s+then$")
CONDITION_OP = re.compile(r"\b(matches|differs\s+from|in|is)\b|interactions")
ENDIF = re.compile(r"^end\s+if$")
BACKTICK_MATCHES = re.compile(r"\bmatches\s*`")
SEND_REQ = re.compile(r"^send\s+request(?:\s+called\s+(\S+?))?\s*:")
SEND_PAY = re.compile(r"^send\s+payload(?:\s+called\s+(\S+?))?\s*:")
REPORT = re.compile(r"^report\s+issue(\s+and\s+continue)?\s*:")
ISSUE_PROP = re.compile(r"^(name|severity|confidence|remediation|detail)\s*:\s*(.*)$")
REQ_PROP = re.compile(
    r"^(?:(?:appending|replacing|removing)\s+(?:headers|queries|query_string|path|method|body)\s*:"
    r"|removing\s+(?:body|query_string|path|method)\s*$"
    r"|(?:appending|replacing)\s*:"
    r"|(?:headers|queries|query_string|path|method|body)\s*:)"
)
META_LINE = re.compile(r"^(language|name|description|author|tags)\s*:")


def scrub(text):
    out = []
    errors = []
    i = 0
    n = len(text)
    line = 1
    quote = None
    start_line = 0
    while i < n:
        c = text[i]
        if quote:
            if c == "\\" and i + 1 < n:
                out.append(" ")
                nxt = text[i + 1]
                if nxt == "\n":
                    out.append("\n")
                    line += 1
                else:
                    out.append(" ")
                i += 2
                continue
            if c == quote:
                out.append(c)
                quote = None
            elif c == "\n":
                out.append("\n")
                line += 1
            else:
                out.append(" ")
            i += 1
            continue
        if c in "\"`":
            quote = c
            start_line = line
            out.append(c)
            i += 1
            continue
        if c == "#":
            errors.append((line, "yorum satiri yasak"))
            while i < n and text[i] != "\n":
                out.append(" ")
                i += 1
            continue
        if c == "\n":
            line += 1
        out.append(c)
        i += 1
    if quote:
        errors.append((start_line, "kapanmamis metin"))
    return "".join(out), errors


def _line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def _value(orig_line):
    _, _, rest = orig_line.partition(":")
    return rest.strip().strip("\"`").strip()


def lint_bcheck(text):
    errors = []
    warnings = []
    if len(text.encode("utf-8")) > MAX_BYTES:
        errors.append((0, "dosya cok buyuk"))
    for m in FORBIDDEN.finditer(text):
        errors.append((_line_of(text, m.start()), "yasak ibare: " + m.group(0)))
    clean, scrub_errors = scrub(text)
    errors.extend(scrub_errors)
    lines = clean.split("\n")
    orig = text.split("\n")
    state = "start"
    meta = {}
    given_kind = None
    given_count = 0
    stack = []
    reports = 0
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        no = i + 1
        if not s:
            i += 1
            continue
        if state == "start":
            if s == "metadata:":
                state = "meta"
                i += 1
                continue
            errors.append((no, "metadata: ilk satir olmali"))
            state = "meta"
        if state == "meta":
            if META_LINE.match(s):
                key = META_LINE.match(s).group(1)
                if key in meta:
                    errors.append((no, "tekrarlanan metadata alani: " + key))
                meta[key] = _value(orig[i])
                i += 1
                continue
            state = "header"
        if state == "header":
            if DEFINE.match(s) or RUN_EACH.match(s):
                name = (DEFINE.match(s) or RUN_EACH.match(s)).group(1)
                if name in RESERVED:
                    errors.append((no, "ayrilmis degisken adi: " + name))
                i += 1
                continue
            m = GIVEN.match(s)
            if m:
                given_count += 1
                kind = m.group(1)
                given_kind = "insertion" if "insertion" in kind else kind
                state = "body"
                i += 1
                continue
            warnings.append((no, "given oncesi taninmayan satir"))
            i += 1
            continue
        if GIVEN.match(s):
            given_count += 1
            errors.append((no, "tek given...then olmali"))
            i += 1
            continue
        if DEFINE.match(s) or RUN_EACH.match(s):
            errors.append((no, "define/run for each given oncesinde olmali"))
            i += 1
            continue
        if ELIF.match(s) or ELSE.match(s):
            if not stack:
                errors.append((no, "if olmadan else"))
            if ELIF.match(s) and not CONDITION_OP.search(ELIF.match(s).group(1)):
                errors.append((no, "gecersiz kosul"))
            if BACKTICK_MATCHES.search(s):
                errors.append((no, "matches yalniz cift tirnakli duz regex alir"))
            i += 1
            continue
        if IF.match(s):
            if not CONDITION_OP.search(IF.match(s).group(1)):
                errors.append((no, "gecersiz kosul"))
            if BACKTICK_MATCHES.search(s):
                errors.append((no, "matches yalniz cift tirnakli duz regex alir"))
            stack.append(no)
            i += 1
            continue
        if s.startswith(("if ", "else ")):
            errors.append((no, "kosul satiri then ile bitmeli"))
            i += 1
            continue
        if ENDIF.match(s):
            if not stack:
                errors.append((no, "if olmadan end if"))
            else:
                stack.pop()
            i += 1
            continue
        m = SEND_REQ.match(s) or SEND_PAY.match(s)
        if m:
            is_payload = bool(SEND_PAY.match(s))
            if is_payload and given_kind != "insertion":
                errors.append((no, "send payload yalniz insertion point given ile"))
            if not is_payload and given_kind == "response":
                errors.append((no, "send request given response ile gecersiz"))
            if m.group(1) and m.group(1).strip("\"`") in RESERVED:
                errors.append((no, "ayrilmis degisken adi: " + m.group(1)))
            i += 1
            while i < len(lines) and (not lines[i].strip() or REQ_PROP.match(lines[i].strip())):
                i += 1
            continue
        if REPORT.match(s):
            reports += 1
            props = []
            i += 1
            while i < len(lines):
                t = lines[i].strip()
                if not t:
                    i += 1
                    continue
                pm = ISSUE_PROP.match(t)
                if not pm:
                    break
                props.append((pm.group(1), pm.group(2).strip(), i + 1))
                i += 1
            keys = [p[0] for p in props]
            for key in keys:
                if keys.count(key) > 1:
                    errors.append((no, "tekrarlanan issue alani: " + key))
                    break
            order = [PROP_ORDER.index(k) for k in keys]
            if order != sorted(order):
                errors.append((no, "issue alan sirasi: name, severity, confidence, remediation, detail"))
            sev = [p for p in props if p[0] == "severity"]
            conf = [p for p in props if p[0] == "confidence"]
            if not sev:
                errors.append((no, "severity eksik"))
            elif sev[0][1] not in SEVERITIES:
                errors.append((sev[0][2], "gecersiz severity: " + sev[0][1]))
            if not conf:
                errors.append((no, "confidence eksik"))
            elif conf[0][1] not in CONFIDENCES:
                errors.append((conf[0][2], "gecersiz confidence: " + conf[0][1]))
            continue
        warnings.append((no, "taninmayan satir"))
        i += 1
    if state == "start":
        errors.append((0, "bos dosya"))
    if given_count != 1:
        errors.append((0, "tam olarak bir given...then olmali (bulunan: %d)" % given_count))
    if stack:
        errors.append((stack[-1], "kapanmamis if"))
    if given_count and reports == 0:
        errors.append((0, "report issue yok"))
    if meta.get("language") != "v2-beta":
        errors.append((0, "metadata language v2-beta olmali"))
    if not meta.get("name"):
        errors.append((0, "metadata name eksik"))
    return sorted(errors), sorted(warnings)


VALUE_SECRET = re.compile(r"\b(bearer|basic)\s+[A-Za-z0-9._~+/=-]{6,}|eyJ[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{5,}\.", re.I)


def _has_content(node):
    if isinstance(node, str):
        return bool(node.strip())
    if isinstance(node, dict):
        return any(_has_content(v) for v in node.values())
    if isinstance(node, list):
        return any(_has_content(v) for v in node)
    return False


def _walk(node, path, errors):
    if isinstance(node, dict):
        name = node.get("name")
        if isinstance(name, str) and SECRET_KEY.search(name) and _has_content(node.get("value")):
            errors.append("sir olabilir: " + path + " (" + name + ")")
        for key, value in node.items():
            here = path + "/" + str(key)
            if SECRET_KEY.search(str(key)) and _has_content(value):
                errors.append("sir olabilir: " + here)
            _walk(value, here, errors)
    elif isinstance(node, list):
        for idx, value in enumerate(node):
            _walk(value, path + "/" + str(idx), errors)
    elif isinstance(node, str) and VALUE_SECRET.search(node):
        errors.append("sir olabilir: " + path)


def check_config_json(text):
    try:
        data = json.loads(text)
    except ValueError as exc:
        return ["gecersiz JSON: " + str(exc)]
    if not isinstance(data, dict):
        return ["kok oge nesne olmali"]
    errors = []
    _walk(data, "", errors)
    return errors


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def manifest_paths(root):
    found = []
    for d in MANIFEST_DIRS:
        base = os.path.join(root, d)
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames.sort()
            for name in sorted(filenames):
                found.append(os.path.relpath(os.path.join(dirpath, name), root))
    for name in MANIFEST_FILES:
        if os.path.isfile(os.path.join(root, name)):
            found.append(name)
    return sorted(found)


def manifest_write(root):
    lines = ["%s  %s" % (sha256_file(os.path.join(root, p)), p) for p in manifest_paths(root)]
    with open(os.path.join(root, MANIFEST_NAME), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return len(lines)


def manifest_check(root):
    path = os.path.join(root, MANIFEST_NAME)
    if not os.path.isfile(path):
        return ["manifest.sha256 yok"]
    recorded = {}
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            raw = raw.rstrip("\n")
            if not raw:
                continue
            digest, _, rel = raw.partition("  ")
            recorded[rel] = digest
    errors = []
    actual = manifest_paths(root)
    for rel in actual:
        if rel not in recorded:
            errors.append("manifestte yok: " + rel)
        elif sha256_file(os.path.join(root, rel)) != recorded[rel]:
            errors.append("hash uyusmuyor: " + rel)
    for rel in recorded:
        if rel not in actual:
            errors.append("dosya eksik: " + rel)
    return errors


def _negates_required(pattern):
    for req in REQUIRED_IGNORE:
        if pattern == req or fnmatch.fnmatch(pattern, req) or req.startswith(pattern):
            return True
    return False


def check_gitignore(root):
    path = os.path.join(root, ".gitignore")
    if not os.path.isfile(path):
        return [".gitignore yok"]
    with open(path, encoding="utf-8") as fh:
        entries = {ln.strip() for ln in fh if ln.strip()}
    problems = [".gitignore eksik giris: " + e for e in REQUIRED_IGNORE if e not in entries]
    problems.extend(
        ".gitignore negasyon yasak: " + e
        for e in sorted(entries)
        if e.startswith("!") and _negates_required(e[1:])
    )
    return problems


def run_all(root):
    problems = []
    notes = []
    checked = 0
    bdir = os.path.join(root, "bchecks")
    for dirpath, dirnames, filenames in os.walk(bdir):
        dirnames.sort()
        for name in sorted(filenames):
            if not name.endswith(".bcheck"):
                continue
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, root)
            with open(full, encoding="utf-8") as fh:
                errs, warns = lint_bcheck(fh.read())
            checked += 1
            for no, msg in errs:
                problems.append("%s:%d: %s" % (rel, no, msg))
            for no, msg in warns:
                problems.append("%s:%d: dogrulanamayan sozdizimi: %s" % (rel, no, msg))
    for rel in manifest_paths(root):
        if not rel.endswith(".json"):
            continue
        with open(os.path.join(root, rel), encoding="utf-8") as fh:
            for msg in check_config_json(fh.read()):
                problems.append("%s: %s" % (rel, msg))
        checked += 1
    problems.extend(check_gitignore(root))
    problems.extend(manifest_check(root))
    return checked, problems, notes


def main(argv):
    if len(argv) > 1 and argv[1] == "--manifest-yaz":
        print("manifest yazildi: %d dosya" % manifest_write(ROOT))
        return 0
    if len(argv) > 1:
        with open(argv[1], encoding="utf-8") as fh:
            errs, warns = lint_bcheck(fh.read())
        for no, msg in errs:
            print("%s:%d: %s" % (argv[1], no, msg))
        for no, msg in warns:
            print("%s:%d: dogrulanamayan sozdizimi: %s" % (argv[1], no, msg))
        return 1 if errs or warns else 0
    checked, problems, notes = run_all(ROOT)
    for line in notes:
        print(line)
    for line in problems:
        print("HATA " + line)
    if problems:
        print("basarisiz: %d sorun" % len(problems))
        return 1
    print("statik kontroller gecti (%d dosya); Burp kabul testi bekliyor: kabul-windows.md" % checked)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
