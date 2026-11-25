"""Bind an inspected face selection to its exact source asset and topology."""
def face_selection(document,source_sha256,face_count):
    if document.get('source_glb_sha256')!=source_sha256:
        raise ValueError('Reviewed selection belongs to a different source')
    faces=document.get('selected')
    if not isinstance(faces,list) or not faces or any(type(i) is not int or not 0<=i<face_count for i in faces):
        raise ValueError('Nonempty in-range integer face IDs required')
    if len(set(faces))!=len(faces):
        raise ValueError('Duplicate reviewed face IDs')
    return set(faces)
