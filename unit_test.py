#!/usr/bin/python3

# (c) David Haworth
#
# Unit tests for parts of the elf/dwarf classes

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

from elf import Elf, ElfError

# Do the testing
#
def DoTesting():
	print('ConvertToSigned(-1, 2)    =', Elf.ConvertToSigned(-1, 2))
	print('ConvertToSigned(0, 1)     =', Elf.ConvertToSigned(0, 1))
	print('ConvertToSigned(127, 1)   =', Elf.ConvertToSigned(127, 1))
	print('ConvertToSigned(128, 1)   =', Elf.ConvertToSigned(128, 1))
	print('ConvertToSigned(255, 1)   =', Elf.ConvertToSigned(255, 1))
	print('ConvertToSigned(0, 2)     =', Elf.ConvertToSigned(0, 2))
	print('ConvertToSigned(32767, 2) =', Elf.ConvertToSigned(32767, 2))
	print('ConvertToSigned(32768, 2) =', Elf.ConvertToSigned(32768, 2))
	print('ConvertToSigned(65535, 2) =', Elf.ConvertToSigned(65535, 2))
	print('ConvertToSigned(2147483647, 4) = ', Elf.ConvertToSigned(2147483647, 4))
	print('ConvertToSigned(2147483648, 4) = ', Elf.ConvertToSigned(2147483648, 4))
	print('ConvertToSigned(4294967295, 4) = ', Elf.ConvertToSigned(4294967295, 4))
	print('ConvertToSigned(9223372036854775807, 8)  = ', Elf.ConvertToSigned(9223372036854775807, 8))
	print('ConvertToSigned(9223372036854775808, 8)  = ', Elf.ConvertToSigned(9223372036854775808, 8))
	print('ConvertToSigned(18446744073709551615, 8) = ', Elf.ConvertToSigned(18446744073709551615, 8))

	try:
		print('ConvertToSigned(256, 1) = ', Elf.ConvertToSigned(256, 1), 'FAIL')
	except ElfError as msg:
		print('ConvertToSigned(256, 1) exception :', msg)

	try:
		print('ConvertToSigned(65536, 2) = ', Elf.ConvertToSigned(65536, 2), 'FAIL')
	except ElfError as msg:
		print('ConvertToSigned(65536, 2) exception :', msg)

	try:
		print('ConvertToSigned(4294967296, 4) = ', Elf.ConvertToSigned(4294967296, 4), 'FAIL')
	except ElfError as msg:
		print('ConvertToSigned(4294967296, 4) exception :', msg)

	try:
		print('ConvertToSigned(18446744073709551616, 8) = ', Elf.ConvertToSigned(18446744073709551616, 8), 'FAIL')
	except ElfError as msg:
		print('ConvertToSigned(18446744073709551616, 8) exception :', msg)
	return

DoTesting()
exit(0)
