"""Cruza los huecos del log DEBUG con el muestreador de memoria/retransmisiones."""
import re, sys, pathlib, datetime

log, sampler, tag = sys.argv[1], sys.argv[2], sys.argv[3]

muestras = []
for l in pathlib.Path(sampler).read_text().splitlines():
    m = re.match(r"([0-9.]+) mem_kB=(\d+) retrans=(-?\d+)", l)
    if m:
        muestras.append((float(m[1]), int(m[2]), int(m[3])))

# los huecos, en tiempo epoch: el log usa HH:MM:SS local del runner (UTC)
hoy = datetime.date.today()
def epoch(hms, ms):
    h, mi, s = map(int, hms.split(":"))
    dt = datetime.datetime(hoy.year, hoy.month, hoy.day, h, mi, s,
                           tzinfo=datetime.timezone.utc)
    return dt.timestamp() + ms/1000.0

lineas = []
for l in pathlib.Path(log).read_text(errors="replace").splitlines():
    m = re.match(r"(\d\d:\d\d:\d\d)\.(\d\d\d) ", l)
    if m:
        lineas.append((epoch(m[1], int(m[2])), l[:150]))

for a, b in zip(lineas, lineas[1:]):
    gap = b[0] - a[0]
    if gap > 20:
        print("GAP[%s] %.1f s  (%s -> %s)" % (tag, gap, a[1][:12], b[1][:12]))
        print("   antes:   %s" % a[1][13:])
        print("   despues: %s" % b[1][13:])
        dentro = [x for x in muestras if a[0] - 4 <= x[0] <= b[0] + 4]
        if dentro:
            r0, r1 = dentro[0][2], dentro[-1][2]
            mems = [x[1] for x in dentro]
            print("   RETRANS durante el hueco: %d -> %d  (delta %d)" % (r0, r1, r1 - r0))
            print("   MemAvailable: min %d MB, max %d MB" % (min(mems)//1024, max(mems)//1024))
        else:
            print("   (sin muestras en la ventana)")
