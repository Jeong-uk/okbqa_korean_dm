# -*- coding: UTF-8 -*-
import json
import class_disambiguation, resource_disambiguation, property_disambiguation
import post_module

class Config :
	attribute_dir = 'attribute files/'
	predicate_used = 'predicate_use.txt'
	predicate_list = 'predicate_list.txt'

	resource_dm = resource_disambiguation.disambiguation_module()
	class_dm = class_disambiguation.disambiguation_module()
	property_dm = property_disambiguation.disambiguation_module("http://143.248.135.20:45103/sparql", "http://ko.dbpedia2015-10.kaist.ac.kr", 'template/predicate_used.txt')

	def __init__ (self) :
		print 'this class is only for configuration data'
		raise Exception

def parse_slot(data) :
	variable_data = {}
	for slot in data['slots']:
		if slot['s'] not in variable_data.keys():
			variable_data[slot['s']] = {'type': u'rdf:Resource'}

		if slot['p'] == 'is':
			variable_data[slot['s']]['type'] = slot['o']
		else:
			variable_data[slot['s']]['verbalization'] = slot['o']

	return variable_data

def initialize() :
	Config.property_dm.load_attributes(Config.attribute_dir)
	Config.property_dm.load_predicate(Config.predicate_used, Config.predicate_list)
	Config.class_dm.load_classes('kengdic.txt', 'class.txt')

def calculate_score(candidates, label, key) :
	result = []
	max_score = 0
	for candidate in candidates:
		result.append({'var': label, 'score': candidate['score'], 'value': candidate[key]})
		if max_score < candidate['score'] :
			max_score = candidate['score']

	return result, max_score


def disambiguation(data) :
	question = data['question']
	print question
	Config.resource_dm.load_entities(json.loads(post_module.post(post_module.Config.elu_url, {"text": question, "lower_bound": 0.5}, post_module.Config.content_type)))
	print
	variable_data = parse_slot(data)

	result = {'entities':[], 'classes':[], 'properties':[]}
	total_score = 1.0
	for label in variable_data.keys() :
		variable = variable_data[label]
		if 'rdf:Resource' in variable['type']:
			candidates = Config.resource_dm.disambiguate(question, variable['verbalization'])
			resource_result, max_score = calculate_score(candidates, label, 'uri')
			result['entities'] += resource_result
			total_score *= max_score
		elif variable['type'] == 'rdf:Property':
			candidates = Config.property_dm.disambiguate(variable['verbalization'])
			resource_result, max_score = calculate_score(candidates, label, 'property')
			result['properties'] += resource_result
			total_score *= max_score
		elif variable['type'] == 'rdf:Class' :
			candidates = Config.class_dm.disambiguate(variable['verbalization'])
			resource_result, max_score = calculate_score(candidates, label, 'class')
			result['classes'] += resource_result
			total_score *= max_score
		elif variable['type'] == '<http://lodqa.org/vocabulary/sort_of>' :
			result['properties'] += [{'score':1.0, 'property':'https://www.w3.org/1999/02/22-rdf-syntax-ns#type', 'var':label}]
		else :
			print 'incorrect variable type : ' + variable['type']
			raise Exception


	result['score'] = total_score

	return {'question':question, 'ned':[result]}

sample_input = json.loads('''
{
  "score": 1,
  "slots": [
    {
      "p": "is",
      "s": "v2",
      "o": "<http://lodqa.org/vocabulary/sort_of>"
    },
    {
      "p": "is",
      "s": "v3",
      "o": "rdf:Class"
    },
    {
      "p": "verbalization",
      "s": "v3",
      "o": "산"
    },
    {
      "p": "is",
      "s": "v4",
      "o": "rdf:Property"
    },
    {
      "p": "verbalization",
      "s": "v4",
      "o": "높"
    }
  ],
  "question": "세계에서 가장 높은 산은?",
  "query": "SELECT v1 WHERE { ?v1 ?v2 ?v3 . ?v1 ?v4 ?v5 . } ORDER BY DESC (v5) LIMIT 1"
}
''')

#initialize()
#print json.dumps(disambiguation(sample_input), ensure_ascii =False)