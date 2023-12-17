using System;
using System.Reflection;
using System.Linq;
using System.Collections.ObjectModel;
using Vector.Tools;
using Vector.CANoe.Runtime;
using Vector.CANoe.Threading;
using Vector.Diagnostics;
using Vector.Scripting.UI;
using Vector.CANoe.TFS;
using Vector.CANoe.VTS;
using System.Collections.Generic;
using NetworkDB;
using System.Threading;

public class MyTestClass
{
  [Export] [TestFunction]
  public static void CheckProjectName(String name)
  {
    //if (System_VAR.)
    Report.TestStepPass("test pass");
    
    var classes = Assembly.GetExecutingAssembly().GetTypes();
    foreach (var c in classes)
    {
        Report.TestStep(String.Format("class name: {0}, full name: {1}", c.Name, c.FullName));
    }
    
    double value = NetworkDB.sgSwitch.Value;
    Report.TestStep("sgswitch type: " + typeof(NetworkDB.sgSwitch).FullName);
    Report.TestStep(String.Format("sgSwitch: {0}", value));
    
    Assembly[] assemblies = AppDomain.CurrentDomain.GetAssemblies(); // 获取当前加载的所有程序集
    List<Type> signalTypes = new List<Type>();

    foreach (var assembly in assemblies)
    {
        var typesInNamespace = assembly.GetTypes();
        foreach (Type type in typesInNamespace)
        {
            //Report.TestStep(type.FullName);
          
          string fullname = type.FullName;
          if (fullname.StartsWith("NetworkDB") && !fullname.Contains("Frames") && !fullname.Contains("Changed")) {
            if (type == null) {
              Report.TestStepFail("type " + type.FullName + " is null");
              return;
            }
            signalTypes.Add(type);
            Report.TestStep("find signal: " + type.FullName);
            
            long timeout = 0;
            while(timeout < 50) {
              var myPropertyInfo = type.GetProperty("Value");
              object sgvalue = myPropertyInfo.GetValue(null, null);
              string reflect_value = Convert.ToString(sgvalue);
              Report.TestStep(String.Format("cnt:{0} signal: {1}, Value: {2}", timeout, type.Name, reflect_value));
              timeout --;
              Thread.Sleep(400);
            }
          }
        }
    }
    
    /*foreach(Type sgtype in signalTypes) {
      FieldInfo info = sgtype.GetField("Value", BindingFlags.Public | BindingFlags.Static);
      object sgvalue = info.GetValue(null);
      string reflect_value = Convert.ToString(sgvalue);
      Report.TestStep(String.Format("reflect get sgSwitch: {0}", reflect_value));
    }*/
    
    
  }
}