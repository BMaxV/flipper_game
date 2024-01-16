from panda3d.core import GeomVertexFormat, GeomVertexData
from panda3d.core import Geom, GeomTriangles,GeomTrifans, GeomVertexWriter
from panda3d.core import Texture, GeomNode
from panda3d.core import NodePath

import random

#actor?

def load_object(showbase,name="cube",path="../Resources/Models/",pos=(0,0,0),scale=(1,1,1)):
    if name==None:
        name="cube"
    print(name, path)
    name = path + name
    
    try:
        ob = showbase.loader.loadModel(name)
    except OSError as e:
        print("my error",e)
        #wait that probably should be in the create load function
        #can't find the file
        return None
    ob.setPos(*pos)
    ob.reparentTo(showbase.render)
    ob.setScale(*scale)
    ob.setTwoSided(True)
    #ob.setColor(0,1,0,1)
    return ob

def make_object(base,verts=[(0,0,0),(1,0,0),(1,1,0),(0,1,0)],
                    faces_vert_index_list=[[0,1,2,3]],
                    twosided=False,
                    tag_tuple=("terrain","1"),
                    collision_mask=None,
                    color=None,
                    texture=None,
                    transparent=0,
                    ):
    
    """this function creates a whole object
    you can just create individual faces as well, but there
    are gains for doing it in bulk."""
    
    faces_vis=faces_vert_index_list
        
    snode = GeomNode('Object')
    
    if color !=None and texture!=None:
        raise ValueError
    if texture==None:
        poly = makecoloredPoly(verts,faces_vis,color)
    else:
        poly = make_textured_poly(verts,faces_vis)
    
    snode.addGeom(poly)
    
    if type(base).__name__=="ShowBase":
        #print("yo what the fuck")
        ob = base.render.attachNewNode(snode)
    else:
        ob=NodePath(snode)
        ob.reparentTo(base)
        
    #ob = base.render.attachNewNode(snode)
    assert transparent in [0,1]
    ob.setTransparency(transparent)
    
    if collision_mask!=None:
        ob.node().setIntoCollideMask(collision_mask)
    
    if tag_tuple!=None:
        ob.setTag(*tag_tuple) #or some other tag?
        
    # OpenGl by default only draws "front faces" (polygons whose vertices are
    # specified CCW).
    ob.setTwoSided(twosided)
    
    #grasstex = loader.loadTexture("tex/sand.png")#grasstex.jpg")
    #ob.setTexture(grasstex)
    
    #ts = TextureStage('ts')
    #ob.setTexture(ts, tex)
    
    return ob
    

def make_textured_poly(verts,faces):
    """this function creates the polygon that will be added to the geom
    datastructure"""
    
    #panda can not by itself create n-gons, it does support
    #"triangle fans" however, a set of triangles with
    #a shared center vertex.
    #so to create n-gons anyway, we just take the verts, add one at
    #the center and use that as a shared vert of all triangles.
    #this center has to be calculated first.
    
    old_vert_len=len(verts)
    #old_verts=list(verts)
    #calculate the center first
    center_ids=[]
    for f in faces:
        vl=[]
        for p in f:
            vl.append(verts[p])
        center_p=calculate_center(vl)
        verts.append(center_p)
        center_ids.append(len(verts)-1)
    
    tformat=GeomVertexFormat.getV3t2()
    
    #this is the format we'll be using.
    vdata = GeomVertexData('convexPoly', tformat, Geom.UHStatic)

    #these are access shortcuts
    vertex = GeomVertexWriter(vdata, 'vertex')
    uv = GeomVertexWriter(vdata, "texcoord")
    #normal = GeomVertexWriter(vdata, 'normal')
    #color = GeomVertexWriter(vdata, 'color')
    
    #tells the format how many vertices we'll create
    vdata.setNumRows(len(verts))
    #eew?
    uvs=[(0,0),(1,0),(1,1),(0,1),(0.5,0.5)]
    #set the data for each vertex.
    ci=0
    for p in verts:
        #color_t=random.choice([(255,0,0),(0,255,0),(0,0,255)])
        color_t=(255,255,0)
        vertex.addData3(p[0],p[1],p[2])
        print(p,ci)
        uvpair=uvs[ci]
        #stretch stuff to matche thing thing?
        uv.addData2(*uvpair)
        #for generated coordinates
        #uv.addData2(p[0],p[1])
        ci+=1
        #color.addData4f(*color_t[:],0.5)
        #normal.addData3(0,0,1)
        #do i need normals?
    
    #this creates the geometry from the data.
    #or rather, this creates a geom object, with the vertex data
    #but in panda, nothing exists yet.
    poly = Geom(vdata)
    
    
    #this loop tells panda which verts in the vdata structure to
    #use to create the triangles
    c=0
    flb=0
    while c < len(faces):
        
        tris = GeomTrifans(Geom.UHStatic)
        #i.e. this face gets added.
        face=faces[c]
        
        #this would skip face #10
        #if c==10:
        #    c+=1
        #    continue
        
        #center
        tris.addVertex(center_ids[c])
        #one time round
        for i in face:
            tris.addVertex(i)
        #last to first
        tris.addVertices(face[-1],face[0])
        tris.closePrimitive()
        poly.addPrimitive(tris)
        flb+=len(face)
        c+=1
    
    return poly
    
def create_vdata(verts,color_tuple):
    #this is the format we'll be using.
    format = GeomVertexFormat.getV3n3c4()
    vdata = GeomVertexData('convexPoly', format, Geom.UHStatic)

    vdata.setNumRows(len(verts))
    
    #these are access shortcuts
    vertex = GeomVertexWriter(vdata, 'vertex')
    normal = GeomVertexWriter(vdata, 'normal')
    color = GeomVertexWriter(vdata, 'color')
    
    #tells the format how many vertices we'll create
    
    if color_tuple == None:
        vran1=random.random()
        vran2=random.random()
        #color_t=random.choice([(255*random.random(),0,0),(0,255*random.random(),0)])#,(0,0,255)])
        color_t=(1*vran1,1*vran2,0)#,(0,255*random.random(),0)])#,
        #color_t=(0,0,255)
    else:
        color_t=color_tuple
        
    #set the data for each vertex.
    for p in verts:
        #color_t=random.choice([(255,0,0),(0,255,0),(0,0,255)])
        #color_t=(255,255,0)
        vertex.addData3(*p)
        color.addData4f(*color_t[:],0.5)
        normal.addData3(0,0,1)
        #do i need normals?
    return vdata

def makecoloredPoly(verts,faces,color_tuple=None):
    """this function creates the polygon that will be added to the geom
    datastructure"""
    verts=verts.copy()
    #panda can not by itself create n-gons, it does support
    #"triangle fans" however, a set of triangles with
    #a shared center vertex.
    #this center has to be calculated first.
    
    old_vert_len=len(verts)
    
    #calculate the center first
    center_ids=[]
    for f in faces:
        vl=[]
        
        for p in f:
            vl.append(verts[p])
        center_p=calculate_center(vl)
        
        verts.append(center_p)
        center_ids.append(len(verts)-1)
    
    tformat=GeomVertexFormat.getV3t2()
    vdata=create_vdata(verts,color_tuple)

    
    #this creates the geometry from the data.
    #or rather, this creates a geom object, with the vertex data
    #but in panda, nothing exists yet.
    poly = Geom(vdata)
    
    
    #this loop tells panda which verts in the vdata structure to
    #use to create the triangles
    c=0
    flb=0
    while c < len(faces):
        
        tris = GeomTrifans(Geom.UHStatic)
        #i.e. this face gets added.
        face=faces[c]
        
        #this would skip face #10
        #keeping it here for easy/easier debugging
        #if c==10:
        #    c+=1
        #    continue
        
        tris.addVertex(center_ids[c])
        for i in face:
            tris.addVertex(i)
        tris.addVertices(face[-1],face[0])
        tris.closePrimitive()
        poly.addPrimitive(tris)
        flb+=len(face)
        c+=1
    
    return poly

def calculate_center(point_list):
    center_p=[0,0,0]
    for p in point_list:
        center_p[0]+=p[0]
        center_p[1]+=p[1]
        center_p[2]+=p[2]
    center_p[0]=center_p[0]/len(point_list)
    center_p[1]=center_p[1]/len(point_list)
    center_p[2]=center_p[2]/len(point_list)
    return center_p

#def spawn(showbase,new_ob,texturename="sand.png"):
    #ob=load_object(showbase,pos=new_ob.pos,scale=(0.2,0.2,0.2))
    #tex = showbase.loader.loadTexture("tex/"+texturename)
    #ob.setTexture(tex,1)
    #return ob
    
