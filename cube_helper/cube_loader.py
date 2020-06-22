# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of cube_helper and is released under the
# BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

import os
import iris
import glob
from iris.exceptions import MergeError, ConstraintMismatchError
from six import string_types
from datetime import datetime

def _fix_partial_datetime(constraint):
    if isinstance(constraint._coord_values['time'], iris.time.PartialDateTime):
        part_datetime = constraint._coord_values['time']
        if part_datetime.year:
            cell_lambda = lambda cell: \
                cell.point.year == part_datetime.year
        elif part_datetime.month:
            cell_lambda = lambda cell: \
                cell.point.month == part_datetime.month
        elif part_datetime.day:
            cell_lambda = lambda cell: \
                cell.point.day == part_datetime.day
        elif part_datetime.hour:
            cell_lambda = lambda cell: \
                cell.point.hour == part_datetime.hour
        elif part_datetime.minute:
            cell_lambda = lambda cell: \
                cell.point.minute == part_datetime.minute
        elif part_datetime.second:
            cell_lambda = lambda cell: \
                cell.point.second == part_datetime.second
        elif part_datetime.microsecond:
            cell_lambda = lambda cell: \
                cell.point.microsecond == part_datetime.microsecond
        else:
            raise OSError("Constraint could not be rectified")
        new_constraint = iris.Constraint(time = cell_lambda)
        return new_constraint
    else:
        return constraint



def _constraint_compatible(cube, constraint):
    try:
        constraint.extract(cube)
        return True
    except Exception:
        return False


def _parse_directory(directory):
    """
    Parses the string representing the directory, makes sure a '/'
    backspace is present at the start and end of the directory string
    so glob can work properly.

    Args:
         directory: the directory string to parse.

    Returns:
        a string representing the directory, having been parsed if
        cd docneeded.
    """
    if not directory.endswith('/'):
        directory = directory + '/'

    if not directory.startswith('/'):
        if os.path.isdir(directory):
            return directory

        else:
            directory = '/' + directory
            return directory
    else:
        return directory


def _sort_by_date(time_coord):
    """
    Private sorting function used by _file
    _sort_by_earliest_date() and sort_by_earl
    iest_date().

    Args:
        time_coord: Cube time coordinate for each cube
        to be sorted by.

    Returns:
        time_origin: The time origin to sort cubes
        by, as a specific start date e.g 1850.
    """
    time_origin = time_coord.units.num2date(0)
    if not isinstance(time_origin, datetime):
        if time_origin.datetime_compatible:
            time_origin = time_origin._to_real_datetime()
        else:
            time_origin = datetime(time_origin.year,
                                   time_origin.month,
                                   time_origin.day)
    return time_origin


def file_sort_by_earliest_date(cube_filename):
    """
    Sorts file names by date from earliest to latest.

    Args:
        cube_filename: list of files in string format to sort,
        to be used with CubeList sort method when cube_load is called.

    Returns:
        datetime object of selected Cubes start time.
    """
    raw_cubes = iris.load_raw(cube_filename)
    if isinstance(raw_cubes, iris.cube.CubeList):
        for cube in raw_cubes:
            if isinstance(cube.standard_name, string_types):
                for time_coord in cube.coords():
                    if time_coord.units.is_time_reference():
                        time_origin = _sort_by_date(time_coord)
                        return time_origin
    else:
        for time_coord in iris.load_cube(cube_filename).coords():
            if time_coord.units.is_time_reference():
                time_origin = _sort_by_date(time_coord)
                return time_origin


def sort_by_earliest_date(cube):
    """
    Sorts Cubes by date from earliest to latest.

    Args:
        cube: CubeList or list to sort, to be used with CubeList
        sort method when cube_load is called.

    Returns:
        datetime object of selected Cubes start time.
    """

    for time_coord in cube.coords():
        if time_coord.units.is_time_reference():
            time_origin = _sort_by_date(time_coord)
            return time_origin


def load_from_dir(directory, filetype, constraint=None):
    """
    Loads a set of cubes from a given directory, single cubes are loaded
    and returned as a CubeList.

    Args:
        directory: a chosen directory
        to operate on. directory MUST start and end with forward
        slashes.

        filetype (optional): a string specifying the expected type
        Of files found in the dataset.

        constraints (optional): a string specifying any constraints
        You wish to load the dataset with.

    Returns:
        iris.cube.CubeList(loaded_cubes), a CubeList of the loaded
        Cubes.
    """
    if constraint is None:
        loaded_cubes = []
        cube_files = []
        directory = _parse_directory(directory)
        for path in glob.glob(directory + '*' + filetype):
            try:
                loaded_cubes.append(iris.load_cube(path))
                cube_files.append(path)
            except (MergeError, ConstraintMismatchError):
                for cube in iris.load_raw(path):
                    if isinstance(cube.standard_name, str):
                        loaded_cubes.append(cube)
                        cube_files.append(path)
        loaded_cubes.sort(key=sort_by_earliest_date)
        cube_files.sort(key=file_sort_by_earliest_date)
        return loaded_cubes, cube_files
    else:
        loaded_cubes = []
        cube_files = []
        directory = _parse_directory(directory)
        cube_paths = glob.glob(directory + '*' + filetype)
        if _constraint_compatible(constraint, iris.load_cube(cube_paths[0])):
            pass
            # do something with the constraints
        for path in cube_paths:
            try:
                loaded_cubes.append(iris.load_cube(path, constraint))
                cube_files.append(path)
            except (MergeError, ConstraintMismatchError):
                for cube in iris.load_raw(path, constraint):
                    if isinstance(cube.standard_name, str):
                        loaded_cubes.append(cube)
                        cube_files.append(path)
        loaded_cubes.sort(key=sort_by_earliest_date)
        cube_files.sort(key=file_sort_by_earliest_date)
        return loaded_cubes, cube_files


def load_from_filelist(data_filelist, filetype, constraint=None):
    """
    Loads the specified files. Individual files are
    returned in a
    CubeList.

    Args:
        data_filelist: a chosen list of filenames to operate on.

        filetype (optional): a string specifying the expected type
        Of files found in the dataset

        constraints (optional): a string, iterable of strings or an
        iris.Constraint specifying any constraints you wish to load
        the dataset with.

    Returns:
        iris.cube.CubeList(loaded_cubes), a CubeList of the loaded
        Cubes.
    """
    loaded_cubes = []
    cube_files = []
    for filename in data_filelist:
        if not filename.endswith(filetype):
            data_filelist.remove(filename)

    for filename in data_filelist:
        if constraint is None:
            try:
                loaded_cubes.append(iris.load_cube(filename))
                cube_files.append(filename)
            except (MergeError, ConstraintMismatchError):
                for cube in iris.load_raw(filename):
                    if isinstance(cube.standard_name, str):
                        loaded_cubes.append(cube)
                        cube_files.append(filename)

        else:
            try:
                loaded_cubes.append(iris.load_cube(filename, constraint))
                cube_files.append(filename)
            except (MergeError, ConstraintMismatchError):
                for cube in iris.load_raw(filename, constraint):
                    if isinstance(cube.standard_name, str):
                        loaded_cubes.append(iris.load_raw(filename,
                                                          constraint))
                        cube_files.append(filename)
    loaded_cubes.sort(key=sort_by_earliest_date)
    cube_files.sort(key=file_sort_by_earliest_date)
    return loaded_cubes, cube_files
