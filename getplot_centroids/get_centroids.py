from osgeo import ogr


def get_centroids(shapefile_in, shapefile_out):
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
    """

    driver = ogr.GetDriverByName("ESRI Shapefile")
    polygons_datasource = driver.Open(shapefile_in, 0)
    layer_polygons = polygons_datasource.GetLayer()

    # creates the output layer and shapefile
    outDriver = ogr.GetDriverByName("ESRI Shapefile")
    outDataSource = outDriver.CreateDataSource(shapefile_out)
    layer_centroid = outDataSource.CreateLayer("centroids", geom_type=ogr.wkbPoint)

    # get the meta from input shapefile
    # the centroid is created with the same original polygon attributes
    layer_polygons_defn = layer_polygons.GetLayerDefn()
    for i in range(0, layer_polygons_defn.GetFieldCount()):
        field_def = layer_polygons_defn.GetFieldDefn(i)
        layer_centroid.CreateField(field_def)

    layer_centroid_def = layer_centroid.GetLayerDefn()

    layer_polygons.GetFeatureCount()

    poligons_readed = layer_polygons.GetFeatureCount()

    # para cada poligono  gera o ceontroid, e copia a geom e attrs
    for polygon_number in range(0, poligons_readed):
        polygon = layer_polygons.GetFeature(polygon_number)
        geom = polygon.GetGeometryRef()
        centroid_feature = ogr.Feature(layer_centroid_def)  # definicao da nova feature (objeto geo)
        centroid = geom.Centroid()

        # copy polygons attributes
        for i in range(0, layer_centroid_def.GetFieldCount()):
            centroid_feature.SetField(layer_centroid_def.GetFieldDefn(i).GetNameRef(), polygon.GetField(i))
        #
        centroid_feature.SetGeometry(centroid)
        layer_centroid.CreateFeature(centroid_feature)

    # just counting
    points_created = layer_centroid.GetFeatureCount()
    outDataSource.Destroy()  # defacto save shapefile

    # retorna uma tupla ...  its bad.
    # talvez uma objeto no futuro.
    return (poligons_readed, points_created)