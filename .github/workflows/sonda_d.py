"""Muestreador: cada 2 s apunta memoria disponible y retransmisiones TCP."""
import time, sys, pathlib
def retrans():
    for l in pathlib.Path("/proc/net/snmp").read_text().splitlines():
        if l.startswith("Tcp:"):
            campos = l.split()
            if campos[1].isdigit() or campos[1].lstrip("-").isdigit():
                return int(campos[hdr.index("RetransSegs")])
            hdr[:] = campos
    return -1
hdr = []
out = open(sys.argv[1], "a")
while True:
    mem = next(l for l in pathlib.Path("/proc/meminfo").read_text().splitlines()
               if l.startswith("MemAvailable"))
    r = retrans()
    out.write("%.1f mem_kB=%s retrans=%d\n" % (time.time(), mem.split()[1], r))
    out.flush()
    time.sleep(2)
