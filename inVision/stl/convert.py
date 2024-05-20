import numpy as np
import cupy as cp
import pandas as pd
import inVision as iV
import sys

"""
process : convert to polyhedral class
input : geometry -> stl.Geometry class
"""
def to_polyhedral(geometry):
	polygons = []

	for patch in geometry.patches:
		for vertex in patch.vertex:
			print(vertex.shape)
			sys.exit()
			polygons.append(iV.geometry.polygon([v for v in vertex]))

	polyhedral = iV.geometry.polyhedral(polygons)

	return polyhedral


def voxelize_cp(geo, dx, decomposed = (1,1,1), rec = True, show = False):
	##########Voxel総数を計算
	geo_size = geo.getSize()
	geo_range = (geo_size[i][1]-geo_size[i][0] for i in range(3))
	voxel_num = tuple(int(ran/dx) for ran in geo_range)

	##########コンテナあたりのボクセル数計算
	container = tuple(int(voxel_num[i]/decomposed[i]) for i in range(3)) #コンテナvoxel数
	x_num = [container[0] for i in range(decomposed[0]-1)] + [voxel_num[0]-(decomposed[0]-1)*container[0]] #X方向分割数
	y_num = [container[1] for i in range(decomposed[1]-1)] + [voxel_num[1]-(decomposed[1]-1)*container[1]] #Y方向分割数
	z_num = [container[2] for i in range(decomposed[2]-1)] + [voxel_num[2]-(decomposed[2]-1)*container[2]] #Z方向分割数

	##########コンテナ毎にボクセル化
	voxel = []
	for ix in range(decomposed[0]):
		x_original = geo_size[0][0] + ix*dx*container[0]
		voxel_x = []
		for iy in range(decomposed[1]):
			y_original = geo_size[1][0] + iy*dx*container[1]
			voxel_y = []
			for iz in range(decomposed[2]):
				z_original = geo_size[2][0] + iz*dx*container[2]

				x_pos = cp.stack([cp.arange(x_num[ix])*dx + (dx/2.) for i in range(y_num[iy])], axis = 1)
				x_pos = cp.stack([cp.copy(x_pos) for i in range(z_num[iz])], axis = -1) + x_original
				y_pos = cp.stack([cp.ones(x_num[ix])*i*dx + (dx/2.) for i in range(y_num[iy])], axis = 1)
				y_pos = cp.stack([cp.copy(y_pos) for i in range(z_num[iz])], axis = -1) + y_original
				z_pos = cp.stack([cp.ones((x_num[ix], y_num[iy]))*i*dx + (dx/2.) for i in range(z_num[iz])], axis = -1) + z_original

				voxel_pos = cp.stack((x_pos, y_pos, z_pos), axis = -1)
				voxel_pos = voxel_pos.reshape(x_num[ix], y_num[iy], z_num[iz], 1, 3)
				voxel_pos = cp.tile(voxel_pos, (1, 1, 1, 3, 1)) #(X, Y, Z, 3, 3)
				triangles = np.concatenate([patch.vertex for patch in geo.patches], axis = 0) #(N, 3, 3)

				voxel_z = cp.zeros((x_num[ix], y_num[iy], z_num[iz]))
				for n in range(len(triangles)):
					if show:
						print(str(ix)+":"+str(iy)+":"+str(iz)+"\t"+str(n+1)+"/"+str(len(triangles)))
					triangle = cp.asarray(triangles[n]).reshape((1, 1, 1, 3, 3))
					triangle = cp.tile(triangle, (x_num[ix], y_num[iy], z_num[iz], 1, 1)) #(X, Y, Z, 3, 3)
					triangle -= voxel_pos
					norm = cp.sqrt(cp.sum(triangle ** 2, axis = -1))
					arc1 = cp.linalg.det(triangle)
					dot_AB = cp.sum(triangle[:,:,:,0,:]*triangle[:,:,:,1,:], axis = -1)
					dot_BC = cp.sum(triangle[:,:,:,1,:]*triangle[:,:,:,2,:], axis = -1)
					dot_CA = cp.sum(triangle[:,:,:,2,:]*triangle[:,:,:,0,:], axis = -1)
					arc2 = (norm[:,:,:,0]*norm[:,:,:,1]*norm[:,:,:,2]) + norm[:,:,:,2]*dot_AB + norm[:,:,:,0]*dot_BC + norm[:,:,:,1]*dot_CA #(N, X, Y, Z)
					voxel_z += cp.arctan2(arc1, arc2)

				voxel_z = cp.asnumpy((voxel_z >= (2.*np.pi-1e-5)))
				voxel_y.append(cp.copy(voxel_z))
			voxel_x.append(voxel_y)
		voxel.append(voxel_x)

	###########コンテナを結合
	voxel = np.concatenate([np.concatenate([np.concatenate([voxel_z for voxel_z in voxel_y], axis = 2) for voxel_y in voxel_x], axis = 1) for voxel_x in voxel], axis = 0)

	###########出力処理
	if rec:
		return voxel
	else:
		return None