#Refractive Index TAG. Get curve from refractive index k/n !!!!! :D
#    Coded by graphos => http://graphos.fr
#    thanks to :
#        xs_yann // valkaari // cesar vonc // oli_d
#        http://frenchcinema4d.fr/
import  c4d,os,math,json

PLUGIN_ID                       =   1037819
VERSION                         =   1

X_INVERTED = 1
Y_INVERTED = 2

UI_GROUP_CURVE              = 0
UI_GROUP_CURVE_METAL_TYPE   = 1
UI_GROUP_CURVE_RED          = 2
UI_GROUP_CURVE_GREEN        = 3
UI_GROUP_CURVE_BLUE         = 4
UI_GROUP_CREATE             = 5

UI_CYCLE                    = 0

UI_BUTTON_REFRESH           = 0
UI_BUTTON_DELETE            = 1
UI_BUTTON_CREATE            = 2

UI_SPLINE_RED               = 0
UI_SPLINE_GREEN             = 1
UI_SPLINE_BLUE              = 2

UI_SLIDER_RED               = 0
UI_SLIDER_GREEN             = 1
UI_SLIDER_BLUE              = 2

UI_BOOL_RED_X               = 0
UI_BOOL_GREEN_X             = 1
UI_BOOL_BLUE_X              = 2
UI_BOOL_RED_Y               = 3
UI_BOOL_GREEN_Y             = 4
UI_BOOL_BLUE_Y              = 5

UI_STR_MAT_NAME             = 0
UI_STR_RED_K                = 1
UI_STR_RED_N                = 2
UI_STR_GREEN_K              = 3
UI_STR_GREEN_N              = 4
UI_STR_BLUE_K               = 5
UI_STR_BLUE_N               = 6

UI_SEPARATOR_RED            = 0
UI_SEPARATOR_GREEN          = 1
UI_SEPARATOR_BLUE           = 2

class miscFunction():
    def getDiff(self,a,b):
        buffer = []
        if type(a) is list:
            for i in xrange(0,len(b)):
                if a[i] != b[i]:
                    buffer.append(i)
        return buffer

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

    def saveJsonFile(self):
        with open(self.file, 'w') as outfile:
            json.dump(self.fileContent, outfile, sort_keys = True, indent = 4)

    def deleteData(self,name):
        self.fileContent.pop(name)

    def addData(self,name,value):
        self.fileContent[name] = value

    def metalExist(self,name):
        if self.fileContent.has_key(name):
            return True
        else:
            return False

    def getAllName(self):
        buffer = []
        for cle,valeur in self.fileContent.items():
            buffer.append(cle)

        return buffer


    def getRGBData(self,activeName):
        return self.fileContent.get(activeName)

class UD():
    def __init__(self,obj):
        self.obj = obj

        #0 = R // 1 = G // 2 = B
        self.idCycle = [None]*1
        self.idGroups = [None]*6       
        self.idSplines = [None]*3
        self.idNbPoints = [None]*3
        self.idInvert = [None]*6
        self.idSeparator = [None]*3
        self.idStringInput = [None]*7
        self.idButtons = [None]*3

        self.oldCycle = None
        self.oldNbPoints = [None]*3
        self.oldInvert = [None]*6

    def createGroup(self, groupId, name, parentGroup=None, columns=None,shortname=None,titleBar = True,Open = False):
        if(self.idGroups[groupId]) is None:
            if shortname is None: shortname = name
            bc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_GROUP)
            bc[c4d.DESC_NAME] = name
            bc[c4d.DESC_SHORT_NAME] = shortname
            bc[c4d.DESC_TITLEBAR] = int(titleBar)
            bc[c4d.DESC_GUIOPEN] = int(Open)
            if parentGroup is not None:
                bc[c4d.DESC_PARENTGROUP] = parentGroup
            if columns is not None:
                #DESC_COLUMNS VALUE IS WRONG IN 15.057 - SHOULD BE 22
                bc[22] = columns
            
            self.idGroups[groupId] = self.obj.AddUserData(bc) 
            return self.idGroups

    def createSeparator(self,separatorId,parentGroup = None, name = ""):
        if(self.idSeparator[separatorId]) is None:
            bc = c4d.GetCustomDataTypeDefault(c4d.DTYPE_SEPARATOR)
            bc[c4d.DESC_NAME] = name
            bc[c4d.DESC_SHORT_NAME] = name
            bc[c4d.DESC_PARENTGROUP] = parentGroup
            bc.SetLong(c4d.DESC_CUSTOMGUI,c4d.DTYPE_SEPARATOR)
            bc.SetBool(c4d.DESC_SEPARATORLINE, False)
            self.idSeparator[separatorId] = self.obj.AddUserData(bc)
            return self.idSeparator

    def createButton(self,buttonId,parentGroup = None, name = ""):
        if(self.idButtons[buttonId]) is None:
            bc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_BUTTON)
            bc[c4d.DESC_NAME] = name
            bc[c4d.DESC_SHORT_NAME] = name
            bc[c4d.DESC_PARENTGROUP] = parentGroup
            bc[c4d.DESC_CUSTOMGUI] = c4d.CUSTOMGUI_BUTTON
            self.idButtons[buttonId] = self.obj.AddUserData(bc)

    def createStringInput(self,floatId,value,parentGroup = None, name = ""):
        if(self.idStringInput[floatId]) is None:
            bc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_STRING)
            bc[c4d.DESC_NAME] = name
            bc[c4d.DESC_PARENTGROUP] = parentGroup
            self.idStringInput[floatId] = self.obj.AddUserData(bc)
            self.obj[self.idStringInput[floatId]] = value
            return self.idStringInput
        else:
            self.obj[self.idStringInput[floatId]] = value
            return self.idStringInput

    def createIntSlider(self,sliderId,value,parentGroup = None,sliderText = ""):
        if(self.idNbPoints[sliderId]) is None:
            bc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_LONG)
            bc[c4d.DESC_CUSTOMGUI] = c4d.CUSTOMGUI_LONGSLIDER
            bc[c4d.DESC_NAME] = sliderText
            bc[c4d.DESC_MIN] = 10
            bc[c4d.DESC_MAX] = 100
            bc[c4d.DESC_PARENTGROUP] = parentGroup
            self.idNbPoints[sliderId] = self.obj.AddUserData(bc) # Add userdata container
            self.obj[self.idNbPoints[sliderId]] = value
            return self.idNbPoints
        else:
            self.obj[self.idNbPoints[sliderId]] = value
            return self.idNbPoints[sliderId]

    def createCycle(self,cycleId,data,parentGroup = None, cycleText = ""):
        if(self.idCycle[cycleId]) is None:
            bc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_LONG)
            bc[c4d.DESC_NAME] = cycleText
            bc[c4d.DESC_CUSTOMGUI] = c4d.CUSTOMGUI_CYCLE
            bc[c4d.DESC_PARENTGROUP] = parentGroup
            bc[c4d.DESC_MIN] = 0
            bc[c4d.DESC_MAX] = len(data)-1
    
            cycle = c4d.BaseContainer()
            for i in xrange(0, len(data)):
                cycle.SetString(i, data[i])

            bc.SetContainer(c4d.DESC_CYCLE, cycle)

            self.idCycle[cycleId] = self.obj.AddUserData(bc)
            return self.idCycle
        else:
            for id, bc in self.obj.GetUserDataContainer():
                if id == self.idCycle[cycleId]:
                    cycle = c4d.BaseContainer()
                    for i in xrange(0, len(data)):
                        cycle.SetString(i, data[i])
                        
                    bc[c4d.DESC_MAX] = len(data)-1
                    bc.SetContainer(c4d.DESC_CYCLE, cycle)
                    self.obj.SetUserDataContainer(id, bc)
            return self.idCycle

    def createSpline(self,colorId,splineData,parentGroup = None,splineText = ""):
        if(self.idSplines[colorId]) is None:
            bc = c4d.GetCustomDatatypeDefault(1009060) # Create default container
            bc[c4d.DESC_NAME] = splineText# Rename the entry
            bc[c4d.DESC_PARENTGROUP] = parentGroup
            self.idSplines[colorId] = self.obj.AddUserData(bc) # Add userdata container
            self.obj[self.idSplines[colorId]] = splineData
            return self.idSplines
        else:
            self.obj[self.idSplines[colorId]] = splineData
            return self.idSplines[colorId]

    def createBool(self,id,value,parentGroup,boolText = ""):
        if(self.idInvert[id]) is None:
            bc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_BOOL) # Create default container
            bc[c4d.DESC_NAME] = boolText# Rename the entry
            bc[c4d.DESC_PARENTGROUP] = parentGroup
            self.idInvert[id] = self.obj.AddUserData(bc) # Add userdata container
            self.obj[self.idInvert[id]] = value
            return self.idInvert
        else:
            self.obj[self.idInvert[id]] = value
            return self.idInvert[id]

    def getCurrentData(self):
        bufferCycle = []
        bufferCycle.append(self.obj[self.idCycle[UI_CYCLE]])

        bufferNbPts = []
        bufferNbPts.append(self.obj[self.idNbPoints[UI_SPLINE_RED]])
        bufferNbPts.append(self.obj[self.idNbPoints[UI_SPLINE_GREEN]])
        bufferNbPts.append(self.obj[self.idNbPoints[UI_SPLINE_BLUE]])

        bufferInvert = []
        bufferInvert.append(self.obj[self.idInvert[UI_BOOL_RED_X]])
        bufferInvert.append(self.obj[self.idInvert[UI_BOOL_GREEN_X]])
        bufferInvert.append(self.obj[self.idInvert[UI_BOOL_BLUE_X]])
        bufferInvert.append(self.obj[self.idInvert[UI_BOOL_RED_Y]])
        bufferInvert.append(self.obj[self.idInvert[UI_BOOL_GREEN_Y]])
        bufferInvert.append(self.obj[self.idInvert[UI_BOOL_BLUE_Y]])

        return bufferNbPts,bufferInvert,bufferCycle

    def setOldValue(self):
        self.oldNbPoints = []
        self.oldInvert = []
        for i in xrange(0,len(self.idNbPoints)):
            self.oldNbPoints.append(self.obj[self.idNbPoints[i]])

        for i in xrange(0,len(self.idInvert)):
            self.oldInvert.append(self.obj[self.idInvert[i]])

    def getModeInverted(self,id):
        buffer = 0
        if self.obj[self.idInvert[id]]:
            buffer += X_INVERTED
        if self.obj[self.idInvert[id+3]]:
            buffer += Y_INVERTED 
        return buffer

    def getCurrentCycleText(self,cycleId):
        for id, bc in self.obj.GetUserDataContainer():
            if id[1].id == self.idCycle[cycleId][1].id :
                bcCycle = bc.GetContainer(c4d.DESC_CYCLE)
                return bcCycle.GetString(self.obj[self.idCycle[cycleId]])

    def createBcFromList(self,liste):
        buffer = c4d.BaseContainer()
        for i in xrange(0,len(liste)):
            buffer[i] = liste[i]
        return buffer

    def createBcFromId(self):
        bc = c4d.BaseContainer()
        bc[0] = self.createBcFromList(self.idCycle)
        bc[1] = self.createBcFromList(self.idGroups)
        bc[2] = self.createBcFromList(self.idSplines)
        bc[3] = self.createBcFromList(self.idNbPoints)
        bc[4] = self.createBcFromList(self.idInvert)
        bc[5] = self.createBcFromList(self.idSeparator)
        bc[6] = self.createBcFromList(self.idStringInput)
        bc[7] = self.createBcFromList(self.idButtons)
        currentBC = self.obj.GetDataInstance()
        currentBC[PLUGIN_ID] = bc

    def createArrayFromBc(self,bc):
        buffer = []
        i = 0
        while i < len(bc):
            buffer.append(bc[i])
            i+=1
        return buffer

    def populateIDFromBc(self):
        bc = self.obj.GetDataInstance().GetContainer(PLUGIN_ID)
        self.idCycle = self.createArrayFromBc(bc[0])
        self.idGroups = self.createArrayFromBc(bc[1])
        self.idSplines = self.createArrayFromBc(bc[2])
        self.idNbPoints = self.createArrayFromBc(bc[3])
        self.idInvert = self.createArrayFromBc(bc[4])
        self.idSeparator = self.createArrayFromBc(bc[5])
        self.idStringInput = self.createArrayFromBc(bc[6])
        self.idButtons = self.createArrayFromBc(bc[7])


class lunchTag(c4d.plugins.TagData):

    def setSplineData(self, id = 4 , first = False):
        self.RGBnk = self.jsonFunction.getRGBData(self.ud.getCurrentCycleText(UI_CYCLE))
        buffer = ["Red","Green","Blue"]
        if id == 4:
            for i in xrange(0,len(self.dataSpline)):
                k = self.RGBnk.get(buffer[i]).get("k")
                n = self.RGBnk.get(buffer[i]).get("n")
                if not first:
                    nbPoints = self.ud.obj[self.ud.idNbPoints[i]]
                    mode = self.ud.getModeInverted(i)
                else:
                    nbPoints = 50
                    mode = 0
                data = self.getCurveData(k,n,nbPoints)
                self.dataSpline[i] = self.getCurveSpline(data,mode)
        else:
            k = self.RGBnk.get(buffer[id]).get("k")
            n = self.RGBnk.get(buffer[id]).get("n")
            if not first:
                nbPoints = self.ud.obj[self.ud.idNbPoints[id]]
                mode = self.ud.getModeInverted(id)
            else:
                nbPoints = 50
                mode = 0
            data = self.getCurveData(k,n,nbPoints)
            self.dataSpline[id] = self.getCurveSpline(data,mode)

    def createCurveTab(self):
        self.ud.createGroup(UI_GROUP_CURVE,"Curve",c4d.DescID())

        self.ud.createGroup(UI_GROUP_CURVE_METAL_TYPE,"Metal Type",self.ud.idGroups[UI_GROUP_CURVE],3,None,False)
        self.ud.createCycle(UI_CYCLE,self.jsonFunction.getAllName(),self.ud.idGroups[UI_GROUP_CURVE_METAL_TYPE],"Metal Type")
        self.ud.createButton(UI_BUTTON_REFRESH,self.ud.idGroups[UI_GROUP_CURVE_METAL_TYPE],"Refresh")
        self.ud.createButton(UI_BUTTON_DELETE,self.ud.idGroups[UI_GROUP_CURVE_METAL_TYPE],"Delete")
            
        self.setSplineData(4,True)

        self.ud.createGroup(UI_GROUP_CURVE_RED,"Red",self.ud.idGroups[UI_GROUP_CURVE])
        self.ud.createIntSlider(UI_SLIDER_RED,50,self.ud.idGroups[UI_GROUP_CURVE_RED],"Precision")
        self.ud.createBool(UI_BOOL_RED_X,False,self.ud.idGroups[UI_GROUP_CURVE_RED],"Invert X")
        self.ud.createBool(UI_BOOL_RED_Y,False,self.ud.idGroups[UI_GROUP_CURVE_RED],"Invert Y")
        self.ud.createSpline(UI_SPLINE_RED,self.dataSpline[0],self.ud.idGroups[UI_GROUP_CURVE_RED],"Red")

        self.ud.createGroup(UI_GROUP_CURVE_GREEN,"Green",self.ud.idGroups[UI_GROUP_CURVE])
        self.ud.createIntSlider(UI_SLIDER_GREEN,50,self.ud.idGroups[UI_GROUP_CURVE_GREEN],"Precision")
        self.ud.createBool(UI_BOOL_GREEN_X,False,self.ud.idGroups[UI_GROUP_CURVE_GREEN],"Invert X")
        self.ud.createBool(UI_BOOL_GREEN_Y,False,self.ud.idGroups[UI_GROUP_CURVE_GREEN],"Invert Y")
        self.ud.createSpline(UI_SPLINE_GREEN,self.dataSpline[1],self.ud.idGroups[UI_GROUP_CURVE_GREEN],"Green")

        self.ud.createGroup(UI_GROUP_CURVE_BLUE,"Blue",self.ud.idGroups[UI_GROUP_CURVE])
        self.ud.createIntSlider(UI_SLIDER_BLUE,50,self.ud.idGroups[UI_GROUP_CURVE_BLUE],"Precision")
        self.ud.createBool(UI_BOOL_BLUE_X,False,self.ud.idGroups[UI_GROUP_CURVE_BLUE],"Invert X")
        self.ud.createBool(UI_BOOL_BLUE_Y,False,self.ud.idGroups[UI_GROUP_CURVE_BLUE],"Invert Y")
        self.ud.createSpline(UI_SPLINE_BLUE,self.dataSpline[2],self.ud.idGroups[UI_GROUP_CURVE_BLUE],"Blue")

    def createCreateTab(self):
        self.ud.createGroup(UI_GROUP_CREATE,"Create",c4d.DescID())
        self.ud.createStringInput(UI_STR_MAT_NAME,"Material Name",self.ud.idGroups[UI_GROUP_CREATE],"Material Name")

        self.ud.createSeparator(UI_SEPARATOR_RED,self.ud.idGroups[UI_GROUP_CREATE],"Red | Value [0.62 => 0.74] ~= 0.68")
        self.ud.createStringInput(UI_STR_RED_N,str(0.0001),self.ud.idGroups[UI_GROUP_CREATE], "n")
        self.ud.createStringInput(UI_STR_RED_K,str(0.0001),self.ud.idGroups[UI_GROUP_CREATE], "k")

        self.ud.createSeparator(UI_SEPARATOR_GREEN,self.ud.idGroups[UI_GROUP_CREATE],"Green | Value [0.495 => 0.570] ~= 0.5325")
        self.ud.createStringInput(UI_STR_GREEN_N,str(0.0001),self.ud.idGroups[UI_GROUP_CREATE], "n")
        self.ud.createStringInput(UI_STR_GREEN_K,str(0.0001),self.ud.idGroups[UI_GROUP_CREATE], "k")

        self.ud.createSeparator(UI_SEPARATOR_BLUE,self.ud.idGroups[UI_GROUP_CREATE],"Blue | Value [0.450 => 0.495] ~= 0.4725")
        self.ud.createStringInput(UI_STR_BLUE_N,str(0.0001),self.ud.idGroups[UI_GROUP_CREATE], "n")
        self.ud.createStringInput(UI_STR_BLUE_K,str(0.0001),self.ud.idGroups[UI_GROUP_CREATE], "k")

        self.ud.createButton(UI_BUTTON_CREATE,self.ud.idGroups[UI_GROUP_CREATE],"Create")

    def Init(self,node):
        self.dataSpline = [None]*3
        self.toInit = True

        self.miscFunction = miscFunction()
        self.jsonFunction = jsonFunction()
        self.ud = UD(node)

        self.jsonFunction.loadJsonFile()

        return True

    def refreshCycle(self, reset = False):
        self.jsonFunction.loadJsonFile()
        self.ud.createCycle(UI_CYCLE,self.jsonFunction.getAllName(),self.ud.idGroups[UI_GROUP_CURVE_METAL_TYPE],"Metal Type")
        if reset:
            if not self.jsonFunction.metalExist(self.ud.getCurrentCycleText(UI_CYCLE)):
                self.ud.obj[self.ud.idCycle[UI_CYCLE]] = 0
        self.refreshSpline()

    def refreshSpline(self):
        self.setSplineData()
        self.ud.createSpline(UI_SPLINE_RED,self.dataSpline[0])
        self.ud.createSpline(UI_SPLINE_GREEN,self.dataSpline[1])
        self.ud.createSpline(UI_SPLINE_BLUE,self.dataSpline[2])

    def Message(self, node, type, data):
        if type == c4d.MSG_MENUPREPARE:
            self.createCurveTab()
            self.createCreateTab()
            self.ud.createBcFromId()
            self.ud.setOldValue()
            self.toInit = False


        if self.toInit:
            if self.ud.idCycle[0] is None:
                self.toInit = False
                self.ud.populateIDFromBc()
                self.ud.setOldValue()
                if not self.jsonFunction.metalExist(self.ud.getCurrentCycleText(UI_CYCLE)):
                   self.refreshCycle(True)

        if type == c4d.MSG_DESCRIPTION_CHECKUPDATE:
            currentNbPts, currentInv, currentCycle = self.ud.getCurrentData()

            if self.ud.oldNbPoints != currentNbPts:
                diff = self.miscFunction.getDiff(self.ud.oldNbPoints,currentNbPts)
                for i in xrange(0,len(diff)):
                    self.setSplineData(diff[i])
                    self.ud.createSpline(diff[i],self.dataSpline[diff[i]])
                self.ud.oldNbPoints = currentNbPts
                

            if self.ud.oldInvert != currentInv:
                diff = self.miscFunction.getDiff(self.ud.oldInvert,currentInv)
                for i in xrange(0,len(diff)):
                    if diff[i] >= 3:
                        y = diff[i] - 3
                    else:
                        y = diff[i]
                    self.setSplineData(y)
                    self.ud.createSpline(y,self.dataSpline[y])
                self.ud.oldInvert = currentInv

            if self.ud.oldCycle != currentCycle:
                self.refreshCycle(True)      
                self.ud.oldCycle = currentCycle

        if type == c4d.MSG_DESCRIPTION_COMMAND:
            if data.has_key('id'):
                id = data['id'][0].id
                if(id == 700):
                    if data['id'] == self.ud.idButtons[UI_BUTTON_REFRESH]:
                        self.jsonFunction.loadJsonFile()
                        self.ud.createCycle(UI_CYCLE,self.jsonFunction.getAllName(),self.ud.idGroups[UI_GROUP_CURVE_METAL_TYPE],"Metal Type")
                        self.refreshCycle(True)

                    elif data['id'] == self.ud.idButtons[UI_BUTTON_CREATE]:
                        if self.checkValidData():
                            name, data = self.getValidData()
                            update = False
                            if self.jsonFunction.fileContent.has_key(name):
                                if c4d.gui.QuestionDialog("Are you sure to update " + str(name) ):
                                    update = True
                                else:
                                    return True
                            
                            self.jsonFunction.addData(name,data)
                            self.jsonFunction.saveJsonFile()

                            self.jsonFunction.loadJsonFile()
                            self.ud.createCycle(UI_CYCLE,self.jsonFunction.getAllName(),self.ud.idGroups[UI_GROUP_CURVE_METAL_TYPE],"Metal Type")
                            if update:
                                c4d.gui.MessageDialog(str(name) + " material successfully updated")
                            else:
                                c4d.gui.MessageDialog(str(name) + " material successfully created")

                    elif data['id'] == self.ud.idButtons[UI_BUTTON_DELETE]:
                        self.jsonFunction.deleteData(self.ud.getCurrentCycleText(UI_CYCLE))
                        self.jsonFunction.saveJsonFile()

                        self.refreshCycle(True)

        return True

    def getValidData(self):
        name = self.ud.obj[self.ud.idStringInput[UI_STR_MAT_NAME]]
        buffer = {}
        bufferR = {}
        bufferR["k"] = float(self.ud.obj[self.ud.idStringInput[UI_STR_RED_K]])
        bufferR["n"] = float(self.ud.obj[self.ud.idStringInput[UI_STR_RED_N]])
                        
        bufferG = {}
        bufferG["k"] = float(self.ud.obj[self.ud.idStringInput[UI_STR_GREEN_K]])
        bufferG["n"] = float(self.ud.obj[self.ud.idStringInput[UI_STR_GREEN_N]])
                        
        bufferB = {}
        bufferB["k"] = float(self.ud.obj[self.ud.idStringInput[UI_STR_BLUE_K]])
        bufferB["n"] = float(self.ud.obj[self.ud.idStringInput[UI_STR_BLUE_N]])
                        
        buffer["Red"] =  bufferR
        buffer["Green"] =  bufferG
        buffer["Blue"] =  bufferB

        return name, buffer

    def checkValidData(self):
        if len(self.ud.obj[self.ud.idStringInput[UI_STR_MAT_NAME]]) == 0:
            c4d.gui.MessageDialog('Material name can\'t be null')
            return False

        if not self.ud.obj[self.ud.idStringInput[UI_STR_RED_K]].replace('.','',1).replace(',','',1).replace(' ','',1).isdigit():
            c4d.gui.MessageDialog('Red k must be a digital number')
            return False

        if not self.ud.obj[self.ud.idStringInput[UI_STR_RED_N]].replace('.','',1).replace(',','',1).replace(' ','',1).isdigit():
            c4d.gui.MessageDialog('Red n must be a digital number')
            return False

        if not self.ud.obj[self.ud.idStringInput[UI_STR_GREEN_K]].replace('.','',1).replace(',','',1).replace(' ','',1).isdigit():
            c4d.gui.MessageDialog('Green k must be a digital number')
            return False

        if not self.ud.obj[self.ud.idStringInput[UI_STR_GREEN_N]].replace('.','',1).replace(',','',1).replace(' ','',1).isdigit():
            c4d.gui.MessageDialog('Green n must be a digital number')
            return False

        if not self.ud.obj[self.ud.idStringInput[UI_STR_BLUE_K]].replace('.','',1).replace(',','',1).replace(' ','',1).isdigit():
            c4d.gui.MessageDialog('Blue k must be a digital number')
            return False

        if not self.ud.obj[self.ud.idStringInput[UI_STR_BLUE_N]].replace('.','',1).replace(',','',1).replace(' ','',1).isdigit():
            c4d.gui.MessageDialog('Bleu n must be a digital number')
            return False

        return True

    def getCurveData(self,k,n,nbPoints):
        fresnelList = self.miscFunction.IOR(n, k)

        # Compensate for non-linear facingRatio
        linearValues = [ float(i)/90 for i in range(91) ]
        rawValues = [ math.sin(linearValues[i]*90*math.pi/180) for i in range(91) ]

        # Reduce curve points
        myline = zip(rawValues, fresnelList)
        precisionVals = [0.000001,0.000003,0.00005,0.00007,0.0001,0.00015,0.0002,0.00025,0.0003,0.0007,0.001,0.005,0.01,0.05]
        simplified = []

        for i in precisionVals:
            if len(simplified) == 0 or len(simplified) > nbPoints:
                simplified = self.miscFunction.ramerdouglas(myline, dist = i)

        return simplified

    def getCurveSpline(self,data,mode):
        spline = c4d.SplineData()
        spline.MakePointBuffer(len(data))
        for i in xrange(0,len(data)):
            vector = c4d.Vector(data[i][0],data[i][1],0)
            spline.SetKnot(i,vector)
        if mode == X_INVERTED:
            spline.Mirror()
        elif mode == Y_INVERTED:
            spline.Flip()
        elif mode == X_INVERTED + Y_INVERTED:
            spline.Flip()
            spline.Mirror()
        return spline

    def Execute(self, tag, doc, op, bt, priority, flags):
        return c4d.EXECUTIONRESULT_OK

if __name__ == "__main__":

    dir, file = os.path.split(__file__)
    bmp = c4d.bitmaps.BaseBitmap()
    bmp.InitWith(os.path.join(dir, "res", "RefractiveIndex.png"))
    c4d.plugins.RegisterTagPlugin(id=PLUGIN_ID, 
                                str='refractiveindex', 
                                g=lunchTag,
                                description="TREFLECTION_INDEX", 
                                icon=bmp,
                                info=c4d.TAG_EXPRESSION|c4d.TAG_VISIBLE|c4d.TAG_MULTIPLE)