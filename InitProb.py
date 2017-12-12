from __future__ import division
import random as r
import math as m
import numpy as np
import matplotlib.pyplot as plt
import copy
import sys


########################################
# General
########################################



def robinsonAspectRatio(QVL):
    """ QuadVertexList : [[X0,Y0],...,[X3,Y3]] """
    bisectors = [ [.5*(QVL[i][0]+QVL[(i+1)%4][0]),.5*(QVL[i][1]+QVL[(i+1)%4][1])] for i in range(4) ]
    
    centroid = [0,0]
    for i in range(4):
        centroid[0] += .25*QVL[i][0]
        centroid[1] += .25*QVL[i][1]

    r1_h1 = ((centroid[0] - bisectors[0][0])**2 + (centroid[1] - bisectors[0][1])**2)**.5
    r2_h1 = ((centroid[0] - bisectors[1][0])**2 + (centroid[1] - bisectors[1][1])**2)**.5

    n1 = ((bisectors[0][0] - centroid[0]) / r1_h1, (bisectors[0][1] - centroid[1]) / r1_h1)
    n2 = ((bisectors[1][0] - centroid[0]) / r2_h1, (bisectors[1][1] - centroid[1]) / r2_h1)

    theta = 180/m.pi * m.acos(n1[0] * n2[0] + n1[1] * n2[1])

    sin = m.sin(theta * m.pi / 180)
    
    r1_h2 = sin * r2_h1
    r2_h2 = sin * r1_h1    

    return max(max(r1_h1,r1_h2)/min(r1_h1,r1_h2), max(r2_h1,r2_h2)/min(r2_h1,r2_h2))



def exportToOFF( quads, filename ):
    """ quads is a list of QVL's such as those given by unitQuad and assessed by robinsonAspectRatio : quads = [ [[X0,Y0],...,[X3,Y3]], ... , [[U0,V0],...,[U3,V3]] ] """
    try:
        f = open(filename, "w")
        f.write("OFF\n")
        f.write("{} {} 0\n".format(str(4*len(quads)), str(len(quads))))
        for i, quad in enumerate(quads):
            for vertex in quad:
                f.write("{} {} 0.0\n".format(float(vertex[0] + 3*i), float(vertex[1])))
        for i in range(len(quads)):
            f.write("4 {} {} {} {}\n".format(*[4*i + j for j in range(4)]))
    except:
        print("exportToOFF(): FileError\n")
        return 1
    finally:
        f.close()
        return 0



def convertOFFtoELENODE( offname ):
    """Converts an off in the same directory to ele node files"""
    with open(offname, "r") as OFF:
        OFFLines = OFF.readlines()

    OFFData = []
    for line in OFFLines:
        OFFData.append(line.split())
        
    numVertices = int(OFFData[1][0])
    numFaces = int(OFFData[1][1])
    numPerFace = int(OFFData[2+numVertices+1][0])

    outname = offname.split(".")[0] #To name the output files

    with open( outname + ".ele", "w") as ELE:
        ELE.write( "{}\t{}\t0\n".format(numFaces, numPerFace)) #Placing the number of elements, and taking the number of vertices in an element from the first element that appears in the off
        
        for i in range(2 + numVertices, 2 + numVertices + numFaces):
            temp = []
            for j in range( 1, 1+numPerFace):
                temp.append( int(OFFData[i][j]) + 1 )

            template = "{}\t" + "{}\t"*numPerFace + "\n"
            ELE.write( template.format( i-numVertices-1, *temp))

    with open( outname + ".node", "w") as NODE:
        NODE.write( "{}\t2\t0\t0\n".format(numVertices)) #Placing the number of elements, and taking the number of vertices in an element from the first element that appears in the off
        
        for i in range(2, 2 + numVertices):

            template = "{}\t{}\t{}\n"
            NODE.write( template.format( i-1, *OFFData[i]))
    
    return



def listFilenameFormat( L ):
    return str(L).strip("[]").replace(",","_").replace(" ","").replace("\'", "")
 



#############################
#Perimarea
#############################



def PerimareaRatio(QVL):
    scale(QVL, perimeter(QVL)**-1)
    return 16 * quadArea(QVL) / perimeter(QVL)

def perimeter(PVL):
    P = 0
    n = len(PVL)
    for i in range(n):
        P += ( (PVL[(i)%n][0] - PVL[(i+1)%n][0])**2 + (PVL[(i)%n][1] - PVL[(i+1)%n][1])**2 )**.5
    return P

def quadArea(QVL):
    area = 0
    for i in [0,2]:
        TVL = []
        for j in range(3): #size of Triangle
            TVL.append(QVL[(i+j)%4])
        area += abs(.5 * (( (TVL[1][0] - TVL[0][0]) * (TVL[2][1] - TVL[0][1]) ) - ( (TVL[2][0] - TVL[0][0]) * (TVL[1][1] - TVL[0][1]) )) )
    return area

def scale(PVL, S):
    for i, Point in enumerate(PVL): #len(PVL)
        for j, Coord in enumerate(Point):
            PVL[i][j] = S*Coord
    return PVL



########################################
# Angle Problem
########################################



def randomConvexQuad( Min = 1, Max = 179 ):
    """ Random Convex Quad
        Produces the angles for a valid, convex quad by 'splitting' 2 180's
        takes the components of the splits and there it is 
    """
    ang = []
    for i in range( 2 ):
        Slice = r.randint( Min, Max )
        ang.extend( [Slice, 180-Slice] )
    ang[1], ang[2] = ang[2], ang[1]
    return ang



def SPAlt( ang ): 
    """
    Returns list ang cycled such that the ang[2] is the smallest angle
    """
    indexMin = 0    
    itemMin = 360
    for i, item in enumerate( ang ):
        if (item < itemMin):
            indexMin = i
            itemMin = item
    return ( ang[(indexMin-2)%4:] + ang[:(indexMin-2)%4] )



def intersection(v1, v2):
    """
    Returns the intersection of v1 and v2. Note however that these are not 'bezier lines', x1, y1, x3, and y3
    are all *changes* in x, not describing a point. So, rather than x0 + (x1 - x0)*t, its just x0 + x1*t.
    It just made the algebra slightly easier.
    list v1 = [x0, x1, y0, y1], list v2 = [x2, x3, y2, y3]
    """
    x = v1[0:2] + v2[0:2]
    y = v1[2:4] + v2[2:4]
    if( x[3] == 0 ): #To avoid a divide by zero, if x[3] is 0 then we just solve for where lineA equals x[2]
        t1 =    (x[2] - x[0])/\
                (x[1])
        return [ v1[0] + v1[1]*t1, v1[2] + v1[3]*t1 ]

    else: 
        t1 =    ( y[0] - y[2] + (y[3]/x[3])*(x[2] - x[0]) )/\
                ( (y[3]*x[1])/x[3] - y[1] )
        return [ v1[0] + v1[1]*t1, v1[2] + v1[3]*t1 ]


def unitQuad(angOriginal, offset = 1):
    """ Returns list of points that describe a unit quad based on ang, which contains angles
        describing a valid convex quad
        For example, [90,90,90,90] returns [Point(0,0),Point(1,0),Point(1,1),Point(0,1)]
    """
    ang = angOriginal.copy()

    for i, item in enumerate(ang):
        ang[i] = m.radians(item)

    points = []
    points.append( [0,0] )#P0
    points.append( [offset,0] )#P1
    points.append( None )#P2 
    points.append( [m.cos(ang[0]), m.sin(ang[0])] )#P3

    # !!! listA = [x0, x1, y0, y1], listB = [x2, x3, y2, y3]
    lineA = [  points[3][0], m.cos( ang[3] - (m.pi - ang[0]) ), points[3][1], m.sin( ang[3] - (m.pi - ang[0]) )  ]
    lineB = [  points[1][0], m.cos( m.pi - ang[1] ), points[1][1], m.sin( m.pi - ang[1] )  ]
    points[2] = (  intersection( lineA, lineB )  )

    return points



########################################
# Edge Problem
########################################



def randomEdgeLengths(): 
    """
    Uses a convoluted method of generating a quad with the Angle code and then taking the edge lengths from that. 
    """

    angles = randomConvexQuad()                     #Random angles
    quad = unitQuad(angles, r.uniform(0.05, 0.95))  #For a random quad, with varied base edge length

    edges = []
    n = len(quad)
    for i in range(n):  #For each edge in the quad, record the edge's length
        edges.append(( (quad[(i)%n][0] - quad[(i+1)%n][0])**2 + (quad[(i)%n][1] - quad[(i+1)%n][1])**2 )**.5) 
   
    maxItem = max(edges)
    maxIndex = edges.index(maxItem) 

    edges = edges[maxIndex:] + edges[:maxIndex] #Reorder the edge lengths so that the greatest one comes first
    for i, item in enumerate(edges):            #And normalize them so that the greatest edge has length 1
        edges[i] = item / maxItem
 
    return edges



def circleIntersection( p0, r0, p1, r1 ):
    circle0 = (*p0, r0) # Reformat the data for our 2 circles to
    circle1 = (*p1, r1) # (xi, yi, ri)

    #Send it out to CCIPP.py's circle intersection function
    intersections = Geometry.circle_intersection(None, circle0, circle1) 
    
    if len(intersections) != 2: #There's 1 or no intersections, in either case the excetpion is handled later
        raise ValueError

    elif intersections[0][1] > intersections[1][1]: #Return the point of intersection with greater y value
        return intersections[0]
    else:
        return intersections[1]
    

    
class Geometry(object):
    def circle_intersection(self, circle1, circle2):
        '''
        Source: https://gist.github.com/xaedes/974535e71009fa8f090e
        @summary: calculates intersection points of two circles
        @param circle1: tuple(x,y,radius)
        @param circle2: tuple(x,y,radius)
        @result: tuple of intersection points (which are (x,y) tuple)
        '''
        # return self.circle_intersection_sympy(circle1,circle2)
        d2r = m.pi/180
        x1,y1,r1 = circle1
        x2,y2,r2 = circle2
        # http://stackoverflow.com/a/3349134/798588
        dx,dy = x2-x1,y2-y1
        d = m.sqrt(dx*dx+dy*dy)
        if d > r1+r2:
            print("#1")
            return None # no solutions, the circles are separate
        if d < abs(r1-r2):
            print("#2")
            return None # no solutions because one circle is contained within the other
        if d == 0 and r1 == r2:
            print("#3")
            return None # circles are coincident and there are an infinite number of solutions

        a = (r1*r1-r2*r2+d*d)/(2*d)
        h = m.sqrt(r1*r1-a*a)
        xm = x1 + a*dx/d
        ym = y1 + a*dy/d
        xs1 = xm + h*dy/d
        xs2 = xm - h*dy/d
        ys1 = ym - h*dx/d
        ys2 = ym + h*dx/d

        return (xs1,ys1),(xs2,ys2)



def unitCircPt(theta):
    return np.array([np.cos(theta),np.sin(theta)])



def angle_between(v1, v2):
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))



def unit_vector(vector):
    return vector / np.linalg.norm(vector)



def unitQuad_Edge(lens, N=3):
    """
    lens, list of edge lengths
    N is the number of desired iterations between the left and right degenerate cases, leftDegenerate and rightDegenerate
    
    """
    template = [ np.array([0,0]), np.array([lens[0], 0]), None, None ] #Template from which to generate other Quad Vertex Lists
    leftDegenerate = template.copy()    #Left Limit of quad if you were to rotate edge 3 CCW about the origin until you no longer can
    rightDegenerate = template.copy()   #Right Limit of quad if you were to rotate edge 2 CW about point 1 until you no longer can,
                                        #   or alternatively, how far edge 3 can rotate CW until the quad is degenerate
    try:
        leftDegenerate[3] = np.array( circleIntersection(leftDegenerate[0], lens[3], leftDegenerate[1], lens[1]+lens[2]) )
        leftDegenerate[2] = ( lens[1] / (lens[2]+lens[1]) ) * (leftDegenerate[3]-leftDegenerate[1]) + leftDegenerate[1]
    except: 
        leftDegenerate[3] = np.array([-lens[3],0])
        leftDegenerate[2] = np.array( circleIntersection(leftDegenerate[3], lens[2], leftDegenerate[1], lens[1]) )

    try:
        rightDegenerate[2] = np.array( circleIntersection(rightDegenerate[0], lens[2]+lens[3], rightDegenerate[1], lens[1]) )
        rightDegenerate[3] = ( lens[3] / (lens[3]+lens[2]) ) * rightDegenerate[2]
    except:
        rightDegenerate[2] = np.array([lens[0]+lens[1], 0])
        rightDegenerate[3] = np.array( circleIntersection(rightDegenerate[0], lens[3], rightDegenerate[2], lens[2]))
        
    rightOfOrigin = np.array([1,0]) #Theta = 0 on the Unit Circle
    thetaMin = angle_between(leftDegenerate[3], rightOfOrigin) #Angle of 
    thetaMax = angle_between(rightDegenerate[3], rightOfOrigin)
    pitch = (thetaMax - thetaMin) / (N-1)

    result = []
    result.append(leftDegenerate) 
    for i in range(1, N-1):
        result.append(template.copy())
        result[i][3] = lens[3]*unitCircPt(i*pitch+thetaMin)
        result[i][2] = np.array(circleIntersection( result[i][3], lens[2], result[i][1], lens[1]))
    result.append(rightDegenerate) 

    return listify(result)



def listify(result):
    for quad in result:
        for i, point in enumerate(quad):
            quad[i] = list(point)
    return(result)



########################################
#Main
########################################



#if __name__ == "__main__" and len(sys.argv) == 1:
#    print("usage")
#   
#if __name__ == "__main__" and sys.argv[2] == "E":
#    templates = []
#
#    if len(sys.argv) == 3:
#        with open(sys.argv[2], 'r') as f:
#            lines = f.readlines()
#
#        for i, list_i in lines:
#            lines[i] = list_i.split()
#            for 
#
#    count = 10
#    f = randomEdgeLengths
##    count = 1
##    f = [1, 0.9, 0.258, 0.242]
#
#    for i in range(count):
#        #template = [1, 1, 1, 1]
#        N = 18
#        template = f()
#        quads = unitQuad_Edge(template, N)
#        print("Success with {}".format(str(template)))
#
#        tCopy = template.copy()
#        for i, item in enumerate(tCopy):
#            tCopy[i] = "{0:0>4}".format(int(item*1000))
#        offname = listFilenameFormat(tCopy)
#        print("Created {}.off\n\n".format(offname))
#        
#        RARs = []
#        xlist = [j/N for j in range(1, N+1)]
#
#        minRAR = float("inf") 
#        minQuad = None
#        for quad in quads:
#            RARs.append(robinsonAspectRatio(quad))
#            #RARs.append(robinsonAspectRatio(quad))
#            if RARs[-1] < minRAR:
#                minRAR = RARs[-1]
#                minQuad = quad
#        
#        print(xlist)
#        print(RARs)
#        plt.plot(xlist, RARs)
#        plt.axis([0,1,0, 10])
#        plt.title(str(template))
#        plt.savefig(offname)
#        plt.clf() 
#        output = [quads[0], minQuad, quads[-1]]
#
#        exportToOFF( output, offname )
#
#        print("\n"*5)
#
#if __name__ == "__main__" and sys.argv[2] == "A":
#    
#    templates = [[30,69,116,145],[30, 116, 69, 145]]
##    templates = [[30,150,120,60], [30, 69, 116, 145], [30, 120, 150, 60], [30, 116, 145, 69], [30, 150, 60, 120], [30, 116, 69, 145]]  #Angles
#    for i, item in enumerate(templates):
#        templates[i] = SPAlt(item)
#        
#    for i in range(len(templates)):    
#        minx = 0
#        maxx = 5
#        pitch = 1/20
#        n = int((maxx-minx)/pitch)
#        
#        template = templates[i]
#        quads = []
#        RARs = []
#        xlist = []
#        
#        for i in range(1, n):
#            x = minx + i*pitch
#            xlist.append(x)
#            quads.append( unitQuad(template, x) )
#       
#        minRAR = float("inf") 
#        minQuad = None
#        for quad in quads:
#            RARs.append(robinsonAspectRatio(quad))
#            if RARs[-1] < minRAR:
#                minRAR = RARs[-1]
#                minQuad = quad
#        
#        name = str(template).strip("[]").replace(",","_").replace(" ","")
#
#        print(xlist)
#        print(RARs)
#        plt.plot(xlist, RARs)
#        plt.axis([minx,maxx,minx, maxx])
#        plt.title(str(template))
#        plt.savefig(name)
#        plt.clf() 
#        quads = [unitQuad(template), minQuad]
#    
#        offname = name + ".off"
#        exportToOFF( quads, offname )
#
