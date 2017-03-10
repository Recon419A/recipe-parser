#execfile('/Users/Omar/Desktop/Code/recipe-parser/recipe.py')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Set up & Utility Functions: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import pattern.en

execfile('/Users/Omar/Desktop/Code/recipe-parser/ingredients.py')
execfile('/Users/Omar/Desktop/Code/recipe-parser/directions.py')
execfile('/Users/Omar/Desktop/Code/recipe-parser/StepClass.py')
execfile('/Users/Omar/Desktop/Code/recipe-parser/RecipeClass.py')

def matchDirnAndIngredientInput(directions, ingredients):
	#This will match each recipe in the directions & ingredients file
	#ASSUMING they have already been SegmentedByNextRecipeTag AND they have same # of recipes
	pairings = []
	while("__SPLIT__\n" in directions):
		dirn_end_index = directions.index("__SPLIT__\n")
		ingr_end_index = ingredients.index("__SPLIT__\n")
		recipe_dirns = directions[:dirn_end_index]
		recipe_ingrs = ingredients[:ingr_end_index]
		
		pairings.append([recipe_ingrs, recipe_dirns])
		directions = directions[dirn_end_index+1:]
		ingredients = ingredients[ingr_end_index+1:]
	return pairings

def getRecipeIngredientsAttributes(recipe_ingrs_raw):
	recipe_ingrs_formatted = []
	for ingr in recipe_ingrs_raw:
		ingr_formatted = parse_ingredient(ingr)
		recipe_ingrs_formatted.append(ingr_formatted)
	recipe_ingrs_extracted = [recipe["Ingredient"] for recipe in recipe_ingrs_formatted]
	return recipe_ingrs_extracted

def getAdjacentIngredient(lower_step_tokens, index, recipe_ingrs_extracted_tokens):
	#where recipe_ingrs_extracted_toks = map(lambda(x): nltk.word_tokenize(x), recipe_ingrs_extracted)
	#& recipe_ingrs_extracted=getRecipeIngredientsAttributes(recipe_ingrs_raw)
	#Basically, recipe_ingrs_extracted_toks is a TOKENIZED LIST OF ALL OF THE 'INGREDIENTS' - no descriptions, measurements, nothing
	lower_step_pos = nltk.pos_tag(lower_step_tokens)

	iterator = index

	while( (iterator<len(lower_step_tokens)) and ((lower_step_pos[iterator][1] in ["DT", "CD"]) or (lower_step_tokens[iterator] in ing_measurements) or (lower_step_tokens[iterator] in ing_descriptors) 
	  or (bool(filter(lambda(x): x.isdigit(), lower_step_tokens[iterator]))))):
		iterator+=1

	if(iterator==len(lower_step_tokens)):
		return None

	susp_ingr  = lower_step_tokens[iterator]
	for ingr_token in recipe_ingrs_extracted_tokens:
		#The tokens of 1 ingredient 
		if(susp_ingr in ingr_token):
			len_ingr_token = len(ingr_token)
			iterator_fwd, iterator_bwd = None, None
			if(len_ingr_token>1):
				token_index = ingr_token.index(susp_ingr)
				len_step_tokens = len(lower_step_tokens)

				if(token_index==0): 
					#if suspected ingredient is found at the start of the token, check if there is a match w the next one
					iterator_fwd = 1
					while( (len_step_tokens > (token_index+iterator_fwd) ) and ( lower_step_tokens[token_index+iterator_fwd] in ingr_token) ):
						iterator_fwd+=1
					iterator_fwd-=1

				elif(token_index == (len_step_tokens-1) ): 
					#if suspected ingredient is found at the end of the token, check if there is a match w the previous one
					iterator_bwd = -1
					while( (len_step_tokens > (token_index+iterator_bwd) ) and ( lower_step_tokens[token_index+iterator_bwd] in ingr_token) ):
						iterator_bwd-=1
					iterator_bwd+=1

				else:
					#may be a chance that it is before OR after.
					iterator_fwd, iterator_bwd = 1, -1
					while( (len_step_tokens > (token_index+iterator_fwd) ) and ( lower_step_tokens[token_index+iterator_fwd] in ingr_token) ):
						iterator_fwd+=1
					
					while( ( (token_index+iterator_bwd) >= 0 ) and ( lower_step_tokens[token_index+iterator_bwd] in ingr_token) ):
						iterator_bwd-=1
					
					#Just to undo the offset
					iterator_fwd-=1
					iterator_bwd+=1

			if((iterator_fwd!=None) and (iterator_bwd!=None)):
				return lower_step_tokens[iterator+iterator_bwd : iterator+iterator_fwd+1]
			elif(iterator_fwd):
				return lower_step_tokens[iterator: iterator+iterator_fwd+1]
			elif(iterator_bwd):
				return lower_step_tokens[iterator+iterator_bwd : iterator]
			else:
				return [lower_step_tokens[iterator]]
		else:
			continue
	return None

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ User Interface: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

directions = segmentByNextRecipeTag(list(open("directions.txt", "r")))
ingredients = segmentByNextRecipeTag(list(open("ingredients.txt", "r")))
recipe_pairings = matchDirnAndIngredientInput(directions, ingredients)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ WorkSpace/Demo-code: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#This would eventually be parameterizable but just for now:
def runTests():
	for recipe in recipe_pairings[:10]:
		print "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
		recipe_ingrs_raw, recipe_dirns_raw = recipe
		recipe_ingrs_formatted = [parse_ingredient(ingr) for ingr in recipe_ingrs_raw]
		recipe_ingrs_extracted = getRecipeIngredientsAttributes(recipe_ingrs_raw)
		recipe_ingrs_extracted_toks = map(lambda(x): nltk.word_tokenize(x), recipe_ingrs_extracted)
		print "recipe ingredients are: ", recipe_ingrs_extracted,"\n"

		recipe_steps = getSteps(recipe_dirns_raw)
		recipe_lower_steps = map(str.lower, recipe_steps)

		myRecipe = Recipe()
		myRecipe.ProvideRawIngrData(recipe_ingrs_raw)
		myRecipe.ProvideRawDirnData(recipe_dirns_raw)
		myRecipe.extractFullIngrData(store=True)
		myRecipe.extractSolelyIngrData(store=True)
		myRecipe.extractSteps(store=True)
		for step in myRecipe.Steps:
			print "step is: ", step.step
			print "step.firstWordAnalysis() returns: ", step.firstWordAnalysis()
			print "step.splitAnalysis() returns: ", step.splitAnalysis(),"\n"

recipe_raw = recipe_pairings[0]
recipe_ingrs_raw, recipe_dirns_raw = recipe_raw

#Get ingredients:
recipe_ingrs_formatted = [parse_ingredient(ingr) for ingr in recipe_ingrs_raw]
recipe_ingrs_extracted = getRecipeIngredientsAttributes(recipe_ingrs_raw)
recipe_ingrs_extracted_toks = map(lambda(x): nltk.word_tokenize(x), recipe_ingrs_extracted)

#Get steps:
recipe_steps = getSteps(recipe_dirns_raw)
recipe_lower_steps = map(str.lower, recipe_steps)
lower_steps_toks = map(nltk.word_tokenize, recipe_lower_steps)

#Class Demo:
myRecipe = Recipe()
myRecipe.ProvideRawIngrData(recipe_ingrs_raw)
myRecipe.ProvideRawDirnData(recipe_dirns_raw)
myRecipe.extractFullIngrData(store=True)
myRecipe.extractSolelyIngrData(store=True)
myRecipe.extractSteps(store=True)

# for step in myRecipe.Steps:
# 	print "step is: ", step.step
# 	print "step.firstWordAnalysis() returns: ", step.firstWordAnalysis()
# 	print "step.splitAnalysis() returns: ", step.splitAnalysis(),"\n"



# Demo:
# for step in recipe_lower_steps:
# 	print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
# 	m1,t1,i1 = firstWordAnalysis(step, recipe_ingrs_extracted_toks)
# 	m2,t2,i2 = splitAnalysis(step, recipe_ingrs_extracted_toks)
# 	print "step is: ", step, "\n"
# 	print "According to First Word Analysis:"
# 	print "method is : ", m1
# 	print "tool is : ", t1
# 	print "ingr is : ", i1, "\n"
# 	print "According to splitAnalysis:"
# 	print "method is : ", m2
# 	print "tool is : ", t2
# 	print "ingr is : ", i2, "\n"


# firstWordAnalysis(recipe_lower_steps[1], recipe_ingrs_extracted_toks)
