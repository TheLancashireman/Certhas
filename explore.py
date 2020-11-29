#!/usr/bin/python3

# (c) David Haworth

import os
import sys

from elf import ElfHeader, ElfSymbolTable, ElfSectionTable
from dwarf import DwarfFile

eh = None
esym = None
esect = None
df = None

# Print the information about a name or type
#
def PrintStuff(v):
	print('Name: ', v)
	v_obj = df.FindObject(v)
	if v_obj == None:
		print('.. not found')
		return

	is_pointer = v_obj.IsPointer()
	if is_pointer:
		print('.. is a pointer type')

	n_array = v_obj.GetArrayElements()
	if n_array >= 0:
		print('.. is an array with', n_array, 'elements')

	is_struct = v_obj.IsComposite()
	if is_struct:
		print('.. is a composite type')

	v_tag = v_obj.GetStrippedTag()
	if v_tag == 'variable':
		addr = v_obj.GetValue()
		if addr == None:
			print('.. variable; no address in dwarf data')
		else:
			print('.. variable at address', hex(addr))
		s = esym.FindByName(v)
		if s < 0:
			print('.. no ELF information')
		else:
			sym = esym.GetSymbol(s)
			addr = esym.GetSymbolAddress(sym)
			sz = esym.GetSymbolSize(sym)

			if is_struct:
				val = 'composite type'
			else:
				if n_array < 0:
					n_items = 1
				else:
					n_items = n_array
				if n_items == 0:
					val = 'array with 0 elements'
				else:
					s = int(sz/n_items)
					val = ''
					for b in range(addr, addr+sz, s):
						val = val + hex(esect.Load(b, s)) + ', '
					val = val[0:-2]
			print('.. ELF: address =', hex(addr), 'size =', hex(sz), 'value =', val)
	else:
		print('..', v_tag)
	p = v_obj.GetParent()
	if p == None:
		print('.. no parent')
		return
	print('.. found in', p.GetBasename())
	t = v_obj
	print('..', end=' ')
	while True:
		r = t.GetAttr('DW_AT_type')
		if r == None:
			print()
			return
		t = p.GetChildByRef(r)
		name = t.GetName()
		tag = t.GetStrippedTag()
		if tag == 'const_type':
			print('const', end=' ')
		elif tag == 'pointer_type':
			print('pointer to', end=' ')
		elif tag == 'volatile_type':
			print('volatile', end=' ')
		elif tag == 'structure_type':
			print('struct', name, end=' ')
		elif tag == 'enumeration_type':
			print('enum', name, end=' ')
		elif tag == 'base_type':
			print(': Base type', name, end=' ')
		elif tag == 'array_type':
			print('array', end=' ')
			e = t.GetNElements()
			if e == None:
				print('[] of', end=' ')
			else:
				print('['+str(e)+'] of', end=' ')
		elif tag == 'typedef':
			print(name, end=' ')
			if v_tag == 'variable':
				# Stop printing when the type of the variable is known
				print()
				return
		else:
			print(tag, name, end=' ')

# Get the filename; if none supplied, print usage message and exit
try:
	elffilename = sys.argv[1]
except:
	print('Usage: '+sys.argv[0]+' ELF-file [name] [...]')
	exit(1)

interactive = False

# If there's a list of names on the command line, print information about them and then exit.
stream = sys.argv[2:]
if len(stream) == 0:
	# No list of names; enter interactive mode; read names from stdin
	stream = sys.stdin
	interactive = True

print('Reading the ELF/DWARF information; this might take some time')

eh = ElfHeader()
eh.Read(elffilename)

esym = ElfSymbolTable()
esym.Read(elffilename)

esect = ElfSectionTable(eh.GetEndian() == 'little')
esect.Read(elffilename)
esym.SetSectionTable(esect)

df = DwarfFile()
df.Read(elffilename)

if interactive:
	print('Interactive mode; CTRL-D to exit')
	print('>', end=' ', flush=True)

for v in stream:
	v = v.rstrip()
	PrintStuff(v)
	if interactive:
		print('>', end=' ', flush=True)

exit(0)
