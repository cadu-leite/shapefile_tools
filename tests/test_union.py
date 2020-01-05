from osgeo import ogr, osr
from shapetool import union

POLY_WKT = 'POLYGON ((-5107960.0745864 -2662481.79176906,-5107951.74137734 -2662261.79504978,-5107910.07533202 -2662108.464003,-5107561.74719315 -2662070.13124131,-5107583.41353672 -2662835.11983337,-5107960.0745864 -2662481.79176906))'
POLY_GEOM = ogr.CreateGeometryFromWkt(POLY_WKT)


def create_create_test_shape():
    '''
    '''
    # The original polygon has used WGS84 - "EPSG","3857"
    geom = ogr.CreateGeometryFromWkt(POLY_WKT)
    # essa ordem é importante !!!!
    minX, maxX, minY, maxY = geom.GetEnvelope()

    # coord0----coord1----coord2
    # |           |           |
    # coord3----coord4----coord5
    # |           |           |
    # coord6----coord7----coord8
    # Create 4 square polygons
    coord0 = minX, maxY
    coord1 = minX + (maxX - minX) / 2, maxY
    coord2 = maxX, maxY
    coord3 = minX, minY + (maxY - minY) / 2
    coord4 = minX + (maxX - minX) / 2, minY + (maxY - minY) / 2
    coord5 = maxX, minY + (maxY - minY) / 2
    coord6 = minX, minY
    coord7 = minX + (maxX - minX) / 2, minY
    coord8 = maxX, minY

    # poly top left
    topl = ogr.Geometry(ogr.wkbLinearRing)
    topl.AddPoint_2D(*coord0)
    topl.AddPoint_2D(*coord1)
    topl.AddPoint_2D(*coord4)
    topl.AddPoint_2D(*coord3)
    topl.AddPoint_2D(*coord0)
    poly_topleft = ogr.Geometry(ogr.wkbPolygon)
    poly_topleft.AddGeometry(topl)

    # poly top right
    topr = ogr.Geometry(ogr.wkbLinearRing)
    topr.AddPoint_2D(*coord1)
    topr.AddPoint_2D(*coord2)
    topr.AddPoint_2D(*coord5)
    topr.AddPoint_2D(*coord4)
    topr.AddPoint_2D(*coord1)
    poly_topright = ogr.Geometry(ogr.wkbPolygon)
    poly_topright.AddGeometry(topr)

    # poly bottom left
    botl = ogr.Geometry(ogr.wkbLinearRing)
    botl.AddPoint_2D(*coord3)
    botl.AddPoint_2D(*coord4)
    botl.AddPoint_2D(*coord7)
    botl.AddPoint_2D(*coord6)
    botl.AddPoint_2D(*coord3)
    poly_bottomleft = ogr.Geometry(ogr.wkbPolygon)
    poly_bottomleft.AddGeometry(botl)

    # poly bottom right
    botr = ogr.Geometry(ogr.wkbLinearRing)
    botr.AddPoint_2D(*coord4)
    botr.AddPoint_2D(*coord5)
    botr.AddPoint_2D(*coord8)
    botr.AddPoint_2D(*coord7)
    botr.AddPoint_2D(*coord4)
    poly_bottomright = ogr.Geometry(ogr.wkbPolygon)
    poly_bottomright.AddGeometry(botr)

    # may the 4 be with us !...
    qrtr_tl = poly_topleft.Intersection(geom)
    qrtr_tr = poly_topright.Intersection(geom)
    qrtr_bl = poly_bottomleft.Intersection(geom)
    qrtr_br = poly_bottomright.Intersection(geom)

    drv = ogr.GetDriverByName('ESRI Shapefile')
    dst_ds = drv.CreateDataSource('teste_union.shp')
    proj = osr.SpatialReference()
    proj.SetWellKnownGeogCS("EPSG:3857")
    dst_layer = dst_ds.CreateLayer('unions', proj, ogr.wkbPolygon)

    for quarter in (qrtr_tl, qrtr_tr, qrtr_bl, qrtr_br):

        feature = ogr.Feature(dst_layer.GetLayerDefn())
        g = ogr.ForceToMultiPolygon(quarter)
        gr = g.GetGeometryRef(0)
        feature.SetGeometry(gr)
        dst_layer.CreateFeature(feature)
        feature = None

    dst_ds = None
    dst_ds = None


def teste_union_has_1_polygon():
    geom = union.union('teste_union.shp', '')
    assert geom.GetGeometryCount() == 1


def teste_union_has_same_are():
    ''' ... or almost :(
    '''
    geom = union.union('teste_union.shp', '')
    assert POLY_GEOM.GetArea() // geom.GetArea() == 1
