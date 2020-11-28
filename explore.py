#!/usr/bin/python3

# (c) David Haworth

import os
import sys

from elf import ElfHeader, ElfSymbolTable, ElfSectionTable
from dwarf import DwarfFile

eh = ElfHeader()
esym = ElfSymbolTable()
esect = ElfSectionTable()

df = DwarfFile()

# Print the information about a name or type
#
def PrintStuff(v):
	print('Name: ', v)
	v_obj = df.FindObject(v)
	if v_obj == None:
		print('.. not found')
		return
	v_tag = v_obj.GetStrippedTag()
	if v_tag == 'variable':
		print('.. variable at address', hex(v_obj.GetValue()))
		s = esym.FindByName(v)
		if s < 0:
			print('.. no ELF information')
		else:
			sym = esym.GetSymbol(s)
			print('.. ELF: address =', hex(esym.GetSymbolAddress(sym)), 'size =', hex(esym.GetSymbolSize(sym)))
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

#eh.Read(elffilename)
#if eh.GetClass() == '':
#	print('Error: '+elffilename+' doesn't look like an ELF file')
#	exit(1)

print('Reading the ELF/DWARF information; this might take some time')

eh.Read(elffilename)
esym.Read(elffilename)
esect.Read(elffilename)
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
