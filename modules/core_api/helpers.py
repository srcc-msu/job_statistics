def shrinked(data, shrink_threshold):
	result = []

	factor = len(data) // shrink_threshold

	chunks = (data[x:x+factor] for x in range(0, len(data), factor))
	for chunk in chunks:
		l = len(chunk)

		result.append({
			"time": chunk[0][0]
			, "min" : min((x[1] for x in chunk))
			, "max" : max((x[2] for x in chunk))
			, "avg_min" : sum((x[3] for x in chunk)) / l
			, "avg_max" : sum((x[4] for x in chunk)) / l
			, "avg" : sum((x[5] for x in chunk)) / l
		})

	return result