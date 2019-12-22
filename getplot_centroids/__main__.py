import os
import argparse

from get_centroids import get_centroids


def main():

    DESCRIPTION = 'gera um shapefile com centroids de polígonos'

    parser = argparse.ArgumentParser('Get Centroid', description=DESCRIPTION)

    parser.add_argument(
        '--file-shapefile', '-f', action='store', dest='shpfile_in', required=True,
        help='input shapefile')

    parser.add_argument(
        '--output', '-o', action='store', dest='shpfile_out', required=False,
        help='output shapefile')

    args = parser.parse_args()

    if not args.shpfile_out:
        filename, file_extension = os.path.splitext(args.shpfile_in)
        args.shpfile_out = f"{filename}_centroids.shp"

    get_centroids(args.shpfile_in, args.shpfile_out)


if __name__ == '__main__':
    main()