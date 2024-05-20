import numpy as np

"""
process : ポイントクラウドの絵を作成
input : position, scalars,scalarname
	position -> <np array> 粒子位置。(N, 3)なshape
	scalars -> <list of np array> np arrayは(N, )なshape
"""
def writeVTK(filename, position, scalars = [], scalarname = []):
	N = len(position)
	if position.shape[1] == 2:
		position = np.concatenate((position, np.ones((N, 1))), axis = 1)

	with open(filename, "w") as file:
		file.write("# vtk DataFile Version 2.0\nnumpyVTK\nASCII\n")
		file.write("DATASET UNSTRUCTURED_GRID\n\n")
		file.write("POINTS "+str(N)+" float\n")
		for pos in position:
			file.write(str(pos[0])+" "+str(pos[1])+" "+str(pos[2])+"\n")

		file.write("\n")
		file.write("CELL_TYPES "+str(N)+"\n")
		file.write("1\n"*N)

		file.write("POINT_DATA "+str(N)+"\n")

		for scalar, name in zip(scalars, scalarname):
			scalar *= (abs(scalar) > 1e-20)

			file.write("SCALARS "+name+" float\n")
			file.write("LOOKUP_TABLE default\n")
			for s in scalar:
				file.write(str(s)+"\n")