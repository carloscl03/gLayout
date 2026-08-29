"""Encuentra los silencios en el log DEBUG de nbconvert y cronometra celdas.

Un cuelgue de mensaje perdido se ve como un hueco largo entre dos lineas de
log; lo que haya justo antes del hueco es lo que se estaba esperando.
"""
import json, re, sys, pathlib

log, nb, tag = sys.argv[1], sys.argv[2], sys.argv[3]

# huecos > 20 s entre lineas con timestamp HH:MM:SS.mmm
lineas = []
for l in pathlib.Path(log).read_text(errors="replace").splitlines():
    m = re.match(r"(\d\d):(\d\d):(\d\d)\.(\d\d\d) ", l)
    if m:
        t = int(m[1])*3600 + int(m[2])*60 + int(m[3]) + int(m[4])/1000.0
        lineas.append((t, l[:170]))
for a, b in zip(lineas, lineas[1:]):
    gap = b[0] - a[0]
    if gap > 20:
        print("GAP[%s] %.1f s de silencio" % (tag, gap))
        print("   antes: %s" % a[1])
        print("   despues: %s" % b[1])

# cronometraje por celda del notebook ejecutado (record_timing)
try:
    doc = json.loads(pathlib.Path(nb).read_text(encoding="utf-8"))
    for i, c in enumerate(doc.get("cells", [])):
        ex = c.get("metadata", {}).get("execution", {})
        ini, fin = ex.get("iopub.execute_input"), ex.get("shell.execute_reply")
        if ini and fin:
            from datetime import datetime
            f = "%Y-%m-%dT%H:%M:%S.%fZ"
            try:
                d = (datetime.strptime(fin, f) - datetime.strptime(ini, f)).total_seconds()
                if d > 5:
                    src = "".join(c.get("source", []))[:60].replace("\n", " ")
                    print("CELL[%s] celda %d: %.1f s  | %s" % (tag, i, d, src))
            except ValueError:
                pass
except Exception as e:
    print("CELL[%s] sin notebook ejecutado (%s)" % (tag, type(e).__name__))
