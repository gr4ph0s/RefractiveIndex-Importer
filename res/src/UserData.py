import c4d

from .Const import Const

class UD():
    """
    Class for handle our UserData. Since we cant access to curve data from Ressource file in python.
    The only solution is to build our object menu ourself via userData.
    It's a bit tricky since we have to rebuild everything from sratch everytime.
    But user don't want to looses their settings if they open/close c4d, so we store all datas in our tag basecontainer
    If there is no BaseCtonainer we build it from scratch
    """
    def __init__(self, obj):
        self.obj = obj

        #List who gonna store our id of our UserData
        # 0 = R // 1 = G // 2 = B
        self.idCycle = [None] * 1
        self.idGroups = [None] * 6
        self.idSplines = [None] * 3
        self.idNbPoints = [None] * 3
        self.idInvert = [None] * 6
        self.idSeparator = [None] * 3
        self.idStringInput = [None] * 7
        self.idButtons = [None] * 3

        self.oldCycle = None
        self.oldNbPoints = [None] * 3
        self.oldInvert = [None] * 6

    def create_group(self, groupId, name, parentGroup=None, columns=None, shortname=None, titleBar=True, Open=False):
        """
        Create a Group
        :param groupId: int => ID of the created groupID
        :param name: str => name of the group
        :param parentGroup: int => groupID of the parent group
        :param columns: int => number of columns
        :param shortname: str => display name of the group if we don't want to display name
        :param titleBar: bool => if we can hide the group
        :param Open: bool => If the group is opened or not
        :return: The list of groups with the newly created one
        """
        if (self.idGroups[groupId]) is None:
            if shortname is None: shortname = name
            bc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_GROUP)
            bc[c4d.DESC_NAME] = name
            bc[c4d.DESC_SHORT_NAME] = shortname
            bc[c4d.DESC_TITLEBAR] = int(titleBar)
            bc[c4d.DESC_GUIOPEN] = int(Open)
            if parentGroup is not None:
                bc[c4d.DESC_PARENTGROUP] = parentGroup
            if columns is not None:
                # DESC_COLUMNS VALUE IS WRONG IN 15.057 - SHOULD BE 22
                bc[22] = columns

            self.idGroups[groupId] = self.obj.AddUserData(bc)
            return self.idGroups

    def create_separator(self, separatorId, parentGroup=None, name=""):
        """
        Create a separator
        :param separatorId: int => ID of the created separator
        :param parentGroup: int => groupID of the parent group
        :param name: name but can be empty string
        :return: The list of separator with the newly created one
        """
        if (self.idSeparator[separatorId]) is None:
            bc = c4d.GetCustomDataTypeDefault(c4d.DTYPE_SEPARATOR)
            bc[c4d.DESC_NAME] = name
            bc[c4d.DESC_SHORT_NAME] = name
            bc[c4d.DESC_PARENTGROUP] = parentGroup
            bc.SetLong(c4d.DESC_CUSTOMGUI, c4d.DTYPE_SEPARATOR)
            bc.SetBool(c4d.DESC_SEPARATORLINE, False)
            self.idSeparator[separatorId] = self.obj.AddUserData(bc)
            return self.idSeparator

    def create_button(self, buttonId, parentGroup=None, name=""):
        """
        Create a button
        :param buttonId: int => ID of the created button
        :param parentGroup: int => groupID of the parent group
        :param name: name but can be empty string
        :return: The list of button with the newly created one
        """
        if (self.idButtons[buttonId]) is None:
            bc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_BUTTON)
            bc[c4d.DESC_NAME] = name
            bc[c4d.DESC_SHORT_NAME] = name
            bc[c4d.DESC_PARENTGROUP] = parentGroup
            bc[c4d.DESC_CUSTOMGUI] = c4d.CUSTOMGUI_BUTTON
            self.idButtons[buttonId] = self.obj.AddUserData(bc)

    def create_string_input(self, floatId, value, parentGroup=None, name=""):
        """
        Create an input string
        :param floatId: int => ID of the created InputField
        :param value: str => value of the InputField
        :param parentGroup: int => groupID of the parent group
        :param name: str => name of the inputField
        :return: The list of InputField with the newly created one
        """
        if (self.idStringInput[floatId]) is None:
            bc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_STRING)
            bc[c4d.DESC_NAME] = name
            bc[c4d.DESC_PARENTGROUP] = parentGroup
            self.idStringInput[floatId] = self.obj.AddUserData(bc)
            self.obj[self.idStringInput[floatId]] = value
            return self.idStringInput
        else:
            self.obj[self.idStringInput[floatId]] = value
            return self.idStringInput

    def create_int_slider(self, sliderId, value, parentGroup=None, sliderText=""):
        """
        Create a slider of integer
        :param sliderId: int => ID of the created Slider
        :param value: int => default value of the slider
        :param parentGroup: int => groupID of the parent group
        :param sliderText: the name of the slider
        :return: The list of IntSlider with the newly created one
        """
        if (self.idNbPoints[sliderId]) is None:
            bc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_LONG)
            bc[c4d.DESC_CUSTOMGUI] = c4d.CUSTOMGUI_LONGSLIDER
            bc[c4d.DESC_NAME] = sliderText
            bc[c4d.DESC_MIN] = 10
            bc[c4d.DESC_MAX] = 100
            bc[c4d.DESC_PARENTGROUP] = parentGroup
            self.idNbPoints[sliderId] = self.obj.AddUserData(bc)  # Add userdata container
            self.obj[self.idNbPoints[sliderId]] = value
            return self.idNbPoints
        else:
            self.obj[self.idNbPoints[sliderId]] = value
            return self.idNbPoints[sliderId]

    def create_cycle(self, cycleId, data, parentGroup=None, cycleText=""):
        """
        Create a cycle
        :param cycleId: int => ID of the created cycle
        :param data: list of value ordered
        :param parentGroup: int => groupID of the parent group
        :param cycleText: the name of the slider
        :return: The list of Cycle with the newly created one
        """
        if (self.idCycle[cycleId]) is None:
            bc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_LONG)
            bc[c4d.DESC_NAME] = cycleText
            bc[c4d.DESC_CUSTOMGUI] = c4d.CUSTOMGUI_CYCLE
            bc[c4d.DESC_PARENTGROUP] = parentGroup
            bc[c4d.DESC_MIN] = 0
            bc[c4d.DESC_MAX] = len(data) - 1

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

                    bc[c4d.DESC_MAX] = len(data) - 1
                    bc.SetContainer(c4d.DESC_CYCLE, cycle)
                    self.obj.SetUserDataContainer(id, bc)
            return self.idCycle

    def create_spline(self, colorId, splineData, parentGroup=None, splineText=""):
        """
        Create a Spline Ui
        :param colorId: int => ID of hte created spline ID
        :param splineData: c4d.SplineData => Data for the spline
        :param parentGroup: int => groupID of the parent group
        :param splineText: str => the name of the slider
        :return: The list of Spline with the newly created one
        """
        if (self.idSplines[colorId]) is None:
            bc = c4d.GetCustomDatatypeDefault(1009060)  # Create default container
            bc[c4d.DESC_NAME] = splineText  # Rename the entry
            bc[c4d.DESC_PARENTGROUP] = parentGroup
            self.idSplines[colorId] = self.obj.AddUserData(bc)  # Add userdata container
            self.obj[self.idSplines[colorId]] = splineData
            return self.idSplines
        else:
            self.obj[self.idSplines[colorId]] = splineData
            return self.idSplines[colorId]

    def create_bool(self, id, value, parentGroup, boolText=""):
        """
        Create a checkbox
        :param id: int => Id of the created Checkbox
        :param value: bool => Default value
        :param parentGroup: int => groupID of the parent group
        :param boolText: str => the name of the slider
        :return: The lsit of Checkboxs with the newly created one
        """
        if (self.idInvert[id]) is None:
            bc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_BOOL)  # Create default container
            bc[c4d.DESC_NAME] = boolText  # Rename the entry
            bc[c4d.DESC_PARENTGROUP] = parentGroup
            self.idInvert[id] = self.obj.AddUserData(bc)  # Add userdata container
            self.obj[self.idInvert[id]] = value
            return self.idInvert
        else:
            self.obj[self.idInvert[id]] = value
            return self.idInvert[id]

    def get_current_data(self):
        """
        Get all data from User Data to variable.
        :return:
        [listOfPoint_Red, listOfPoint_Blue, listOfPoint_Red],
        [list of the InvertState], #actually there 6 since there is INVERT_X and INVERT_Y for each component of RGB
        [list of the cycle value] #There is always only one value
        """
        bufferCycle = list()
        bufferCycle.append(self.obj[self.idCycle[Const.UI_CYCLE]])

        bufferNbPts = list()
        bufferNbPts.append(self.obj[self.idNbPoints[Const.UI_SPLINE_RED]])
        bufferNbPts.append(self.obj[self.idNbPoints[Const.UI_SPLINE_GREEN]])
        bufferNbPts.append(self.obj[self.idNbPoints[Const.UI_SPLINE_BLUE]])

        bufferInvert = list()
        bufferInvert.append(self.obj[self.idInvert[Const.UI_BOOL_RED_X]])
        bufferInvert.append(self.obj[self.idInvert[Const.UI_BOOL_GREEN_X]])
        bufferInvert.append(self.obj[self.idInvert[Const.UI_BOOL_BLUE_X]])
        bufferInvert.append(self.obj[self.idInvert[Const.UI_BOOL_RED_Y]])
        bufferInvert.append(self.obj[self.idInvert[Const.UI_BOOL_GREEN_Y]])
        bufferInvert.append(self.obj[self.idInvert[Const.UI_BOOL_BLUE_Y]])

        return bufferNbPts, bufferInvert, bufferCycle

    def set_old_value(self):
        """
        Set the value which are typed previously
        """
        self.oldNbPoints = list()
        self.oldInvert = list()

        for i in xrange(0, len(self.idNbPoints)):
            self.oldNbPoints.append(self.obj[self.idNbPoints[i]])

        for i in xrange(0, len(self.idInvert)):
            self.oldInvert.append(self.obj[self.idInvert[i]])

    def get_mode_inverted(self, id):
        """
        Return the state of invert data
        :param id: the id to get (R G B)
        :return: 0 if X and Y not inverted
        1 if X inverted and Y not inverted
        2 if X not inverted and Y inverted
        3 if X and Y inverted
        """
        buffer = 0
        if self.obj[self.idInvert[id]]:
            buffer += Const.X_INVERTED

        if self.obj[self.idInvert[id + 3]]:
            buffer += Const.Y_INVERTED
        return buffer

    def get_current_cycle_text(self, cycleId):
        """
        Get all the datas of a cycle
        :param cycleId: the cycle id to get the data
        :return: str => the string representation of the actual value
        """
        for id, bc in self.obj.GetUserDataContainer():
            if id[1].id == self.idCycle[cycleId][1].id:
                bcCycle = bc.GetContainer(c4d.DESC_CYCLE)
                return bcCycle.GetString(self.obj[self.idCycle[cycleId]])

    def create_bc_from_list(self, liste):
        """
        Create a c4d.BaseContainer reprensation of a list.
        Allow us to store the actual user data in the object for recreation
        Inverse function of create_list_from_bc
        :param liste:
        :return: c4d.BaseContainer => the basecontainer representation of our list
        """
        buffer = c4d.BaseContainer()
        for i in xrange(0, len(liste)):
            buffer[i] = liste[i]
        return buffer

    def create_bc_from_id(self):
        """
        Get all data from our UD and store them to self.obj[Const.PLUGIN_ID] Container
        Inverse function of populateIDFromBc
        """
        bc = c4d.BaseContainer()
        bc[0] = self.create_bc_from_list(self.idCycle)
        bc[1] = self.create_bc_from_list(self.idGroups)
        bc[2] = self.create_bc_from_list(self.idSplines)
        bc[3] = self.create_bc_from_list(self.idNbPoints)
        bc[4] = self.create_bc_from_list(self.idInvert)
        bc[5] = self.create_bc_from_list(self.idSeparator)
        bc[6] = self.create_bc_from_list(self.idStringInput)
        bc[7] = self.create_bc_from_list(self.idButtons)
        currentBC = self.obj.GetDataInstance()
        currentBC[Const.PLUGIN_ID] = bc

    def create_list_from_bc(self, bc):
        """
        Create a list from c4d.BaseContainer
        Inverse function of createBcFromList
        :param bc: c4d.BaseContainer => The basecontainer to read value from
        :return: list => The list representation of our basecontainer
        """
        buffer = list()
        i = 0
        while i < len(bc):
            buffer.append(bc[i])
            i += 1
        return buffer

    def populate_id_from_bc(self):
        """
        Get all datas from self.obj[Const.PLUGIN_ID] Container and set userdata according thoses data
        """
        bc = self.obj.GetDataInstance().GetContainer(Const.PLUGIN_ID)
        self.idCycle = self.create_list_from_bc(bc[0])
        self.idGroups = self.create_list_from_bc(bc[1])
        self.idSplines = self.create_list_from_bc(bc[2])
        self.idNbPoints = self.create_list_from_bc(bc[3])
        self.idInvert = self.create_list_from_bc(bc[4])
        self.idSeparator = self.create_list_from_bc(bc[5])
        self.idStringInput = self.create_list_from_bc(bc[6])
        self.idButtons = self.create_list_from_bc(bc[7])