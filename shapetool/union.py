'''


In [1]: from shp_tool import union

In [2]: geom = union.union('/Volumes/kduNTfs128/geo_data/RG2017_regioesgeograficas2017_20180911', "UF = '15'")

In [3]: union.create_shp(geom, '/Volumes/kduNTfs128/geo_data/saida_3_union/')

In [4]: union.plot_multipoly(geom)

In [5]: geom
Out[5]: <osgeo.ogr.Geometry; proxy of <Swig Object of type 'OGRGeometryShadow *' at 0x11418cd80> >

'''

import os

from pathlib import Path
import shutil

from osgeo import ogr

from matplotlib import path as mpath
from matplotlib import patches as mpatches
from matplotlib import pyplot
from matplotlib.collections import PatchCollection


def union(shapefile, expression):
    """
    Args:
        expression (string): filter expression
        shapefile (file path): shapefile polygons or multipolygons
        outputdir (path): directory where the new shapefile will be created

    Return:
    return a new shapefile with a layer of 1 Multipolygon Feature
    """
    drvr = ogr.GetDriverByName('ESRI Shapefile')
    ds_pol = drvr.Open(shapefile, 0)
    layer = ds_pol.GetLayer()
    layer.SetAttributeFilter(expression)
    layer.GetFeatureCount()

    poly_union = ogr.Geometry(3)

    for feature in layer:
        geom = feature.GetGeometryRef()
        poly_union = poly_union.Union(geom)

    ds_pol.Destroy()

    return poly_union


def _overwrite_dir_(dir, overwritedir=True):
    '''

    todo: definir exceptions
    '''
    dirpath = Path(dir)
    dir_exists_isdir = dirpath.exists() and dirpath.is_dir()
    if overwritedir and dir_exists_isdir:
        shutil.rmtree(dirpath)

    return (dir_exists_isdir and overwritedir)


def create_shp(geom, dir='saida', layer_name='multpol', overwritedir=True):
    """gera um shapefile com a geometria recebida em `geom`.

    .. warning:: O diretório de saida é apagado se existir.

    Se a geometria (`param::geom`) não tiver o SPatialRef setado,
    o arquivo `.prj` shapefile não é criado.

    ver https://en.wikipedia.org/wiki/EPSG_Geodetic_Parameter_Dataset

    .. code::python

        # print <ogr.Geometry>  Spatial Ref System.
        print(geom.GetSpatialReference())
        GEOGCS["SIRGAS 2000",
        DATUM["Sistema_de_Referencia_Geocentrico_para_las_AmericaS_2000",
            ...
        AUTHORITY["EPSG","9122"]],
        AUTHORITY["EPSG","4674"]]

    TODO
    ----

    Se o `param::geom` não contém SpatialRefSYs ...

    .. code::python

        spatialRef.MorphToESRI()
        file = open('shapefiel.prj', 'w')
        file.write(spatialRef.ExportToWkt())
        file.close()

    Args:
        geom (osgeo.ogr.Geometry ):
        dir (str, optional): shapefile directory name
        layer_name (str, optional): layer name

    """
    # new shapefile
    _overwrite_dir_(dir, overwritedir)
    outDriver = ogr.GetDriverByName("ESRI Shapefile")
    outDataSource = outDriver.CreateDataSource(dir)

    # srs = osr.SpatialReference()
    # srs.ImportFromEPSG(geom.GetSpatialReference())
    srs = geom.GetSpatialReference()

    layer = outDataSource.CreateLayer(layer_name, srs, ogr.wkbMultiPolygon)

    field = ogr.FieldDefn("Name", ogr.OFTString)
    field.SetWidth(24)
    layer.CreateField(field)

    # Set attrs
    feature = ogr.Feature(layer.GetLayerDefn())
    feature.SetField("Name", 'union')

    # cria geom defacto
    feature.SetGeometry(geom)
    layer.CreateFeature(feature)

    # if not, layer and shape not create properly.
    feature.Destroy()
    outDataSource.Destroy()


def plot_multipoly(poly_union):
    '''
    recebe uma tipo MultiPolygon
    <osgeo.ogr.Geometry; proxy of <Swig Object of type 'OGRGeometryShadow *' at 0x10c4179f0> >
    e plota em  um gráfico.
    '''

    xmin, xmax, ymin, ymax = poly_union.GetEnvelope()
    geom = poly_union.GetGeometryRef(1)
    patches = []
    for i in range(poly_union.GetGeometryCount()):
        geom_ref = poly_union.GetGeometryRef(i)
        geom = geom_ref.GetGeometryRef(0)
        vertices = [(x, y) for x, y, z in geom.GetPoints()]

        # pc = geom.Centroid()
        # pyplot.text(pc.GetPoint()[1], pc.GetPoint()[0], 'area', size=1,ha="center", va="center")

        pol = mpatches.Polygon(vertices)
        patch = mpatches.PathPatch(pol)
        patches.append(pol)

    p = PatchCollection(patches, color='#6CA043', alpha=0.9, lw=0.5, ec='#1D388C', label='NECTO Systems')

    pyplot.ioff()
    pyplot.subplot(111)
    ax = pyplot.gca()
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.add_collection(p)
    ax.set_aspect(1.0)
    ax.autoscale()
    ax.set_title('Union Shape (Polygon)')
    pyplot.savefig('union.pdf', dpi=100)
    pyplot.show()

