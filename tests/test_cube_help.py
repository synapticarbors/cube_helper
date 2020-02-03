# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of cube_helper and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

import iris
import cube_helper as ch
from glob import glob
import os

def test_concatenate():
    abs_path = os.path.dirname(os.path.abspath(__file__))
    glob_path = abs_path + '/test_data/realistic_3d_time' + '/*.nc'
    filepaths = glob(glob_path)
    test_load = [iris.load_cube(cube) for cube in filepaths]
    test_case_a = ch.concatenate(test_load)
    test_load = iris.cube.CubeList(test_load)
    test_case_b = ch.concatenate(test_load)
    assert isinstance(test_case_a, iris.cube.Cube)
    assert isinstance(test_case_b, iris.cube.Cube)


def test_load():
    abs_path = os.path.dirname(os.path.abspath(__file__))
    glob_path = abs_path + '/test_data/realistic_3d_time' + '/*.nc'
    filepaths = glob(glob_path)
    directory = abs_path + '/test_data/realistic_3d_time'
    test_case_a = ch.load(filepaths)
    assert isinstance(test_case_a, iris.cube.Cube)
    assert test_case_a.dim_coords[0].units.origin == "hours" \
                                                     " since 1970-01-01" \
                                                     " 00:00:00"
    assert test_case_a.dim_coords[0].units.calendar == "gregorian"
    test_case_b = ch.load(directory)
    assert test_case_b.dim_coords[0].units.origin == "hours" \
                                                     " since 1970-01-01" \
                                                     " 00:00:00"
    assert test_case_b.dim_coords[0].units.calendar == "gregorian"


def test_add_categorical():
    abs_path = os.path.dirname(os.path.abspath(__file__))
    glob_path = abs_path + '/test_data/realistic_3d_time' + '/*.nc'
    filepaths = glob(glob_path)
    test_case_a = ch.load(filepaths)
    test_case_b = [iris.load_cube(cube) for cube in filepaths]
    test_categoricals = ["season_year", "season_number",
                          "season_membership", "season",
                          "year", "month_number",
                          "month_fullname", "month",
                          "day_of_month", "day_of_year",
                          "weekday_number", "weekday_fullname",
                          "weekday", "hour"]
    for categorical in test_categoricals:
        test_case_a = ch.add_categorical(test_case_a, categorical)
        assert test_case_a.coord(categorical)
        test_case_a.remove_coord(categorical)

    for categorical in test_categoricals:
        for cube in test_case_b:
            cube = ch.add_categorical(cube, categorical)
            assert cube.coord(categorical)
            cube.remove_coord(categorical)
    test_case_a = ch.load(filepaths)
    test_case_a = ch.add_categorical(test_case_a,
                                     ["clim_season",
                                      "season_year"])
    assert test_case_a.coord("clim_season")
    assert test_case_a.coord("season_year")


def test_extract_categoircal():
    abs_path = os.path.dirname(os.path.abspath(__file__))
    glob_path = abs_path + '/test_data/realistic_3d_time' + '/*.nc'
    filepaths = glob(glob_path)
    test_constraint = iris.Constraint(grid_longitude=lambda cell: cell > 0,
                                      grid_latitude=lambda cell: cell > 0)
    test_cube_a = ch.load(filepaths)
    test_cube_b = ch.load(filepaths)
    test_cube_a = ch.extract_categorical(test_cube_a,
                                         ["clim_season", 'season_year'],
                                         test_constraint)
    assert isinstance(test_cube_a, iris.cube.Cube)
    iris.coord_categorisation.add_season(test_cube_b, 'time', name='clim_season')
    iris.coord_categorisation.add_season_year(test_cube_b, 'time', name='season_year')
    test_cube_b = test_cube_b.aggregated_by(["season_year",
                                             'clim_season'],
                                            iris.analysis.MEAN)
    test_cube_b = test_cube_b.extract(test_constraint)
    assert (test_cube_a == test_cube_b).all()