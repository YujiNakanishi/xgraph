import struct
import sys

from inVision import ensight as en
from airou.Char import setString, forceASCII, bwrite

"""
process : read geometry file
input : CASE, geometryFile
	CASE -> CASE class
	GeometryFile -> str. Geometry file name
"""
def readGeometry(CASE, GeometryFile):
	with open(GeometryFile, "rb") as file:
		#####read first 240 bit chars which is ignorable.
		arbit_str = file.read(240)
		#####read node id style which is "off", "given", "assign" or "ignore"
		#If ensight gold is from OpenFOAM7, node_id is assign.
		node_id = getNodeIDStyle(file)
		#####read element id style which is "off", "given", "assign" or "ignore"
		#If ensight gold is from OpenFOAM7, element_id is assign.
		element_id = getElementIdStyle(file)

		#####read next 80 bits which may be "extents" or "part".
		#If extents, read more 24 bits as ignorable chars since information about range (xmin, xmax and so on) isn't required.
		#If ensight gold is from OpenFOAM7, arbit_str is "part".
		arbit_str = setString(file.read(80).decode())
		if arbit_str == "extents":
			extents_num = file.read(24)
			arbit_str = file.read(80) #part

		#####read all parts information
		fin_flag = False #flag for checking whether all parts are recorded or not.
		while True:
			part = en.PART()
			part_num = file.read(4) #part number. Ignorable
			name = setString(file.read(80).decode()) #part name
			part.name = forceASCII(name)
			cor_str = file.read(80) #coordinates. Ignorable
			nn = struct.unpack("i", file.read(4))[0] #number of node

			if nn == 0:
				#####parts often has no elements
				CASE.Parts.append(part)
				arbit_str = file.read(80) #part
				continue

			#####since node id isn't always required, cut node id information from reading file. 
			cutNodeId(file, nn, node_id) #node idの情報を読み込み，捨てる.

			#####extract X, Y and Z information
			part.X = [struct.unpack("f", file.read(4))[0] for i in range(nn)]
			part.Y = [struct.unpack("f", file.read(4))[0] for i in range(nn)]
			part.Z = [struct.unpack("f", file.read(4))[0] for i in range(nn)]

			#####extract element information
			element_type = setString(file.read(80).decode()) #element type
			while True:
				ne = struct.unpack("i", file.read(4))[0] #element ne
				cutElementId(file, ne, element_id)
				#####get structure information
				info = getStructure(file, element_type, ne)
				part.append(element_type, ne, info)

				#####get next 80 bits char
				element_type = file.read(80)
				if element_type == b'':
					#####if void, file has been read. make fin_flag True
					CASE.Parts.append(part)
					fin_flag = True
					break
				elif setString(element_type.decode()) == "part":
					#####if "part", start reading next part.
					CASE.Parts.append(part)
					break
				else:
					#####else, start reading next element
					element_type = setString(element_type.decode())

			if fin_flag:
					break

"""
process : write geometry file
input : CASE, geometryFile
	CASE -> CASE class
	GeometryFile -> str. Geometry file name
"""
def writeGeometry(CASE, GeometryFile, parts_name = None):
	if parts_name is None:
		parts_name = [part.name for part in CASE.Parts]

	with open(GeometryFile, "wb") as file:
		bwrite(80, "C Binary", file)
		bwrite(80, "inVision", file)
		bwrite(80, "", file)
		bwrite(80, "node id off", file)
		bwrite(80, "element id off", file)

		for idx, pn in enumerate(parts_name):
			part = CASE.callParts(pn)
			bwrite(80, "part", file)
			file.write(struct.pack("i", idx+1))
			bwrite(80, part.name, file)
			bwrite(80, "coordinates", file)

			#####write node info
			if part.X is None:
				file.write(struct.pack("i", 0))
				continue
			else:	
				file.write(struct.pack("i", len(part.X)))
				for x in part.X:
					file.write(struct.pack("f", x))
				for y in part.Y:
					file.write(struct.pack("f", y))
				for z in part.Z:
					file.write(struct.pack("f", z))

			#####write element info
			for element in part.Elements:
				writeStructure(file, element)



"""
process : get element information
input : file, element_type, ne
	file -> file class
	element_type -> str. element type name
	ne -> int. element num
output : info
Note : 
---type of element---
type of info depends on element type.
	if nsided:
		haven't been defined
	elif nfaced:
		haven't been defined
	else:
		info is list of list. len(info) is ne, and len(info[0]) is Np,
		where Np is num of node per element.
		deepest elements are int which represents node index.
		The value of axis can be known from part.X, Y and Z
"""
def getStructure(file, element_type, ne):
	#####get node num per element
	if not(element_type in ["nsided", "nfaced", "point"]):
		Np = int(element_type[-1])
	elif element_type == "point":
		Np = 1
	elif element_type in ["nfaced", "nsided"]:
		pass
	else:
		print("getStructure")
		print(element_type)
		sys.exit()

	if element_type == "nsided":
		Np = [struct.unpack("i", file.read(4))[0] for i in range(ne)]
		info = [[struct.unpack("i", file.read(4))[0] for j in range(Np[i])] for i in range(ne)]
	elif element_type == "nfaced":
		Nf = [struct.unpack("i", file.read(4))[0] for i in range(ne)] #number of face per elements
		Np = [[struct.unpack("i", file.read(4))[0] for j in range(Nf[i])] for i in range(ne)]

		info = []
		for i in range(ne):
			info.append([[struct.unpack("i", file.read(4))[0] for k in range(Np[i][j])] for j in range(Nf[i])])
	else:
		info = [[struct.unpack("i", file.read(4))[0] for j in range(Np)] for i in range(ne)]

	return info

"""
process : write element structure
input : file, element
	file -> file class
	element -> dictionary. element of PART.Elements.
"""
def writeStructure(file, element):
	if not(element["name"] in ["nsided", "nfaced", "point"]):
		Np = int(element["name"][-1])
	elif element["name"] == "point":
		Np = 1
	elif element["name"] == "nfaced":
		pass
	else:
		print("writeStructure")
		print(element["name"])
		sys.exit()

	bwrite(80, element["name"], file)
	file.write(struct.pack("i", element["ne"]))

	#####write node info
	if not(element["name"] in ["nsided", "nfaced"]):
		for i in range(element["ne"]):
			for j in range(Np):
				file.write(struct.pack("i", element["info"][i][j]))
	elif element["name"] == "nfaced":
		for e in element["info"]:
			file.write(struct.pack("i", len(e)))

		for e in element["info"]:
			for face in e:
				file.write(struct.pack("i", len(face)))

		for e in element["info"]:
			for face in e:
				for point in face:
					file.write(struct.pack("i", point))

	else:
		print("writeStructure")
		print(element["name"])
		sys.exit()




def getNodeIDStyle(file):
	style_str = file.read(80)

	if style_str[8:11].decode() == "off":
		return "off"
	elif style_str[8:14].decode() == "assign":
		return "assign"
	elif style_str[8:13].decode() == "given":
		return "given"
	else:
		print("node id error")
		sys.exit()


def getElementIdStyle(file):
	style_str = file.read(80)

	if style_str[11:14].decode() == "off":
		return "off"
	elif style_str[11:17].decode() == "assign":
		return "assign"
	elif style_str[11:16].decode() == "given":
		return "given"
	else:
		print("element id error")
		sys.exit()

def cutNodeId(file, nn, node_id):
	if node_id == "given":
		node_id_list = [struct.unpack("i", file.read(4))[0] for i in range(nn)]

	elif node_id == "ignore":
		print(node_id)
		print("cutNodeId")
		sys.exit()

def cutElementId(file, ne, element_id):
	if element_id == "given":
		element_id_list = [struct.unpack("i", file.read(4))[0] for i in range(ne)]
	elif element_id == "ignore":
		print(element_id)
		print("cutelementId")
		sys.exit()