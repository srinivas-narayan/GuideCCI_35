import os
import sys
import vtk
# import PyQt4.QtGui as QtGui #for Qt4 - not in python 3.5
import PyQt5.QtWidgets as QtGui
from vtk.util.colors import red, blue, white, black

# --------------------------------------------------- FILE SELECTION ---------------------------------------------------
app = QtGui.QApplication (sys.argv)
dialog = QtGui.QFileDialog()

input_dir = QtGui.QFileDialog.getExistingDirectory ( dialog, 'Open Directory', os.getenv ( 'HOME' ),
                                                     dialog.ShowDirsOnly | dialog.DontResolveSymlinks )
print ( input_dir )
if input_dir:  # True if a directory  was selected
    # input_stl = input_stl[0]  # input_stl is a tuple in Qt5 - first entry is complete path - keep this and discard rest!
    # dir_name = os.path.dirname(input_stl)
    mesh_list = []
    for root, dirs, files in os.walk ( input_dir ):
        for file in files:
            if file.endswith ( ".stl" ) and not (
                    file[0] == "." and "_Monaco"  in file):  # choose only stl files and not hidden ones or already flipped ones
                input_stl = file
                full_path = os.path.join ( root, file )
                print ( 'Processing : ', full_path )
                mesh_list.append ( full_path )
                # output_stl = file.replace ( '.stl', '_Monaco.stl' )
                output_stl = full_path.replace ( '.stl', '_Monaco.stl' )
                # ---------------------------------------------- VTK: READ & TRANSFORM & WRITE -----------------------------------------
                reader = vtk.vtkSTLReader ()
                reader.SetFileName ( full_path )
                reader.Update ()

                # 180 rotation around Z
                transform = vtk.vtkTransform ()
                transform.RotateZ ( 180 )

                transform_filter = vtk.vtkTransformPolyDataFilter ()
                transform_filter.SetTransform ( transform )
                transform_filter.SetInputConnection ( reader.GetOutputPort () )
                transform_filter.Update ()

                # Save transformed stl file
                stl_writer = vtk.vtkSTLWriter ()
                stl_writer.SetFileName ( output_stl )
                stl_writer.SetInputConnection ( transform_filter.GetOutputPort () )
                stl_writer.Write ()

                # ----------------------------------------------- FOR VISUALIZATION ONLY -----------------------------------------------
                # Visualize the stl input file
                mapper_stl1 = vtk.vtkPolyDataMapper ()
                mapper_stl1.SetInputConnection ( reader.GetOutputPort () )

                actor_stl1 = vtk.vtkActor ()
                actor_stl1.SetMapper ( mapper_stl1 )
                actor_stl1.GetProperty ().SetRepresentationToWireframe ()
                actor_stl1.GetProperty ().SetColor ( red )

                # Visualize the stl output file (transformed)
                mapper_stl2 = vtk.vtkPolyDataMapper ()
                mapper_stl2.SetInputConnection ( transform_filter.GetOutputPort () )

                actor_stl2 = vtk.vtkActor ()
                actor_stl2.SetMapper ( mapper_stl2 )
                actor_stl2.GetProperty ().SetRepresentationToWireframe ()
                actor_stl2.GetProperty ().SetColor ( blue )
                actor_stl2.GetProperty ().SetOpacity ( 0.5 )

                # Visualize a source_sphere at the Coordinate system origin
                source_sphere = vtk.vtkSphereSource ()
                source_sphere.SetCenter ( 0.0, 0.0, 0.0 )
                source_sphere.SetRadius ( 1 )
                source_sphere.SetPhiResolution ( 360 )
                source_sphere.SetThetaResolution ( 360 )
                source_sphere.Update ()

                mapper_sphere = vtk.vtkPolyDataMapper ()
                mapper_sphere.SetInputConnection ( source_sphere.GetOutputPort () )

                actor_sphere = vtk.vtkActor ()
                actor_sphere.SetMapper ( mapper_sphere )
                actor_sphere.GetProperty ().SetColor ( black )

                # Visualize a legend box
                actor_legend = vtk.vtkLegendBoxActor ()
                actor_legend.SetNumberOfEntries ( 2 )
                actor_legend.BorderOn ()
                # actor_legend.SetBorder(1)
                # actor_legend.BoxOn()
                actor_legend.SetEntryString ( 0, 'stl 1' )
                actor_legend.SetEntryColor ( 0, red )
                actor_legend.SetEntryColor ( 1, blue )
                actor_legend.SetEntryString ( 1, 'stl 2' )

                # place legend in lower right
                actor_legend.GetPositionCoordinate ().SetCoordinateSystemToView ()
                actor_legend.GetPositionCoordinate ().SetValue ( .5, -1.0 )
                actor_legend.GetPosition2Coordinate ().SetCoordinateSystemToView ()
                actor_legend.GetPosition2Coordinate ().SetValue ( 1.0, -0.5 )

                # Create a rendering window and renderer
                renderer = vtk.vtkRenderer ()
                renderer.SetBackground ( white )
                renderer_window = vtk.vtkRenderWindow ()
                renderer_window.AddRenderer ( renderer )

                # Create a render window interactor
                interactor = vtk.vtkRenderWindowInteractor ()
                interactor.SetRenderWindow ( renderer_window )

                # Assign actors to the renderer
                renderer.AddActor ( actor_stl1 )
                renderer.AddActor ( actor_stl2 )
                renderer.AddActor ( actor_sphere )
                renderer.AddActor ( actor_legend )

                # Visualize coordinate axes
                axes = vtk.vtkAxesActor ()
                widget = vtk.vtkOrientationMarkerWidget ()
                widget.SetOrientationMarker ( axes )
                widget.SetInteractor ( interactor )
                widget.SetEnabled ( 1 )
                widget.InteractiveOn ()

                renderer.ResetCamera ()
                renderer.GetActiveCamera ().Zoom ( 1.3 )

                # Enable user interface interactor
                interactor.Initialize ()
                renderer_window.Render ()
                interactor.Start ()
else:
    sys.exit ( 'NO DIRECTORY WAS CHOSEN' )
