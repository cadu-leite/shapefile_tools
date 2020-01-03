'''




In [1]: from shapetool import centroids

In [2]: centroids.get_shp_centroids('/Volumes/kduNTfs128/geo_data/jd_estoril', '/Volumes/kduNTfs128/geo_data/jd_estoril/centroids')

In [3]:


Macapa - centroid nao esta contio no polígono.

'''

from pathlib import Path

from osgeo import ogr
from osgeo import osr

from matplotlib import path as mpath
from matplotlib import patches as mpatches
from matplotlib import pyplot
from matplotlib.collections import PatchCollection


class OGRVectorLayerField:
    '''
    pt:  uma classe que representa os atributos da classe `GeomFieldDefn`

    en: A Class to represent the attributes of  GeomFieldefn

    OSGEO Module:
        Package osgeo :: Module ogr :: Class GeomFieldDefn



    '''
    def __init__(
        self, fieldtypename=None, justify=None, name=None, nameref=None, precision=None,
        subtype=None, type_code=None, typename=None, width=None, isnullable=None
        ):
        self.fieldtypename = fieldtypename
        self.justify = justify
        self.name = name
        self.nameref = nameref
        self.precision = precision
        self.subtype = subtype
        self.type_code = type_code
        self.typename = typename
        self.width = width
        self.isnullable = isnullable


def __create_shp__(shapefile_path, SRS_num, field_list, layer_name='newlayer'):
    '''
        'FieldTypeName': field_def.GetFieldTypeName(field_def.GetType()),
        'Justify': field_def.GetJustify(),
        'Name': field_def.GetName(),
        'NameRef': field_def.GetNameRef(),
        'Precision': field_def.GetPrecision(),
        'SubType': field_def.GetSubType(),
        'Type': field_def.GetType(),
        'TypeName': field_def.GetTypeName(),
        'Width': field_def.GetWidth(),
        'IsNullable': field_def.IsNullable()==1,

        OFTInteger
        OFTIntegerList
        OFTReal
        OFTRealList
        OFTString
        OFTStringList
        OFTWideString
        OFTWideStringList
        OFTBinary
        OFTDate
        OFTTime
        OFTDateTime
        OFTMaxType

    '''

    driver = ogr.GetDriverByName("ESRI Shapefile")
    data_source = driver.CreateDataSource(shapefile_path)

    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4674)
    layer = data_source.CreateLayer(layer_name, srs, ogr.wkbPoint)

    for field in field_list:
        fld = ogr.FieldDefn(field.name, field.type_code )
        fld.SetWidth(field.width)
        layer.CreateField(fld)

    data_source = None
    return shapefile_path


def get_shp_centroids(shp_in, shp_out, expression=None, overwrite=True):
    """
    [en] build a shapefile with points features
    based on centroids from a polygon shapefile

    [pt-BR] cria um shapefile com pontos baseados
    nos centroids vindos de um shapefile de poligonos.


    Args:
        shapefile_in (string): path of a valid polygons shapefile
        shapefile_out (string): path for output.

    Returns:
        returns the number of points features rceated

    todo:
    detach the shape creation ... only possible throught serialization of metadata.
    impossible to bring the `layer`  variable out of context... it causes a CPython crash. 
    """

    drvr = ogr.GetDriverByName('ESRI Shapefile')
    ds_pol = drvr.Open(shp_in, 0)
    layer = ds_pol.GetLayer()

    if expression:
        layer.SetAttributeFilter(expression)

    layer_def = layer.GetLayerDefn()
    #layer_copy = copy.copy(layer)
    layer_spt_ref = layer.GetSpatialRef()
    layer_spt_ref.AutoIdentifyEPSG()
    code = int(layer_spt_ref.GetAuthorityCode(None))

    field_def_list = []  # it will be a list of OGRVectorLayerField()
    layer_def = layer.GetLayerDefn()
    for i in range(0, layer_def.GetFieldCount()):
        field_def = layer_def.GetFieldDefn(i)
        field_def_list.append(
            OGRVectorLayerField(
                fieldtypename=field_def.GetFieldTypeName(field_def.GetType()),
                justify=field_def.GetJustify(), name=field_def.GetName(),
                nameref=field_def.GetNameRef(), precision=field_def.GetPrecision(),
                subtype=field_def.GetSubType(), type_code=field_def.GetType(),
                typename=field_def.GetTypeName(), width=field_def.GetWidth(),
                isnullable=field_def.IsNullable() == 1
            )
        )

    # create a new shapefile based on OGRVectorLayerField list
    cntr_path = __create_shp__(shp_out, code, field_def_list, 'centroids')

    # open the just created shapefile to fillup with new features
    # cEntrOid stuff
    cntr_ds_drvr = ogr.GetDriverByName('ESRI Shapefile')
    cntr_ds = cntr_ds_drvr.Open(cntr_path, 1)
    cntr_lyr = cntr_ds.GetLayer()
    cntr_lyr_def = cntr_lyr.GetLayerDefn()

    for feature in layer:
        # copia valore dos campos
        fref = feature.GetDefnRef()
        cntr_feature = ogr.Feature(cntr_lyr_def)
        for field_def in field_def_list:
            index = fref.GetFieldIndex(field_def.name)  # get index do campo
            cntr_feature.SetField(
                field_def.name, feature.GetField(index))  # nome e valor
        geom = feature.GetGeometryRef()
        point = geom.Centroid()
        cntr_feature.SetGeometry(point)
        cntr_lyr.CreateFeature(cntr_feature)

    cntr_ds = None
    ds_pol = None
