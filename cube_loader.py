import os
import iris


class CubeLoader(object):


	def load_from_dir(self, dir, opt_filetype='.nc', opt_constraint=None):
		"""
		Loads a set of cubes from a given directory, single cubes are loaded and
		appended into an iterable as well as being loaded into a cubelist.

		:param string dir: directory to load data from
		:return iris.cube.CubleList: CubeList loaded form directory
		:return list loaded cubes: List of loaded cubes (needed to manipulate metadata etc)
		"""
		if opt_constraint == None:
			loaded_cubes = []
			for path in os.listdir(dir):
				full_path = os.path.join(dir, path)
				if os.path.isfile(full_path) and full_path.endswith(opt_filetype):
					loaded_cubes.append(iris.load_cube(full_path))
			return loaded_cubes
		else:
			loaded_cubes = []
			for path in os.listdir(dir):
				full_path = os.path.join(dir, path)
				if os.path.isfile(full_path) and full_path.endswith(opt_filetype):
					loaded_cubes.append(iris.load_cube(full_path, opt_constraint))
			return loaded_cubes

	def load_from_filelist(self, data_filelist, opt_filetype='.nc', opt_constraint =None):
		"""
		Loads a set of cubes from a given directory, single cubes are loaded and
		appended into an iterable as well as being loaded into a cubelist.

		:param list data_filelist: directory to load data from
		:return iris.cube.CubleList: CubeList loaded from file list
		:return list loaded_cubes: List of loaded cubes (needed to manipulate metadata etc)
		"""
		loaded_cubes = []
		for filename in data_filelist:
			if filename.endswith(opt_filetype):
				break
			else:
				print('\n\nThe selected filetype is not present in data_filelist\n\n')

		for filename in data_filelist:
			if opt_constraint == None:
				try:
					loaded_cubes.append(iris.load_cube(filename))
				except:
					pass
			else:
				try:
					loaded_cubes.append(iris.load_cube(filename, opt_constraint))
				except:
					pass

		return loaded_cubes
