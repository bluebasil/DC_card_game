#Constants
import random
import cardtype
import visibilities
import owners
import controlers
import effects
import deck_builder
import globe
import ai_hint


class pile:
	#List of cards
	contents = None
	visibility = visibilities.PUBLIC
	owner = None

	#I'll start the deck empty
	def __init__(self,owner = None,visibility = visibilities.PUBLIC):
		self.owner = owner
		self.visibility = visibility
		self.contents = []

	def shuffle(self):
		random.shuffle(self.contents)

	def size(self):
		return len(self.contents) 

	def can_draw(self):
		if self.size() > 0:
			return True
		else:
			return False

	def draw(self):
		if len(self.contents) > 0:
			return self.contents.pop()
		else:
			return None

	def add(self,card):
		self.contents.append(card)

	def add_bottom(self,card):
		self.contents.insert(0,card)

	def get_count(self,find_type = cardtype.ANY):
		if find_type == cardtype.ANY:
			return self.size()
		else:
			#if self.visibility == visibilities.PUBLIC \
			#	or (self.visibility == visibilities.PRIVATE and self.owner.pid = pid)
			count = 0
			for c in self.contents:
				if c.ctype == find_type:
					count += 1
			return count

class playing(pile):
	power = 0
	card_mods = []
	double_modifier = 0
	played_this_turn = []

	def no_mod(self,card,player):
		return card.play_action(player)

	def __init__(self,owner = None,visibility = visibilities.PUBLIC):
		self.owner = owner
		self.visibility = visibility
		self.contents = []
		self.played_this_turn = []
		self.card_mods = [self.no_mod]


	def turn_end(self):
		self.power = 0
		self.played_this_turn = []
		self.card_mods = [self.no_mod]

		#self.owner.persona.set_modifiers()
		self.double_modifier = 0
		while self.size() > 0:
			c = self.contents.pop()
			if c.owner_type == owners.PLAYER:
				c.owner.discard.add(c)
			elif c.owner_type == owners.MAINDECK:
				globe.boss.main_deck.add(c)
			elif c.owner_type == owners.LINEUP:
				globe.boss.lineup.add(c)
			elif c.owner_type == owners.VILLAINDECK:
				globe.boss.supervillain_stack.add(c)

	def add(self,card):
		self.play(card)


	def play(self,card,ongoing = False):
		if not ongoing:
			card.times_played += 1
			self.contents.append(card)
		modifier = 0

		# SO that the mods can delete themselves afterwards
		assemble = []
		for mod in self.card_mods:
			assemble.append(mod)

		for mod in assemble:
			modifier += mod(card,self.owner)
		#modifier = card.play_action(self.owner)
		#modifier = post_power()

		for i in range(self.double_modifier):
			modifier *= 2

		#print("MOD WAS",modifier)
		self.power += modifier
		if not ongoing:
			self.played_this_turn.append(card)
		#print("PLAYED!", self.power, self)

	def parallax_double(self):
		self.power *= 2
		self.double_modifier += 1

	def plus_power(self,power):
		for i in range(self.double_modifier):
			power *= 2
		self.power += power


class ongoing_pile(pile):

	def begin_turn(self):
		for c in self.contents:
			self.owner.played.play(c,True)

class supervillain_pile(pile):
	current_sv = None

class player:
	pid = -1
	deck = None
	hand = None
	discard = None
	ongoing = None
	played = None
	controler = None
	persona = None
	under_superhero = None

	gain_redirect = []
	gained_this_turn = []
	discount_on_sv = 0
	played_riddler = False
	sv_bought_this_turn = False

	def __init__(self,pid, controler):
		self.controler = controler
		self.pid = pid
		self.deck = pile(self, visibilities.SECRET)
		self.hand = pile(self, visibilities.PRIVATE)
		self.discard = pile(self)
		self.under_superhero = pile(self)
		self.ongoing = ongoing_pile(self)
		self.played = playing(self)

		#These should be reinitialized or they share values with all insatnces
		self.gain_redirect = []
		self.gained_this_turn = []

		self.deck.contents = deck_builder.get_starting_deck(self)
		self.discard.contents = deck_builder.debug_discard(self)

		for i in range(8):
			self.hand.add(self.deck.draw())

	def choose_persona(self,persona_list):
		self.persona = self.controler.choose_persona(persona_list)
		persona_list.remove(self.persona)
		self.persona = self.persona(self)
		self.persona.reset()

	def turn(self):
		self.persona.ready()
		self.ongoing.begin_turn()
		self.controler.turn()
		self.end_turn()

	def draw_card(self):
		if not self.manage_reveal():
			return None
		drawn_card = self.deck.draw()
		self.hand.add(drawn_card)
		self.persona.draw_power()

		return drawn_card

	def reveal_card(self):
		if not self.manage_reveal():
			return None
		return self.deck.contents[-1]

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

	def play(self, cardnum):
		self.played.play(self.hand.contents.pop(cardnum))

	def play_and_return(self, card, pile):
		self.played.play(card)
		self.played.contents.remove(card)
		pile.add(card)

	def buy_supervillain(self):
		if globe.boss.supervillain_stack.current_sv == globe.boss.supervillain_stack.contents[-1] \
				and self.played.power >= globe.boss.supervillain_stack.contents[-1].cost - self.discount_on_sv:
			if globe.DEBUG:
				print(f" {globe.boss.supervillain_stack.contents[-1].name} bought")
			self.sv_bought_this_turn = True
			self.played.power -= globe.boss.supervillain_stack.contents[-1].cost - self.discount_on_sv
			self.gain(globe.boss.supervillain_stack.contents.pop())
			return True
		return False

	def buy_kick(self):
		if globe.boss.kick_stack.size() > 0 and self.played.power >= globe.boss.kick_stack.contents[-1].cost:
			if globe.DEBUG:
				print(f"kick bought")
			globe.boss.kick_stack.contents[-1].bought = True
			self.played.power -= globe.boss.kick_stack.contents[-1].cost
			self.gain(globe.boss.kick_stack.contents.pop())
			return True
		return False

	def riddle(self):
		if self.played_riddler and globe.boss.main_deck.size() > 0 and self.played.power >= 3:
			self.played.power -= 3
			self.gain(globe.boss.main_deck.contents.pop())
			return True
		return False

	def gain_a_weakness(self):
		if globe.boss.weakness_stack.size() > 0:
			self.gain(globe.boss.weakness_stack.contents.pop())
			return True
		return False

	def buy(self,cardnum):
		if cardnum < 0 or cardnum >= len(globe.boss.lineup.contents):
			return False
		elif self.played.power >= globe.boss.lineup.contents[cardnum].cost:
			globe.boss.lineup.contents[cardnum].bought = True
			if globe.DEBUG:
				print(f"{globe.boss.lineup.contents[cardnum]} bought")
			self.played.power -= globe.boss.lineup.contents[cardnum].cost
			self.gain(globe.boss.lineup.contents.pop(cardnum))
			return True
		return False

	def buy_c(self,card):
		if self.played.power >= card.cost:
			card.bought = True
			if globe.DEBUG:
				print(f"{card.name} bought")
			self.played.power -= card.cost
			self.gain(card.pop_self())
			return True
		return False

	def gain(self, card):
		card.set_owner(player=self)
		self.gained_this_turn.append(card)
		card.buy_action()

		redirected = False
		if len(self.gain_redirect) > 0:
			assemble = []
			for re in self.gain_redirect:
				assemble.append(re)


			for re in assemble:
				redirect_responce = re(self,card)
				if not redirected and redirect_responce[0]:
					redirect_responce[1].add(card)
					redirected = True


		if not redirected:
			self.discard.add(card)
		return
			

	def discard_hand(self):
		self.discard.contents.extend(self.hand.contents)
		self.hand.contents = []

	def end_turn(self):
		self.gain_redirect = []
		self.discount_on_sv = 0
		self.played_riddler = False
		for c in self.played.contents:
			c.end_of_turn()
		self.discard_hand()
		self.played.turn_end()
		self.persona.reset()
		self.gained_this_turn = []
		for i in range(5):
			self.draw_card()
		self.sv_bought_this_turn = False


	def calculate_vp(self):
		self.deck.contents.extend(self.discard.contents)
		self.deck.contents.extend(self.hand.contents)
		self.deck.contents.extend(self.played.contents)
		self.deck.contents.extend(self.ongoing.contents)
		vp = 0
		for c in self.deck.contents:
			vp += c.calculate_vp()
		return vp





class model:
	main_deck = None
	weakness_stack = None
	kick_stack = None
	supervillain_stack = None
	lineup = None
	players = []
	player_score = []
	destroyed_stack = None
	notify = None
	whose_turn = 0
	persona_list = []
	turn_number = 0

	#initialize Game
	def __init__(self,number_of_players=2):
		self.main_deck = pile()
		self.main_deck.contents = deck_builder.initialize_deck()
		self.weakness_stack = pile()
		self.weakness_stack.contents = deck_builder.initialize_weaknesses()
		self.kick_stack = pile()
		self.kick_stack.contents = deck_builder.initialize_kicks()
		self.supervillain_stack = supervillain_pile()
		self.supervillain_stack.contents = deck_builder.initialize_supervillains()
		self.supervillain_stack.current_sv = self.supervillain_stack.contents[-1]
		self.lineup = pile()
		self.destroyed_stack = pile()
		self.persona_list = deck_builder.get_personas()

		for c in range(8):
			self.lineup.add(self.main_deck.draw())

		#2 human players for initialization
		
		invisible = False

		#for i in range(4):
		#	new_player = player(i,None)
		#	new_controler = controlers.cpu(new_player,invisible)
		#	new_player.controler = new_controler
		#	self.players.append(new_player)

		new_player = player(0,None)
		new_controler = controlers.human(new_player,invisible)
		new_player.controler = new_controler
		self.players.append(new_player)

		new_player = player(1,None)
		new_controler = controlers.cpu(new_player,invisible)
		new_player.controler = new_controler
		self.players.append(new_player)

		new_player = player(2,None)
		new_controler = controlers.cpu_greedy(new_player,invisible)
		new_player.controler = new_controler
		self.players.append(new_player)

		new_player = player(3,None)
		new_controler = controlers.cpu_greedy(new_player,invisible)
		new_player.controler = new_controler
		self.players.append(new_player)

		new_player = player(4,None)
		new_controler = controlers.cpu_greedy(new_player,invisible)
		new_player.controler = new_controler
		self.players.append(new_player)


		new_player = player(5,None)
		new_controler = controlers.cpu_greedy(new_player,invisible)
		new_player.controler = new_controler
		self.players.append(new_player)


		# in range(2):
		#	new_player = player(player_id,None)
		#	new_controler = controlers.human(new_player)
		#	new_player.controler = new_controler
		#	self.players.append(new_player)

	def choose_personas(self):
		for i,p in enumerate(self.players):
			p.choose_persona(self.persona_list)
			print(f"{i} choose {p.persona.name}")
			if p.persona.name == "The Flash":
				self.whose_turn = i
		

	def start_game(self):
		self.choose_personas()
		while self.supervillain_stack.get_count() > 0:
			self.turn_number += 1
			if self.notify != None:
				self.notify()
			if globe.DEBUG:
				print(f"{self.whose_turn} turn")

			self.players[self.whose_turn].turn()

			if self.supervillain_stack.get_count() > 0 and \
					self.supervillain_stack.current_sv != self.supervillain_stack.contents[-1]:
				self.supervillain_stack.current_sv = self.supervillain_stack.contents[-1]
				#first apearance attack
				self.supervillain_stack.current_sv.first_apearance()
				

			for i in range(5 - self.lineup.size()):
				card_to_add = self.main_deck.draw()
				#The main deck is empty
				if card_to_add == None:
					print("MAIN DECK RAN OUT!")
					return
				else:
					card_to_add.owner_type = owners.LINEUP
				self.lineup.add(card_to_add)

			self.whose_turn += 1
			if self.whose_turn >= len(self.players):
				self.whose_turn = 0


		for p in self.players:
			self.player_score.append(p.calculate_vp())



	def register(self,func):
		self.notify = func

