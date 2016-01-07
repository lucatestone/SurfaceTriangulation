# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SurafaceTriangulation
                                 A QGIS plugin
 Plugin that creates a Delaunay triangulation from a dtm raster
                             -------------------
        begin                : 2015-12-14
        copyright            : (C) 2015 by Luca Testone
        email                : lucatestone@yahoo.it
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load SurafaceTriangulation class from file SurafaceTriangulation.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .surface_triangulation import SurafaceTriangulation
    return SurafaceTriangulation(iface)
