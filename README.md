# SurfaceTriangulation for QGIS


/***************************************************************************
 *                                                                         *
 *   This program is free software. It has been developed as part of my    *
 *   Master's Degree Thesis @ Politecnico di Torino, being supervised by   *
 *   Prof. M. Barla and PhD. F. Antolini and hosted/supported by CDM       *
 *   Dolmen. One can redistribute it and/or modify it under the terms of   *
 *   the GNU General Public License as published by the Free Software      *
 *   Foundation; either version 2 of the License, or any later version.    *
 *                                                                         *
 ***************************************************************************/
 
 QGIS Plugin useful for the triangulation of a surface from both a dtm raster 
 layer (.ASC is mandatory) or contour vector layer. 
 If the input is a raster file, the triangulation is built on the grid points, 
 If the input is a vector file, the triangulation is computed using a Delaunay 
 algorithm.
 Three output files are possible:  .txt .stl (binary) .stl (ASCII).
 
 HOW TO INSTALL
 This plugin relies on the numpy-stl package which must be installed by the user.
 
 LINUX (Ubuntu)
 
 1) Install the numpy-stl package; from terminal:
 pip install numpy-stl
 2) Copy the folder SurfaceTriangulation to your QGIS plugins folder (e.g. 
 /usr/share/qgis/python/plugins)
 3) From QGIS, under the "Plugins" menu, install "Surface Triangulation"
 
 WINDOWS
 
 1) Download the file ez_setup.py from http://peak.telecommunity.com/dist/ez_setup.py
 2) Open an OSGeo4W Shell (under Start=>Qgis=>OSGeo4W Shell) with administration 
 priviledges (Right click=>Run as administrator or 
 Right click=>Open path=>OSGeo4W Shell=>Run as administrator)
 3) From this shell set your path to the downloaded ez_setup.py file 
 (e.g. cd C:\Users\username\Downloads) and run it with the command:
 python ez_setup.py
 4) Install pip with the command:
 easy_install pip
 5) Install the numpy-stl package with the command:
 pip install numpy-stl
	If you get an error in numpy compilation, just ignore it.
6) Copy the folder SurfaceTriangulation to your QGIS plugins folder (e.g.
C:\Users\username\.qgis2\python\plugins)
7) From QGIS, under the "Plugins" menu, install "Surface Triangulation"