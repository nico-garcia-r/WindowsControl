 # coding: utf-8
"""
Base para desarrollo de modulos externos.
Para obtener el modulo/Funcion que se esta llamando:
     GetParams("module")

Para obtener las variables enviadas desde formulario/comando Rocketbot:
    var = GetParams(variable)
    Las "variable" se define en forms del archivo package.json

Para modificar la variable de Rocketbot:
    SetVar(Variable_Rocketbot, "dato")

Para obtener una variable de Rocketbot:
    var = GetVar(Variable_Rocketbot)

Para obtener la Opcion seleccionada:
    opcion = GetParams("option")


Para instalar librerias se debe ingresar por terminal a la carpeta "libs"
    
    pip install <package> -t .

"""
import os.path
base_path = tmp_global_obj["basepath"]
cur_path = base_path + "modules" + os.sep + "WindowsControl" + os.sep + "libs" + os.sep
sys.path.append(cur_path)

import pywinauto
from time import sleep
from uiautomation import uiautomation as auto
import json
import xml.etree.ElementTree as ET
import copy

try:
    #import pywinauto as pw
    """"""
except:
    pass
"""
    Obtengo el modulo que fueron invocados
"""
global module
module = GetParams("module")

"""
    Resuelvo catpcha tipo reCaptchav2
"""
global windowScope, ET


def getSelector(Selector):    
    command_ = {}    
    try:        
        if type(Selector) == str:
            Selector = Selector.replace("\\","\\\\")
            tmp = json.loads(Selector)
        else:
            tmp = Selector
        if "app" in tmp and len(str(tmp["app"])) > 0:
            command_["path"] = tmp["app"]
        if "title" in tmp and len(str(tmp["title"])) > 0:
            command_["title"] = tmp["title"]
        if "ctrlid" in tmp and len(str(tmp["ctrlid"])) > 0:
            command_["control_id"] = (int(tmp["ctrlid"]) if tmp["ctrlid"].isdigit() else tmp["ctrlid"])
        if "cls" in tmp and len(str(tmp["cls"])) > 0:
            command_["class_name"] = tmp["cls"]
        if "idx" in tmp and len(str(tmp["idx"])) > 0:
            command_["ctrl_index"] = int(tmp["idx"]) - 1
    except Exception as e:
        PrintException()
        raise Exception("Error on Selector XML or JSON :" + str(e))
    print("command \n",command_)
    return command_


def create_control(select, ancestor):
    # class_name = select["parent"]["cls"]
    if len(select["children"]) > 1:
        parent = select["children"][-2]
        has_parent = True
    else:
        parent = select["children"][-1]
        has_parent = False
    parent_control = None
    position_child = select["children"][-1]["idx"]
    automation_id = None
    name = None
    if "ctrlid" in parent:
        automation_id = parent["ctrlid"]
    if "title" in parent:
        name = parent["title"]

    if automation_id and name:

        parent_control = ancestor.Control(ControlTypeName=parent["ctrltype"], AutomationId=automation_id, Name=name)
    elif automation_id:
        parent_control = ancestor.Control(ControlTypeName=parent["ctrltype"], AutomationId=automation_id)
    elif name:
        parent_control = ancestor.Control(ControlTypeName=parent["ctrltype"], Name=name)

    if not has_parent:
        return parent_control

    if parent_control:
        for i, child in enumerate(parent_control.GetChildren()):
            if i == position_child:
                print(child)
                return child



def getChildren(window, Selector):
    global getSelector, ET
    """ Busca los hijos de la ventana"""
    da = []
    if str(Selector).startswith("<"):
        Selector = "<data>" + Selector + "</data>"
        da = ET.XML(Selector)
        for item in da:
           da.append(item)
        
        
    if str(Selector).startswith("{"):
        Selector = "[" + Selector + "]"
    if str(Selector).startswith("["):
        da = json.loads(Selector)
    print("da",da)
    w = window.child_window(**getSelector(da[0])).wait('visible', timeout=20)
    print("DA", da)
    if len(da[1:]) > 0:
        for item in da[1:]:
            try:                
                w = w.child_window(**getSelector(item)).wait('visible', timeout=20)
            except Exception as e:
                print("error w", e)
                PrintException()
                raise Exception(e)  
    print("w",w)
    return w

if module == "WindowScope":
    windowScope = None    
    Selector = GetParams("Selector")
    TimoutMS = GetParams("TimeoutMs")
    var_ = GetParams("result")    
    timeout_ = 30
    command_ = ""
    app = None

    try:
        if len(str(TimoutMS).strip()) > 0:
            timeout_ = int(TimoutMS)
    except:
        pass
    command_ = getSelector(Selector)
    command_["timeout"]=str(timeout_)
    if len(str(command_)) > 1:
        windowScope = pywinauto.Application()
        try:
            command_ = windowScope.connect( **command_ )
            windowScope.top_window().set_focus()
            # windowScope.top_window().print_control_identifiers()
        except Exception as e:
            SetVar( var_,  False)
            raise Exception(e)    

    else:
        raise Exception("No Selector")
    try:
        SetVar( var_,  True)
    except Exception as e:
        SetVar( var_,  False)
        raise Exception(e)

if module == "GetValue":
    Selector = GetParams("Selector")
    var_ = GetParams("result")
    parentControl = GetParams("parentControl")    
    control_by = GetParams("controlBy")    
    timeout_ = 30
    try:
        if not control_by:
            control_by = "ctrlid"
        selector = eval(Selector)

        className = selector["parent"]["cls"]
        ancestor = auto.WindowControl(ClassName=className)
        control = create_control(selector, ancestor)
        control.SetFocus()
        try:
            currentValue = control.GetPattern(10002).Value
        except:
            currentValue = control.GetWindowText()
        if currentValue is None:
            currentValue = control.Name
    
        SetVar( var_,  str(currentValue))
    except Exception as e:
        PrintException()
        raise e

if module == "SetValue":
    Selector = GetParams("Selector")
    var_ = GetParams("result")
    Text = GetParams("Text")
    clean = GetParams("Clean")
    timeout_ = 30
    
    try:
        selector = eval(Selector)
    except Exception as ex:
        PrintException()

    if "mozilla" in selector["parent"]["cls"].lower() or "chrome" in selector["parent"]["cls"].lower():
        className = selector["children"][0]["cls"]
    else:
        className = selector["parent"]["cls"]
    ancestor = auto.WindowControl(ClassName=className)
    control = create_control(selector, ancestor)
    control.SetFocus()
    if not clean:        
        try:
            currentValue = control.GetPattern(10002).Value
        except:
            currentValue = control.GetWindowText()

        if currentValue:
            Text = currentValue + "\r\n" + Text
    try:
        control.GetPattern(10002).SetValue(Text)
    except:
        control.SetWindowText(Text)
    
if module == "SelectItem":
    Selector = GetParams("Selector")
    var_ = GetParams("result")
    Item = GetParams("Item")
    timeout_ = 30
    result_=False
    try:
        selector = eval(Selector)
    except Exception as ex:
        PrintException()

    if str(Item).isnumeric():
        Item = int(Item)

    className = selector["parent"]["cls"]
    ancestor = auto.WindowControl(ClassName=className)
    control = create_control(selector, ancestor)

    control.GetValuePattern().SetValue(Item)
    try:
        SetVar( var_,  str(result_))
    except Exception as e:
        SetVar( var_, False)
        raise Exception(e)


if module == "Click":
    timeout_ = 30
    command_ = ""
    result_ = False
    simulateclick_ = False
    mousebutton_ = "left"
    double_= False
    button_down = True
    button_up = True
    var_ = GetParams("result")
    Selector = GetParams("Selector")
    TimoutMS = GetParams("TimeoutMs")
    SimulateClick = GetParams("SimulateClick")
    MouseButton = GetParams("MouseButton")
    ClickType = GetParams("ClickType")
    
    selector = eval(Selector)

    if not SimulateClick is None:
        simulateclick_ = SimulateClick

    if not ClickType == None:
        if ClickType == "CLICK_DOUBLE":
            double_ = True
        if ClickType == "CLICK_DOWN":
            button_up = False        
        if ClickType == "CLICK_UP":
            button_down = False

    if len(str(Selector)) > 1:
        try:
            if "mozilla" in selector["parent"]["cls"].lower() or "chrome" in selector["parent"]["cls"].lower():
                className = selector["children"][0]["cls"]
            else:
                className = selector["parent"]["cls"]
            ancestor = auto.WindowControl(ClassName=className)
            control = create_control(selector, ancestor)
        
            if ClickType != "CLICK_DOUBLE":
                if MouseButton == "BTN_LEFT":
                    control.Click(simulateMove=False, waitTime=0.5)
                if MouseButton == "BTN_RIGHT":
                    control.RightClick(simulateMove=False)
                if MouseButton == "BTN_MIDDLE":
                    control.MiddleClick(simulateMove=False)
            else:
                control.DoubleClick(simulateMove=False, waitTime=0.5)
            result_ = True
        except Exception as e:
            PrintException()
            raise e
    try:
        SetVar( var_,  str(result_))
    except Exception as e:
        PrintException()
        raise e

    
    