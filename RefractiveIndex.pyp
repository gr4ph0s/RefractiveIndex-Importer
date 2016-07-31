#Easy Wheel TAG. Make it turnnn !!!!! :D
#    Coded by graphos => http://graphos.fr
#    thanks to :
#        xs_yann // valkaari // cesar vonc // oli_d
#        http://frenchcinema4d.fr/
#        Inspirate By http://therenderblog.com/custom-fresnel-curves-in-maya/


import  c4d,os,math,json

MODULE_ID                                   =  1037819
VERSION                                     =  1

REFLECTION_INDEX                            = 1000
REFLECTION_INDEX_SPLINE_RED_GRP             = 1001
REFLECTION_INDEX_SPLINE_RED_NUM_POINTS      = 1002
REFLECTION_INDEX_SPLINE_RED                 = 1003

REFLECTION_INDEX_SPLINE_GREEN_GRP           = 1004
REFLECTION_INDEX_SPLINE_GREEN_NUM_POINTS    = 1005
REFLECTION_INDEX_SPLINE_GREEN               = 1006

REFLECTION_INDEX_SPLINE_BLUE_GRP            = 1007
REFLECTION_INDEX_SPLINE_BLUE_NUM_POINTS     = 1008
REFLECTION_INDEX_SPLINE_BLUE                = 1009

REFLECTION_INDEX_TEXT                       = 1010

ID_CREATE                                   = 1011
METALTYPE                                   = 1012
ALUMINIUM                                   = 1013
OR                                          = 1014

class miscFunction():
    def IOR(self,n,k):
        theta_deg = 0
        fresnel = []

        while theta_deg <= 90:
            theta = math.radians(theta_deg)
            a = math.sqrt((math.sqrt((n**2-k**2-(math.sin(theta))**2)**2 + ((4 * n**2) * k**2)) + (n**2 - k**2 - (math.sin(theta))**2))/2)
            b = math.sqrt((math.sqrt((n**2-k**2-(math.sin(theta))**2)**2 + ((4 * n**2) * k**2)) - (n**2 - k**2 - (math.sin(theta))**2))/2)

            Fs = (a**2+b**2-(2 * a * math.cos(theta))+(math.cos(theta))**2)/(a**2+b**2+(2 * a * math.cos(theta))+(math.cos(theta))**2)
            Fp = Fs * ((a**2+b**2-(2 * a * math.sin(theta) * math.tan(theta))+(math.sin(theta))**2*(math.tan(theta))**2)/(a**2+b**2+(2 * a * math.sin(theta) * math.tan(theta))+(math.sin(theta))**2*(math.tan(theta))**2))

            R = (Fs + Fp)/2
            fresnel.append(R)
            theta_deg += 1
        return fresnel 

    """
    -----------------------
    Ramer Douglas Algorithm
    -----------------------
    """

    def vec2dDist(self,p1, p2):
        return (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2

    def vec2dSub(self,p1, p2):
        return (p1[0]-p2[0], p1[1]-p2[1])

    def vec2dMult(self,p1, p2):
        return p1[0]*p2[0] + p1[1]*p2[1]

    def ramerdouglas(self,line, dist):
        if len(line) < 3:
            return line
        (begin, end) = (line[0], line[-1]) if line[0] != line[-1] else (line[0], line[-2])
        distSq = []

        for curr in line[1:-1]:
            tmp = (self.vec2dDist(begin, curr) - self.vec2dMult(self.vec2dSub(end, begin), self.vec2dSub(curr, begin)) ** 2 / self.vec2dDist(begin, end))
            distSq.append(tmp)

        maxdist = max(distSq)
        if maxdist < dist ** 2:
            return [begin, end]

        pos = distSq.index(maxdist)
        return (self.ramerdouglas(line[:pos + 2], dist) +
                self.ramerdouglas(line[pos + 1:], dist)[1:])

class jsonFunction():

    def __init__(self):
        self.fileContent = ""
        self.file = os.path.join(os.path.split(__file__)[0],"index.json")


    def loadJsonFile(self):
        with open(self.file) as json_data:
            self.fileContent = json.load(json_data)


    def getAllName(self):
        buffer = []
        for cle,valeur in self.fileContent.items():
            buffer.append(cle)

        return buffer


    def getRGBData(self,activeName):
        return self.fileContent.get(activeName)

class lunchTag(c4d.plugins.TagData):

    def Init(self,node):
        self.miscFunction = miscFunction()
        self.jsonFunction = jsonFunction()
        
        data = node.GetDataInstance()
        data.SetLong(REFLECTION_INDEX_SPLINE_RED_NUM_POINTS,50)
        data.SetLong(REFLECTION_INDEX_SPLINE_GREEN_NUM_POINTS,50)
        data.SetLong(REFLECTION_INDEX_SPLINE_BLUE_NUM_POINTS,50)

        #---------------------------------------------
        #               SOME TRYYYYYYY
        #---------------------------------------------

        # Create and initialize user data container for an integer for the children
        bc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_LONG)
        bc.SetInt32(c4d.DESC_CUSTOMGUI, c4d.CUSTOMGUI_CYCLE)
        bc.SetInt32(c4d.DESC_MIN, 0)
        bc.SetInt32(c4d.DESC_MAX, 2)
        
        # Create a container for the dropdown cycle values
        cycle = c4d.BaseContainer()
        
        cycle.SetString(0, "Test")
        cycle.SetString(1, "haha")
        
        # Set cycle values container
        data.SetContainer(c4d.DESC_CYCLE, cycle)
        #---------------------------------------------
        #               SOME TRYYYYYYY
        #---------------------------------------------


        self.jsonFunction.loadJsonFile()
        self.jsonFunction.getAllName()
        RGBnk = self.jsonFunction.getRGBData("aluminium")
        self.setCurves(RGBnk,node)

        return True

    def createCycleButton(self):
        allMetal = self.jsonFunction.getAllName()
        
    def getActiveCycleButton(self):
        pass

    def setCurves(self,RGBnk,node):
        node[REFLECTION_INDEX_SPLINE_RED] = self.getCurveSpline(self.getCurveData(RGBnk.get("Red").get("n"),RGBnk.get("Red").get("k"),50))
        node[REFLECTION_INDEX_SPLINE_GREEN] = self.getCurveSpline(self.getCurveData(RGBnk.get("Green").get("n"),RGBnk.get("Green").get("k"),50))
        node[REFLECTION_INDEX_SPLINE_BLUE] = self.getCurveSpline(self.getCurveData(RGBnk.get("Blue").get("n"),RGBnk.get("Blue").get("k"),50))

    def getCurveData(self,n,k,numberOfPoints):
        fresnelList = self.miscFunction.IOR(n, k)

        # Compensate for non-linear facingRatio
        linearValues = [ float(i)/90 for i in range(91) ]
        rawValues = [ math.sin(linearValues[i]*90*math.pi/180) for i in range(91) ]

        # Reduce curve points
        myline = zip(rawValues, fresnelList)
        precisionVals = [0.00005,0.0001,0.0002,0.0003]
        simplified = []

        for i in precisionVals:
            if len(simplified) == 0 or len(simplified) > numberOfPoints:
                simplified = self.miscFunction.ramerdouglas(myline, dist = i)

        return simplified

    def getCurveSpline(self,data):
        spline = c4d.SplineData()
        spline.MakePointBuffer(len(data))
        for i in xrange(0,len(data)):
            vector = c4d.Vector(data[i][0],data[i][1],0)
            spline.SetKnot(i,vector)

        return spline

if __name__ == "__main__":

    dir, file = os.path.split(__file__)
    bmp = c4d.bitmaps.BaseBitmap()
    bmp.InitWith(os.path.join(dir, "res", "EasyWheel.tif"))
    c4d.plugins.RegisterTagPlugin(id=MODULE_ID, 
                                str='ReflectionIndex', 
                                g=lunchTag,
                                description="TREFLECTION_INDEX", 
                                icon=bmp,
                                info=c4d.TAG_EXPRESSION|c4d.TAG_VISIBLE)
