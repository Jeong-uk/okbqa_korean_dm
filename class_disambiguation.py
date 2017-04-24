import json
import collections

class disambiguation_module :
	def __init__(self):
		pass

	def load_classes(self, dic_file, class_file) :
		f = open(dic_file)
		self.dic = collections.defaultdict(lambda:[])
		for line in f :
			cols = line.split('\t')
			if len(cols) > 3 :
				if cols[3][:2] in ['a ', 'A '] :
					cols[3] = cols[3][2:]
				elif cols[3][:3] in ['an ', 'An '] :
					cols[3] = cols[3][3:]
				elif cols[3][:4] in ['the ', 'The ']:
					cols[3] = cols[3][4:]

				self.dic[cols[1].replace('  ',' ').decode('utf-8')].append(cols[3].lower())
		f.close()

		self.classes = []
		f = open(class_file)
		for line in f :
			pos = line.find(' (edit)')
			self.classes.append(line[:pos])
		f.close()

	def disambiguate(self, verbalization):
		result = [{'score':0.99, 'class':'https://www.w3.org/2002/07/owl#Thing'}]
		verbalization = verbalization.replace(' ', '_')
#		print self.dic.keys()
		if verbalization in self.dic.keys() :
			for eng_verbalizaiton in self.dic[verbalization] :
				converted_word = eng_verbalizaiton.title().replace(' ','')
				for dbo_class in self.classes :
					if converted_word in dbo_class :
						result.append({'score':float(len(converted_word))/len(dbo_class), 'class':'http://dbpedia.org/ontology/'+dbo_class})
		return result