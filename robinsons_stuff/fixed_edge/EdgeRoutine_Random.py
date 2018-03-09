import sys
sys.path.append('../../imports')
from InitProb import *

"""
Error codes from CCIPP.py:

        if d > r1+r2:
            print("#1")
            return None # no solutions, the circles are separate
        if d < abs(r1-r2):
            print("#2")
            return None # no solutions because one circle is contained within the other
        if d == 0 and r1 == r2:
            print("#3")
            return None # circles are coincident and there are an infinite number of solutions
"""
if __name__ == "__main__":
   
    templates = []
    count = 10
    f = randomEdgeLengths
#    count = 1
#    f = [1, 0.9, 0.258, 0.242]

    for i in range(count):
        #template = [1, 1, 1, 1]
        N = 18
        template = f()
        quads = unitQuad_Edge(template, N)
        print("Success with {}".format(str(template)))

        tCopy = template.copy()
        for i, item in enumerate(tCopy):
            tCopy[i] = "{0:0>4}".format(int(item*1000))
        offname = listFilenameFormat(tCopy)
        print("Created {}.off\n\n".format(offname))
        
        RARs = []
        xlist = [j/N for j in range(1, N+1)]

        minRAR = float("inf") 
        minQuad = None
        for quad in quads:
            RARs.append(robinsonAspectRatio(quad))
            #RARs.append(robinsonAspectRatio(quad))
            if RARs[-1] < minRAR:
                minRAR = RARs[-1]
                minQuad = quad
        
        print(xlist)
        print(RARs)
        plt.plot(xlist, RARs)
        plt.axis([0,1,0, 10])
        plt.title(str(template))
        plt.savefig(offname)
        plt.clf() 
        output = [quads[0], minQuad, quads[-1]]

        offname = offname + ".off"
        exportToOFF( output, offname )

        print("Minimum Robinson's: {}".format(minRAR))

        print("\n"*5)

##    """    
##    template = [1, 0.48, 0.56, 0.18]
#    template = [1, 0.55, 0.95, 0.75]
#        #Found the source of the error with this edge list. Its the classic fucking arctan limitation.
#        #Should probably switch to just scaling the original point to unit circle format and 
#        #applying a rotation matrix to that so I don't have to do any more trig shit
##    template = [1, .5, .5, .5]
#    quads = unitQuad_Edge(template, 5)
#    print("Success with {}".format(str(template)))
#
#    tCopy = template.copy()
#    for i, item in enumerate(tCopy):
#        tCopy[i] = "{0:0>4}".format(int(item*1000))
#    offname = listFilenameFormat(tCopy)
#    print("EdgeRoutine Line 50")
#    [print(quad) for quad in quads]
#    exportToOFF( quads, offname + ".off" )
#    print("Created {}.off\n\n".format(offname))
#
#    """
#    try: 
#        quads = unitQuad_Edge(template, 5)
#        print("Success with {}".format(str(template)))
#
#        tCopy = template.copy()
#        for i, item in enumerate(tCopy):
#            tCopy[i] = "{0:0>4}".format(int(item*1000))
#        offname = listFilenameFormat(tCopy)
#        print("EdgeRoutine Line 50")
#        [print(quad) for quad in quads]
#        exportToOFF( quads, offname + ".off" )
#        print("Created {}.off\n\n".format(offname))
#
#    except:
#            print("Failed with {}\n\n".format(str(template)))
#    """
