# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeoDanmarkChecker
                                 A QGIS plugin
 This plugin provides methods to check GeoDanmark data
                             -------------------
        begin                : 2016-06-20
        copyright            : (C) 2016 by Septima
        email                : asger@septima.dk
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
    """Load GeoDanmarkChecker class from file GeoDanmarkChecker.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .geodanmark_checker import GeoDanmarkChecker
    return GeoDanmarkChecker(iface)
