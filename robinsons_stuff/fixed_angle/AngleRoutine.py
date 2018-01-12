import sys
sys.path.append('../../imports')
from InitProb import *
import math

def create_quad_list():
    angle0 = 179
    angle1 = 1
    quad_list = []
    while angle0 != 0:
        quad_list.append([angle0, angle1, angle0, angle1])
        angle0 -= 1
        angle1 += 1
    return quad_list

def create_quad_list_v2(lowerbound, pitch=5):
    """Returns a list of quads starting with angles lowerbound and 180-lowerbound.
    Increments/decrements angles by pitch."""
    if lowerbound <= 0 or lowerbound >= 90 or pitch <= 0 or pitch >= 90:
        raise ValueError
    angle0 = 180-lowerbound
    angle1 = lowerbound
    angle2 = 180-lowerbound
    angle3 = lowerbound
    quad_list = []
    while angle0 > lowerbound:
        while angle2 > lowerbound:
            if not angle1 == angle2:
                quad_list.append([angle0, angle1, angle3, angle2])
            angle2 -= pitch
            angle3 += pitch
        angle0 -= pitch
        angle1 += pitch
        angle2 = 180-lowerbound
        angle3 = lowerbound
    return quad_list

def get_distances(quad):
    """Takes a quad and finds the smallest distance between 2 adjacent points and largest 
    distance between 2 adjacent points. quad should be of the form: [[x0,y0],[x1,y1],[x2,y2],[x3,y3]]"""
    distances = []
    for i in range(4):
        if i < 3:
            distances.append(math.sqrt( ((quad[i][0]-quad[i+1][0])**2)+((quad[i][1]-quad[i+1][1])**2)  ))
        else:
            distances.append(math.sqrt( ((quad[3][0]-quad[0][0])**2)+((quad[3][1]-quad[0][1])**2)  ))
    return distances

if __name__ == '__main__':
    """
    Haven't gotten scipy's optimization to work yet.
    This just creates a test.off file containing some sample quads
    """

    #templates = create_quad_list_v2(50)
    #templates = [[30, 60, 150, 120]]
#    templates = [[30,150,120,60], [30, 69, 116, 145], [30, 120, 150, 60], [30, 116, 145, 69], [30, 150, 60, 120], [30, 116, 69, 145]]  #Angles
    templates = [[135, 45, 45, 135]]
    #templates = [ [75, 110, ] , [] ]
    #for i, item in enumerate(templates):
    #    templates[i] = SPAlt(item)

#        templates.append(SPAlt(randomConvexQuad(40, 140)))

#    templates = [[178, 32, 2, 148]] #Extreme test cases for debugging purposes
#    templates = [[176, 153, 4, 27]]
    """
    offsets = []
    quads = []
    for i, template in enumerate(templates):
        print("Quad {}: {}\n".format(i, str(template)))
        for j, offset in enumerate([.5, 1, 2]): #From each anglelist/template, we'll have 3 offsets, 1/2, 1, and 2
            quads.append(unitQuad(template.copy(), offset))
            print(  "\tOffset {}: {}\n\tRAR: {}\n".format( (offset),str(quads[-1]), robinsonAspectRatio(quads[-1]) )  )
            print("\n")
    exportToOFF( quads, "test.off" )
    """
    for i in range(len(templates)):
        minx = 0
        maxx = 10
        pitch = 1/20
        n = int((maxx-minx)/pitch)

        template = templates[i]
        quads = []
        RARs = []
        xlist = []

        # Generate list of quads
        for i in range(1, n):
            x = minx + i*pitch
            xlist.append(x)
            quads.append( unitQuad(template, x) )

        minRAR = float("inf")
        minQuad = None
        minOffset = float("inf")
        # Generate list of RARs
        for quad in quads:
            RARs.append(robinsonAspectRatio(quad))
            if RARs[-1] < minRAR:
                minRAR = RARs[-1]
                minQuad = quad
                minOffset = quad[1][0]
            #Print some stuff about distance between adjacent points
            if quad[1][0] % 1 == 0:
                distances = get_distances(quad)
                ratio = min(distances)/max(distances)
                avg = sum(distances)/len(distances)
                print("For AR: {}, {:4f}, {:4f}".format(int(quad[1][0]), ratio, avg))

        name = str(template).strip("[]").replace(",","_").replace(" ","")

        #print(xlist)
        #print(RARs)
        plt.plot(xlist, RARs)
        plt.xlabel("Offset")
        plt.ylabel("Robinson's Aspect Ratio")
        plt.axis([minx,maxx,minx, 5])
        plt.title(str(template))
        plt.savefig(name)
        plt.clf()
        quads = [unitQuad(template), minQuad]

        offname = name + ".off"
        exportToOFF( quads, offname )
        print("Minimum Robinson's Aspect Ratio: {}".format(minRAR))
        print("Minimum Offset: {}".format(minOffset))
