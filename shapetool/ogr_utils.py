


def copy_layer_attrs(source_lyr, target_lyr):
    '''
    copy attributes from source to target
    '''
    source_lyr_defn = source_lyr.GetLayerDefn()
    for i in range(0, source_lyr_defn.GetFieldCount()):
        field_def = source_lyr_defn.GetFieldDefn(i)
        target_lyr.CreateField(field_def)

    return target_lyr


def overwrite_dir(dir, overwritedir=True):
    '''
    check dir exists and if overwrite==True delete it.

    todo: definir exceptions
    '''
    dirpath = Path(dir)
    dir_exists_isdir = dirpath.exists() and dirpath.is_dir()
    if overwritedir and dir_exists_isdir:
        shutil.rmtree(dirpath)

    return (dir_exists_isdir and overwritedir)
