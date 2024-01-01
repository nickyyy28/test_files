import time, os, msvcrt
from win32com.client import *
from win32com.client.connect import *


def DoEvents():
    pythoncom.PumpWaitingMessages()
    time.sleep(.1)


def DoEventsUntil(cond):
    while not cond():
        DoEvents()

class CanoeSync(object):
    """Wrapper class for CANoe Application object"""
    Started = False
    Stopped = False
    ConfigPath = ""

    def __init__(self):
        app = DispatchEx('CANoe.Application')
        app.Configuration.Modified = False
        ver = app.Version
        print('Loaded CANoe version ',
              ver.major, '.',
              ver.minor, '.',
              ver.Build, '...', sep='')
        self.App = app
        self.Measurement = app.Measurement
        self.Running = lambda: self.Measurement.Running
        self.WaitForStart = lambda: DoEventsUntil(lambda: CanoeSync.Started)
        self.WaitForStop = lambda: DoEventsUntil(lambda: CanoeSync.Stopped)
        self.Namespaces = self.App.System.Namespaces
        WithEvents(self.App.Measurement, CanoeMeasurementEvents)

    def Load(self, cfgPath):
        # current dir must point to the script file
        cfg = os.path.join(os.curdir, cfgPath)
        cfg = os.path.abspath(cfg)
        print('Opening: ', cfg)
        self.ConfigPath = os.path.dirname(cfg)
        self.Configuration = self.App.Configuration
        self.App.Open(cfg)

    def NamespaceCount(self):
        return self.Namespaces.Count

    def getNamespaces(self):
        # for i in range(0, self.NamespaceCount()):
        #     namespace = self.Namespaces.get_Item(i)
        #     name = namespace.Name
        #     print(f"name: {name}")
        name_space_obj = self.App.System.Namespaces.Item("demo1")
        variables = name_space_obj.Variables
        sysvar_obj = variables.Item("svTest")
        # sysvar_type = sysvar_obj.Type()
        sys_var_value = sysvar_obj.Value

        print("sysvar: svTest = {}".format(sys_var_value))
        time.sleep(10)
        sysvar_obj.Value = 1

    def get_sysvar(self, namespace: str, variable_name: str):
        name_space_obj = self.App.System.Namespaces.Item(namespace)
        variables = name_space_obj.Variables
        sysvar_obj = variables.Item(variable_name)
        return sysvar_obj.Value

    def set_sysvar(self, namespace: str, variable_name: str, value):
        name_space_obj = self.App.System.Namespaces.Item(namespace)
        variables = name_space_obj.Variables
        sysvar_obj = variables.Item(variable_name)
        sysvar_obj.Value = value

    def get_signal_var(self, channel_num, msg_name: str, signal_name: str, bus_type = "CAN"):
        result = self.App.GetBus(bus_type).GetSignal(channel_num, msg_name, signal_name)
        return result.Value

    def LoadTestSetup(self, testsetup):
        self.TestSetup = self.App.Configuration.TestSetup
        path = os.path.join(self.ConfigPath, testsetup)
        testenv = self.TestSetup.TestEnvironments.Add(path)
        testenv = CastTo(testenv, "ITestEnvironment2")
        # TestModules property to access the test modules
        self.TestModules = []
        self.TraverseTestItem(testenv, lambda tm: self.TestModules.append(CanoeTestModule(tm)))

    def LoadTestConfiguration(self, testcfgname, testunits):
        """ Adds a test configuration and initialize it with a list of existing test units """
        tc = self.App.Configuration.TestConfigurations.Add()
        tc.Name = testcfgname
        tus = CastTo(tc.TestUnits, "ITestUnits2")
        for tu in testunits:
            tus.Add(tu)
        # TestConfigs property to access the test configuration
        self.TestConfigs = [CanoeTestConfiguration(tc)]

    def Start(self):
        if not self.Running():
            self.Measurement.Start()
            self.WaitForStart()

    def Stop(self):
        if self.Running():
            self.Measurement.Stop()
            self.WaitForStop()

    def RunTestModules(self):
        """ starts all test modules and waits for all of them to finish"""
        # start all test modules
        for tm in self.TestModules:
            tm.Start()

        # wait for test modules to stop
        while not all([not tm.Enabled or tm.IsDone() for tm in app.TestModules]):
            DoEvents()

    def RunTestConfigs(self):
        """ starts all test configurations and waits for all of them to finish"""
        # start all test configurations
        for tc in self.TestConfigs:
            tc.Start()

        # wait for test modules to stop
        while not all([not tc.Enabled or tc.IsDone() for tc in app.TestConfigs]):
            DoEvents()

    def TraverseTestItem(self, parent, testf):
        for test in parent.TestModules:
            testf(test)
        for folder in parent.Folders:
            found = self.TraverseTestItem(folder, testf)


class CanoeMeasurementEvents(object):
    """Handler for CANoe measurement events"""

    def OnStart(self):
        CanoeSync.Started = True
        CanoeSync.Stopped = False
        print("< measurement started >")

    def OnStop(self):
        CanoeSync.Started = False
        CanoeSync.Stopped = True
        print("< measurement stopped >")


class CanoeTestModule:
    """Wrapper class for CANoe TestModule object"""

    def __init__(self, tm):
        self.tm = tm
        self.Events = DispatchWithEvents(tm, CanoeTestEvents)
        self.Name = tm.Name
        self.IsDone = lambda: self.Events.stopped
        self.Enabled = tm.Enabled

    def Start(self):
        if self.tm.Enabled:
            self.tm.Start()
            self.Events.WaitForStart()


class CanoeTestConfiguration:
    """Wrapper class for a CANoe Test Configuration object"""

    def __init__(self, tc):
        self.tc = tc
        self.Name = tc.Name
        self.Events = DispatchWithEvents(tc, CanoeTestEvents)
        self.IsDone = lambda: self.Events.stopped
        self.Enabled = tc.Enabled

    def Start(self):
        if self.tc.Enabled:
            self.tc.Start()
            self.Events.WaitForStart()


class CanoeTestEvents:
    """Utility class to handle the test events"""

    def __init__(self):
        self.started = False
        self.stopped = False
        self.WaitForStart = lambda: DoEventsUntil(lambda: self.started)
        self.WaitForStop = lambda: DoEventsUntil(lambda: self.stopped)

    def OnStart(self):
        self.started = True
        self.stopped = False
        print("<", self.Name, " started >")

    def OnStop(self, reason):
        self.started = False
        self.stopped = True
        print("<", self.Name, " stopped >")


# -----------------------------------------------------------------------------
# main
# -----------------------------------------------------------------------------
app = CanoeSync()

# loads the sample configuration
app.Load(r'F:\BaiduSyncdisk\CANoe\demo1\demo_CAN.cfg')

# add test modules to the configuration
# app.LoadTestSetup('TestEnvironments\Test Environment.tse')

# add a test configuration and a list of test units
# app.LoadTestConfiguration('TestConfiguration', ['TestConfiguration\EasyTest\EasyTest.vtuexe'])

# start the measurement
app.Start()

print(f"namespaces count: {app.NamespaceCount()}")
app.getNamespaces()
# runs the test modules
# app.RunTestModules()

# runs the test configurations
# app.RunTestConfigs()
i = 20
while True:
    signal_value = app.get_signal_var(0, "msgTest", "sgTest")
    print("signal value = {}".format(signal_value))
    i -= 1
    time.sleep(5)

# wait for a keypress to end the program
input("press enter to continue")
# while not msvcrt.kbhit():
#     DoEvents()
#     print("waiting")

# stops the measurement
app.Stop()
