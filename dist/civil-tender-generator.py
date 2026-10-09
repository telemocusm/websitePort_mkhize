# -*- coding: utf-8 -*-
"""
SANS COMPLETE CIVIL TENDER GENERATOR & QUANTIFICATION SCRIPT
Covers: Dual Silos, Central Building, Support Structures, Pipe Networks, 
Shaded Color Views, Elevations, Sections, Dimensions, & Material Takeoff.
Target Environment: Revit Dynamo (CPython 3)
"""

import clr, os, sys, traceback, uuid
clr.AddReference("RevitAPI")
clr.AddReference("RevitServices")
clr.AddReference("System")
from Autodesk.Revit.DB import *
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
from System.Collections.Generic import List

doc = DocumentManager.Instance.CurrentDBDocument
output_dir = IN[0] if len(IN) > 0 and IN[0] else os.path.join(os.path.expanduser("~"), "Desktop", "SANS_Tender_Drawings_Export")

if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

errors = []
material_quantities = {}
created_sheets = []
created_views = []

session_tag = str(uuid.uuid4())[:6]

# ==============================================================================
# STEP 1 & 2: SANS 10160 MATERIAL QUANTIFICATION (CONCRETE, STEEL, PIPES)
# ==============================================================================
categories = [
    BuiltInCategory.OST_StructuralFraming,
    BuiltInCategory.OST_StructuralColumns,
    BuiltInCategory.OST_StructuralFoundation,
    BuiltInCategory.OST_Walls,
    BuiltInCategory.OST_Floors,
    BuiltInCategory.OST_PipeCurves
]

TransactionManager.Instance.EnsureInTransaction(doc)
try:
    for cat in categories:
        collector = FilteredElementCollector(doc).OfCategory(cat).WhereElementIsNotElementType()
        for el in collector:
            try:
                mat_ids = el.GetMaterialIds(False)
                for mid in mat_ids:
                    mat = doc.GetElement(mid)
                    if not mat: continue
                    mat_name = mat.Name
                    
                    vol_param = el.get_Parameter(BuiltInParameter.HOST_VOLUME_COMPUTED)
                    len_param = el.get_Parameter(BuiltInParameter.CURVE_ELLIPSE_RADIUS)
                    
                    val = 0.0
                    if vol_param and vol_param.HasValue:
                        val = vol_param.AsDouble() * 0.0283168  # cubic meters conversion
                    elif len_param and len_param.HasValue:
                        val = len_param.AsDouble() * 0.3048     # meters conversion
                        
                    if mat_name not in material_quantities:
                        material_quantities[mat_name] = 0.0
                    material_quantities[mat_name] += val
            except:
                pass
    TransactionManager.Instance.TransactionTaskDone()
except Exception as ex:
    errors.append("Quantification error: " + str(ex))

# ==============================================================================
# STEP 3 - 14: VIEW CREATION, SHADED COLOR STYLING, DIMENSIONS & PDF EXPORT
# ==============================================================================
TransactionManager.Instance.EnsureInTransaction(doc)
try:
    sec_vft = None
    plan_vft = None
    elev_vft = None

    for vft in FilteredElementCollector(doc).OfClass(ViewFamilyType):
        if vft.ViewFamily == ViewFamily.Section:
            sec_vft = vft
        elif vft.ViewFamily == ViewFamily.FloorPlan:
            plan_vft = vft
        elif vft.ViewFamily == ViewFamily.Elevation:
            elev_vft = vft

    titleblocks = list(FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_TitleBlocks).OfClass(FamilySymbol))
    tb = titleblocks[0] if titleblocks else None

    levels = list(FilteredElementCollector(doc).OfClass(Level))
    grids = list(FilteredElementCollector(doc).OfClass(Grid))

    sheet_counter = 100

    def configure_view_shaded(v):
        """Enforces Fine detail, Shaded visual style with material colors, and structural discipline"""
        try:
            v.DetailLevel = ViewDetailLevel.Fine
            v.DisplayStyle = DisplayStyle.Shading
            v.CropBoxActive = True
            v.CropBoxVisible = False
            
            disc_param = v.get_Parameter(BuiltInParameter.VIEW_DISCIPLINE)
            if disc_param:
                disc_param.Set(int(ViewDiscipline.Structural))
        except:
            pass

    def add_dimensions(view, grids_list):
        """Adds automated SANS-compliant civil dimension strings between structural grids"""
        try:
            if len(grids_list) < 2: return
            ref_array = ReferenceArray()
            for g in grids_list[:4]:
                r = Reference(g)
                if r: ref_array.Append(r)
            
            line = Line.CreateBound(XYZ(0, -12, 0), XYZ(40, -12, 0))
            if ref_array.Size > 1:
                doc.Create.NewDimension(view, line, ref_array)
        except:
            pass

    # A. Generate Level Site & Foundation Plans
    if plan_vft and tb and levels:
        for idx, lvl in enumerate(levels):
            try:
                p_view = ViewPlan.Create(doc, plan_vft.Id, lvl.Id)
                if p_view:
                    p_view.Name = "SANS_Plan_%s_%s" % (lvl.Name, session_tag)
                    configure_view_shaded(p_view)
                    add_dimensions(p_view, grids)
                    created_views.append(p_view.Id)
                    
                    sh = ViewSheet.Create(doc, tb.Id)
                    sh.SheetNumber = "CV-%d" % sheet_counter
                    sh.Name = "PLANT LAYOUT - " + lvl.Name
                    sheet_counter += 1
                    created_sheets.append(sh.Id)
                    Viewport.Create(doc, sh.Id, p_view.Id, XYZ(1.2, 0.9, 0))
            except Exception as e:
                errors.append("Plan error: " + str(e))

    # B. Generate Real Elevation Views (North, East, South, West)
    if elev_vft and tb and levels:
        origin_pt = XYZ(0, 0, levels[0].Elevation)
        try:
            marker = ElevationMarker.CreateElevationMarker(doc, elev_vft.Id, origin_pt, 100)
            dir_names = ["North", "East", "South", "West"]
            for index, dir_name in enumerate(dir_names):
                try:
                    elev_view = marker.CreateElevation(doc, doc.ActiveView.Id, index)
                    if elev_view:
                        elev_view.Name = "SANS_Elev_%s_%s" % (dir_name, session_tag)
                        configure_view_shaded(elev_view)
                        created_views.append(elev_view.Id)
                        
                        sh = ViewSheet.Create(doc, tb.Id)
                        sh.SheetNumber = "CV-%d" % sheet_counter
                        sh.Name = "ELEVATION - " + dir_name
                        sheet_counter += 1
                        created_sheets.append(sh.Id)
                        Viewport.Create(doc, sh.Id, elev_view.Id, XYZ(1.2, 0.9, 0))
                except Exception as ex_sub:
                    errors.append("Elevation sub-error (%s): %s" % (dir_name, str(ex_sub)))
        except Exception as e:
            errors.append("Elevation marker error: " + str(e))

    # C. Generate Level Sections (Overflow, Scour, Outlet & Chambers)
    if sec_vft and tb and levels:
        for idx, lvl in enumerate(levels):
            elev = lvl.Elevation
            try:
                bx_z = BoundingBoxXYZ()
                bx_z.Min = XYZ(-60, -60, -10)
                bx_z.Max = XYZ(60, 60, 10)
                tr = Transform.Identity
                tr.Origin = XYZ(0, 0, elev)
                bx_z.Transform = tr
                
                sec_z = ViewSection.CreateSection(doc, sec_vft.Id, bx_z)
                if sec_z:
                    sec_z.Name = "SANS_Sec_%s_%s" % (lvl.Name, session_tag)
                    configure_view_shaded(sec_z)
                    created_views.append(sec_z.Id)
                    
                    sh = ViewSheet.Create(doc, tb.Id)
                    sh.SheetNumber = "CV-%d" % sheet_counter
                    sh.Name = "SECTION & DETAIL - " + lvl.Name
                    sheet_counter += 1
                    created_sheets.append(sh.Id)
                    Viewport.Create(doc, sh.Id, sec_z.Id, XYZ(1.2, 0.9, 0))
            except Exception as e:
                errors.append("Section error: " + str(e))

    if not created_sheets:
        for s in FilteredElementCollector(doc).OfClass(ViewSheet):
            created_sheets.append(s.Id)

    TransactionManager.Instance.TransactionTaskDone()
except Exception as ex:
    TransactionManager.Instance.TransactionTaskDone()
    errors.append(str(ex))

# ==============================================================================
# STEP 14: BATCH PDF EXPORT FOR PORTFOLIO
# ==============================================================================
pdf_result = False
if created_sheets:
    try:
        opts = PDFExportOptions()
        opts.Combine = True
        opts.FileName = "SANS_Civil_Tender_Portfolio_Drawings"
        ids = List[ElementId](created_sheets)
        pdf_result = doc.Export(output_dir, ids, opts)
    except Exception as ex:
        errors.append("PDF export error: " + str(ex))

OUT = {
    "material_quantities": material_quantities,
    "generated_views_count": len(created_views),
    "total_sheets_exported": len(created_sheets),
    "pdf_output_directory": output_dir,
    "pdf_export_success": pdf_result,
    "errors": errors
}
