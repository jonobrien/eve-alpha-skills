# =============================================================================
# ripped apart: https://github.com/ntt/eveapi/blob/master/apitest.py
# =============================================================================

# Python 2/3 compatibility http://python-future.org/
from __future__ import print_function
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import object

import time
import tempfile
import pickle
import zlib
import os
from os.path import join, exists
import sys

import eveapi

# Put your userID and apiKey (full access) here before running this script.
YOUR_KEYID = os.environ['EVE_API_KEY']
YOUR_VCODE = os.environ['EVE_API_VCODE']




"""
- parse the allowed_skills.txt file of skills allowed
- for alpha clones defined by each race respectively
- into a dictionary of races with dictionaries of groups of skills
- not all races have same skills, so not separated by group
- instead kept as listed on devblog (in README)
"""
def parseAlpha():
	allTheSkills = {}
	allTheSkills['Minmatar'] = {}
	allTheSkills['Gallente'] = {}
	allTheSkills['Caldari'] = {}
	allTheSkills['Amarr'] = {}


	allTheLines = []
	lvls = ['1','2','3','4','5']
	with open('./allowed_skills.txt', 'r') as fd:
		allTheLines = fd.readlines()
	for line2 in allTheLines[1:]:
		line = line2.replace('\n','').split(' ')
		## Handle dynamic skill number indexing with cases for:
		# single word skills
		# multi-word skills with:
		# single word groups
		# multi-word groups
		sNum = None
		for idx in line:
			if idx in lvls:
				sNum = line.index(idx)
		if sNum is None:
			print('[!!] skill has no level specified:')
			print('[!!] ' + str(line))
			exit(-1)
		# ['Minmatar', 'Negotiation', '2', 'Social']
		# ['Gallente', 'High', 'Speed', 'Maneuvering', '3', 'Navigation']
		# ['Amarr', 'Amarr', 'Cruiser', '4', 'Spaceship', 'Command']
		#print([x for x in line if x in lvls])
		group = ' '.join(line[(sNum+1):])
		race = line[0]
		skill = ' '.join(line[1:sNum])
		# we need to initialize the nested dictionaries
		if group not in allTheSkills[race]:
			allTheSkills[race][group] = {}
		allTheSkills[race][group][skill] = sNum
	return allTheSkills


### eveapi.set_user_agent("eveapi.py/1.3")
## the set_user_agent function seems broken...


def main(args):
	alphaSkills = parseAlpha()
	api = eveapi.EVEAPIConnection()
	auth = api.auth(keyID=YOUR_KEYID, vCode=YOUR_VCODE)
	result2 = auth.account.Characters()
	## TODO either dynamically get this or just iterate 
	### over characters array depending on api masks
	RACE = 'Caldari' # race of character CHAR_INDEX
	CHAR_INDEX = 0 # index on character login screen of character you want, needs fixing
	# -----------------------------------------------------------------------------
	print()
	print('GETTING CHARACTER SHEET INFORMATION') ## TODO -- char name...
	print()

	# We grab ourselves a character context object.
	# Note that this is a convenience function that takes care of passing the
	# characterID=x parameter to every API call much like auth() does (in fact
	# it's exactly like that, apart from the fact it also automatically adds the
	# "/char" folder). Again, it is possible to use the API functions directly
	# from the api or auth context, but then you have to provide the missing
	# keywords on every call (characterID in this case).
	#
	me = auth.character(result2.characters[CHAR_INDEX].characterID)

	# Now that we have a character context, we can display skills trained on
	# a character. First we have to get the skill tree. A real application
	# would cache this data; all objects returned by the api interface can be
	# pickled.
	skilltree = api.eve.SkillTree()

	# Now we have to fetch the charactersheet.
	# Note that the call below is identical to:
	#
	#   acc.char.CharacterSheet(characterID=your_character_id)
	#
	# But, as explained above, the context ("me") we created automatically takes
	# care of adding the characterID parameter and /char folder attribute.
	sheet = me.CharacterSheet()

	# Now the fun bit starts. We walk the skill tree, and for every group in the
	# tree...
	for g in skilltree.skillGroups:
	    # ... iterate over the skills in this group...
	    for skill in g.skills:
	    	if g.groupName in alphaSkills[RACE]:
				currGroup = alphaSkills[RACE][g.groupName]
				if skill.typeName in currGroup:
					currSkill = alphaSkills[RACE][g.groupName][skill.typeName]
					trained = sheet.skills.Get(skill.typeID, False)
					if trained:
						# we trained the skill, and alpha can train it too
						print("{} - you: {} alpha: {} - group: {}".format(
						    skill.typeName,  trained.level, currSkill, g.groupName))
					# alpha allows, we haven't trained it yet
					else:
						print('* alpha allows for: {} - {}'.format(skill.typeName, currSkill))

	exit()

if __name__ == '__main__':
	main(sys.argv)