#!/usr/bin/python3

# ELF classes
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

class ElfError(Exception):
	pass

# ==============================================================================
#
# Elf - standalone functions and other useful odds'n'ends
#
class Elf:
	def __init__(self):
		return

# Convert an unsigned value to signed
#   v = unsigned value
#   s = size in bytes
#
	@staticmethod
	def ConvertToSigned(v, s):
		limit = 2 ** (s * 8)
		if v < limit:				# Avoid strange aliasing effects: raise an exception
			if v < int(limit/2):
				return v			# Number is positive, zero or already negative
			return v - limit		# Convert to negative
		raise ElfError(str(v) + ' is out of range for ' + str(s) + '-byte variable')

# ==============================================================================
#
# ElfHeader - read and store the ELF header
#
class ElfHeader:
	def __init__(self):
		self.elfclass = ''
		self.endian = ''
		self.machine = ''
		self.target = ''
		self.bits = 0

	# Get the ELF class
	#
	def GetClass(self):
		return self.elfclass

	# Get the endianness
	#
	def GetEndian(self):
		return self.endian

	# Get the ELF machine
	#
	def GetMachine(self):
		return self.machine

	# Get the machine word size
	#
	def GetBits(self):
		return self.bits

	# Read the header and extract useful information from it
	#
	def Read(self, elffilename):
		cmd = 'readelf -h ' + elffilename
		elfpipe = os.popen(cmd)
		for line in elfpipe:
			line = line.rstrip()
			fields = line.split()
			try:
				if fields[0] == 'Class:':
					self.elfclass = fields[1]
				elif fields[0] == 'Data:':
					self.endian = fields[-2]
				elif fields[0] == 'Machine:':
					self.machine = fields[-1]
			except:
				pass
		elfpipe.close()
		if self.elfclass == 'ELF64':
			self.bits = 64
		elif self.elfclass == 'ELF32':
			self.bits = 32
		else:
			raise ElfError(elffilename + ' doesn\'t appear to be an ELF binary file')
		return

# ==============================================================================
#
# ElfSymbol - one symbol in the ELF symbol table
#
class ElfSymbol:
	def __init__(self, fields):
		self.num = fields[0]
		self.value = int(fields[1], 16)
		self.size = int(fields[2])
		self.type = fields[3]
		self.bind = fields[4]
		self.vis = fields[5]
		self.ndx = fields[6]
		if len(fields) >= 8:
			self.name = fields[7]
		else:
			self.name = None


# ==============================================================================
#
# ElfSymbolTable - read and store the ELF symbol table
#
class ElfSymbolTable:
	def __init__(self):
		self.symtab = []
		self.byName = {}
		self.byAddress = {}
		self.sortedAddress = []
		self.sectiontable = None

	# Set the section table
	# Must be done before GetVariableValue() can be used.
	#
	def SetSectionTable(self, st):
		self.sectiontable = st

	# Reads the symbol table from the specified file
	#
	def Read(self, elffilename):
		cmd = 'readelf -sW ' + elffilename
		idx = 0
		elfpipe = os.popen(cmd)
		for line in elfpipe:
			line = line.rstrip()
			fields = line.split()
			if len(fields) == 0 or fields[0] == 'Symbol' or fields[0] == 'Num:':
				# Ignore headers and blank lines
				pass
			else:
				# Add the fields to the symbol table
				s = ElfSymbol(fields)
				self.symtab.append(s)
				# The symbol name is in field 7 so we need at least 8 fields
				if s.name != None:
					# Add the symbol name to the byName dictionary.
					# The names should be unique, so we overwrite anything that's already there
					self.byName[s.name] = idx

					# Add the symbol to the byAddress dictionary.
					# There could be several symbols at any address, so we append to the list.
					# If there's no symbol at the address we create an empty list first.
					addr = s.value
					try:
						x = self.byAddress[addr]
					except:
						self.byAddress[addr] = []
					self.byAddress[addr].append(idx)
				idx = idx + 1
		elfpipe.close()

		# Store the symbol addresses in a sorted list for looking up arrays
		self.sortAddress = sorted(list(self.byAddress.keys()))

		return

	# Returns the index of the symbol whose name is passed
	#
	def FindByName(self, sym):
		try:
			x = self.byName[sym]
		except KeyError:
			x = -1
		return x

	# Returns the indexes of the symbols whose address is passed
	#
	def FindByAddress(self, addr):
		try:
			x = self.byAddress[addr]
		except KeyError:
			x = []				# No symbols at this address
		return x

	# Returns the entire symbol information for the given index
	#
	def GetSymbol(self, idx):
		if idx < 0:
			return None
		try:
			s = self.symtab[idx]
		except KeyError:
			s = None
		return s

	# Returns the name field of a symbol
	#
	def GetSymbolName(self, s):
		return s.name

	# Returns the address field of a symbol as a number
	#
	def GetSymbolAddress(self, s):
		return s.value

	# Returns the name size field of a symbol as a number
	#
	def GetSymbolSize(self, s):
		return s.size

	# Returns the full symbol information for a named symbol
	#
	def GetSymbolByName(self, name):
		idx = self.FindByName(name)
		if idx < 0:
			return None
		sym = self.GetSymbol(idx)
		return sym

	# Returns the value of a simple variable
	# Note: if the variable is not simple, may return a very large number.
	#
	def GetVariableValue(self, name):
		sym = self.GetSymbolByName(name)
		a = self.GetSymbolAddress(sym)
		l = self.GetSymbolSize(sym)
		v = self.sectiontable.Load(a, l)
		return v

	# Returns the value of a simple variable
	# Note: if the variable is not simple, may return a very large number.
	#
	def GetSignedVariableValue(self, name):
		sym = self.GetSymbolByName(name)
		a = self.GetSymbolAddress(sym)
		l = self.GetSymbolSize(sym)
		v = self.sectiontable.LoadSigned(a, l)
		return v

	# Returns the name of the first symbol at a given address that starts with a given pattern
	# If the address is 0, returns 'NULL'
	# If there are no symbols at the address, looks for the symbol with the next lower address
	# If there is no match, returns the first symbol
	#
	def BestMatch(self, addr, pattern):
		# NULL pointer: assume no symbol
		if addr == 0:
			return 'NULL'

		sym = self.BestMatchSym(addr, pattern)
		return self.GetSymbolName(sym)

	# Returns the first symbol at a given address that starts with a given pattern
	# If the address is 0, returns 'NULL'
	# If there are no symbols at the address, looks for the symbol with the next lower address
	# If there is no match, returns the first symbol
	#
	def BestMatchSym(self, addr, pattern):
		# NULL pointer: assume no symbol
		if addr == 0:
			return None

		syms = self.FindByAddress(addr)
		if len(syms) == 0:
			addrl = self.FindLowerSymbol(addr)
			if addrl == 0:
				return None		# No symbol found
			syms = self.FindByAddress(addrl)
			if len(syms) == 0:
				return None		# No symbol found (shouldn't happen)
		first = self.GetSymbol(syms[0])
		for s in syms:
			sym = self.GetSymbol(s)
			name = self.GetSymbolName(sym)
			if name.startswith(pattern):
				return sym
		return first

	# Returns the next lower address that holds a symbol
	# Note: linear search. Is a binary search possible?
	#
	def FindLowerSymbol(self, addr):
		n = len(self.sortAddress)
		if self.sortAddress[0] > addr:
			return 0					# Address is below the lowest symbol
		for i in range(1,n):
			if self.sortAddress[i] > addr:
				return self.sortAddress[i-1]
		return self.sortAddress[n-1]	# Address is above the highest symbol

	# Returns the name and the index for an array member
	# Return value is a tuple  name, index, ok  where ok is true only if the address is an EXACT index
	# Error message printed if address is not an element of the array
	#
	def FindArrayRef(self, addr, pattern, msize):
		# NULL pointer: assume no symbol
		if addr == 0:
			return 'NULL',0,False
		sym = self.BestMatchSym(addr, pattern)
		name = self.GetSymbolName(sym)
		if name == '':
			return name,0,False
		
		baseaddr = self.GetSymbolAddress(sym)
		idx = int( (addr - baseaddr) / msize )
		ok = ( (addr - baseaddr) % msize ) == 0
		if not ok:
			print('FindAddrRef(): ERROR! Address is not an array member', addr, name)
		return name,idx,ok

# ==============================================================================
#
# ElfSection - representation of an ELF section including the contents if needed
#
class ElfSection:
	def __init__(self, fn, idx, fields):
		self.elffilename = fn
		self.Nr = idx

		if len(fields) == 8 and fields[0] == 'NULL':
			fields.insert(0, '')		# Insert a blank name
		if len(fields) == 9:
			fields.insert(6, '')		# Insert an empty set of flags
		#print('DEBUG: ', fields)

		self.Name = fields[0]
		self.Type = fields[1]
		self.Addr = fields[2]
		self.Offset = fields[3]
		self.Size = fields[4]
		self.ES = fields[5]
		self.Flg = fields[6]
		self.Lk = fields[7]
		self.Inf = fields[8]
		self.Al = fields[9]

		self.baseaddr = int(self.Addr, 16)
		self.size = int(self.Size, 16)
		self.loaded = False		# Tried loading
		self.hasdata = False	# There is data in the data array
		self.data = []
		#print('DEBUG: section', self.Nr, self.Name, self.Type, self.Addr, self.Size)

	# Read the section into the self.data list
	# The hex dump prints the bytes in byte-address order in groups of up to 4 bytes, regardless of endianness
	#
	def Read(self):
		#print('DEBUG: reading section', self.Name, 'from', self.elffilename)
		offset = 0
		cmd = 'readelf -x' + self.Name + ' ' + self.elffilename
		hexdump = os.popen(cmd)
		for line in hexdump:
			line = line.rstrip()
			#print('DEBUG hexdump = |'+line+'|')

			# This is tricky now. line.split() doesn't work because there could be spaces in the character
			# representation at the end. However, the data block (including leading and trailing space)
			# should b 37 characters long. Let's assume that, for now.
			pos = line.find('0x')
			if pos < 0:
				continue		# '0x' not found; ignore line
			line = line[pos:]	# Trim off everything before the '0x'
			pos = line.find(' ')
			if pos < 0:
				continue		# ' ' not found; ignore line
			addr = int(line[0:pos], 16)
			if offset != addr - self.baseaddr:
				# A gap. Does this ever happen? If it does we'll have to insert padding
				raise ElfError('Gap found in hex dump of section ' + self.Name + ' at ' + hex(self.baseaddr + offset))
			block = line[pos:pos+37]			# The data part, including spaces
			block = block.replace(' ', '')		# Remove all the spaces
			for i in range(0, len(block), 2):	# length should be even. If not, ignore the last half-byte.
				byte = block[i:i+2]
				self.data.append(int(byte, 16))
				offset = offset + 1
		hexdump.close()
		self.loaded = True
		self.hasdata = (offset != 0)
		if self.hasdata and offset != self.size:
			print('Warning: section ' + self.name + ': length of hexdump differs from section size')

	# Load n bytes of data from a given address
	#
	def Load(self, addr, n, littleendian):
		if addr < self.baseaddr:
			return None					# Not in section
		offset = addr - self.baseaddr
		if offset + n > self.size:
			return None					# Extends beyond section
		if not self.hasdata:
			if not self.loaded:
				self.Read()
			if not self.hasdata:
				return None				# Section has no data
		tval = 0
		if littleendian:
			order = range(n-1, -1, -1)
		else:
			order = range(n)
		for i in order:
			tval = tval * 256 + self.data[offset+i]
		return tval

	# Load a 0-terminated string from a given address
	#
	def LoadString(self, addr, max):
		if addr < self.baseaddr:
			return None					# Not in section
		if addr >= self.baseaddr + self.size:
			return None					# Not in section
		if not self.hasdata:
			if not self.loaded:
				self.Read()
			if not self.hasdata:
				return None				# Section has no data
		i = addr - self.baseaddr
		if max > self.size - i:
			max = self.size - i				# Don't allow load to extend beyond section
		count = 0
		str = ''
		while self.data[i] != 0 and count < max:
			str = str + chr(self.data[i])
			i = i + 1
			count = count + 1
		return str


# ==============================================================================
#
# ElfSectionTable - read and store the content of a section
#
class ElfSectionTable:
	def __init__(self, e):
		self.sections = []
		self.littleendian = e
		return

	# Read and store the section table
	#
	def Read(self, elffilename):
		cmd = 'readelf -SW ' + elffilename
		sects = os.popen(cmd)
		for line in sects:
			line = line.rstrip()
			m = line.find('[')
			if m >= 0:
				n = line.find(']')
				if n > m and line[m+1:n] != 'Nr':
					idx = int(line[m+1:n])
					fields = line[n+1:].split()
					self.sections.append(ElfSection(elffilename, idx, fields))
		sects.close()
		return

	# Load n bytes of data from a given address
	#
	def Load(self, addr, n):
		for s in self.sections:
			v = s.Load(addr, n, self.littleendian)
			if v != None:
				return v
		return None

	# Load n bytes of data from a given address, converted to a signed number
	#
	def LoadSigned(self, addr, n):
		v = self.Load(addr, n)
		if v != None:
			return Elf.ConvertToSigned(v, n)
		return None

	# Load a 0-terminated string from a given address
	#
	def LoadString(self, addr, max):
		for s in self.sections:
			str = s.LoadString(addr, max)
			if str != None:
				return str
		return None
