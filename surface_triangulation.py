# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SurafaceTriangulation
                                 A QGIS plugin
 Plugin that creates a Delaunay triangulation from a dtm raster
                              -------------------
        begin                : 2015-12-14
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Luca Testone
        email                : lucatestone@yahoo.it
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QFileDialog, QDesktopServices
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from surface_triangulation_dialog import SurafaceTriangulationDialog
import os.path

import numpy as np
import scipy.spatial
import matplotlib
import math
import re
import linecache
import time
import matplotlib.tri as mtri
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from stl import mesh

class SurafaceTriangulation:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'SurafaceTriangulation_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = SurafaceTriangulationDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Surface Triangulation')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'SurafaceTriangulation')
        self.toolbar.setObjectName(u'SurafaceTriangulation')

        self.dlg.lineEdit.clear()
        self.dlg.pushButton.clicked.connect(self.select_output_file)
        self.dlg.rbVECTOR.clicked.connect(self.inputSwitch)
        self.dlg.rbASC.clicked.connect(self.inputSwitch)
        self.dlg.rbTXT.clicked.connect(self.outputSwitch)
        self.dlg.rbSTLASCII.clicked.connect(self.outputSwitch)
        self.dlg.rbSTLbinary.clicked.connect(self.outputSwitch)
        self.dlg.spinBox.setMaximum(100000)
    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('SurafaceTriangulation', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/SurafaceTriangulation/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Create triangulation'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Surface Triangulation'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
        
    def select_output_file(self):
		if self.dlg.rbSTLASCII.isChecked() or self.dlg.rbSTLbinary.isChecked():
			filename = QFileDialog.getSaveFileName(self.dlg, "Select output file ", QDesktopServices.storageLocation(QDesktopServices.DocumentsLocation) , '*.stl')
			self.dlg.lineEdit.setText(filename)
		elif self.dlg.rbTXT.isChecked():
			filename = QFileDialog.getSaveFileName(self.dlg, "Select output file ", QDesktopServices.storageLocation(QDesktopServices.DocumentsLocation) , '*.txt')
			self.dlg.lineEdit.setText(filename)
			
    def inputSwitch(self):
		if self.dlg.rbVECTOR.isChecked():
			#self.dlg.rbSTLASCII.setDisabled(True)
			#self.dlg.rbSTLbinary.setDisabled(True)
			#self.dlg.rbTXT.setChecked(True)
			self.dlg.lineEdit.clear()
			#self.dlg.spinBox.setDisabled(True)
		#if self.dlg.rbASC.isChecked():
			#self.dlg.spinBox.setDisabled(False)
			#self.dlg.rbSTLASCII.setDisabled(False)
			#self.dlg.rbSTLbinary.setDisabled(False)
    def outputSwitch(self):
        self.dlg.lineEdit.clear()
		
    def run(self):
        """Run method that performs all the real work"""
        layers = self.iface.legendInterface().layers()
        layer_list = []
        for layer in layers:
            layer_list.append(layer.name())
        self.dlg.comboBox.clear()
        self.dlg.comboBox.addItems(layer_list)
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            #Ciccia is here
            filename = str(self.dlg.lineEdit.text())
            selectedLayerIndex = self.dlg.comboBox.currentIndex()
            selectedLayer = layers[selectedLayerIndex]
			##=======CASE VECTOR LAYER=======##
            if self.dlg.rbVECTOR.isChecked():
				iter = selectedLayer.getFeatures()
				myList=[]
				##=======Reading feature 'ELEV' from vector contour layer=======##
				for feature in iter:
					entry=[]
					entry.append(feature['ELEV'])
					geom = feature.geometry()
					entry.append(geom.asPolyline())
					myList.append(entry)
					
				##=======Fitting data into variables=======##
				z=np.empty(0)
				xy=np.empty([0,2])
				n=self.dlg.spinBox.value()+1
				for i in range(0,len(myList)):
					index=0
					L=range(0,len(myList[i][1]),n)
					zz=np.zeros(len(L))
					xxyy=np.zeros((len(L),2))
					for j in L:
						zz[index]=myList[i][0]
						xxyy[index][0]=myList[i][1][j][0]
						xxyy[index][1]=myList[i][1][j][1]
						index+=1
					#xx=np.asarray(myList[i][1])[:,0]
					#yy=np.asarray(myList[i][1])[:,1]
					#xxyy=np.asarray(myList[i][1])
					#zz=np.empty(len(myList[i][1]))
					#zz.fill(myList[i][0])
					#x=np.hstack([x,xx])
					#y=np.hstack([y,yy])
					z=np.hstack([z,zz])
					xy=np.vstack([xy,xxyy])
				#Creating the scipy Spatial object
				#xyz=np.zeros((len(z),3))
				#xyz[:,0]=xy[:,0]
				#xyz[:,1]=xy[:,1]
				#xyz[:,2]=z
				tess = scipy.spatial.Delaunay(xy)
				xmin=tess.points[:, 0].min()
				ymin=tess.points[:, 1].min()
				#To avoid large numbers
				for i in range(0,len(tess.points)):
					tess.points[i, 0]=tess.points[ i, 0]-xmin
					tess.points[i, 1]=tess.points[i, 1]-ymin
				x=tess.points[:,0]
				y=tess.points[:,1]
				#Creating the matplotlib Triangulation object
				tri = tess.simplices # tess.vertices is deprecated
				triang = mtri.Triangulation(x, y, triangles=tri)
				##=======Eliminating excessively flat border triangles from the triangulation=======##
				filteringMask=mtri.TriAnalyzer(triang).get_flat_tri_mask(min_circle_ratio=0.01, rescale=True)
				triang.set_mask(filteringMask)
				triangFiltered=triang.get_masked_triangles()
				##triangFiltered is not a mtri object, but numpy.ndarray
				##=======Writing TXT file=======##
				if self.dlg.rbTXT.isChecked():
					with open(filename, 'w') as myFile:
						for i in range(0,len(x)):
							##??Print only useful points??##
							s="{0} {1:.2f} {2:.2f} {3:.2f}\n".format(i, x[i], y[i], z[i])
							myFile.write(s)
						for i in range(0,len(triangFiltered)):
							myFile.write(np.array_str(triangFiltered[i]))
							myFile.write("\n")
						
				##=======Writing STL file (Itasca)=======##
				if self.dlg.rbSTLASCII.isChecked() or self.dlg.rbSTLbinary.isChecked():
					data = np.zeros(len(triangFiltered), dtype=mesh.Mesh.dtype)
					for i in range(0,len(triangFiltered)):
						data['vectors'][i]=np.array([[x[triangFiltered[i][0]],y[triangFiltered[i][0]],z[triangFiltered[i][0]]],
													 [x[triangFiltered[i][1]],y[triangFiltered[i][1]],z[triangFiltered[i][1]]],
													 [x[triangFiltered[i][2]],y[triangFiltered[i][2]],z[triangFiltered[i][2]]]])
					your_mesh = mesh.Mesh(data, remove_empty_areas=False)
					your_mesh.normals
					##!!!!!mode=1 forces to ASCII mode=2 BINARY mode = 0 AUTOMATIC!!!!!##
					if self.dlg.rbSTLASCII.isChecked():
						userChooses=1
					elif self.dlg.rbSTLbinary.isChecked():
						userChooses=2
					your_mesh.save(filename,mode=userChooses)
				##=======Plotting with matplotlib=======##
				if self.dlg.checkBox.isChecked():
					fig = plt.figure()
					ax = fig.gca(projection='3d')
					ax.plot_trisurf(triang, z, cmap=cm.Spectral, linewidth=0.05)
					ax.view_init(elev=20, azim=45)
					#TG
					#elev=10 azim=120
					#ROASCHIA
					#elev=20, azim=45
					plt.show()
					

			##=======CASE ASC LAYER=======#
            elif self.dlg.rbASC.isChecked():
				##Reading all ASC file
				layerPath=selectedLayer.source()
				altitude = np.loadtxt(layerPath, skiprows=6)
				ncol=int(re.findall("[-+]?\d+[\.]?\d*", linecache.getline(layerPath,1))[0])
				nrow=int(re.findall("[-+]?\d+[\.]?\d*", linecache.getline(layerPath,2))[0])
				xllcorner=float(re.findall("[-+]?\d+[\.]?\d*", linecache.getline(layerPath,3))[0])
				yllcorner=float(re.findall("[-+]?\d+[\.]?\d*", linecache.getline(layerPath,4))[0])
				cellsize=float(re.findall("[-+]?\d+[\.]?\d*", linecache.getline(layerPath,5))[0])
				NODATA=float(re.findall("[-+]?\d+[\.]?\d*", linecache.getline(layerPath,6))[0])
				##Properly matrix reshape: otherwise EST and WEST would be swapped
				altitude=np.flipud(altitude)
				##=======Initializing variables and reshaping data read before=======##
				##Reading data every n cells
				##e.g. n=2 
				##  read skip read skip...
				##  skip skip skip skip...
				##  read skip read skip...
				##  ...
				##Remember, in the interface we are asking the user to specify the entries to skip,
				##so n=readValue+1
				n=self.dlg.spinBox.value()+1
				if n>ncol-1 or n>nrow-1:
					raise IOError, "Cant read the grid, n must be lower"
				numOfX=len(range(0,nrow,n))
				numOfY=len(range(0,ncol,n))
				##Creating arrays and reshaping needed read data into them
				x=np.zeros(numOfX*numOfY)
				y=np.zeros(numOfX*numOfY)
				altitudeResized=np.zeros(numOfX*numOfY)
				index=0
				for j in range(0,nrow,n):
					for i in range(0,ncol,n):
					   altitudeResized[index]=altitude[j][i] 
					   index+=1
				del altitude
				for j in range(0,numOfX):
					for i in range(0,numOfY):
						x[j*numOfY+i]=n*i*cellsize
				for j in range(0,numOfX):
					for i in range(0,numOfY):
						y[j*numOfY+i]=n*j*cellsize
						
				triangulationUp=np.zeros(((numOfY-1)*(numOfX-1),3),dtype=int)
				triangulationLo=np.zeros(((numOfY-1)*(numOfX-1),3),dtype=int)
				
				##=======Creating Triangulation for plot or txt file if specified=======##
				#4 points of the grid determine a square divided into 2 triangles:
				#	*---------------------------*
				#	|**                         |
				#	|  **                       |
				#	|    *                      |
				#	|     **                    |
				#	|       **                  |
				#	|         *         trUp    |
				#	|          **               |
				#	|            **             |
				#	|              *            |
				#	|               **          |
				#	|     trLo        *         |
				#	|                  **       |
				#	|                    **     |
				#	*---------------------------*
				if self.dlg.rbTXT.isChecked() or self.dlg.checkBox.isChecked():
					for j in range(0,numOfX-1):
							for i in range(0,numOfY-1):
								trUp=[j*numOfY+i,(j+1)*numOfY+i+1,j*numOfY+i+1]
								trLo=[j*numOfY+i,(j+1)*numOfY+i,(j+1)*numOfY+i+1]
								triangulationUp[i+(j*(numOfY-1))]=trUp
								triangulationLo[i+(j*(numOfY-1))]=trLo
				
				##=======Writing TXT file=======##
				if self.dlg.rbTXT.isChecked():
					with open(filename,'w') as myFile:
						##POINTS	
						for i in range(0,len(x)):
							s="{0} {1:.2f} {2:.2f} {3:.2f}\n".format(i, x[i], y[i], altitudeResized[i])
							myFile.write(s)
						##TRIANGLES
						for i in range(0,np.shape(triangulationUp)[0]):
							s="{0} {1} {2} \n{3} {4} {5}\n".format(triangulationUp[i][0],triangulationUp[i][1],triangulationUp[i][2],triangulationLo[i][0],triangulationLo[i][1],triangulationLo[i][2])
							myFile.write(s)

				##=======Writing STL file (Itasca)=======##
				if self.dlg.rbSTLASCII.isChecked() or self.dlg.rbSTLbinary.isChecked():
					data = np.zeros(2*(numOfX-1)*(numOfY-1), dtype=mesh.Mesh.dtype)
					index=0
					for j in range(0,numOfX-1):
						for i in range(0,numOfY-1):
							#Upper triangle of the cell (trUp)
							data['vectors'][index]=np.array([[x[j*numOfY+i],y[j*numOfY+i],altitudeResized[j*numOfY+i]],
															 [x[(j+1)*numOfY+i+1],y[(j+1)*numOfY+i+1],altitudeResized[(j+1)*numOfY+i+1]],
															 [x[j*numOfY+i+1],y[j*numOfY+i+1],altitudeResized[j*numOfY+i+1]]])
							#Lower triangle of the cell tr(Lo)
							data['vectors'][(numOfY-1)*(numOfX-1)+index]=np.array([[x[j*numOfY+i],y[j*numOfY+i],altitudeResized[j*numOfY+i]],
																				   [x[(j+1)*numOfY+i],y[(j+1)*numOfY+i],altitudeResized[(j+1)*numOfY+i]],
																				   [x[(j+1)*numOfY+i+1],y[(j+1)*numOfY+i+1],altitudeResized[(j+1)*numOfY+i+1]]])
							index+=1
													
					your_mesh = mesh.Mesh(data, remove_empty_areas=False)
					your_mesh.normals
					##!!!!!mode=1 forces to ASCII mode=2 BINARY mode = 0 AUTOMATIC!!!!!##
					if self.dlg.rbSTLASCII.isChecked():
						userChooses=1
					elif self.dlg.rbSTLbinary.isChecked():
						userChooses=2
					your_mesh.save(filename,mode=userChooses)

				##=======Plotting with matplotlib if specified=======##
				if self.dlg.checkBox.isChecked():
					tri=np.vstack((triangulationUp, triangulationLo))
					triang = mtri.Triangulation(x, y, triangles=tri)
					fig = plt.figure()
					ax = fig.gca(projection='3d')
					ax.plot_trisurf(triang, altitudeResized, cmap=cm.Spectral, linewidth=0.05)
					ax.view_init(elev=20, azim=45)
					#TG
					#elev=10 azim=115
					#ROASCHIA
					#elev=20, azim=45
					plt.show()