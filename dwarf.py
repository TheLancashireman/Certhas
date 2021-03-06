#!/usr/bin/python3

# dwarf.py - DWARF classes
#
# (c) David Haworth

# This file is part of Certhas.
#
# Certhas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Certhas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Certhas.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys

class DwarfError(Exception):
	pass

# ==============================================================================
#
# A class to read and parse the dwarf.info output from readelf
#
class DwarfInfo:
	def __init__(self, elffilename):
		# The lines in this stream should contain either DW_TAG_ or DW_AT_
		cmd = 'readelf -wi ' + elffilename + ' | grep DW_'
		self.dwarfpipe = os.popen(cmd)
		self.type = ''
		self.level = -1
		self.ident = -1
		self.name = ''
		self.value = ''

	# Read and parse the next line
	#
	def Next(self):
		for line in self.dwarfpipe:
			self.level = -1
			self.ident = -1
			self.name = ''
			self.value = ''

			line = line.rstrip()
			fields = line.split()

			# There might be no space between the attribute name and the colon.
			if fields[1][-1] == ':':
				fields[1] = fields[1][0:-1]
				fields.insert(2, ':')
			if len(fields) >= 4:
				x = fields[1]
				if x[0:6] == 'DW_AT_':
					self.name = x
					# ':' is a field by itself. Value starts at field 3
					if fields[3] == '(indirect' and fields[4] == 'string,' and fields[5] == 'offset:':
						self.value = ' '.join(fields[7:])
					else:
						self.value = ' '.join(fields[3:])
					self.type = 'attr'
					return self.type
				elif len(fields) >= 5:
					x = fields[4]
					if x[0:8] == '(DW_TAG_':
						self.name = x[1:-1]
						x = fields[0].split('><')
						y = x[0]
						y = y[1:]
						self.level = int(y, 16)
						y = x[1]
						y = y[0:-2]
						self.ident = int(y, 16)
						self.type = 'tag'
						return self.type
			print('DwarfInfo.Next(): unrecognized line', line)
		self.dwarfpipe.close()
		self.type = 'eof'
		return self.type

# ==============================================================================
#
# A class to hold a DWARF object and its children
# Level 0: compile_unit
# Level 1: variables, constants, types etc. in the compile unit. Children of the compile unit.
# Structure/union members and enumerations are at level 2 below the structure/union/enum-type
# Also at level 2 subrange type, indicating the upper bound of an array type.
# Also at level 2 are local variables and formal parameters defined inside functions
# Levels 3..9 ... also exist
#
class DwarfObject:
	def __init__(self, parent):
		self.parent = parent
		self.tag = ''
		self.level = -1
		self.ident = -1
		self.name = ''
		self.basename = ''		# Base filename (for compile units)
		self.value = None		# Address (for variables), enumeration (for enums)
		self.specref = None		# The 'definition' DW_TAG_variable object, if any
		self.attr = {}
		self.children = []
		self.refs = {}

	def GetName(self):
		return self.name

	def GetBasename(self):
		return self.basename

	def GetParent(self):
		return self.parent

	def GetTag(self):
		return self.tag

	def GetStrippedTag(self):
		return self.tag[7:]

	def GetLevel(self):
		return self.level

	def GetIdent(self):
		return self.ident

	def GetValue(self):
		return self.value

	def GetSpecref(self):
		return self.specref

	def SetSpecref(self, specref):
		self.specref = specref

	# Get an attribute
	#
	def GetAttr(self, attrname):
		try:
			return self.attr[attrname]
		except:
			return None

	# Get a child element, given its reference ID
	#
	def GetChildByRef(self, ref):
		try:
			idx = self.refs[ref]
			return self.children[idx]
		except:
			return None

	# Get number of elements from an 'array_type' object
	#
	def GetNElements(self):
		if self.tag != 'DW_TAG_array_type':
			return None
		if len(self.children) <= 0:
			return None
		return self.children[0].GetAttr('DW_AT_upper_bound')+1

	# Read all the information (attributes) about an object, then read its children
	#
	def Read(self, dwp):
		if dwp.type == 'tag':
			self.tag = dwp.name
			self.level = dwp.level
			self.ident = dwp.ident
			#print('DEBUG: New object', self.tag, self.level, self.ident)
			while dwp.Next() == 'attr':
				self.AddAttr(dwp.name, dwp.value)
				#print('DEBUG:  ', dwp.name, dwp.value)
			while dwp.type == 'tag':
				if dwp.level <= self.level:
					return
				c = DwarfObject(self)
				c.Read(dwp)
				if c.ident > 0:
					self.refs[c.ident] = len(self.children)		# Index of the child, starting at 0
				self.children.append(c)
			# Now go through the list and link up the DW_AT_specification objects with their declarations.
			for c in self.children:
				sr = c.GetAttr('DW_AT_specification')
				if sr != None:
					c1 = self.GetChildByRef(sr)
					if c1 != None:
						c1.SetSpecref(c)
			return
		else:
			raise DwarfError('Not a tag')

	# Add an attribute to the attribute dictionary.
	# Some attributes are treated specially.
	#
	def AddAttr(self, attr, value):
		if attr == 'DW_AT_type' or attr == 'DW_AT_specification':
			value = int(value[1:-1], 16)
		elif attr == 'DW_AT_name':
			if self.tag == 'DW_TAG_compile_unit':			# Name is the filename
				self.name = value.replace('\\', '/')		# Convert filename to unix form
				self.basename = self.name.split('/')[-1]	# Remove the path
			else:
				self.name = value
		elif attr == 'DW_AT_upper_bound':
			value = int(value)
		elif attr == 'DW_AT_const_value':
			value = int(value)
			self.value = value
		elif attr == 'DW_AT_location':
			#print('DEBUG: DW_AT_location value = ', value)
			f = value.split()
			if f[-2] == '(DW_OP_addr:':
				#print('DEBUG', self.name, '|'+f[-1][0:-1]+'|')
				value = int(f[-1][0:-1], 16)
		elif attr == 'DW_AT_data_member_location':
			# Value might be just a number, or a DW_OP_plus_uconst string
			#print('DEBUG: DW_AT_data_member_location value = ', value)
			f = value.split()
			if len(f) == 1:
				value = int(f[0])
			elif f[-2] == '(DW_OP_plus_uconst:':
				#print('DEBUG |'+f[-1][0:-1]+'|')
				value = int(f[-1][0:-1], 10)
		self.attr[attr] = value

	# Find a child object; return None if not found
	#
	def FindObject(self, objname):
		for c in self.children:
			if c.name == objname:
				return c
		return None

	# Returns True if object is a pointer
	# Returns None if not a data type (no parent)
	#
	def IsPointer(self):
		p = self.parent
		if p == None:
			return False
		o = self
		while True:
			if o.GetTag() == 'DW_TAG_pointer_type':
				return True
			ref = o.GetAttr('DW_AT_type')
			if ref == None:
				return False
			o = p.GetChildByRef(ref)
			if o == None:
				return False

	# Returns True if object is a composite type (struct or union)
	# Returns None if not a data type (no parent)
	#
	def IsComposite(self):
		p = self.parent
		if p == None:
			return None
		o = self
		while True:
			t = o.GetTag()
			if t == 'DW_TAG_pointer_type':
				return False
			if t == 'DW_TAG_structure_type':
				return True
			if t == 'DW_TAG_union_type':
				return True
			ref = o.GetAttr('DW_AT_type')
			if ref == None:
				return False
			o = p.GetChildByRef(ref)
			if o == None:
				return False

	# Returns True if object is an enumeration type
	# Returns None if not a data type (no parent)
	#
	def IsEnum(self):
		p = self.parent
		if p == None:
			return None
		o = self
		while True:
			t = o.GetTag()
			if t == 'DW_TAG_pointer_type':
				return False
			if t == 'DW_TAG_enumeration_type':
				return True
			ref = o.GetAttr('DW_AT_type')
			if ref == None:
				return False
			o = p.GetChildByRef(ref)
			if o == None:
				return False

	# Returns no. of elements if object is an array; 0 if array type has no subrange; -1 otherwise
	#
	def GetArrayElements(self):
		p = self.parent
		if p == None:
			return -1
		o = self
		while True:
			if o.GetTag() == 'DW_TAG_array_type':
				n = o.GetNElements()
				if n == None:
					return 0
				return n
			ref = o.GetAttr('DW_AT_type')
			if ref == None:
				return -1
			o = p.GetChildByRef(ref)
			if o == None:
				return -1

	# Returns a list of enumerators if the object is an enumerated type; None otherwise
	#
	def GetEnumerators(self):
		if self.tag == 'DW_TAG_enumeration_type':
			e = []
			for c in self.children:
				if c.GetTag() == 'DW_TAG_enumerator':
					e.append(c)
			return e
		else:
			return None

	# Returns the enumerator name (symbol) for a given number
	# If not found, or if the object is not an enumerated type, return None
	#
	def GetEnumeratorName(self, num):
		if self.tag == 'DW_TAG_enumeration_type':
			for c in self.children:
				if c.GetTag() == 'DW_TAG_enumerator' and c.GetValue() == num:
					return c.name
			return None
		else:
			return None

	# Returns a list of members if the object is a struct or union; None otherwise
	#
	def GetMembers(self):
		if self.tag == 'DW_TAG_structure_type' or self.tag == 'DW_TAG_union_type':
			m = []
			for c in self.children:
				if c.GetTag() == 'DW_TAG_member':
					e.append(m)
			return e
		else:
			return None

# ==============================================================================
#
# Class to store the top-level objects (compile_units) of the dwarf info tree and
# provide top-level search functions
#
class DwarfFile:
	def __init__(self):
		self.objects = []

	# Read the file and construct the object tree
	#
	def Read(self, elffilename):
		dwp = DwarfInfo(elffilename)
		dwp.Next()
		while dwp.type == 'tag':
			o = DwarfObject(None)
			o.Read(dwp)
			self.objects.append(o)

	# Find a named object in the children of a top-level object
	#
	def FindObject(self, objname):
		for o in self.objects:
			obj = o.FindObject(objname)
			if obj != None:
				return obj
		return None

	# Find a named variable with either a location or a reference to a specification object
	# If there's no object with either, return the first match (same behavior as FindObject()
	#
	def FindObjectDefinition(self, objname):
		match = None				# Matches name only
		for o in self.objects:
			obj = o.FindObject(objname)
			if obj != None:
				if match == None:
					match = obj
				if obj.GetSpecref() != None:
					return obj
				if obj.GetAttr('DW_AT_location') != None:
					return obj
		return match
