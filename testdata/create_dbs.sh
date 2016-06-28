#!/usr/bin/env bash

#ogrinfo /vsizip/607_Fredericia.zip/607_Fredericia_fot5_fra_prod.gml

#ogr2ogr -f SQLite -gt 65536 -lco SPATIAL_INDEX=YES fot5.sqlite /vsizip/607_Fredericia.zip/607_Fredericia_fot5_fra_prod.gml

# Vi får illegale geometrier med vsizip
unzip 607_Fredericia.zip

# Hvis GDAL < 2.0 så forstår den ikke srsDimension på top level geom element

echo 607_Fredericia_fot5_fra_prod
sed 's/posList>/posList srsDimension="3">/' 607_Fredericia_fot5_fra_prod.gml > tmp1.gml
ogr2ogr -f SQLite -gt 65536 -lco SPATIAL_INDEX=YES fot5.sqlite tmp1.gml

rm tmp1.gml
rm tmp1.gfs

echo Mapped_Fredericia_original_fot_5
sed 's/posList>/posList srsDimension="3">/' Mapped_Fredericia_original_fot_5.gml > tmp2.gml
ogr2ogr -f SQLite -gt 65536 -lco SPATIAL_INDEX=YES mapped_fot4.sqlite tmp2.gml

rm tmp2.gml
rm tmp2.gfs

rm 607_Fredericia_fot5_fra_prod.gml
rm Mapped_Fredericia_original_fot_5.gml

rm -rf ./__MACOSX

# xmllint --noout --schema ./schemas/gml/3.1.1/base/gml.xsd 461_Odense_Rev3_20160310/607_Fredericia_fot5_fra_prod.gml