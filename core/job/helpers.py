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
