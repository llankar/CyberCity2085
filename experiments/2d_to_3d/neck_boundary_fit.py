"""Localized harmonic fitting of an existing anatomical neck boundary."""
import heapq
import numpy as np


def closed_loop(edges):
    neighbors={}
    for a,b in edges:
        if a==b:raise ValueError('Degenerate boundary edge')
        neighbors.setdefault(a,set()).add(b);neighbors.setdefault(b,set()).add(a)
    if len(neighbors)<3 or any(len(n)!=2 for n in neighbors.values()):
        raise ValueError('One closed unbranched boundary required')
    start=min(neighbors);ordered=[start];previous=None;current=start
    while True:
        following=min(n for n in neighbors[current] if n!=previous)
        if following==start:break
        if following in ordered:raise ValueError('Invalid boundary cycle')
        ordered.append(following);previous,current=current,following
    if len(ordered)!=len(neighbors):raise ValueError('Disconnected boundary loops')
    return ordered


def fit_boundary(points,edges,boundary,target_z,protected=(),radius=.06):
    points=np.asarray(points,dtype=float)
    if points.ndim!=2 or points.shape[1]!=3 or not np.isfinite(points).all() or not np.isfinite(target_z) or not np.isfinite(radius) or radius<=0:
        raise ValueError('Finite points and positive anatomical band required')
    boundary=set(boundary);protected=set(protected)
    if not boundary or boundary&protected or any(i<0 or i>=len(points) for i in boundary|protected):
        raise ValueError('Disjoint valid boundary/protected vertices required')
    if target_z>=min(points[i,2] for i in boundary):raise ValueError('Target must extend below the entire source boundary')
    adjacency=[{} for _ in points]
    for a,b in edges:
        if a<0 or b<0 or a>=len(points) or b>=len(points):raise ValueError('Invalid source edge')
        length=float(np.linalg.norm(points[a]-points[b]))
        if length<1e-10:continue
        adjacency[a][b]=length;adjacency[b][a]=length
    distances=[float('inf')]*len(points);queue=[]
    for i in boundary:distances[i]=0.;heapq.heappush(queue,(0.,i))
    while queue:
        distance,i=heapq.heappop(queue)
        if distance!=distances[i]:continue
        for j,length in adjacency[i].items():
            if distance+length<distances[j]:
                distances[j]=distance+length;heapq.heappush(queue,(distances[j],j))
    unknown=[i for i,d in enumerate(distances) if d<radius and i not in boundary|protected]
    lookup={v:i for i,v in enumerate(unknown)}
    displacement=np.zeros(len(points))
    for i in boundary:displacement[i]=target_z-points[i,2]
    if unknown:
        matrix=np.zeros((len(unknown),len(unknown)));rhs=np.zeros(len(unknown))
        for vertex,row in lookup.items():
            for neighbor,length in adjacency[vertex].items():
                weight=1/length;matrix[row,row]+=weight
                if neighbor in lookup:matrix[row,lookup[neighbor]]-=weight
                else:rhs[row]+=weight*displacement[neighbor]
        displacement[unknown]=np.linalg.solve(matrix,rhs)
    if not np.isfinite(displacement).all() or displacement.max()>1e-10:
        raise ValueError('Invalid anatomical extension solution')
    result=points.copy();result[:,2]+=displacement
    return result,displacement


def neck_weights(height):
    if not np.isfinite(height):raise ValueError('Finite neck height required')
    def smooth(t):
        t=max(0.,min(1.,t));return t*t*(3-2*t)
    if height<1.49:
        neck=smooth((height-1.43)/.06)
        return {'Spine02':1-neck,'neck':neck,'Head':0.}
    head=smooth((height-1.49)/.065)
    return {'Spine02':0.,'neck':1-head,'Head':head}
