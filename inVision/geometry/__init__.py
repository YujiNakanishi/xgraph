"""
/*********************/
inVision.geometry
/*********************/
"""
import numpy as np
import sys
import copy as cpy


"""
/****************/
polygon
/****************/
Field : points, value
	points -> list of np array. series of points should be CCW with respect to facet normal
	value -> list of any type. values per point
"""
class polygon:

	def __init__(self, points, value = None, subsetdim = False):
		self.points = points
		self.value = value

		if subsetdim:
			if self.SubsetDim() != 2:
				print(self.SubsetDim())
				print("Error@inVision.geometry.SubsetDim")
				print("subset dim isn't 2")
				sys.exit()

	def __call__(self):
		return self.points

	def origin(self):
		return self.points[0]

	def copy(self):
		points = cpy.deepcopy(self.points)

		if self.value is None:
			return type(self)(points)
		else:
			value = cpy.deepcopy(self.value)
			return type(self)(points, value)

	"""
	/*****************/
	SubsetDim
	/*****************/
	process : return sebset dim which points are in
	output : rank -> int. subset dim
	"""
	def SubsetDim(self):
		vectors = np.stack([p-self.points[0] for p in self.points[1:]], axis = 0)
		rank = np.linalg.matrix_rank(vectors)

		return rank

	"""
	/*****************/
	getBase
	/*****************/
	process : return orthonormal basis
	output : list of np array.
	Note : Subset dim of points should be 2.
	"""
	def getBase(self):
		e1 = (self.points[1]-self.points[0])/np.linalg.norm(self.points[1]-self.points[0], ord = 2)
		unit2 = (self.points[-1]-self.points[0])/np.linalg.norm(self.points[-1]-self.points[0], ord = 2)

		inner = e1@unit2

		if inner == 0.:
			return [e1, unit2]
		else:
			c = 1./inner
			e2 = (-e1+c*unit2)/np.linalg.norm(-e1+c*unit2, ord = 2)

			return [e1, e2]

	"""
	/***************/
	OnPlatePos
	/***************/
	process : return the position on subdim(dim = 2)
	Output : list of points
	"""
	def OnPlatePos(self):
		e1, e2 = self.getBase()
		return [np.array([p@e1, p@e2]) for p in self.points]

	"""
	/***************/
	getArea
	/***************/
	process : return area
	"""
	def getArea(self):
		onplatepoints = self.OnPlatePos()
		onplatepoints.append(onplatepoints[0])
		
		return 0.5*sum([p1[0]*p2[1]-p2[0]*p1[1] for p1, p2 in zip(onplatepoints[:-1], onplatepoints[1:])])

	"""
	/***************/
	getCentroid
	/***************/
	process : return centroid
	"""
	def getCentroid(self):
		area = self.getArea()

		e1, e2 = self.getBase()
		onplatepoints = [np.array([p@e1, p@e2]) for p in self.points]
		onplatepoints.append(onplatepoints[0])

		x = 0; y = 0
		for p1, p2 in zip(onplatepoints[:-1], onplatepoints[1:]):
			x += (p1[0]+p2[0])*(p1[0]*p2[1]-p2[0]*p1[1])
			y += (p1[1]+p2[1])*(p1[0]*p2[1]-p2[0]*p1[1])

		x /= (6.*area)
		y /= (6.*area)

		return x*e1+y*e2

	"""
	/***************/
	facet_normal
	/***************/
	process : return facet normal
	"""
	def facet_normal(self):
		e1, e2 = self.getBase()
		return np.cross(e1, e2)

	"""
	/***************/
	checkConvex
	/***************/
	process : check Convex
	Output : if convex -> return True, else, False
	"""
	def checkConvex(self):
		onplatepoints = self.OnPlatePos()
		onplatepoints.append(onplatepoints[0])

		judge = None
		for idx in range(1, len(onplatepoints)-1):
			vector1 = onplatepoints[idx+1]-onplatepoints[idx]
			vector2 = onplatepoints[idx-1]-onplatepoints[idx]

			cross = np.cross(vector1, vector2)

			if judge is None:
				if cross < 0:
					judge = "MINUS"
				elif cross > 0:
					judge = "PLUS"

			else:
				if (judge == "MINUS") & (cross > 0):
					return False
				elif (judge == "PLUS") & (cross < 0):
					return False

		return True

	"""
	/***************/
	splitTriangles
	/***************/
	process : split polygon by triangle
	Output : triangles -> list of polygon class
	Note : Since defined polygon in case of simulation is convex, we adopt the easiest way. 
	"""
	def splitTriangles(self, check = False):
		if check:
			if self.checkConvex() == False:
				print("Error@inVision.geometry.splitTriangles")
				print("Since polygon isnt convex, this method can't be used.")
				sys.exit()
				
		triangles = []
		if self.value is None:
			for p1, p2 in zip(self.points[1:-1], self.points[2:]):
				points = [cpy.deepcopy(self.points[0]), cpy.deepcopy(p1), cpy.deepcopy(p2)]
				new_class = type(self)(points)
				triangles.append(new_class)
		else:
			for p1, p2, v1, v2 in zip(self.points[1:-1], self.points[2:], self.value[1:-1], self.value[2:]):
				points = [cpy.deepcopy(self.points[0]), cpy.deepcopy(p1), cpy.deepcopy(p2)]
				value = [cpy.deepcopy(self.value[0]), cpy.deepcopy(v1), cpy.deepcopy(v2)]
				new_class = type(self)(points, value)
				triangles.append(new_class)

		return triangles


class polyhedral:

	def __init__(self, polygons):
		self.polygons = polygons

		if self.SubsetDim() < 3:
			print("Error@inVision.geometry.polyhedral.__init__")
			print("this is zero volume")
			sys.exit()

	"""
	/*****************/
	SubsetDim
	/*****************/
	process : return sebset dim which points are in
	output : rank -> int. subset dim
	"""
	def SubsetDim(self):
		points = []

		for polygon in self.polygons:
			points += cpy.deepcopy(polygon())

		vectors = np.stack([p-points[0] for p in points[1:]], axis = 0)
		rank = np.linalg.matrix_rank(vectors)

		return rank

	"""
	/*****************/
	isIn
	/*****************/
	process : X is in polyhedral or not
	input : X -> np array
	output : boolean
	"""
	def isIn(self, X):
		for polygon in self.polygons:
			vector = X-polygon.origin()
			if vector@polygon.facet_normal() > 0:
				return False

		return True

	"""
	/*****************/
	getVolume
	/*****************/
	process : return volume
	"""
	def getVolume(self):
		polygons = []

		for polygon in self.polygons:
			polygons += polygon.splitTriangles()

		triangles = type(self)(polygons)

		V = 0.
		for polygon in triangles.polygons:
			facet = np.cross(polygon.points[1]-polygon.points[0], polygon.points[2]-polygon.points[0])

			V += polygon.origin()@facet

		V /= 6.
		return V

	def getCentroid(self):
		polygons = []

		for polygon in self.polygons:
			polygons += polygon.splitTriangles()

		triangles = type(self)(polygons)
		V = self.getVolume()

		x = 0.; y = 0.; z = 0.
		for polygon in triangles.polygons:
			a = polygon.points[0]; b = polygon.points[1]; c = polygon.points[2]
			facet = np.cross(b-a, c-a)

			x += ((a[0]+b[0])**2+(b[0]+c[0])**2+(c[0]+a[0])**2)*facet[0]
			y += ((a[1]+b[1])**2+(b[1]+c[1])**2+(c[1]+a[1])**2)*facet[1]
			z += ((a[2]+b[2])**2+(b[2]+c[2])**2+(c[2]+a[2])**2)*facet[2]

		centroid = np.array([x, y, z])/(48.*V)

		return centroid


	def ElementValue(self):

		values = []
		for polygon in self.polygons:
			values += cpy.deepcopy(polygon.value)

		return np.mean(values, axis = 0)