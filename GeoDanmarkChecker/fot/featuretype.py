# -*- coding: utf-8 -*-
"""
Routines for quality control of GeoDanmark map data
Copyright (C) 2016
Developed by Septima.dk for the Danish Agency for Data Supply and Efficiency

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

class FeatureType(object):

    def __init__(self, name, tablename, displayname):
        self.name = name
        self.tablename = tablename
        self.displayname = displayname
        self.id_attribute = 'FOT_ID'

    def __repr__(self):
        return self.name


featuretypes = []
featuretypes_others = []

BRUGSGRAENSE = FeatureType('BRUGSGRAENSE', 'brugsgraense', '')
featuretypes_others.append(BRUGSGRAENSE)

HEGN = FeatureType('HEGN', 'hegn', '')
featuretypes_others.append(HEGN)

BYGNING = FeatureType('BYGNING', 'bygning', '')
featuretypes.append(BYGNING)

BROENDDAEKSEL = FeatureType('BROENDDAEKSEL', 'broenddaeksel', '')
featuretypes_others.append(BROENDDAEKSEL)

SKOV = FeatureType('SKOV', 'skov', '')
featuretypes_others.append(SKOV)

SKRAENT = FeatureType('SKRAENT', 'skraent', '')
featuretypes_others.append(SKRAENT)

TRAE = FeatureType('TRAE', 'trae', '')
featuretypes_others.append(TRAE)

TRAFIKHEGN = FeatureType('TRAFIKHEGN', 'trafikhegn', '')
featuretypes_others.append(TRAFIKHEGN)

TEKNISK_AREAL = FeatureType('TEKNISK_AREAL', 'teknisk_areal', '')
featuretypes_others.append(TEKNISK_AREAL)

VAADOMRAADE = FeatureType('VAADOMRAADE', 'vaadomraade', '')
featuretypes_others.append(VAADOMRAADE)

TELEMAST = FeatureType('TELEMAST', 'telemast', '')
featuretypes_others.append(TELEMAST)

NEDLOEBSRIST = FeatureType('NEDLOEBSRIST', 'nedloebsrist', '')
featuretypes_others.append(NEDLOEBSRIST)

MAST = FeatureType('MAST', 'mast', '')
featuretypes_others.append(MAST)

PARKERING = FeatureType('PARKERING', 'parkering', '')
featuretypes_others.append(PARKERING)

BYGVAERK = FeatureType('BYGVAERK', 'bygvaerk', '')
featuretypes_others.append(BYGVAERK)

TRAEGRUPPE = FeatureType('TRAEGRUPPE', 'traegruppe', '')
featuretypes_others.append(TRAEGRUPPE)

CHIKANE = FeatureType('CHIKANE', 'chikane', '')
featuretypes_others.append(CHIKANE)

BEGRAVELSESOMRAADE = FeatureType('BEGRAVELSESOMRAADE', 'begravelsesomraade', '')
featuretypes_others.append(BEGRAVELSESOMRAADE)

HOEFDE = FeatureType('HOEFDE', 'hoefde', '')
featuretypes_others.append(HOEFDE)

KRAT_BEVOKSNING = FeatureType('KRAT_BEVOKSNING', 'krat_bevoksning', '')
featuretypes_others.append(KRAT_BEVOKSNING)

STATUE_STEN = FeatureType('STATUE_STEN', 'statue_sten', '')
featuretypes_others.append(STATUE_STEN)

SKORSTEN = FeatureType('SKORSTEN', 'skorsten', '')
featuretypes_others.append(SKORSTEN)

ANLAEG_DIVERSE = FeatureType('ANLAEG_DIVERSE', 'anlaeg_diverse', '')
featuretypes_others.append(ANLAEG_DIVERSE)

VINDMOELLE = FeatureType('VINDMOELLE', 'vindmoelle', '')
featuretypes.append(VINDMOELLE)

HEDE = FeatureType('HEDE', 'hede', '')
featuretypes_others.append(HEDE)

RAASTOFOMRAADE = FeatureType('RAASTOFOMRAADE', 'raastofomraade', '')
featuretypes_others.append(RAASTOFOMRAADE)

BASSIN = FeatureType('BASSIN', 'bassin', '')
featuretypes_others.append(BASSIN)

STARTBANE = FeatureType('STARTBANE', 'startbane', '')
featuretypes_others.append(STARTBANE)

GARTNERI = FeatureType('GARTNERI', 'gartneri', '')
featuretypes_others.append(GARTNERI)

SAND_KLIT = FeatureType('SAND_KLIT', 'sand_klit', '')
featuretypes_others.append(SAND_KLIT)

LAV_BEBYGGELSE = FeatureType('LAV_BEBYGGELSE', 'lav_bebyggelse', '')
featuretypes_others.append(LAV_BEBYGGELSE)

ERHVERV = FeatureType('ERHVERV', 'erhverv', '')
featuretypes_others.append(ERHVERV)

HOEJ_BEBYGGELSE = FeatureType('HOEJ_BEBYGGELSE', 'hoej_bebyggelse', '')
featuretypes_others.append(HOEJ_BEBYGGELSE)

BYKERNE = FeatureType('BYKERNE', 'bykerne', '')
featuretypes_others.append(BYKERNE)

OMRAADEPOLYGON = FeatureType('OMRAADEPOLYGON', 'omraadepolygon', '')
featuretypes_others.append(OMRAADEPOLYGON)

VANDLOEBSMIDTE_BRUDT = FeatureType('VANDLOEBSMIDTE_BRUDT', 'vandloebsmidte_brudt', '')
featuretypes.append(VANDLOEBSMIDTE_BRUDT)

VANDLOEBSKANT = FeatureType('VANDLOEBSKANT', 'vandloebskant', '')
featuretypes.append(VANDLOEBSKANT)

SOE = FeatureType('SOE', 'soe', '')
featuretypes_others.append(SOE)

HAVN = FeatureType('HAVN', 'havn', '')
featuretypes_others.append(HAVN)

AFVANDINGSGROEFT = FeatureType('AFVANDINGSGROEFT', 'afvandingsgroeft', '')
featuretypes_others.append(AFVANDINGSGROEFT)

BADE_BAADEBRO = FeatureType('BADE_BAADEBRO', 'bade_baadebro', '')
featuretypes_others.append(BADE_BAADEBRO)

KYST = FeatureType('KYST', 'kyst', '')
featuretypes_others.append(KYST)

DIGE = FeatureType('DIGE', 'dige', '')
featuretypes_others.append(DIGE)

VEJKANT = FeatureType('VEJKANT', 'vejkant', '')
featuretypes_others.append(VEJKANT)

HOEJSPAENDINGSLEDNING = FeatureType('HOEJSPAENDINGSLEDNING', 'hoejspaendingsledning', '')
featuretypes_others.append(HOEJSPAENDINGSLEDNING)

JERNBANE_BRUDT = FeatureType('JERNBANE_BRUDT', 'jernbane_brudt', '')
featuretypes.append(JERNBANE_BRUDT)

KOMMUNEGRAENSE = FeatureType('KOMMUNEGRAENSE', 'kommunegraense', '')
featuretypes_others.append(KOMMUNEGRAENSE)

HELLE = FeatureType('HELLE', 'helle', '')
featuretypes_others.append(HELLE)

VEJMIDTE_BRUDT = FeatureType('VEJMIDTE_BRUDT', 'vejmidte_brudt', '')
featuretypes.append(VEJMIDTE_BRUDT)

