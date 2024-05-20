import numpy as np
import os
import sys
import struct

from inVision.stl import convert

"""
/***************/
Geometry
/***************/
Field  : delimeter, patches
	delimeter -> str. mainly " ".
	patches -> list of Patch class

Method : 
<defined in this class> __init__, convert, write
Note   :
--- Introduction ---
This class is about stl file information. Geometry written by stl file formats are constructed by some patches.

"""
class Geometry:

	"""
	input : filename, scale, delimeter, filetype
		filename -> str. stl file name.
		scale -> "m" or "mm". scale adopted in stl file.
		delimeter -> str. mainly " ".
		filetype -> "binary" or "ascii".
	"""
	def __init__(self, filename, scale = "mm", delimiter = " ", filetype = "binary"):
		self.delimiter = delimiter
		self.patches = []

		##########read file
		if filetype == "ascii":
			#####read ascii file
			with open(filename, "r") as file:
				###remove delimeter char
				for f in file:
					f = f[:-1].split(self.delimiter)
					f = [s for s in f if s != ""]

					###read solid name and append new Patch class
					if "solid" in f:
						self.patches.append(Patch(scale))
						self.patches[-1].name = f[-1]

					###read facet information
					elif f[0] == "facet":
						x, y, z = float(f[2]), float(f[3]), float(f[4])
						if self.patches[-1].facet_normal is None:
							self.patches[-1].facet_normal = np.array([[x, y, z]])
						else:
							self.patches[-1].facet_normal = np.concatenate((self.patches[-1].facet_normal, np.array([[x, y, z]])), axis = 0)
					
					###read vertex information
					elif f[0] == "vertex":
						x, y, z = float(f[1]), float(f[2]), float(f[3])

						if self.patches[-1].vertex is None:
							self.patches[-1].vertex = np.array([[x, y, z]])
						else:
							self.patches[-1].vertex = np.concatenate((self.patches[-1].vertex, np.array([[x, y, z]])), axis = 0)
					
					###*loop and endsolid
					else:
						pass

				for p in self.patches:
					p.vertex = np.expand_dims(p.vertex, axis = 1).reshape((-1, 3, 3))

		else:
			#####read binary file
			filesize = os.path.getsize(filename) # file size

			with open(filename, "rb") as file:
				while filesize > 0:
					###read solid name and append new Patch
					self.patches.append(Patch(scale))
					self.patches[-1].name = file.read(80).decode()
					filesize -= 80

					tri_num = struct.unpack("I", file.read(4))[0] #triangle number
					filesize -= 4
					###read facet normal
					for i in range(tri_num):
						x = struct.unpack("f", file.read(4))[0]
						y = struct.unpack("f", file.read(4))[0]
						z = struct.unpack("f", file.read(4))[0]
						filesize -= 12
						if self.patches[-1].facet_normal is None:
							self.patches[-1].facet_normal = np.array([[x, y, z]])
						else:
							self.patches[-1].facet_normal = np.concatenate((self.patches[-1].facet_normal, np.array([[x, y, z]])), axis = 0)

						###read vertex
						tri1_x = struct.unpack("f", file.read(4))[0]
						tri1_y = struct.unpack("f", file.read(4))[0]
						tri1_z = struct.unpack("f", file.read(4))[0]

						tri1 = np.array([[tri1_x, tri1_y, tri1_z]])

						tri2_x = struct.unpack("f", file.read(4))[0]
						tri2_y = struct.unpack("f", file.read(4))[0]
						tri2_z = struct.unpack("f", file.read(4))[0]

						tri2 = np.array([[tri2_x, tri2_y, tri2_z]])

						tri3_x = struct.unpack("f", file.read(4))[0]
						tri3_y = struct.unpack("f", file.read(4))[0]
						tri3_z = struct.unpack("f", file.read(4))[0]

						filesize -= 36

						tri3 = np.array([[tri3_x, tri3_y, tri3_z]])

						tri = np.concatenate((tri1, tri2, tri3), axis = 0)
						tri = np.expand_dims(tri, axis = 0)

						if self.patches[-1].vertex is None:
							self.patches[-1].vertex = tri
						else:
							self.patches[-1].vertex = np.concatenate((self.patches[-1].vertex, tri), axis = 0)

						unknown = file.read(2)
						filesize -= 2

	"""
	process : convert scale
	input : scale -> "mm" or "m"
	"""
	def convert(self, scale):
		for p in self.patches:
			p.convert(scale)

	"""
	process : return xmin, xmax and so on.
	"""
	def getSize(self):
		points = np.concatenate([patch.vertex.reshape((-1, 3)) for patch in self.patches], axis = 0)
		x = points[:,0]
		y = points[:,1]
		z = points[:,2]

		return [(np.min(x), np.max(x)), (np.min(y), np.max(y)), (np.min(z), np.max(z))]


	"""
	process : check whether X is in the closed geometry or not.
	input : X -> np array
	"""
	def isIn(self, X):
		triangles = np.concatenate([patch.vertex for patch in self.patches], axis = 0) - X
		norm = np.sqrt(np.sum(triangles ** 2, axis = 2))

		winding_number = 0.

		for (A, B, C), (a, b, c) in zip(triangles, norm):
			winding_number += np.arctan2(np.linalg.det(np.array([A, B, C])), (a * b * c) + c * np.dot(A, B) + a * np.dot(B, C) + b * np.dot(C, A))
		
		return winding_number >= 2. * np.pi

	"""
	process : write a stl file
	input : filename, partial_patch, filetype
		filename  -> str. stl file name
		partial_patch -> list of str. list of patch classes which is defined in a stl file.
		filetype -> "binary" or "ascii" 
	"""
	def write(self, filename, partial_patch = None, filetype = "binary"):
		if partial_patch is None:
			partial_patch = [patch.name for patch in self.patches]

		if filetype == "ascii":
			with open(filename, "w") as file:
				for name in partial_patch:
					for patch in self.patches:
						if name == patch.name:
							patch.write(file, geo_flag = True, filetype = filetype)
							break
		else:
			with open(filename, "wb") as file:
				for name in partial_patch:
					for patch in self.patches:
						if name == patch.name:
							patch.write(file, geo_flag = True, filetype = filetype)
							break


"""
/***************/
Patch
/***************/
Field  : scale, name, facet_normal, vertex
	scale -> str. "m" or "mm"
	name -> str. patch name
	facet_normal -> np array. facet normal. shape is (N, 3)
	vertex -> np array. vertex. shape is (N, 3, 3)

Method : 
<defined in this class>
Note :
--- Introduction ---

"""
class Patch:

	def __init__(self, scale):
		self.scale = scale
		self.name = None
		self.facet_normal = None
		self.vertex = None

	def convert(self, scale):
		if self.scale == "mm":
			if scale == "m":
				self.vertex *= 0.001
		else:
			if scale == "mm":
				self.vertex *= 1000

	def numTriangle(self):
		return len(self.vertex)

	def copy(self, name):
		new_patch = Patch(self.scale)
		new_patch.name = name
		new_patch.facet_normal = self.facet_normal.copy()
		new_patch.vertex = self.vertex.copy()

		return new_patch

	def move(self, distance):
		self.vertex += distance

	def write(self, file, geo_flag = False, filetype = "binary"):

		if filetype == "ascii":
			if geo_flag:
				file.write("solid "+self.name+"\n")

				for fn, v in zip(self.facet_normal, self.vertex):
					file.write("facet normal "+str(fn[0])+" "+str(fn[1])+" "+str(fn[2])+"\n")
					file.write("outer loop\n")
					file.write("vertex "+str(v[0, 0])+" "+str(v[0, 1])+" "+str(v[0, 2])+"\n")
					file.write("vertex "+str(v[1, 0])+" "+str(v[1, 1])+" "+str(v[1, 2])+"\n")
					file.write("vertex "+str(v[2, 0])+" "+str(v[2, 1])+" "+str(v[2, 2])+"\n")
					file.write("endloop\n")
					file.write("endfacet\n")
				file.write("endsolid\n")
			else:
				with open(file, "w") as fileobject:
					fileobject.write("solid "+self.name+"\n")

					for fn, v in zip(self.facet_normal, self.vertex):
						fileobject.write("facet normal "+str(fn[0])+" "+str(fn[1])+" "+str(fn[2])+"\n")
						fileobject.write("outer loop\n")
						fileobject.write("vertex "+str(v[0, 0])+" "+str(v[0, 1])+" "+str(v[0, 2])+"\n")
						fileobject.write("vertex "+str(v[1, 0])+" "+str(v[1, 1])+" "+str(v[1, 2])+"\n")
						fileobject.write("vertex "+str(v[2, 0])+" "+str(v[2, 1])+" "+str(v[2, 2])+"\n")
						fileobject.write("endloop\n")
						fileobject.write("endfacet\n")
					fileobject.write("endsolid")

		else:
			if geo_flag:
				for s in self.name:
					file.write(struct.pack("c", s.encode()))
				file.write(struct.pack("x"*(80-len(self.name))))

				file.write(struct.pack("i", self.numTriangle()))

				for fn, v in zip(self.facet_normal, self.vertex):
					file.write(struct.pack("f", fn[0])); file.write(struct.pack("f", fn[1])); file.write(struct.pack("f", fn[2]))
					file.write(struct.pack("f", v[0, 0])); file.write(struct.pack("f", v[0, 1])); file.write(struct.pack("f", v[0, 2]))
					file.write(struct.pack("f", v[1, 0])); file.write(struct.pack("f", v[1, 1])); file.write(struct.pack("f", v[1, 2]))
					file.write(struct.pack("f", v[2, 0])); file.write(struct.pack("f", v[2, 1])); file.write(struct.pack("f", v[2, 2]))
					file.write(struct.pack("xx"))

			else:
				with open(file, "wb") as fileobject:
					for s in self.name:
						fileobject.write(struct.pack("c", s.encode()))
					fileobject.write(struct.pack("x"*(80-len(self.name))))

					fileobject.write(struct.pack("i", self.numTriangle()))

					for fn, v in zip(self.facet_normal, self.vertex):
						fileobject.write(struct.pack("f", fn[0])); fileobject.write(struct.pack("f", fn[1])); fileobject.write(struct.pack("f", fn[2]))
						fileobject.write(struct.pack("f", v[0, 0])); fileobject.write(struct.pack("f", v[0, 1])); fileobject.write(struct.pack("f", v[0, 2]))
						fileobject.write(struct.pack("f", v[1, 0])); fileobject.write(struct.pack("f", v[1, 1])); fileobject.write(struct.pack("f", v[1, 2]))
						fileobject.write(struct.pack("f", v[2, 0])); fileobject.write(struct.pack("f", v[2, 1])); fileobject.write(struct.pack("f", v[2, 2]))
						fileobject.write(struct.pack("xx"))