import urllib2, json

class Config :
	pos_url = 'http://143.248.135.60:31235/etri_pos'
	elu_url = 'http://143.248.135.150:2221/entity_linking'
	content_type = 'application/json; charset=utf-8'

def post(url, json_data, content_type):

	print  url
	print `json_data`
	print content_type
	request = urllib2.Request(url,
	                        data=json.dumps(json_data).encode('utf-8'),
	                        headers={'Content-Type':content_type})
	response = urllib2.urlopen(request)
	data = response.read()

	return data
