import nukescripts
import nuke

def edgextend():
 
    nuke.message('Make sure you did not choose any node. If you did, it could appear in the created EdgeExtension group')
    edge=nuke.collapseToGroup()
    edge['name'].setValue("EdgeExtention")
    mainGroup = nuke.toNode('EdgeExtention')
 
    for node in mainGroup.nodes():
        if node.Class() == "Input":
            inp = node
        elif node.Class() == "Output":
            outp = node

    #get max values for blurring and extension
    blur = nuke.getInput("Maximum value for blurring slider:", "5")
    exten = nuke.getInput("Maximum value for extension slider:", "5")
 
    #convert to floats
    exrange = int(float(exten))
    blrange = int(float(blur))
 
    #create floating point scrollbar for extension
    knobex = nuke.WH_Knob("extention")
    mainGroup.addKnob(knobex)
 
    #set range for extension scrollbar
    knobex.setRange(0,exrange)
 
    #create floating point scrollbar for blurring
    knobbl = nuke.WH_Knob("blurring")
    mainGroup.addKnob(knobbl)
 
    #set range for blurring scrollbar
    knobbl.setRange(0,blrange)
 #create buttons for creating new EdgeExtend group and deleting last EdgeExtend group
    createBTN = nuke.PyScript_Knob("Create_BTN", "Create new EdgeExtention", command=createNewEdgeExtensionGroup(mainGroup, inp, outp, exrange, blrange))
    mainGroup.addKnob(createBTN)
    fileCreate = open("D:\WORK for Tomasz\Edge extention\commandCreateScript.txt","r")
    createCommand = fileCreate.read()
    mainGroup['Create_BTN'].setCommand(createCommand)
    deleteBTN = nuke.PyScript_Knob("Del_BTN", "Delete one EdgeExtention")
    mainGroup.addKnob(deleteBTN)
    fileDelete = open("D:\WORK for Tomasz\Edge extention\commandDeleteScript.py","r")
    deleteCommand = fileDelete.read()
    mainGroup['Del_BTN'].setCommand(deleteCommand)
 
 
def createNewEdgeExtensionGroup(main, inp, outp, exrange, blrange):
    i=0
    with main:
        for nodes in nuke.selectedNodes():
            nodes.setSelected(False)
        for node in main.nodes():
            if node.Class()=='Group':
                i+=1
        index=str(i)
        nameNode = "EdgeExtend"+index
        create=nuke.collapseToGroup()
        create.hideControlPanel()
        create['name'].setValue(nameNode)
        subGroup = nuke.toNode(nameNode)
        create.setInput(0,inp)
        outp.setInput(0, create)
  
        #create floating point scrollbar for extension
        knobex = nuke.WH_Knob("extention")
        create.addKnob(knobex)
        expression_subext='''[python -exec {ret=nuke.toNode("EdgeExtention")["extention"].value()}][python ret] '''
        create['extention'].setExpression(expression_subext, 0)
        #set range for extension scrollbar
        knobex.setRange(0,exrange)
        
        #create floating point scrollbar for blurring
        knobbl = nuke.WH_Knob("blurring")
        create.addKnob(knobbl)
        expression_subblu='''[python -exec {ret=nuke.toNode("EdgeExtention")["blurring"].value()}][python ret] '''
        create['blurring'].setExpression(expression_subblu, 0)
  
        #set range for blurring scrollbar
        knobbl.setRange(0,blrange)
  
        for node in create.nodes():
            if node.Class() == "Input":
                inpSub = node
            elif node.Class() == "Output":
                outSub = node
        with create:
            prem = nuke.createNode("Premult", inpanel=False)
            nameKernel='BoxBlur2D'
            fileText1 = 'kernel BoxBlur2D : public ImageComputationKernel<eComponentWise>\n{\n  Image<eRead, eAccessRanged2D, eEdgeClamped> src;\n  Image<eWrite, eAccessPoint> dst;\n param:\n  int xRadius;  //The horizontal radius of our box blur\n  int yRadius;  //The vertical radius of our box blur\n\nlocal:\n  int _filterSize;\n\n  void define() {\n    defineParam(xRadius, "RadiusX", 5); \n    defineParam(yRadius, "RadiusY", 3); \n  }\n\n  void init() {\n    //Set the range we need to access from the source \n    src.setRange(-xRadius, -yRadius, xRadius, yRadius);\n\n    _filterSize = (2 * xRadius + 1) * (2 * yRadius + 1);\n  }\n\n  void process() {\n    float sum = 0.0f;\n    for(int j = -yRadius; j <= yRadius; j++)\n      for(int i = -xRadius; i <= xRadius; i++)\n        sum += src(i, j);\n    dst() = sum / (float)_filterSize;\n  }\n}; '
            blinkNode = nuke.nodes.BlinkScript(kernelSource=fileText1, name=nameKernel)
            blinkNode['reloadKernelSourceFile'].execute()
            blinkNode['recompile'].execute()
            blinkNode['publishButton'].execute()
            blur1 = nuke.selectedNode()
            extentionx = blur1['RadiusX']
            expression_ext='''[python -exec {ret=nuke.toNode("EdgeExtend'''+index+'''")["extention"].value()}][python ret] '''
            extentionx.setExpression(expression_ext,0)
            extentiony = blur1['RadiusY']
            extentiony.setExpression(expression_ext,0)
            blinkNode['publishButton'].execute()
            expression_blur='''[python -exec {ret=nuke.toNode("EdgeExtend'''+index+'''")["blurring"].value()}][python ret] '''
            blur2=nuke.selectedNode()
            blurringx = blur2['RadiusX']
            blurringx.setExpression(expression_blur,0)
            blurringy = blur2['RadiusY']
            blurringy.setExpression(expression_blur,0)
            unprem = nuke.createNode("Unpremult", inpanel=False)
            mer = nuke.createNode("Merge2", inpanel=False)
            prem.setInput(0, inpSub)
            blur1.setInput(0, prem)
            unprem.setInput(0, blur1)
            blur2.setInput(0, unprem)
            mer.setInput(0, blur2)
            mer.setInput(1, prem)
            outSub.setInput(0, mer)


nuke.menu('Nodes').addCommand('CustomCommands/EdgeExtend',edgextend)