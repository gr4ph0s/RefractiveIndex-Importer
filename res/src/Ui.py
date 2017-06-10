import c4d
import math

from .Const import Const
from .MiscFunction import MiscFunction

class Ui():
    """
    Helper class for managing all our UI.
    Since we cant access to curve data from Ressource file in python.
    The only solution is to build our object menu ourself via userData.
    """
    miscFunct = MiscFunction()

    def __set_spline_data(self, gedialog, id, first):
        """
        set spline data of the according ID
        :param id: int => 0 = R // 1 = G // 2 = B
        :param first: boolf => if is the first tiem we build the ui
        """
        #Get rgb data from the json according cycle key value
        gedialog.RGBnk = gedialog.jsonFunction.get_RGB_data(gedialog.ud.get_current_cycle_text(Const.UI_CYCLE))

        buffer = ["Red","Green","Blue"]

        k = gedialog.RGBnk.get(buffer[id]).get("k")
        n = gedialog.RGBnk.get(buffer[id]).get("n")
        if not first:
            nbPoints = gedialog.ud.obj[gedialog.ud.idNbPoints[id]]
            mode = gedialog.ud.get_mode_inverted(id)
        else:
            nbPoints = 50
            mode = 0
        data = self.get_curve_data(k, n, nbPoints)
        gedialog.dataSpline[id] = self.get_curve_spline(data, mode)

    def set_spline_data(self, gedialog, id = 4 , first = False):
        """
        Set the spline data according self.dataSpline
        :param id: int => according id to set, if 4 set all splines
        :param first: bool => if is the first time we build the ui
        """
        if id == 4:
            for i in xrange(0,len(gedialog.dataSpline)):
                self.__set_spline_data(gedialog, i, first)
        else:
            self.__set_spline_data(gedialog, id, first)

    def get_curve_data(self, k, n, nbPoints):
        """
        Get the curve data for k, n and a given number of points
        more informations http://therenderblog.com/custom-fresnel-curves-in-maya/
        :param k: k material info
        :param n: n material info
        :param nbPoints: the total number of points
        :return: list of 2d vector(list with 2 entry)
        """
        fresnelList = self.miscFunct.IOR(n, k)

        # Compensate for non-linear facingRatio
        linearValues = [ float(i)/90 for i in range(91) ]
        rawValues = [ math.sin(linearValues[i]*90*math.pi/180) for i in range(91) ]

        # Reduce curve points
        myline = zip(rawValues, fresnelList)
        precisionVals = [0.000001,0.000003,0.00005,0.00007,0.0001,0.00015,0.0002,0.00025,0.0003,0.0007,0.001,0.005,0.01,0.05]
        simplified = []

        for i in precisionVals:
            if len(simplified) == 0 or len(simplified) > nbPoints:
                simplified = self.miscFunct.ramer_douglas(myline, dist = i)

        return simplified

    def get_curve_spline(self, datas, mode):
        """
        Get the c4d.SplineData of a list of 2d vector
        :param datas: list of 2d vector (list with 2 entry, see get_curve_data)
        :param mode:    0 if X and Y not inverted
                        1 if X inverted and Y not inverted
                        2 if X not inverted and Y inverted
                        3 if X and Y inverted
        :return: c4d.SplineData represnetation of list of 2d vector
        """

        #Create your Spline data
        spline = c4d.SplineData()
        spline.MakePointBuffer(len(datas))

        #Set our point
        for i, data in enumerate(datas):
            vector = c4d.Vector(data[0], data[1], 0)
            spline.SetKnot(i, vector)

        #Set if the curve is inverted / flipped or not
        if mode == Const.X_INVERTED:
            spline.Mirror()

        elif mode == Const.Y_INVERTED:
            spline.Flip()

        elif mode == Const.X_INVERTED + Const.Y_INVERTED:
            spline.Flip()
            spline.Mirror()

        return spline

    def refresh_cycle(self, gedialog, reset = False):
        """
        Refresh cycle data and spline data according the cycle data
        :param gedialog: c4d.plugins.TagData => tagData who store all our datas
        :param reset: bool => if True reset to first item
        """

        #Read data from json file and create/update our cycle data
        gedialog.jsonFunction.load_json_file()
        gedialog.ud.create_cycle(Const.UI_CYCLE,
                                gedialog.jsonFunction.get_all_name(),
                                gedialog.ud.idGroups[Const.UI_GROUP_CURVE_METAL_TYPE],
                                "Metal Type")

        #If reset we set ou cycle data to the first element
        if reset:
            if not gedialog.jsonFunction.metal_exist(gedialog.ud.get_current_cycle_text(Const.UI_CYCLE)):
                gedialog.ud.obj[gedialog.ud.idCycle[Const.UI_CYCLE]] = 0

        #Then we reset SplineUi
        self.set_spline_data(gedialog)
        gedialog.ud.create_spline(Const.UI_SPLINE_RED, gedialog.dataSpline[0])
        gedialog.ud.create_spline(Const.UI_SPLINE_GREEN, gedialog.dataSpline[1])
        gedialog.ud.create_spline(Const.UI_SPLINE_BLUE, gedialog.dataSpline[2])

    def get_valid_data(self, gedialog):
        """
        Get data from ud in proper dict
        :param gedialog: c4d.plugins.TagData => tagData who store all our datas
        :return: str name of the preset, dict of color of k/n dict
        """
        #Get the name from ud
        name = gedialog.ud.obj[gedialog.ud.idStringInput[Const.UI_STR_MAT_NAME]]

        #Get Red value from ud
        bufferR = dict()
        bufferR["k"] = float(gedialog.ud.obj[gedialog.ud.idStringInput[Const.UI_STR_RED_K]])
        bufferR["n"] = float(gedialog.ud.obj[gedialog.ud.idStringInput[Const.UI_STR_RED_N]])

        #Get Green value from ud
        bufferG = dict()
        bufferG["k"] = float(gedialog.ud.obj[gedialog.ud.idStringInput[Const.UI_STR_GREEN_K]])
        bufferG["n"] = float(gedialog.ud.obj[gedialog.ud.idStringInput[Const.UI_STR_GREEN_N]])

        #Get Blue value from ud
        bufferB = dict()
        bufferB["k"] = float(gedialog.ud.obj[gedialog.ud.idStringInput[Const.UI_STR_BLUE_K]])
        bufferB["n"] = float(gedialog.ud.obj[gedialog.ud.idStringInput[Const.UI_STR_BLUE_N]])

        #Concatenate our data into a unique dict
        buffer = dict()
        buffer["Red"] = bufferR
        buffer["Green"] = bufferG
        buffer["Blue"] = bufferB

        return name, buffer

    def check_valid_data(self, gedialog):
        """
        Check if value from user data are valid
        :param gedialog:  c4d.plugins.TagData => tagData who store all our datas
        :return: False if not valid, True if it's ok
        """
        if len(gedialog.ud.obj[gedialog.ud.idStringInput[Const.UI_STR_MAT_NAME]]) == 0:
            c4d.gui.MessageDialog('Material name can\'t be null')
            return False

        if not gedialog.ud.obj[gedialog.ud.idStringInput[Const.UI_STR_RED_K]].replace('.','',1).replace(',','',1).replace(' ','',1).isdigit():
            c4d.gui.MessageDialog('Red k must be a digital number')
            return False

        if not gedialog.ud.obj[gedialog.ud.idStringInput[Const.UI_STR_RED_N]].replace('.','',1).replace(',','',1).replace(' ','',1).isdigit():
            c4d.gui.MessageDialog('Red n must be a digital number')
            return False

        if not gedialog.ud.obj[gedialog.ud.idStringInput[Const.UI_STR_GREEN_K]].replace('.','',1).replace(',','',1).replace(' ','',1).isdigit():
            c4d.gui.MessageDialog('Green k must be a digital number')
            return False

        if not gedialog.ud.obj[gedialog.ud.idStringInput[Const.UI_STR_GREEN_N]].replace('.','',1).replace(',','',1).replace(' ','',1).isdigit():
            c4d.gui.MessageDialog('Green n must be a digital number')
            return False

        if not gedialog.ud.obj[gedialog.ud.idStringInput[Const.UI_STR_BLUE_K]].replace('.','',1).replace(',','',1).replace(' ','',1).isdigit():
            c4d.gui.MessageDialog('Blue k must be a digital number')
            return False

        if not gedialog.ud.obj[gedialog.ud.idStringInput[Const.UI_STR_BLUE_N]].replace('.','',1).replace(',','',1).replace(' ','',1).isdigit():
            c4d.gui.MessageDialog('Bleu n must be a digital number')
            return False

        return True

    def create_preset(self, gedialog):
        """
        Create a new preset, save into jsonFile, Refresh UserData
        :param gedialog: c4d.plugins.TagData => tagData who store all our datas
        """
        if self.check_valid_data(gedialog):
            name, data = self.get_valid_data(gedialog)
            update = False
            if gedialog.jsonFunction.fileContent.has_key(name):
                if c4d.gui.QuestionDialog("Are you sure to update {}".format(name)):
                    update = True
                else:
                    return True

            gedialog.jsonFunction.add_data(name, data)
            gedialog.jsonFunction.save_json_file()

            gedialog.jsonFunction.load_json_file()
            gedialog.ud.create_cycle(Const.UI_CYCLE,
                                    gedialog.jsonFunction.get_all_name(),
                                    gedialog.ud.idGroups[Const.UI_GROUP_CURVE_METAL_TYPE],
                                    "Metal Type")
            if update:
                c4d.gui.MessageDialog("{} material successfully updated".format(name))
            else:
                c4d.gui.MessageDialog("{} material successfully created".format(name))

    def delete_preset(self, gedialog):
        """
        Delete a preset, delete from jsonFile, Refresh UserData
        :param gedialog: c4d.plugins.TagData => tagData who store all our datas
        """
        gedialog.jsonFunction.delete_data(gedialog.ud.get_current_cycle_text(Const.UI_CYCLE))
        gedialog.jsonFunction.save_json_file()

        self.refresh_cycle(gedialog, True)

    def refresh_preset(self, gedialog):
        """
        Refresh alls preset, reload jsonData and refresh UserData
        :param gedialog: c4d.plugins.TagData => tagData who store all our datas
        """
        gedialog.jsonFunction.load_json_file()
        gedialog.ud.create_cycle(Const.UI_CYCLE,
                            gedialog.jsonFunction.get_all_name(),
                            gedialog.ud.idGroups[Const.UI_GROUP_CURVE_METAL_TYPE],
                            "Metal Type")
        self.refresh_cycle(gedialog, True)