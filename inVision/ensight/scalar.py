import struct
import numpy as np

from airou.Char import bwrite
import sys

class ScalarPerElement:

	def __init__(self, CASE, ScalarFile = None, field = None):
		self.CASE = CASE

		if field is None:
			with open(ScalarFile, "rb") as file:
				arbit_str = file.read(80) #ignorable string
				self.field = []

				for part in CASE.Parts:
					v = []
					part_str = file.read(80)
					part_num = file.read(4)
					for element in part.Elements:
						element_type = file.read(80)
						v += [struct.unpack("f", file.read(4))[0] for i in range(element["ne"])]
					self.field.append({"name" :  part.name, "value" : np.array(v)})
		
		else:
			self.field = field

	def callField(self, name):
		for f in self.field:
			if f["name"] == name:
				return f

	def numpy(self, parts_name = None):
		if parts_name is None:
			parts_name = [part.name for part in self.CASE.Parts]

		scalar_field = []
		for pn in parts_name:
			scalar_field.append(self.callField(pn)["value"]) #np array. Shape is (N, )

		scalar_field = np.concatenate(scalar_field)

		return scalar_field




	def write(self, ScalarFile, parts_name = None):
		if parts_name is None:
			parts_name = [part.name for part in self.CASE.Parts]
		
		with open(ScalarFile, "wb") as file:
			bwrite(80, "Scalar", file)

			for idx, pn in enumerate(parts_name):
				part = self.CASE.callParts(pn)
				value = self.callField(pn)["value"]
				bwrite(80, "part", file)
				file.write(struct.pack("i", idx+1))
				
				index = 0
				for element in part.Elements:
					bwrite(80, element["name"], file)
					for i in range(index, index+element["ne"]):
						file.write(struct.pack("f", value[i]))
					index += element["ne"]


class ScalarPerNode(ScalarPerElement):
	def __init__(self, CASE, ScalarFile = None, field = None):
		self.CASE = CASE

		if field is None:
			with open(ScalarFile, "rb") as file:
				arbit_str = file.read(80) #ignorable string
				self.field = []

				for part in CASE.Parts:
					v = []
					part_str = file.read(80)
					part_num = file.read(4)
					cor_str = file.read(80)
					v += [struct.unpack("f", file.read(4))[0] for i in range(len(part.X))]
					self.field.append({"name" :  part.name, "value" : np.array(v)})
		
		else:
			self.field = field


	def write(self, ScalarFile, parts_name = None):
		if parts_name is None:
			parts_name = [part.name for part in self.CASE.Parts]
		
		with open(ScalarFile, "wb") as file:
			bwrite(80, "Scalar", file)

			for idx, pn in enumerate(parts_name):
				part = self.CASE.callParts(pn)
				value = self.callField(pn)["value"]
				bwrite(80, "part", file)
				file.write(struct.pack("i", idx+1))
				bwrite(80, "coordinates", file)

				for i in range(len(part.X)):
					file.write(struct.pack("f", value[i]))