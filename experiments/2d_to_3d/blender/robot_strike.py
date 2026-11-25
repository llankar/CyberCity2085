"""A staged open-hand mechanical strike target, in source-world metres."""


def strike_offset(time_s):
    keys = [(0., (0., 0., 0.)), (.32, (0., .10, .40)),
            (.50, (0., -.50, .52)), (.60, (0., -.50, .52)),
            (1., (0., 0., 0.))]
    time_s = min(1., max(0., time_s))
    for (start, first), (end, second) in zip(keys, keys[1:]):
        if time_s <= end:
            p = (time_s-start)/(end-start)
            blend = p*p*(3-2*p)
            return tuple(a+(b-a)*blend for a,b in zip(first,second))
    return keys[-1][1]
