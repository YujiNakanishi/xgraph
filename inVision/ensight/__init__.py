import numpy as np
import struct
import sys

import inVision as iV
from inVision.ensight import geometry as geo
from inVision.ensight.scalar import ScalarPerElement,ScalarPerNode
from inVision.ensight.vector import VectorPerElement

"""
/***************/
CASE
/***************/
Field  : Scale, Parts
	Scale -> str. scale used in geometry file
	parts -> list of PART class

Method : 
<defined in this class> __init__, readGeometry, writeGeometry
Note   :
--- Introduction ---
This is for case class about ensight gold file.

"""
class CASE:

	def __init__(self, Scale = "m", Parts = []):
		self.Scale = Scale
		self.Parts = Parts

	def readGeometry(self, GeometryFile):
		geo.readGeometry(self, GeometryFile)

	def writeGeometry(self, GeometryFile, parts_name = None):
		geo.writeGeometry(self, GeometryFile, parts_name)

	def callParts(self, name):
		for part in self.Parts:
			if part.name == name:
				return part

	def getCentroid(self, parts_name = None):
		if parts_name is None:
			parts_name = [part.name for part in self.Parts]

		field = []

		for pn in parts_name:
			part = self.callParts(pn) #PART class
			centroid = part.CentroidList() #list of np array which shape is (3, )

			field.append({"name" : pn, "value" : centroid})

		return VectorPerElement(self, field = field)

	def getVolume(self, parts_name = None):
		if parts_name is None:
			parts_name = [part.name for part in self.Parts]

		field = []

		for pn in parts_name:
			part = self.callParts(pn) #PART class
			volume = part.VolumeList()
			field.append({"name" : pn, "value" : volume})
		
		return ScalarPerElement(self, field = field)

"""
/***************/
PART
/***************/
Field  : name, X, Y, Z, Elements
	name -> str. parts name
	X, Y, Z -> list of node axis.
	Elements -> list of dictionary
		name -> element name
		ne -> num of element
		info -> depends of element name. written in ensight.geometry.getStructure 

Method : 
<defined in this class> __init__, append
Note   :
--- Introduction ---
This is for parts class about ensight gold file.
"""
class PART:

	def __init__(self):
		self.name = None
		self.X = None
		self.Y = None
		self.Z = None
		self.Elements = []

	def append(self, name, ne, info):
		self.Elements.append({"name" : name, "ne" : ne, "info" : info})

	def callNode(self, i):
		return np.array([self.X[i-1], self.Y[i-1], self.Z[i-1]])

	def CentroidList(self):
		c_list = []
		for i in range(len(self.Elements)):
			for j in range(len(self.Elements[i]["info"])):
				c_list.append(self.getCentroid(i, j))
		c_list = np.stack(c_list, axis = 0)
		return c_list

	def VolumeList(self):
		v_list = []
		for i in range(len(self.Elements)):
			for j in range(len(self.Elements[i]["info"])):
				v_list.append(self.getVolume(i, j))

		return np.array(v_list)

	def getCentroid(self, i, j):
		info = self.Elements[i]["info"][j]

		if self.Elements[i]["name"] == "hexa8":
			centroid = np.zeros(3)
			for idx in info:
				centroid += self.callNode(idx)/8.

		elif self.Elements[i]["name"] == "penta6":
			nodes = [self.callNode(i) for i in info]
			polygon1 = iV.geometry.polygon([nodes[0], nodes[2], nodes[1]])
			polygon2 = iV.geometry.polygon([nodes[3], nodes[4], nodes[5]])
			polygon3 = iV.geometry.polygon([nodes[1], nodes[4], nodes[3], nodes[0]])
			polygon4 = iV.geometry.polygon([nodes[2], nodes[5], nodes[4], nodes[1]])
			polygon5 = iV.geometry.polygon([nodes[0], nodes[3], nodes[5], nodes[2]])

			penta6 = iV.geometry.polyhedral([polygon1, polygon2, polygon3, polygon4, polygon5])
			centroid = penta6.getCentroid()

		elif self.Elements[i]["name"] == "nfaced":
			polygons = []
			for ainf in info:
				plg = iV.geometry.polygon([self.callNode(ai) for ai in ainf])
				polygons.append(plg)

			nfaced = iV.geometry.polyhedral(polygons)
			centroid = nfaced.getCentroid()

		else:
			print("getCentroid")
			print(self.Elements[i]["name"])
			sys.exit()

		return centroid

	def getVolume(self, i, j):
		info = self.Elements[i]["info"][j]

		if self.Elements[i]["name"] == "hexa8":
			v = np.abs(self.callNode(info[6])-self.callNode(info[0]))
			return v[0]*v[1]*v[2]
		else:
			print("getCentroid")
			sys.exit()