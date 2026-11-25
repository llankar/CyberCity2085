"""Select anatomical skin groups by rig ancestry, never by naming substrings."""
def descendants(parents,root):
    if root not in parents:raise ValueError('Anatomical root missing')
    selected=set()
    for name in parents:
        chain=set();current=name
        while current is not None:
            if current not in parents:raise ValueError('Unknown bone parent')
            if current in chain:raise ValueError('Cyclic bone hierarchy')
            chain.add(current);current=parents[current]
        if root in chain:selected.add(name)
    return selected
