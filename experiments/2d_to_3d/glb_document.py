"""Small strict reader for local experimental, single-buffer GLB files."""
import copy
import json
import struct

COMPONENT_BYTES={5120:1,5121:1,5122:2,5123:2,5125:4,5126:4}
COMPONENTS={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}


class Glb:
    def __init__(self,path):
        payload=path.read_bytes()
        if len(payload)<28 or struct.unpack_from('<III',payload)!=(0x46546c67,2,len(payload)):
            raise ValueError('Invalid GLB header')
        size,kind=struct.unpack_from('<II',payload,12)
        if kind!=0x4e4f534a: raise ValueError('JSON chunk required')
        self.doc=json.loads(payload[20:20+size])
        start=20+size
        binary_size,binary_kind=struct.unpack_from('<II',payload,start)
        if binary_kind!=0x004e4942 or start+8+binary_size!=len(payload):
            raise ValueError('Exactly one binary chunk required')
        self.bin=bytearray(payload[start+8:])
        if len(self.doc['buffers'])!=1 or 'uri' in self.doc['buffers'][0]:
            raise ValueError('One embedded buffer required')
        declared=self.doc['buffers'][0]['byteLength']
        if declared<0 or not 0<=len(self.bin)-declared<=3: raise ValueError('Invalid embedded buffer length')
        for view in self.doc.get('bufferViews',[]):
            if view.get('buffer')!=0 or view.get('byteOffset',0)<0 or view['byteLength']<0 or view.get('byteOffset',0)+view['byteLength']>declared:
                raise ValueError('Buffer view outside embedded buffer')

    def values(self,index):
        accessor=self.doc['accessors'][index]
        if 'sparse' in accessor: raise ValueError('Sparse accessor requires explicit expansion')
        view=self.doc['bufferViews'][accessor['bufferView']]
        width=COMPONENT_BYTES[accessor['componentType']]*COMPONENTS[accessor['type']]
        stride=view.get('byteStride',width)
        if stride<width or accessor['count']<1 or accessor.get('byteOffset',0)<0:
            raise ValueError('Invalid accessor layout')
        start=view.get('byteOffset',0)+accessor.get('byteOffset',0)
        if accessor['count'] and start+(accessor['count']-1)*stride+width>view.get('byteOffset',0)+view['byteLength']:
            raise ValueError('Accessor outside view')
        return b''.join(self.bin[start+i*stride:start+i*stride+width] for i in range(accessor['count']))

    def copy_accessor(self,source,index):
        accessor=copy.deepcopy(source.doc['accessors'][index])
        raw=source.values(index)
        self.bin.extend(b'\0'*(-len(self.bin)%4))
        view={'buffer':0,'byteOffset':len(self.bin),'byteLength':len(raw)}
        self.bin.extend(raw)
        accessor['bufferView']=len(self.doc['bufferViews'])
        accessor.pop('byteOffset',None)
        self.doc['bufferViews'].append(view)
        self.doc['accessors'].append(accessor)
        return len(self.doc['accessors'])-1

    def add_floats(self,values,count,type_name='SCALAR'):
        if count<1 or len(values)!=count*COMPONENTS[type_name]: raise ValueError('Invalid float count')
        self.bin.extend(b'\0'*(-len(self.bin)%4))
        raw=struct.pack('<'+'f'*len(values),*values)
        self.doc['bufferViews'].append({'buffer':0,'byteOffset':len(self.bin),'byteLength':len(raw)})
        self.bin.extend(raw)
        self.doc['accessors'].append({'bufferView':len(self.doc['bufferViews'])-1,
            'componentType':5126,'count':count,'type':type_name})
        return len(self.doc['accessors'])-1

    def save(self,path):
        self.doc['buffers'][0]['byteLength']=len(self.bin)
        self.bin.extend(b'\0'*(-len(self.bin)%4))
        encoded=json.dumps(self.doc,separators=(',',':')).encode()
        encoded+=b' '*(-len(encoded)%4)
        payload=struct.pack('<III',0x46546c67,2,28+len(encoded)+len(self.bin))
        payload+=struct.pack('<II',len(encoded),0x4e4f534a)+encoded
        payload+=struct.pack('<II',len(self.bin),0x004e4942)+self.bin
        path.write_bytes(payload)
