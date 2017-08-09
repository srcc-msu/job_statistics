from typing import List
import re

def reverse(n: int) -> int:
	return int(str(n)[::-1])

def id2hash(n: int, shift = 1) -> str:
	alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'
	base = 36

	result = ""

	n = reverse((n << shift) + 1)

	while n:
		result += alphabet[n % base]
		n = n // base

	return result[::-1]

def hash2id(hash: str, shift = 1) -> int:
	n = int(hash, 36)
	return reverse(n) >> shift

def username2id(username: str) -> int:
	result = 0

	for i in  username:
		result *= 255
		result += ord(i)

	return result

def id2username(id: int) -> str:
	result = ""

	while id > 0:
		result += chr(id % 255)
		id //= 255

	return result[::-1]

def __token2range(tokens: str) -> List[str]:
	result = []

	m = re.search("(.*)\[(.*)\]", tokens)

	if m is None:
		return [tokens]

	prefix = m.group(1)
	numbers = m.group(2)

	for pair in numbers.split(","):
		arr = pair.split("-")

		if len(arr) == 2:
			start = int(arr[0])
			end = int(arr[1])
		elif len(arr) == 1:
			start = int(arr[0])
			end = start
		else:
			raise RuntimeError("bad token: ", pair)

		for i in range(start, end + 1):
			result.append("%s%02d" % (prefix, i))

	return result

def expand_nodelist(nodelist) -> List[str]:
	"""expand nodelist compressed in slurm style"""
	tokens = nodelist.replace(",n", ".n")  # used to separate ',node' from 'node[1,3]'
	tokens = tokens.split(".")

	result = []

	for token in tokens:
		result += __token2range(token)

	return result
