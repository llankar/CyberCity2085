"""Exact exposed surfaces of the existing map's stepped cell volumes."""
import math


def surfaces(heights):
    if not heights or any(len(cell)!=2 or any(type(v) is not int for v in cell) or
                          not math.isfinite(height) or height<=0 for cell,height in heights.items()):
        raise ValueError('Integer cell coordinates and positive finite heights required')
    levels = sorted({0.,*heights.values()})
    output = []
    for (x,y),height in sorted(heights.items()):
        output.append(('roof',(x,y),[(x,y,height),(x+1,y,height),(x+1,y+1,height),(x,y+1,height)]))
        output.append(('bottom',(x,y),[(x,y,0),(x,y+1,0),(x+1,y+1,0),(x+1,y,0)]))
        for dx,dy in ((-1,0),(1,0),(0,-1),(0,1)):
            neighbor = heights.get((x+dx,y+dy),0)
            for low,high in zip(levels,levels[1:]):
                if low < neighbor or high > height:
                    continue
                if dx == -1: points=[(x,y,low),(x,y,high),(x,y+1,high),(x,y+1,low)]
                elif dx == 1: points=[(x+1,y,low),(x+1,y+1,low),(x+1,y+1,high),(x+1,y,high)]
                elif dy == -1: points=[(x,y,low),(x+1,y,low),(x+1,y,high),(x,y,high)]
                else: points=[(x,y+1,low),(x,y+1,high),(x+1,y+1,high),(x+1,y+1,low)]
                output.append(('wall',(x,y),points))
    return output
