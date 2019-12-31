import random

#Import all implimented decks
from base import deck as base_deck
from fe import deck as fe_deck
from crossover_1 import deck as c1_deck
from crossover_2 import deck as c2_deck
from hu import deck as hu_deck
# For testing individual cards
from base import cards as custom
# I have just implimented the personas of HU for now.  They can be accessed if any_pick == True
# from hu import persona as hu_personas
from frames import card_frame
import arcade
import globe

# As sets are chosen, they are moved from decks to choosen_sets
decks = [base_deck.this_set,fe_deck.this_set,hu_deck.this_set,c1_deck.this_set,c2_deck.this_set]
choosen_sets = []
#Specifies weather small set personas muct be picked when playing with small sets
any_pick = False

# This is a terminal interface to choose which sets we are playing with.
# Right now, it must be called before everything else
# This should be changed to a gui interface...
def choose_sets():
	print("Which sets would you like to play with? type 'play' to start game.")
	for i,d in enumerate(decks):
		print(f"{i}  {d.name}    (large set:{d.large_set})")
	x = input()
	if x == 'play':
		if len(choosen_sets) == 0:
			print("You must choose at least 1 set.")
			return choose_sets()
		return
	else:
		intx = -1
		safe = True
		try:
			intx = int(x)
		except:
			print("?")
			safe = False
		if safe and intx >= 0 and intx < len(decks):
			choosen_sets.append(decks.pop(intx))
		return choose_sets()

# Once the sets are choosen, this loads and returns the avalable personas
# If any_pick == False and there is 1 or more small set (like crossover packs)
# Then only the personas from the smaller sets can be choosen
def get_personas():
	small_sets = []
	large_sets = []
	# Goes thoguh all the choosen sets and loads the personas into either the small or large set lists
	for d in choosen_sets:
		if globe.DEBUG:
			print(f"Loading {d.name}'s personas...",flush = True)
		if d.large_set:
			large_sets.extend(d.load_personas())
		else:
			small_sets.extend(d.load_personas())
	# If any_pick, you can only choose between any of the small sets personas, if any
	if not any_pick:
		if len(small_sets) > 0:
			return small_sets
	else:
		# if not any_pick, combines large sets, small sets, and the HU personas
		large_sets.extend(small_sets)
	return large_sets

# Assembles each players starting hand
def get_starting_deck(player):
	assemble = []
	for c in range(3):
		assemble.append(card_frame.vunerability(player))
	for c in range(7):
		assemble.append(card_frame.punch(player))

	#Shuffles here
	random.shuffle(assemble)
	# Any cards that are added here will be at the top of each players starting deck
	# and will be drawn before their first turn.  This is very usefull for testing cards.

	# make sure that we cange where 'custom' points, it should point to the set of the cards we are testing
	#assemble.append(custom.shazam(player))
	#assemble.append(custom.catwoman(player))
	#assemble.append(custom.green_arrows_bow(player))
	#assemble.append(custom.green_arrows_bow(player))
	#assemble.append(custom.green_arrows_bow(player))
	#assemble.append(custom.green_arrows_bow(player))

	return assemble

# For debug, sets what players discard pile starts as.
# Should be an empty list when not testing
def debug_discard(player):
	assemble = []
	return assemble

# Initialize weakness and kick stacks
# I was told these were the starting amounts
def initialize_weaknesses():
	assemble = []
	for c in range(20):
		assemble.append(card_frame.weakness())
	return assemble

def initialize_kicks():
	assemble = []
	for c in range(16):
		assemble.append(card_frame.kick())
	return assemble

#if there are any small sets, it only pulls SV's out of them
#the number of SV's to use is the least of the avalable sets of SV's
#Last SV is choosen, and then the rest of the SV's are choosen in the order they are given
# For example, in crossover 1 & 2 the SV's are suposed to be played in a specific order.
# This order is maintained, but each SV is individually pulled from a random set
def initialize_supervillains():
	small_sets = []
	large_sets = []
	for d in choosen_sets:
		if globe.DEBUG:
			print(f"Loading {d.name}'s SV's...",flush = True)
		if d.large_set:
			large_sets.append(d.load_supervilains())
		else:
			small_sets.append(d.load_supervilains())
	# If there are any small sets, we will prioritize adding them
	# Otherwise we will add SV's from the large sets
	prioritize = large_sets
	if len(small_sets) > 0:
		prioritize = small_sets
	# Messy way of finding the smallest set
	smallest_villain_amount = 99
	for d in prioritize:
		smallest_villain_amount = min(smallest_villain_amount,len(d))
	# If there are more than 1 set to choose from...
	if len(prioritize) > 1:
		assemble = []
		#Set last SV
		assemble.append(random.choice(prioritize)[0])
		for d in prioritize:
			d.pop(0)

		# Set the rest of the SV's counting down
		while len(assemble) < smallest_villain_amount:
			count_from_end = smallest_villain_amount - len(assemble)
			assemble.append(random.choice(prioritize)[-count_from_end])
	else:
		assemble = prioritize[0]
	return assemble

# Initializes the main deck
def initialize_deck():
	small_sets_cards = []
	#large_sets = []
	assemble = []
	for d in choosen_sets:
		if globe.DEBUG:
			print(f"Loading {d.name}'s deck...",flush = True)
		if d.large_set:
			assemble.extend(d.load_deck())
		else:
			small_sets_cards.extend(d.load_deck())
	#All large sets should be shuffled (although there may be none)
	random.shuffle(assemble)
	random.shuffle(small_sets_cards)
	# If there are no cards from large sets, then we are only playing with the small sets
	# I allow this, for experimentation, but really this is not a good way to play.
	# The deck will run out of cards very fast.
	if len(assemble) == 0:
		return small_sets_cards
	elif len(small_sets_cards) > 0:
		#  If there are sa mix of small set(s) and large set(s) then we split
		# The small sets in the top half of the large sets
		# Split the deck
		bottom_split = assemble[:int(len(assemble)/2)]
		top_split = assemble[int(len(assemble)/2):]
		# Shuffle the small sets into the top half
		top_split.extend(small_sets_cards)
		random.shuffle(top_split)
		# Put the deck back togeather
		assemble = bottom_split
		assemble.extend(top_split)

	return assemble
	


