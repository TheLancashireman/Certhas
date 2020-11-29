#!/usr/bin/python3

# dwarf.py - DWARF classes
#
# (c) David Haworth

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
			if len(fields) >= 4:
				x = fields[1]
				if x[0:6] == 'DW_AT_':
					if x == ':':
						# No space before the ':' so trim it off. Value starts at field 2
						self.name = x[0:-1]
						self.value = ' '.join(fields[2:])
					else:
						self.name = x
						# ':' is a field by itself. Value starts at field 3
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
		self.value = -1			# Address (for variables), enumeration (for enums)
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
			return
		else:
			raise DwarfError('Not a tag')

	# Add an attribute to the attribute dictionary.
	# Some attributes are treated specially.
	#
	def AddAttr(self, attr, value):
		if attr == 'DW_AT_type':
			value = int(value[1:-1], 16)
		elif attr == 'DW_AT_name':
			if self.tag == 'DW_TAG_compile_unit':			# Name is the filename
				self.name = value.replace('\\', '/')		# Convert filename to unix form
				self.basename = self.name.split('/')[-1]	# Remove the path
			else:
				self.name = value
		elif attr == 'DW_AT_upper_bound':
			value = int(value)
		elif attr == 'DW_AT_location':
			#print('DEBUG: DW_AT_location value = ', value)
			f = value.split()
			if f[-2] == '(DW_OP_addr:':
				self.value = int(f[-1][0:-1], 16)
		self.attr[attr] = value

	# Find a child object; return None if not found
	#
	def FindObject(self, objname):
		for c in self.children:
			if c.name == objname:
				return c
		return None

	# Returns True if object is a pointer
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
	# Returns None if not a data type
	#
	def IsComposite(self):
		p = self.parent
		if p == None:
			return None
		o = self
		while True:
			if o.GetTag() == 'DW_TAG_pointer_type':
				return False
			if o.GetTag() == 'DW_TAG_structure_type':	# FIXME ... or union?
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


# ==============================================================================
#
# Class to store the top-level objects (compile_units) of the dwarf info tree and
# provide search functions
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
