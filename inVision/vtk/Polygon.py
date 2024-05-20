import numpy as np

def writeVTK(filename, position, polygon_list):
	with open(filename, "w") as file:
		#####ジオメトリ構造の書き込み
		file.write("# vtk DataFile Version 2.0\nnumpyVTK\nASCII\n")
		file.write("DATASET POLYDATA\n")
		file.write("POINTS "+str(len(position))+" float\n")

		for pos in position: file.write(str(pos[0])+" "+str(pos[1])+" "+str(pos[2])+"\n")
		poly_num = sum([len(pl)+1 for pl in polygon_list])
		file.write("POLYGONS "+str(len(polygon_list))+" "+str(poly_num)+"\n")

		for pl in polygon_list:
			poly_str = str(len(pl))
			for p in pl: poly_str += (" "+str(p))
			file.write(poly_str+"\n")