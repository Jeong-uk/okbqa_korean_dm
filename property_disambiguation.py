# -*- coding: UTF-8 -*-

import os, collections, json
import sparql_endpoint
import post_module

class disambiguation_module :
	def __init__(self, endpoint, graph_iri, query_file):
		self.endpoint = endpoint
		self.graph_iri = graph_iri

		f = open(query_file)
		self.query_template = f.read().replace('\xef\xbb\xbf', '')

		f.close()

	def load_attributes(self, attribute_dir):
		self.mapping = collections.defaultdict(lambda: [])
		for (path, dir, files) in os.walk(attribute_dir):
			for filename in files:
				f = open(path + filename)
				for line in f:
					cols = line.split('\t')
					if len(cols) > 2 and cols[0] == '1':
						self.mapping[cols[2].strip().decode('utf-8')].append(
							'http://dbpedia.org/ontology/' + filename.replace('.attr', ''))

				f.close()

	def load_predicate(self, predicate_use, predicate_list):
		f = open(predicate_use)
		predicate_use_data = json.loads(f.read())
		self.predicate_map = collections.defaultdict(lambda:0)
		for predicate in predicate_use_data :
			self.predicate_map[predicate['p']] = int(predicate['callret-1'])

		f.close()

		f = open(predicate_list)
		predicate_list = json.loads(f.read())
		self.predicate_list = []
		for predicate in predicate_list :
			if 'ko.dbpedia' in predicate['p'] :
				self.predicate_list.append(predicate['p'][predicate['p'].rfind('/')+1:])

		f.close()

	def semantic_disambiguate(self, verbalization):
		candidates_with_score = []
		total_predicate = 0
		for candidate in self.mapping[verbalization] :
			candidate_with_score = {}
			candidate_with_score['property'] = candidate
			total_predicate += self.predicate_map[candidate_with_score['property']]
			candidates_with_score.append(candidate_with_score)

		for candidate_with_score in candidates_with_score :
			candidate_with_score['score'] = float(self.predicate_map[candidate_with_score['property']]) / total_predicate

		return candidates_with_score

	def lexical_disambiguate(self, verbalization):
		sent = json.loads(post_module.post(post_module.Config.pos_url, {'text':verbalization}, post_module.Config.content_type))[0]
		lemmas = []
		for morp in sent['morp'] :
			if morp['type'][0] != "X" :
				lemmas.append(morp['lemma'])

		result = []
		lemma_score = float(len(lemmas[0]))/len(verbalization)
		for predicate in self.predicate_list :
			if verbalization in predicate and float(len(verbalization)) / len(predicate) >= 0.29:
				result.append({'property': 'http://ko.dbpedia.org/property/' + predicate, 'score': float(len(verbalization)) / len(predicate)})
			elif lemmas[0] in predicate and lemma_score*float(len(lemmas[0])) / len(predicate) >= 0.29:
				result.append({'property': 'http://ko.dbpedia.org/property/' + predicate, 'score':lemma_score * float(len(lemmas[0]))/len(predicate)})

		return result

	def disambiguate(self, verbalization):
		candidates = []
#		f = open('preicate_list.txt', 'w')
#		f.write(json.dumps(sparql_endpoint.query(self.endpoint, self.graph_iri, 'select distinct ?p where {?s ?p ?o .}')))
#		f.close()
		candidates += self.semantic_disambiguate(verbalization)
		candidates += self.lexical_disambiguate(verbalization)

		return candidates
