# Missing Features Roadmap

Features not yet implemented in ClaudeBridge, with API documentation references.

## API Documentation Links

- **Fusion 360 API Reference**: https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-7B5A90C8-E94C-48DA-B16B-430729B734DC
- **API Object Model (PDF)**: https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/ExtraFiles/Fusion.pdf
- **Python API Samples**: https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-A92A4B10-3781-4925-94C6-47DA85A4F65A

---

## Delete & Edit Operations (High Priority)

These enable reverting changes and iterative design.

| Feature | Description | API Reference |
|---------|-------------|---------------|
| `delete_feature` | Delete feature from timeline | https://adndevblog.typepad.com/manufacturing/2016/07/delete-objects-with-fusion-360-api.html |
| `delete_body` | Delete/remove a body | Use `body.deleteMe()` - same reference as above |
| `delete_sketch` | Delete a sketch | Use `sketch.deleteMe()` - same reference as above |
| `suppress_feature` | Temporarily disable feature | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/TimelineObject_isSuppressed.htm |
| `unsuppress_feature` | Re-enable suppressed feature | Same as above - set `isSuppressed = False` |
| `timeline_rollback` | Move timeline marker | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Timeline_markerPosition.htm |
| `edit_feature` | Modify existing feature parameters | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ExtrudeFeature.htm |

---

## Additional 3D Features (High Priority)

| Feature | Description | API Reference |
|---------|-------------|---------------|
| `sweep` | Extrude profile along path | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/SweepFeatureSample_Sample.htm |
| `loft` | Create shape between profiles | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/LoftFeatureSample_Sample.htm |
| `hole` | Create holes (simple/counterbore/countersink) | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/HoleFeature.htm |
| `thread` | Add threads to cylindrical faces | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ThreadFeature.htm |
| `combine` | Join/cut/intersect bodies | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/CombineFeature.htm |
| `split_body` | Split body with plane/face | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/SplitBodyFeature.htm |

---

## Patterns & Mirrors (Medium Priority)

| Feature | Description | API Reference |
|---------|-------------|---------------|
| `rectangular_pattern` | Pattern in rows/columns | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/RectangularPatternFeature.htm |
| `circular_pattern` | Pattern around axis | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/CircularPatternFeature.htm |
| `mirror_feature` | Mirror across plane | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/MirrorFeature.htm |
| `path_pattern` | Pattern along path | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/PathPatternFeature.htm |

---

## Construction Geometry (Medium Priority)

| Feature | Description | API Reference |
|---------|-------------|---------------|
| `create_offset_plane` | Plane offset from existing | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ConstructionPlaneSample_Sample.htm |
| `create_plane_at_angle` | Angled construction plane | Same sample - use `setByAngle()` |
| `create_plane_through_points` | Plane through 3 points | Same sample - use `setByThreePoints()` |
| `create_construction_axis` | Axis through points/edges | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ConstructionAxisSample_Sample.htm |
| `create_construction_point` | Reference point | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ConstructionPointSample_Sample.htm |

---

## Additional Sketch Curves (Medium Priority)

| Feature | Description | API Reference |
|---------|-------------|---------------|
| `draw_arc` | Arc by center/start/end | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/SketchArcs.htm |
| `draw_arc_three_points` | Arc through 3 points | Same - use `addByThreePoints()` |
| `draw_ellipse` | Draw ellipse | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/SketchEllipses.htm |
| `draw_spline` | Spline through points | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/SketchFittedSplines.htm |
| `draw_polygon` | Regular polygon | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/SketchLines.htm (loop) |
| `draw_slot` | Slot shapes | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/SketchSlots.htm |
| `project_geometry` | Project edges/faces to sketch | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Sketch_project.htm |
| `offset_curves` | Offset existing curves | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Sketch_offset.htm |
| `mirror_sketch_entities` | Mirror within sketch | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/GeometricConstraints_addSymmetry.htm |

---

## Sketch Constraints & Dimensions (Medium Priority)

| Feature | Description | API Reference |
|---------|-------------|---------------|
| `add_sketch_dimension` | Parametric dimension | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/SketchDimensions.htm |
| `add_constraint_horizontal` | Horizontal constraint | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/GeometricConstraints_addHorizontal.htm |
| `add_constraint_vertical` | Vertical constraint | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/GeometricConstraints_addVertical.htm |
| `add_constraint_coincident` | Connect points | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/GeometricConstraints_addCoincident.htm |
| `add_constraint_tangent` | Tangent curves | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/GeometricConstraints_addTangent.htm |
| `add_constraint_perpendicular` | Perpendicular | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/GeometricConstraints_addPerpendicular.htm |
| `add_constraint_parallel` | Parallel lines | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/GeometricConstraints_addParallel.htm |
| `add_constraint_equal` | Equal lengths | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/GeometricConstraints_addEqual.htm |
| `add_constraint_concentric` | Concentric circles | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/GeometricConstraints_addConcentric.htm |
| `add_constraint_midpoint` | Point at midpoint | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/GeometricConstraints_addMidPoint.htm |

**Constraints Overview**: https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Sketch_geometricConstraints.htm

---

## Body Operations (Lower Priority)

| Feature | Description | API Reference |
|---------|-------------|---------------|
| `move_body` | Move/rotate body | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/MoveFeature.htm |
| `copy_body` | Duplicate body | Use rectangular pattern with count=1 (API limitation) |
| `scale_body` | Scale body | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ScaleFeature.htm |
| `offset_faces` | Push/pull faces | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/OffsetFacesFeature.htm |
| `draft` | Add draft angle | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/DraftFeature.htm |
| `rib` | Create structural ribs | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/RibFeature.htm |
| `web` | Create structural web | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/WebFeature.htm |
| `press_pull` | Direct face manipulation | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/PressPullFeature.htm |

---

## Components & Assembly (Lower Priority)

| Feature | Description | API Reference |
|---------|-------------|---------------|
| `create_component` | Create new component | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Occurrences_addNewComponent.htm |
| `create_joint` | Add assembly joint | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Joints.htm |
| `create_as_built_joint` | Joint from position | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/AsBuiltJoints.htm |
| `ground_component` | Fix in place | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Occurrence_isGrounded.htm |

---

## Export & File Operations (Utility)

| Feature | Description | API Reference |
|---------|-------------|---------------|
| `export_stl` | Export to STL | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ExportManager_createSTLExportOptions.htm |
| `export_step` | Export to STEP | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ExportManager_createSTEPExportOptions.htm |
| `export_f3d` | Export Fusion archive | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ExportManager_createFusionArchiveExportOptions.htm |
| `export_iges` | Export to IGES | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ExportManager_createIGESExportOptions.htm |
| `save_design` | Save current design | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/FusionDocument_save.htm |
| `save_as` | Save with new name | https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/FusionDocument_saveAs.htm |

**Export Manager Overview**: https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ExportManager.htm

---

## Additional Resources

- **Manufacturing DevBlog (Fusion 360)**: https://adndevblog.typepad.com/manufacturing/fusion-360/
- **Mod the Machine Blog**: https://modthemachine.typepad.com/
- **Autodesk Fusion API Forum**: https://forums.autodesk.com/t5/fusion-api-and-scripts/bd-p/22
- **GitHub API Samples**: https://autodeskfusion360.github.io/
- **What's New in API**: https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/WhatsNew.htm
