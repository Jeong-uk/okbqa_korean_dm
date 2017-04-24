# -*- coding: UTF-8 -*-
import re

class disambiguation_module :
	def __init__(self):
		pass

	def load_entities(self, entities):
		self.entities = entities

		print entities

	def disambiguate(self, question, verbalization):
		candidates = []
		for index in [m.start() for m in re.finditer(verbalization, question)] :
			converted_begin = len(question[:index].encode('utf-8'))
			converted_end = len(question[:index+len(verbalization)].encode('utf-8'))
			for entity in self.entities :
				if entity['offset_start'] >= converted_begin and converted_end >= entity['offset_end'] :
					candidates.append({'uri':entity['uri'], 'score':entity['score']})

		"""
		max_uri = ''
		max_score = -1
		for candidate in candidates :
			if max_score < candidate[1] :
				max_score = candidate[1]
				max_uri = candidate[0]
		"""
		return candidates