#Author-Autodesk
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback

# Dimensions for wardrobe
# unit is mm
HeightOfWardrobe = 240
WidthOfWardrobe = 200
DepthOfOuterwall = 60
DepthOfInnerwall = 49.5
ThicknessOfWall = 1.8
CountOfCombo = 2
CountOfPartition = 6

def createWardrobePattern(comp):
    # Create a new sketch
    sketch = comp.sketches.add(comp.xYConstructionPlane)
    sketch.isVisible = False
    
    # Create 4 outer walls
    cornerpt1 = adsk.core.Point3D.create(0, 0, 0)
    cornerpt2 = adsk.core.Point3D.create(WidthOfWardrobe, 0, 0)
    cornerpt3 = adsk.core.Point3D.create(WidthOfWardrobe, HeightOfWardrobe, 0)
    cornerpt4 = adsk.core.Point3D.create(0, HeightOfWardrobe, 0)
    outerwalls = adsk.core.ObjectCollection.create()
    lines = sketch.sketchCurves.sketchLines
    outerwalls.add(lines.addByTwoPoints(cornerpt1, cornerpt2))
    outerwalls.add(lines.addByTwoPoints(cornerpt2, cornerpt3))
    outerwalls.add(lines.addByTwoPoints(cornerpt3, cornerpt4))
    outerwalls.add(lines.addByTwoPoints(cornerpt4, cornerpt1))
    
    # Create inner walls according to the number of combo and partition
    widthOfCombo = WidthOfWardrobe / CountOfCombo
    heightOfPartition = HeightOfWardrobe / CountOfPartition
    innerwalls = adsk.core.ObjectCollection.create()
    for i in range(0, CountOfCombo):
        if i != 0:
            leftwallpt1 = adsk.core.Point3D.create(i * widthOfCombo + ThicknessOfWall/2 + 0.05, ThicknessOfWall, 0)
            leftwallpt2 = adsk.core.Point3D.create(i * widthOfCombo + ThicknessOfWall/2 + 0.05, HeightOfWardrobe - ThicknessOfWall, 0)
            innerwalls.add(lines.addByTwoPoints(leftwallpt1, leftwallpt2))
        if i != CountOfCombo - 1:
            rightwallpt1 = adsk.core.Point3D.create((i + 1) * widthOfCombo - ThicknessOfWall/2 - 0.05, ThicknessOfWall, 0)
            rightwallpt2 = adsk.core.Point3D.create((i + 1) * widthOfCombo - ThicknessOfWall/2 - 0.05, HeightOfWardrobe - ThicknessOfWall, 0)
            innerwalls.add(lines.addByTwoPoints(rightwallpt1, rightwallpt2))
            middlewallpt1 = adsk.core.Point3D.create((i + 0.5) * widthOfCombo, ThicknessOfWall, 0)
            middlewallpt2 = adsk.core.Point3D.create((i + 0.5) * widthOfCombo, HeightOfWardrobe - ThicknessOfWall, 0)
            innerwalls.add(lines.addByTwoPoints(middlewallpt1, middlewallpt2))
        for j in range(1, CountOfPartition):
            p1 = adsk.core.Point3D.create(i * widthOfCombo + ThicknessOfWall, j * heightOfPartition, 0)
            p2 = adsk.core.Point3D.create((i + 0.5) * widthOfCombo - ThicknessOfWall/2 - 0.05, j * heightOfPartition, 0)
            p3 = adsk.core.Point3D.create((i + 0.5) * widthOfCombo + ThicknessOfWall/2 + 0.05, j * heightOfPartition, 0)
            p4 = adsk.core.Point3D.create((i + 1) * widthOfCombo - ThicknessOfWall, j * heightOfPartition, 0)
            if i != CountOfCombo - 1:             
                innerwalls.add(lines.addByTwoPoints(p1, p2)) 
                innerwalls.add(lines.addByTwoPoints(p3, p4)) 
            elif j == CountOfPartition - 1:
                innerwalls.add(lines.addByTwoPoints(p1, p4))
                
    return outerwalls, innerwalls

def generateWardrobe(comp, outerwalls, innerwalls):
    # Extrude outer walls
    extrudes = comp.features.extrudeFeatures    
    outerwallsprofile = comp.createOpenProfile(outerwalls)
    outerwallsinput = extrudes.createInput(outerwallsprofile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    outerwallsinput.isSolid = False
    outerwallsinput.setDistanceExtent(False, adsk.core.ValueInput.createByReal(DepthOfOuterwall))
    outerwallsextrude = extrudes.add(outerwallsinput)
    
    # Thicken outer walls
    thickens = comp.features.thickenFeatures
    outerwallsfaces = adsk.core.ObjectCollection.create()
    for outerwallface in outerwallsextrude.sideFaces:
        outerwallsfaces.add(outerwallface)
    outerwallthickeninput = thickens.createInput(outerwallsfaces, adsk.core.ValueInput.createByReal(-1 * ThicknessOfWall), False, adsk.fusion.FeatureOperations.NewBodyFeatureOperation, False)
    thickens.add(outerwallthickeninput)
    
    # Create back wall
    patches = comp.features.patchFeatures
    backwallinput = patches.createInput(outerwalls, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    backwallpatch = patches.add(backwallinput)
        
    # Thicken back wall
    backwallfaces = adsk.core.ObjectCollection.create()
    for backwallface in backwallpatch.faces:
        backwallfaces.add(backwallface)
    backwallthickeninput = thickens.createInput(backwallfaces, adsk.core.ValueInput.createByReal(ThicknessOfWall), False, adsk.fusion.FeatureOperations.NewBodyFeatureOperation, False)
    thickens.add(backwallthickeninput)    
    
    # Extrude inner walls
    innerwallsprofiles = adsk.core.ObjectCollection.create()
    for innerwall in innerwalls:
        innerwallsprofiles.add(comp.createOpenProfile(innerwall))
    innerwallsinput = extrudes.createInput(innerwallsprofiles, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    innerwallsinput.isSolid = False
    innerwallsinput.setDistanceExtent(False, adsk.core.ValueInput.createByReal(DepthOfInnerwall))
    innerwallsextrude = extrudes.add(innerwallsinput)
    
    # Thicken inner walls
    innerwallsfaces = adsk.core.ObjectCollection.create()
    for innerwallface in innerwallsextrude.sideFaces:
        innerwallsfaces.add(innerwallface)
    innerwallsthickeninput = thickens.createInput(innerwallsfaces, adsk.core.ValueInput.createByReal(ThicknessOfWall/4), True, adsk.fusion.FeatureOperations.NewBodyFeatureOperation, False)
    thickens.add(innerwallsthickeninput)

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        
        # Get root component of current design.
        design = adsk.fusion.Design.cast(app.activeProduct)
        if design is None:
            ui.messageBox('Active product is not Design. Please switch to Model or Patch workspace and try again.')
        rootComp = design.rootComponent
        
        # Create design pathern of wardrobe according to predefined information 
        outerwalls, innerwalls = createWardrobePattern(rootComp)
        
        # Generate solids for the wardrobe
        generateWardrobe(rootComp, outerwalls, innerwalls)
        
        # Assign wood material 'Cherry' to the wardrobe
        lib = app.materialLibraries.itemById('C1EEA57C-3F56-45FC-B8CB-A9EC46A9994C')
        if lib:
            mat = lib.materials.itemById('PrismMaterial-245')
            if mat:
                rootComp.material = mat
        
        # Fit view
        app.activeViewport.fit()
        
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
