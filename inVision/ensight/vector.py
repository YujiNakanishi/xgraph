import struct
import numpy as np
import sys

from airou.Char import bwrite
from inVision.ensight.scalar import ScalarPerElement

class VectorPerElement(ScalarPerElement):

	def __init__(self, CASE, VectorFile = None, field = None):
		self.CASE = CASE

		if field is None:
			with open(VectorFile, "rb") as file:
				arbit_str = file.read(80) #ignorable string
				self.field = []

				for part in CASE.Parts:
					data_x = []
					data_y = []
					data_z = []
					part_str = file.read(80)
					part_num = file.read(4)
					for element in part.Elements:
						element_type = file.read(80)
						data_x += [struct.unpack("f", file.read(4))[0] for i in range(element["ne"])]
						data_y += [struct.unpack("f", file.read(4))[0] for i in range(element["ne"])]
						data_z += [struct.unpack("f", file.read(4))[0] for i in range(element["ne"])]

					data = np.stack((data_x, data_y, data_z), axis = 1)
					self.field.append({"name" :  part.name, "value" : data})
		
		else:
			self.field = field

	def write(self, VectorFile, parts_name = None):
		if parts_name is None:
			parts_name = [part.name for part in self.CASE.Parts]

		with open(VectorFile, "wb") as file:
			bwrite(80, "Vector", file)

			for idx, pn in enumerate(parts_name):
				part = self.CASE.callParts(pn)
				value = self.callField(pn)["value"]
				bwrite(80, "part", file)
				file.write(struct.pack("i", idx+1))
				
				index = 0
				for element in part.Elements:
					bwrite(80, element["name"], file)
					for j in range(3):
						for i in range(index, index+element["ne"]):
							file.write(struct.pack("f", value[i, j]))
					index += element["ne"]