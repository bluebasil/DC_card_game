"""
The main portion of the program.
This hosts the game controler (called the 'boss' to differentiate itself 
from controlers in the Model/View/Controler pettern)
This also hosts the two most prominent objects used: Pile's and Player's
They should probably be split up into seperate files infact...

"""
import random
import controlers
import effects
import deck_builder
import globe
import error_checker
import queue

from constants import cardtype
from constants import owners
from constants import ai_hint
from constants import trigger

#Custom exception for ending the game early
class MainDeckEmpty(Exception):
    pass

class DupeFailure(Exception):
    pass

"""
A pile refers to any collection of cards in the game.
For instance, all of the stacks (Villain, Kick, Weakness)
are piles, but so are the main deck, each players deck, 
each players hand, the ongoing section, the in-play section
under and on top of each players Persona

The 'contents' is the list of the cards that the pile contains
"""
class pile:
	#List of cards
	contents = None
	#Not all piles have owners, like the line-up
	#Note: the owners constants could be set as owners here if desired
	#but right now, any non-player piles and None as their owner
	owner = None
	#Not nessesary but usefull for debuging
	name = ""

	#I'll start the deck empty
	def __init__(self,name,owner = None):
		self.name = name
		self.owner = owner
		self.contents = []

	#I made a bunch of functions for dealing with the contents,
	#but i think it's more pyhonic to deal with the contents list
	#directly, so they are depreciated
	#depreciated
	def shuffle(self):
		random.shuffle(self.contents)

	#depreciated
	def size(self):
		return len(self.contents) 

	def can_draw(self):
		if self.size() > 0:
			return True
		else:
			return False

	def reveal(self):
		if len(self.contents) > 0:
			return self.contents[-1]
		elif self.name == "Main Deck":
			raise MainDeckEmpty
		else:
			return None

	def draw(self):
		if len(self.contents) > 0:
			return self.contents.pop()
		elif self.name == "Main Deck":
			raise MainDeckEmpty
		else:
			return None

	#depreciated
	def add(self,card):
		self.contents.append(card)

	#depreciated
	def add_bottom(self,card):
		self.contents.insert(0,card)

	#used well, but maybe should be depreciated?
	def get_count(self,find_type = cardtype.ANY):
		if find_type == cardtype.ANY:
			return self.size()
		else:
			count = 0
			for c in self.contents:
				if c.ctype_eq(find_type):
					count += 1
			return count

"""
cards considered 'in-play' have a special pile
On top of holding cards that are in-play, this pile also
tracks the amount of power that has been generated, and
the list of all cards that have been played
NOTE: Some cards have been played but are not 'in-play' like
cards played from other locations and then removed, or cards 
played and then destroyed.

"""
class playing(pile):
	power = 0
	played_this_turn = []
	#double modifier was put in special for Paralax.
	#I am trying to avoid putting in anything that is card specific 
	#I could probably turn this into a mod now, but there is a few complications
	#For example: this mod would have to run on all other mods as well
	#This could be fixed if I switched how power is stored, which I do plan to do
	# see the 'play' function for more
	#This is an int so that paralax can be played multiple times.  Its number
	#coresponds with how many times all the power should be doubles
	double_modifier = 0
	#Mods are pices of code that personas or cards can run on cards played after them
	#For example: Locations effects being triggered on other played cards
	card_mods = []
	#Options are actions that can be taken at a specific time, usually by pressing a 
	#coresponding button.
	#Note: I have been using 'action' and 'option' interchangablly, which is bad, I
	#should stick with one or the other
	special_options = []

	#Each card is played by running this basic mod, all of which it does it run the
	#cards play action
	def no_mod(self,card,player):
		return card.play_action(player)

	def __init__(self,name,owner = None):
		super().__init__(name,owner)
		self.played_this_turn = []
		self.special_options = []
		#The basic mod always exists, which is how cards are played
		self.card_mods = [self.no_mod]

	#Cleanup for turn end
	def turn_end(self):
		#reset variables
		self.power = 0
		self.played_this_turn = []
		self.special_options = []
		self.card_mods = [self.no_mod]
		self.double_modifier = 0

		#Put cards back into their respective locations
		#Most will go in the players discard pile, but if a card has been played
		#from somewherew else, they should go there
		#Note: This may not be an exsaustive list!!

		#discard_a_card now handles discarding cards that do not belong to you
		while self.size() > 0:
			self.owner.discard_a_card(self.contents[0],valid_tigger = False)
			#c = self.contents.pop()
			#if c.owner_type == owners.PLAYER:
			#	c.owner.discard.add(c)
			#elif c.owner_type == owners.MAINDECK:
			#	globe.boss.main_deck.add(c)
			#elif c.owner_type == owners.LINEUP:
			#	globe.boss.lineup.add(c)
			#elif c.owner_type == owners.VILLAINDECK:
			#	globe.boss.supervillain_stack.add(c)

	#To play a card, run this
	#Ongoing cards are not played with ongoing = True.
	#Ongoing is only true when the ongoing pile calls this
	def play(self,card,ongoing = False):
		if globe.DEBUG:
			if card.owner != self.owner:
				if card.owner_type == owners.PLAYER:
					print(f"{self.owner.persona.name} playing {card.owner.persona.name}'s {card.name}",flush = True)
				else:
					print(f"{self.owner.persona.name} playing {card.owner_type}'s {card.name}",flush = True)
			else:
				print(f"{card.name} being played",flush = True)

		#Cards played from the ongoing pile do not get added to this 'in-play' pile
		#Note, ongoing cards are considered in play by the game rules, so if something refers
		#to in-play cards, they have to both check the ongoing and playing pile
		if not ongoing:
			#For statistics, but has not been fully implimented
			card.times_played += 1
			self.contents.append(card)
			
		#runs the cards code
		card.play_action(self.owner)
		#the card is not officially played until its code is done,
		#it gets added to 'played this turn' afterwards

		if not ongoing:
			self.played_this_turn.append(card)
			trigger.all(trigger.PLAY,[card],self.owner)

		

	def parallax_double(self):
		#Paralax double on power already accumulated
		self.power *= 2
		self.double_modifier += 1

	#Officially add power to this turn
	#This should be used now instead of adding power by returning
	#This way power is added at the right point on the cards text
	def plus_power(self,power):
		for i in range(self.double_modifier):
			power *= 2
		self.power += power


#Cards stored in the ongoing pile have their play function ran every turn,
#But dont go into the 'playing' pile and are not recoreded in 'played_this_turn'
class ongoing_pile(pile):
	def begin_turn(self):
		for c in self.contents:
			self.owner.played.play(c,True)

#Just keeps track of the last SV seen, so that multiple cannot be bought in a single turn
#I could just modify the pile directly
class supervillain_pile(pile):
	current_sv = None

"""
Functionally controls each player
Has a connected persona and controller
The contoler is what human and ai players actiolly interact with
The controler is usually touched through the effects file
I could add the ability to have multiple personas, which will be required with Teen-Titans Go

"""
class player:
	pid = -1
	#The vp score, which can be tracked as the gae progresses, good for determining how good
	#one is doing
	score = 0
	#This refers to the physiscal tokens
	vp = 0

	#All of the piles assotiated with the player
	deck = None
	hand = None
	discard = None
	ongoing = None
	played = None
	under_superhero = None
	over_superhero = None

	#Important links
	controler = None
	persona = None

	#Note: I would like to rework the  'redirect' functionality
	#Cards or personas can register reditections here
	#When a card is bought or gained, all the redistered code is ran
	#Right now, they return a location where the card is put
	#But this is also used for being notified about what cards were bought this turn
	gain_redirect = []
	#Stores all fo the cards bought or gained this turn
	gained_this_turn = []
	discarded_this_turn = []
	#Stores how much cheeper the SV should be.
	discount_on_sv = 0
	#So  far i have no method of settign how much cheeper other cards should be
	already_drawn = False


	#For cards to use on generic rare things
	#like if they have to detect discarding cards and such
	#I should switch the personas that detect drawing to use this as well
	#and passing
	#and discarding
	#and gaining vps
	triggers = []
	
	def __init__(self,pid, controler):
		#persona is not initialized until the use has chosen a persona.
		#If personas are choosen befor game, they  should be initalied here
		self.controler = controler
		self.pid = pid

		#Initialize all piles, with self as their owner
		self.deck = pile("Deck",self)
		self.hand = pile("Hand",self)
		self.discard = pile("Discard",self)
		self.under_superhero = pile("Under Persona",self)
		self.over_superhero = pile("Over Persona",self)
		self.ongoing = ongoing_pile("Ongoing",self)
		self.played = playing("Played",self)

		#If testing with cards that affect vp tokens, this can be set
		#self.vp = 5

		#These should be reinitialized or they share values with all insatnces
		self.gain_redirect = []
		self.gained_this_turn = []
		self.discarded_this_turn = []
		self.triggers = []

		#Initialize the players sterting deck
		self.deck.contents = deck_builder.get_starting_deck(self)

		#For degugging if cards are required in the discard
		self.discard.contents = deck_builder.debug_discard(self)

		#Draw the first hand
		self.draw_card(num=5,from_card = False,should_trigger = False)

	#asks the controler directly which persona 
	def choose_persona(self,persona_list):
		self.persona = self.controler.choose_persona(persona_list)
		persona_list.remove(self.persona)
		self.persona.set_owner(self)

		self.persona.reset()

	#Starts and runs the turn
	#End-turn is called outside for things that need to affect 
	#in-between turn and turn end
	def turn(self):
		#unfreeze all cards in lineup that were frozen by me
		for c in globe.boss.lineup.contents:
			if self.pid in c.frozen:
				c.frozen.remove(self.pid)

		#Most things are reset in end_turn
		#Since cards can be discarded between turns, this has to be reset again
		self.discarded_this_turn = []
		self.already_drawn = False

		#sets up the turn
		#crossover 2's 'Promise to a friend' + 'roy harper' require
		#ongoing to begin before personas.  If something else 
		#requires the opposite, this will have to be re-worked
		self.ongoing.begin_turn()
		self.persona.ready()

		#Asks the controler to as the player or AI whats next
		self.controler.turn()

	#Draws 'num' cards.  Returns the last card that was drawn
	#the returned card is from legacy
	def draw_card(self,num = 1,from_card = True,should_trigger = True):
		#print("PLAYER HAS BEEN TOLD TO DRAW",self.persona.name,flush = True)
		all_drawn = []
		
		#if from_card:
		#	self.persona.draw_power()
		if should_trigger:
			trigger.all(trigger.DRAW,[num,from_card,all_drawn],self)
		for i in range(num):
			#Check that there is a card to draw
			if not self.manage_reveal():
				#This will break things, but is so rare it shouldn't happen really?
				#This will need to be protected for in the future!!
				#print("ERR: No more cards in deck",flush = True)
				pass
			else:
				drawn_card = self.deck.draw()
				all_drawn.append(drawn_card)
				self.hand.add(drawn_card)
		

		#Used for cards that say "The first time a card tells you to draw on each of your turns..."
		self.drawn_card = True
		
		return all_drawn

	#returns the top card of the deck
	#if public = True, runs the reveal effect
	#Maybe this should take a number of cards to reveal, beacuse cards that have
	#'look at the top three cards of your deck' have to do some annoying things to get the top 3
	#(They pop the card after reveling, in a loop, and then later put the cards back)
	def reveal_card(self,public = True):
		if not self.manage_reveal():
			return None
		top_card = self.deck.contents[-1]
		if public:
			reveal_text = f"{top_card.name} was on the top of {self.persona.name}'s deck."
			effects.reveal(reveal_text,self,[top_card])
		return top_card

	#If the deck is empty, shufflethe discard pile into the deck
	def manage_reveal(self):
		if not self.deck.can_draw():
			self.deck.contents = self.discard.contents
			self.discard.contents = []
			self.deck.shuffle()
			if self.deck.size() == 0:
				return False
			return True
		else:
			return True

	#Depreciated
	def play(self, cardnum):
		if globe.DEBUG:
			print("play-START",flush = True)
		self.played.play(self.hand.contents.pop(cardnum))
		globe.boss.clear_queue()

	#Playes the given card IF IT IS IN YOUR HAND
	#If the card is being played from somewhere else play_and_return or
	#playing.play directly should be used
	def play_c(self, card):
		if card in self.hand.contents:
			if globe.DEBUG:
				print("play_c-START",flush = True)
			self.hand.contents.remove(card)
			self.played.play(card)
			globe.boss.clear_queue()

	#Given card must be already poped
	#Plays it, and retusn it to the indicated pile
	def play_and_return(self, card, pile):
		save_owner_type = card.owner_type
		save_owner = card.owner
		self.played.play(card)
		card.pop_self()
		#gets put back at the location specified, no matetr what
		#even if it was destroyed
		card.owner_type = save_owner_type
		card.owner = save_owner
		pile.contents.append(card)

	#Formally discards the given card
	#Triggers anything that needs to know that a card has been discarded
	def discard_a_card(self,card,valid_tigger = True):
		card.pop_self()
		if valid_tigger:
			self.persona.discard_power()
			trigger.all(trigger.DISCARD,[card],self)
			self.discarded_this_turn.append(card)

		#Put cards back into their respective locations
		#Most will go in the players discard pile, but if a card has been played
		#from somewherew else, they should go there
		#Note: This may not be an exsaustive list!!
		if card.owner_type == owners.PLAYER:
			card.owner.discard.add(card)
		elif card.owner_type == owners.MAINDECK:
			globe.boss.main_deck.add(card)
		elif card.owner_type == owners.LINEUP:
			globe.boss.lineup.add(card)
		elif card.owner_type == owners.DESTROYED:
			globe.boss.destroyed_stack.add(card)
		elif card.owner_type == owners.VILLAINDECK:
			globe.boss.supervillain_stack.add(card)

		#self.discard.add(card.pop_self())
		#self.discarded_this_turn.append(card)

	#Call this if a card has been passed, to triggerharly quins ability
	#I would like to create a 'move' method on a card that automatically calls this is a card changes owners
	def card_has_been_passed(self,card):
		self.persona.card_pass_power()
		trigger.all(trigger.PASS,[card],self)


	def click_action(self,action):
		if action in self.played.special_options:
			if globe.DEBUG:
				print("click-START",flush = True)
			action.click_action(self)
			globe.boss.clear_queue()

	def get_cost(self,card):
		results = trigger.all(trigger.PRICE,[card.cost,card],self,pay_forward = True,immediate = True)
		#since pay forward is on, the cost will already be calculatec
		predicted_cost = card.cost
		if len(results) > 0:
			predicted_cost = results[-1]
		return predicted_cost

#The following buy or gain functions return False is they are unsucsesfull, and True if the card is gained

	#Tries to buy the SV
	def buy_supervillain(self):
		#print("Trying to buy sv",globe.boss.supervillain_stack.contents[-1].cost - self.discount_on_sv,flush = True)
		#Is the top SV visible, or is it flipped over.
		#Do we have enough power (minus discount) to buy the sv
		if globe.boss.supervillain_stack.current_sv == globe.boss.supervillain_stack.contents[-1]:
			card = globe.boss.supervillain_stack.contents[-1]

			predicted_cost = self.get_cost(card)

			#remember to take discount_on_sv out once trigger.PRICE has been fully implimented
			if self.played.power >= predicted_cost - self.discount_on_sv:
				if globe.DEBUG:
					print(f" {card.name} bought")
					print("buy_sv-START",flush = True)
				#This is the only time that SV's can be 'defeated', and therefore defeat=True
				if self.gain(card,price = predicted_cost - self.discount_on_sv,defeat = True):
					globe.boss.clear_queue()
					return True
		return False

	def buy_kick(self):
		if globe.boss.kick_stack.size() > 0:
			card = globe.boss.kick_stack.contents[-1]

			predicted_cost = self.get_cost(card)

			if self.played.power >= predicted_cost:
				if globe.DEBUG:
					print(f"kick bought")
					print("buy_kick-START",flush = True)
				if self.gain(card,price = predicted_cost):
					globe.boss.clear_queue()
					return True
		return False

	def gain_a_weakness(self):
		if globe.boss.weakness_stack.size() > 0:
			return self.gain(globe.boss.weakness_stack.contents[-1])
		return False

#depreciated
	def buy(self,cardnum):
		if cardnum < 0 or cardnum >= len(globe.boss.lineup.contents):
			return False
		card = globe.boss.lineup.contents[cardnum]
		
		predicted_cost = self.get_cost(card)

		if self.played.power >= predicted_cost:
			#card.bought = True
			if globe.DEBUG:
				print(f"{card.name} bought")
				print("buy-START",flush = True)
			#self.played.power -= card.cost
			if self.gain(globe.boss.lineup.contents[cardnum],price = predicted_cost):
				globe.boss.clear_queue()
				return True
			#return True
		return False

	#No discounds have been applied, that may need to be added in the future
	def buy_c(self,card):
		predicted_cost = self.get_cost(card)

		if self.played.power >= predicted_cost and len(card.frozen) == 0:
			if globe.DEBUG:
				print(f"{card.name} bought")
				print("buy_c-START",flush = True)
			if self.gain(card,price = predicted_cost):
				globe.boss.clear_queue()
				return True
		return False

	#cards that are bought are also gained
	#This can return False if the card does not want to be gained (like if it enforces
	#certain criteria that have not been met)

	def gain(self, card,price = None,defeat = False):
		bought = False
		#Trying to buy card. Have not payed yet, but funds have been secured
		if price != None:
			bought = True
			#card is frozen, cannot buy
			if len(card.frozen) != 0:
				return False

		#Trying to buy card.  Card may resist, if not, it may do other effects
		if not card.buy_action(self,bought,defeat):
			return False

		if price != None:
			# All checks passed, paying
			#avoids negative
			self.played.power -= max(price,0)

		card.pop_self()
		self.gained_this_turn.append(card)

		
		#I can replace redirecting with triggers.  
		#Right now I will have both features untill I patch the other sets
		redirected = False
		results = trigger.all(trigger.GAIN_CARD,[redirected,card,bought,defeat],self,pay_forward = True)
		#Ownser should be set after gain trigger, so that it can be determined where it came from
		card.set_owner(player=self)

		if True in results:
			redirected = True
		
		#If the card has not been redirected, gained cards go in the playes discard
		if not redirected:
			self.discard.add(card)

		return True

	#Adds vp tokens
	def gain_vp(self,amount):
		self.vp += amount
		self.persona.gain_vp_power()
		trigger.all(trigger.GAIN_VP,[amount],self)
			

	#for ending the turn, or other cards like the batmobile
	def discard_hand(self):
		for c in self.hand.contents.copy():
			self.discard_a_card(c)


	#This resets everything for the player
	#The order of these is very important!
	#For example: persona.reset must be before 'gained_this_turn' is reset
	#but after self.discard_hand and played.turn_end so that Wonder Woman can properly 
	#add cards to the next hand
	def end_turn(self):
		if globe.DEBUG:
			print("end-START",flush = True)
		trigger.all(trigger.END_TURN,[],self,immediate = True)
		globe.boss.clear_queue()
		self.triggers = []
		self.gain_redirect = []
		self.discount_on_sv = 0
		for c in self.played.played_this_turn:
			c.end_of_turn()
		self.discard_hand()
		#used so that cards can choose how many cards to draw next turn or add a card to the enxt hand
		#must be before played.turn_end and after self.discard_hand
		#This should follow the trigger model, but unfortunatly i am removing triggers before here
		for c in self.played.played_this_turn:
			c.next_turn()
		#empties cards in play_and returns them to their pile.
		#must be before persona.reset()
		self.played.turn_end()
		self.persona.reset()
		#must be after persona.reset for abilities like wonder woman
		self.gained_this_turn = []
		self.discarded_this_turn = []
		self.draw_card(num=5, from_card = False,should_trigger = False)

		#Updates the players score at the end of each of their turns
		self.calculate_vp()


	def calculate_vp(self):
		#Puts all the cards owned by the palyer (and to be counted for VP)
		#in one lsit for easy calculation
		assemble = []
		assemble.extend(self.deck.contents)
		assemble.extend(self.discard.contents)
		assemble.extend(self.hand.contents)
		assemble.extend(self.played.contents)
		assemble.extend(self.ongoing.contents)
		vp = 0
		for c in assemble:
			vp += c.calculate_vp(assemble)
		#add the vp tokens
		self.score = vp + self.vp
		return self.score


"""
model as in from model/view/controler
Controls the game board
global.boss refers to the instantiation of this object, which is probably bad practise, but so niice
#This object contains the game loop
"""
class model:
	#all global piles
	main_deck = None
	weakness_stack = None
	kick_stack = None
	supervillain_stack = None
	lineup = None
	destroyed_stack = None

	#This list of players in the match
	players = []
	player_score = []
	
	#I do not belive this is used
	#can set code here to be ran at the begining of each players turn
	notify = None
	#Check if game is still ongoing
	game_ongoing = False
	#Tracks whoes turn it is
	whose_turn = 0
	#All the avalable personas ensures that the players cannot choose duplicate
	persona_list = []
	#for statistics
	turn_number = 0
	#For error checking/debugging
	dupe_checker = None
	#Triggered affects will not run right away
	trigger_queue = None

	#initialize Game
	def __init__(self,number_of_players=2):
		self.players = []
		self.player_score = []
		#all piles assembled and initialized with the deck_builder
		self.main_deck = pile("Main Deck")
		self.main_deck.contents = deck_builder.initialize_deck()
		self.weakness_stack = pile("Weakness Stack")
		self.weakness_stack.contents = deck_builder.initialize_weaknesses()
		self.kick_stack = pile("Kick Stack")
		self.kick_stack.contents = deck_builder.initialize_kicks()
		self.supervillain_stack = supervillain_pile("SV Stack")
		self.supervillain_stack.contents = deck_builder.initialize_supervillains()
		self.supervillain_stack.current_sv = self.supervillain_stack.contents[-1]

		self.lineup = pile("Linup")
		self.destroyed_stack = pile("Destroyed")
		self.persona_list = deck_builder.get_personas()

		self.trigger_queue = []

		#starts the line-up
		for c in range(5):
			card_to_add = self.main_deck.draw()
			card_to_add.set_owner(owners.LINEUP)
			self.lineup.add(card_to_add)

		#Now we load the players!
		#any amount can technically be added, but large amounts may not be graphically compatable
		#right now this is hard coded

		
		invisible = globe.CPU_TERMINAL_INVISIBLE
		pid = 0

		#player initialization
		#There is a loop, where the player needs the controler and the conroler needs the player
		#Which is why contolers are set as 'None' and then manually set
		#increments pid
		#avalable contolers are:
		#cpu
		#cpu_greedy (a worse cpu, buys the cheepest cards)
		#human -the original terminal based controler
		#human_view -Only works with window.py.  Gets input from the window.

		#more cpus can be added
		#each new view should have a coresponding new controler to get input
		#(althought the view can be made before the contoler, and the terminal
		#controler can be used for testing, which is nice)

		new_player = player(pid,None)
		new_controler = controlers.human_view(new_player,invisible)
		new_player.controler = new_controler
		self.players.append(new_player)
		pid += 1

		new_player = player(pid,None)
		new_controler = controlers.cpu(new_player,invisible)
		new_player.controler = new_controler
		self.players.append(new_player)
		pid += 1

		new_player = player(pid,None)
		new_controler = controlers.cpu(new_player,invisible)
		new_player.controler = new_controler
		self.players.append(new_player)
		pid += 1

		new_player = player(pid,None)
		new_controler = controlers.cpu(new_player,invisible)
		new_player.controler = new_controler
		self.players.append(new_player)
		pid += 1

	#asks each player what their persona shall be
	#starting player can be set by changing whos turn
	def choose_personas(self):
		for i,p in enumerate(self.players):
			p.choose_persona(self.persona_list)
			if globe.DEBUG:
				print(f"{i} choose {p.persona.name}")
			if p.persona.name == "The Flash":
				self.whose_turn = i

	#This has not been fully adopted
	def get_current_player(self):
		if self.whose_turn == -1:
			return None
		else:
			return self.players[self.whose_turn]

	#starts and runs the game loop
	def start_game(self):
		self.dupe_checker = error_checker.dupe_checker()
		#sets up personas in-game
		#with certain views, this should be set beforhand
		self.choose_personas()

		#We are going to keep track of which end condition has been met
		#'regular' refers to beating all of the SV's
		end_reason = "regular"
		check_result = None
		try:
			#TODO: test alternate way to end game not based on supervillain stack
			self.game_ongoing = True
			#The game ends when the supervaillin stack is empty
			while self.supervillain_stack.get_count() > 0:
			#while self.game_ongoing:
				#if self.supervillain_stack.get_count() == 0:
				#	self.game_ongoing = False
				#Tracks the number of turns
				self.turn_number += 1
				if self.notify != None:
					self.notify()

				if globe.DEBUG:
					print(f"{self.players[self.whose_turn].persona.name}'s' turn")

				current_turn = self.players[self.whose_turn]

				#Sets up SV's Stack ongoing
				if len(self.supervillain_stack.contents) > 0 \
						and self.supervillain_stack.current_sv.has_stack_ongoing:
					self.supervillain_stack.current_sv.stack_ongoing(current_turn)

				#run the players turn
				current_turn.turn()

				save_whose_turn = self.whose_turn
				check_result = self.dupe_checker.check()
				if check_result[0]:
					raise DupeFailure({"msg":check_result[1]})
				#It's between turns for the SV attack
				self.whose_turn = -1

				#Ends the players turn.  I dont rememebr why this is done seperatly
				current_turn.end_turn()

				#refills the line-up
				#if the main deck runs out, the game is also over
				#unfortunatly if the main decks runs out because of a card (like pandoras box)
				#The game dosnt end until the end of their turn, when it tried to refil, which is not acurat
				for i in range(max(5 - self.lineup.size(),0)):
					card_to_add = self.main_deck.draw()
					card_to_add.set_owner(owners.LINEUP)
					self.lineup.add(card_to_add)

				#If there is a new superviallin on top of it's stack, then First Apearance!
				if self.supervillain_stack.get_count() > 0 \
						and self.supervillain_stack.current_sv != self.supervillain_stack.contents[-1]:
					self.supervillain_stack.current_sv = self.supervillain_stack.contents[-1]
					#first apearance attack
					self.supervillain_stack.current_sv.first_apearance()
					
				#sets who is going to play next
				self.whose_turn = save_whose_turn + 1
				if self.whose_turn >= len(self.players):
					self.whose_turn = 0
		#If the main deck has ran out, the game is over, with an alternative end condition
		except MainDeckEmpty:
			print("Main Deck Ran Out!",flush = True)
			end_reason = "main_deck"
		except DupeFailure as e:
			print("Duplicate or unmatched found",flush = True)
			details = e.args[0]
			print(details["msg"],flush = True)
			output_persona_stats(self.players,"crash",details["msg"])
			return

		#the game has ended, calculate vp (things may have changed since they last 
		#calulated their vp at the end of their turn)
		for p in self.players:
			self.player_score.append(p.calculate_vp())

		output_persona_stats(self.players,end_reason)

	def register(self,func):
		self.notify = func

	def clear_queue(self):
		if globe.DEBUG:
			print("start clear",flush = True)
		while len(self.trigger_queue) > 0:
			self.trigger_queue.pop(0).run()
		if globe.DEBUG:
			print("end clear",flush = True)


#just forwards with function
def choose_sets():
	deck_builder.choose_sets()

def output_persona_stats(players,end_type,report = "empty"):
	f = open("output2.csv","a+")
	base = False
	hu = False
	fe = False
	tt = False
	crossover_1 = False
	crossover_2 = False
	for d in deck_builder.choosen_sets:
		if d.name == "Base set":
			base = True
		elif d.name == "Forever Evil":
			fe = True
		elif d.name == "Crossover 1, Justice Society of America":
			crossover_1 = True
	ordered_players = sorted(players, key=lambda x: x.score, reverse=True)
	line = f"0,{base},{hu},{fe},{tt},{crossover_1},{crossover_2}"
	for p in ordered_players:
		line += f",{p.persona.name},{p.score}"
	line += f",{end_type}\n"
	f.write(line)
	f.close() 
	if end_type == "crash":
		f = open("crash_log.txt","a+")
		f.write(report+"\n\n\n\n\n\n")
		f.close() 