#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Set-up: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import nltk, string, os
# os.chdir("documents/eecs/eecs337/recipe-parser")
#execfile('/Users/Omar/Desktop/Code/recipe-parser/directions.py')

#for list of all possible NLTK P.O.S.s
#nltk.help.upenn_tagset()

if(os.getcwd() != '/Users/Omar/Desktop/Code/recipe-parser'):
	os.chdir("../Desktop/Code/recipe-parser")


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Vocabulary ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
dirn_descriptors = ["baking", "cold", "covered", "deep", "dutch", "foil", "glass", "greased", "heavy", "large", "loaf", "medium", "medium-size", "mixing", "nylon", "oiled", "paper", "plastic", "roasting", "shallow", "small","soup", "steak", "towel-lined", "well", "zipper"]

dirn_measurements = ["inch"]

dirn_methods = ["add", "adjust", "air", "allow", "arrange", "assemble", "bake", "baste", "be","beat", "begin", "blanch", "blend", "boil", "bone", "braise", "bread", "break", "bring",
"broil", "brown", "bronze", "brush", "butter", "caramelize", "carve", "check", "chill", "chop", "coat", "combine", "continue", "cook", "cool", "cover", 
"crack", "crisp", "cube", "cut", "deglaze", "dice", "dip", "discard", "dissolve", "dig", "divide", "do", "drain", "dredge", "drizzle", "drop", "dry", "dust", "fill", "flip", "fluff", "freeze", "fry", 
"fold", "form", "garnish", "gather", "glaze", "grate", "grease", "grill", "heat", "increase", "julienne", "keep", "knead", "ladle", "lay", "layer", "leave", "let", "lift", "line", "lower", "make", "marinate", 
"mash", "massage", "measure", "melt", "microwave", "mince", "mix", "moisten", "note", "oil", "pat", "place", "peel", "plate", "plunge", "pinch", "pink", "poach", "poke", "pound", "pour", "preheat", "press", "prevent", "prick", "process", 
"punch", "puree", "put", "raise", "read", "record", "reduce", "refrigerate", "reheat", "remember", "remove", "repeat", "replace", "reserve", "return", "rinse", "roast", "roll", "rub", "run", "salt", "saute", "scale", 
"scatter", "scoop", "scramble", "scrape", "seal", "sear", "season", "seed", "select", "separate", "serve", "set", "shake", "shape", "shave", "shred", "sift", "simmer", "skewer", "skim", "skin", 
"slice", "smear", "smoke", "soak", "soften", "soup", "spear", "spice", "split", "spoon", "spray", "spread", "sprinkle", "spritz", "squeeze", "squirt", "stand", "steam", "stir", "stirfry", "stir-fry","store", "strain", "stuff", "suspend", "sweeten", 
"swirl", "tap", "taste", "thread", "tie", "tilt", "time", "toast", "top", "toss", "transfer", "turn", "unroll", "use","wait", "wash", "warm", "weigh", "wet", "whip", "whisk", "wipe", "wrap"]

dirn_tools = ["barbeque", "bowl", "coal", "cooker", "colander", "cover", "deep-fryer", "dish", "fork", "grate", "grill", "knife", "oven", "pan", "pot","saucepan", "set", "skillet", "spatula",
	"thongs", "toaster", "water", "wok"]

dirn_time_units = ["day", "days", "hour", "hours", "minute", "minutes", "second", "seconds"]

dirn_bad_adverbs = ["then", "there", "meanwhile", "once"]

#Maybe check if it starts with "do not"


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Utility Functions: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def removeNextRecipeTag(ing_lst):
	while("NEXT RECIPE\n" in ing_lst):
		ing_lst.remove("NEXT RECIPE\n")
	return ing_lst

def segmentByNextRecipeTag(ing_lst):
	new_ing_lst = map(lambda(x): x.replace("NEXT RECIPE", "__SPLIT__"), ing_lst)
	return new_ing_lst

def clear():
	print "\n"*70

def formatDirn(dirn):
	#remove initial number; split by sentences; remove \n
	try:
		test =  dirn[dirn.index('. ')+2:].replace('  ',' ').replace('.\n','').replace('\n','').split('. ')
		return test
	except:
		print "dirn is", dirn, "."

def findConsecutiveWords(lower_arr_words, lower_arr_tokens):
	#returns the index of the first of the consecutive word block, or None if it is absent
	length_words = len(lower_arr_words)
	for i in range(len(lower_arr_tokens)-length_words):
		if(lower_arr_tokens[i:i+length_words] == lower_arr_words):
			return i
	return None

def getSteps(directions):
	steps = []
	for dirn in directions:
		formatted = formatDirn(dirn) 
		if formatted!=[""]:
			steps+=formatted
	return steps

def getSteps_AdvFirst(directions):
	special = []
	steps = getSteps(directions)
	lower_steps = map(str.lower, steps)
	for lower_step in lower_steps:
		lower_step_tokens = nltk.word_tokenize(lower_step)
		lower_step_pos = nltk.pos_tag(lower_step_tokens)
		if( (lower_step_pos[0][1]=="RB") and (lower_step_tokens[0] not in dirn_methods)):	
			special.append(lower_step)
	return special

def getSteps_MethFirst(directions):
	special = []
	steps = getSteps(directions)
	lower_steps = map(str.lower, steps)
	for lower_step in lower_steps:
		lower_step_tokens = nltk.word_tokenize(lower_step)
		if (lower_step_tokens[0] in dirn_methods):	
			special.append(lower_step)
	return special

def getSteps_InFirst(directions):
	special = []
	steps = getSteps(directions)
	lower_steps = map(str.lower, steps)
	for lower_step in lower_steps:
		lower_step_tokens = nltk.word_tokenize(lower_step)
		if (lower_step_tokens[0]=="in"):	
			special.append(lower_step)
	return special

def getSteps_AllElseFirst(directions):
	special = []
	steps = getSteps(directions)
	lower_steps = map(str.lower, steps)
	for lower_step in lower_steps:
		lower_step_tokens = nltk.word_tokenize(lower_step)
		lower_step_pos = nltk.pos_tag(lower_step_tokens)
		if( (lower_step_pos[0][1]!="RB") and (lower_step_tokens[0] not in dirn_methods)):	
			special.append(lower_step)
	return special

def getFirstWord_AllElseSteps(directions):
	#Just to get each first word that is neither Method nor Adjective
	steps = getSteps_AllElseFirst(directions)
	first_words = set()
	for step in steps:
		step_toks = nltk.word_tokenize(step)
		first_words.add(step_toks[0])
	return first_words

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Work Space ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def getAdjacentTool(index, lower_step_tokens, lower_step_pos, retIterator=False):
	#checks if there is a tool starting from that index
	iterator, tool = index, None

	#remove "determiners" such as 'a'
	while(lower_step_pos[iterator][1]=='DT'):
		iterator+=1

	start = iterator

	#While the next_word is compatible but not a tool, we continue onwards.
	while ((lower_step_tokens[iterator] in dirn_measurements) or (lower_step_tokens[iterator] in dirn_descriptors) 
	  or (bool(filter(lambda(x): x.isdigit(), lower_step_tokens[iterator])))):
		iterator+=1

	#To ensure accuraccy some more
	if(lower_step_tokens[iterator] in dirn_tools):
		#In event we have "grill grate" or something.
		while((iterator<len(lower_step_tokens)) and (lower_step_tokens[iterator] in dirn_tools)):
			iterator+=1

		next_tool, next_iterator = None, None

		if((iterator<len(lower_step_tokens)) and (lower_step_tokens[iterator]=="or")):
			next_tool, next_iterator = getAdjacentTool(iterator+1, lower_step_tokens, lower_step_pos, retIterator=True)

		if(next_iterator!=None):
			iterator = next_iterator
			tool = lower_step_tokens[start:iterator]
		else:
			tool = lower_step_tokens[start:iterator]

		if(retIterator):
			return tool, iterator
		else:
			return tool

	if(retIterator):
		return None, None
	else:
		return None

def getAdjacentIngredient(index, lower_step_tokens, lower_step_pos, retIterator=False):
	#Call after the first_word is method.
	#checks if there is an ingredient starting from that index

	#examples:
		# heat [4 cups vegetable oil] in a deep-fryer
		# beat the [egg] in a mixing bowl
		# add the [chicken cubes];
	iterator, ingredient = index, None

	#remove "determiners" such as 'a', 'the', 'an', 'these', 'those',
	while( (lower_step_pos[iterator][1]=='DT') or lower_step_pos[iterator][1]=='IN' ):
		iterator+=1

	#While the next_word is compatible but not a tool, we continue onwards.

	start = iterator



	#checks if there is a tool starting from that index
	iterator, tool = index, None

def firstWordAdverb(lower_step, lower_step_tokens, lower_step_pos):
	#Call this function when the firstWord is an Adverb.
	#It will extract METHOD & TOOL.
	#If it can't find either, it will return None in their place
	if(lower_step_tokens[1] in dirn_methods): 
		method = lower_step_tokens[1] #Should always be the case
		iterator = 2
		tool = getAdjacentTool(iterator, lower_step_tokens, lower_step_pos)
		print "lower_step is: ", lower_step
		print "method is: ", method
		print "tool is: ", tool
		return method, tool
	else:
		print "FAILED lower_step is: ", lower_step
		raise ValueError('Adverb wasnt followed by a method')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Work Space ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def firstWordAnalysis(lower_step):
	lower_step_tokens = nltk.word_tokenize(lower_step)
	lower_step_pos = nltk.pos_tag(lower_step_tokens)
	method, tool = None, None
	fw = lower_step_tokens[0]
	if(fw == "("):
		#In the event of this
		return firstWordAnalysis(lower_step[lower_step.index(")")+1:])
	
	elif (fw in dirn_methods):
		# If it is a verb
		method = fw
		in_a_index = findConsecutiveWords(["in", "a"], lower_step_tokens)
		if(in_a_index):
			tool = getAdjacentTool(in_a_index+2, lower_step_tokens, lower_step_pos)
			print "~~~~~~~~~~~~~~"
			print "lower_step: ", lower_step
			print "method: ", method
			print "tool: ", tool
		else:
			iterator = 1
			tool = getAdjacentTool(iterator, lower_step_tokens, lower_step_pos)

	elif (fw == "in"):
		#Functionality works! 
		iterator = 1
		tool, iterator = getAdjacentTool(iterator, lower_step_tokens, lower_step_pos, retIterator=True)
		if( (tool==None) or (iterator==None) ): iterator = 1

		# Check for "over ____ heat"
		if((lower_step_tokens[iterator] == "over") and (lower_step_tokens[iterator+2] == "heat")):
			iterator+=3
			
		#Get the method name. Checks for commas mainly.
		while(lower_step_tokens[iterator] not in dirn_methods):
			iterator+=1

		method = lower_step_tokens[iterator]
		
	elif ( (lower_step_pos[0][1]=="RB") and (lower_step_tokens[0] not in dirn_bad_adverbs)) :
		# if slowly, lightly, generously, lightly
		method, tool = firstWordAdverb(lower_step, lower_step_tokens, lower_step_pos)

	return method, tool

def getTime(lower_step):
	lower_step_tokens = nltk.word_tokenize(lower_step)
	lower_step_pos = nltk.pos_tag(lower_step_tokens)
	# if("for" in lower_step_tokens):
	
def understandDirections(directions):
	steps = getSteps(directions)
	for step in steps:
		tool, method = firstWordAnalysis
		if(tool == None):
			tool = extractTool()
		time = getTime(step.lower())


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Interface ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# directions = removeNextRecipeTag(list(open("directions.txt", "r")))
# allDirections = removeNextRecipeTag(list(open("Directions/allDirections.txt", "r")))
# asianDirections = removeNextRecipeTag(list(open("Directions/asianDirections.txt", "r")))
# diabeticDirections = removeNextRecipeTag(list(open("Directions/diabeticDirections.txt", "r")))
# dietHealthDirections = removeNextRecipeTag(list(open("Directions/dietHealthDirections.txt", "r")))
# glutenfreeDirections = removeNextRecipeTag(list(open("Directions/gluten-freeDirections.txt", "r")))
# healthyrecipesDirections = removeNextRecipeTag(list(open("Directions/healthy-recipesDirections.txt", "r")))
# indianDirections = removeNextRecipeTag(list(open("Directions/indianDirections.txt", "r")))
# italianDirections = removeNextRecipeTag(list(open("Directions/italianDirections.txt", "r")))
# lowcalorieDirections = removeNextRecipeTag(list(open("Directions/low-calorieDirections.txt", "r")))
# lowfatDirections = removeNextRecipeTag(list(open("Directions/low-fatDirections.txt", "r")))
# mexicanDirections = removeNextRecipeTag(list(open("Directions/mexicanDirections.txt", "r")))
# southernDirections = removeNextRecipeTag(list(open("Directions/southernDirections.txt", "r")))
# worldDirections = removeNextRecipeTag(list(open("Directions/worldDirections.txt", "r")))
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Tests ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



