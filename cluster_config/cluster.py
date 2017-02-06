name = "Lomonosov-2"

def node2int(node):
	"""custom function to convert nodename to int
	this one removes all chars from names like node1-001-01"""
	return int(''.join(filter(lambda x: x.isdigit(), node)))
