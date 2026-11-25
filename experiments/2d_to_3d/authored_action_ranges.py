"""Read the authored IQM name:start:end:fps[:loop] export table."""
import math


def source_action_ranges(text):
    result={}
    for line in text.splitlines():
        line=line.strip()
        if not line or line.startswith('#'):continue
        fields=line.split(':')
        if len(fields) not in (4,5) or not fields[0] or fields[0] in result:raise ValueError('Invalid or duplicate authored action')
        first,last=int(fields[1]),int(fields[2]);fps=float(fields[3])
        if last<first or not math.isfinite(fps) or not 0<fps<=240:raise ValueError('Invalid authored frame range/rate')
        if len(fields)==5 and fields[4] not in ('0','1'):raise ValueError('Invalid loop flag')
        result[fields[0]]={'first':first,'last':last,'fps':fps,'loop':bool(int(fields[4])) if len(fields)==5 else None}
    return result
