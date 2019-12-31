from constants import cardtype
from constants import owners
import effects
from constants import option
import globe
from constants import ai_hint
import random
import arcade
from frames import actions
from frames import card_frame
from frames import persona_frame
from constants import trigger



#Done
class citizen_steel(card_frame.card):
	name = "Citizen Steel"
	vp = 1
	cost = 5
	ctype = cardtype.HERO
	text = "Draw a card.\nSuper-Villains cost you 1 less to defeat this turn\nfor each Punch you play or have played this turn."
	image = "crossover_1/images/cards/Citizen Steel 5.jpg"
	total_discount = 0

	def triggerSV(self,ttype,data,player,active,immediate):
		if globe.DEBUG:
			print("test",self.name,flush=True)
		if trigger.test(immediate,\
						trigger.PRICE, \
						self.triggerSV, \
						player,ttype) \
				and data[1].owner_type == owners.VILLAINDECK:
			if globe.DEBUG:
				print("active",self.name,flush=True)
			return data[0] - self.total_discount

	def trigger(self,ttype,data,player,active,immediate):
		if globe.DEBUG:
			print("test",self.name,flush=True)
		if trigger.test(not immediate,\
						trigger.PLAY, \
						self.trigger, \
						player,ttype) \
				and data[0].name == "Punch":
			self.total_discount += 1
	
	
	def play_action(self,player):
		player.draw_card()
		count = 0
		for c in player.played.played_this_turn:
			if c.name == "Punch":
				count += 1
		self.total_discount = count
		player.triggers.append(self.trigger)
		player.triggers.append(self.triggerSV)
		return 0


#done
class dr_mid_nite(card_frame.card):
	name = "Dr. Mid-Nite"
	vp = 1
	cost = 4
	ctype = cardtype.HERO
	text = "+2 Power\nLook at the top two cards of your deck. You may\ndiscard any of them and put the rest back in\nany order."
	image = "crossover_1/images/cards/Dr Mid Nite 4.jpg"
	
	def play_action(self,player):
		player.played.plus_power(2)
		assemble = []
		for i in range(2):
			to_add = player.reveal_card(public = False)
			if to_add != None:
				assemble.append(to_add)
				player.deck.contents.pop()
		if len(assemble) > 0:
			result = effects.choose_however_many("Choose any number to discard",player,assemble,ai_hint.IFBAD)
			if result != None:
				for c in result:
					player.deck.contents.append(c)
					player.discard_a_card(c)
					assemble.remove(c)

		total_times = len(assemble)
		while len(assemble) > 0:
			result = effects.choose_one_of(f"Place card back on top of your deck ({total_times - len(assemble) + 1}/{total_times})?",player,assemble,ai_hint.WORST)
			assemble.remove(result)
			player.deck.contents.append(result)
		return 0

#Done
class girl_power(card_frame.card):
	name = "Girl Power"
	vp = 1
	cost = 5
	ctype = cardtype.SUPERPOWER
	defense = True
	text = "+2 Power\nDefence:: You may reveal this card and discard\nit or a Punch to avoid an Attack. If you do,\ndraw a card."
	image = "crossover_1/images/cards/Girl Power 5.jpg"
	
	def play_action(self,player):
		player.played.plus_power(2)
		return 0

	def defend(self,attacker = None,defender = None):
		punch = None
		for c in self.owner.hand.contents:
			if c.name == "Punch":
				punch = c
		if punch != None:
			if effects.ok_or_no("Would you like to discard one of your Punch cards?\nIf not, Girl Power will be discarded.",self.owner,self,ai_hint.ALWAYS):
				self.owner.discard_a_card(punch)
				self.owner.draw_card()
				return
		self.owner.discard_a_card(self)
		self.owner.draw_card()
		return

#done
class liberty_belle(card_frame.card):
	name = "Liberty Belle"
	vp = 1
	cost = 3
	ctype = cardtype.HERO
	defense = True
	text = "+2 Power\nDefence:: You may discard this card to avoid an\nAttack. If you do, draw three cards and put two\ncards from your hand on top of your deck."
	image = "crossover_1/images/cards/Liberty Belle 3.jpg"
	
	def play_action(self,player):
		player.played.plus_power(2)
		return 0

	def defend(self,attacker = None,defender = None):
		self.owner.discard_a_card(self)
		self.owner.draw_card(3)
		for i in range(2):
			instruction_text = f"Choose a card to put on top your deck ({i+1}/2)."
			if len(self.owner.hand.contents) > 0:
				result = effects.choose_one_of(instruction_text,self.owner,self.owner.hand.contents,ai_hint.WORST)
				result.pop_self()
				self.owner.deck.contents.append(result)
		return

class monument_point(card_frame.card):
	name = "Monument Point"
	vp = 2
	cost = 6
	ctype = cardtype.LOCATION
	text = "Ongoing: When you play your first Punch on each of your turns, draw a card."
	image = "crossover_1/images/cards/Monument Point 6.jpg"
	ongoing = True

	def trigger(self,ttype,data,player,active,immediate):
		if globe.DEBUG:
			print("test",self.name,flush=True)
		if trigger.test(not immediate,\
						trigger.PLAY, \
						self.trigger, \
						player,ttype) \
				and data[0].name == "Punch":
			if globe.DEBUG:
				print("active",self.name,flush=True)
			player.triggers.remove(self.trigger)
			player.draw_card()
			return True
	
	
	def play_action(self,player):
		if self in player.ongoing.contents:
			player.triggers.append(self.trigger)
		else:
			player.ongoing.add(self.pop_self())

			already_played = False
			for c in player.played.played_this_turn:
				if c.name == "Punch":
					already_played = True
			if not already_played:
				player.triggers.append(self.trigger)
		return 0

#done
class mystic_bolts(card_frame.card):
	name = "Mystic Bolts"
	vp = 2
	cost = 6
	ctype = cardtype.SUPERPOWER
	text = "+1 Power\nPut up to two cards each with cost 5 or less and\neach with a different cost from your discard pile\ninto your hand."
	image = "crossover_1/images/cards/Mystic Bolts 6.jpg"
	
	def play_action(self,player):
		player.played.plus_power(1)
		instruction_text = "Put up to two cards each with cost 5 or less and\neach with a different cost from your discard pile\ninto your hand. (1/2)"
		assemble = []
		for c in player.discard.contents:
			if c.cost <= 5:
				assemble.append(c)

		if len(assemble) > 0:
			result = effects.may_choose_one_of(instruction_text,player,assemble,ai_hint.BEST)
			if result != None:
				result.pop_self()
				player.hand.contents.append(result)
				assemble = []
				for c in player.discard.contents:
					if c.cost <= 5 and c.cost != result.cost:
						assemble.append(c)
				if len(assemble) > 0:
					instruction_text = "Put up to two cards each with cost 5 or less and\neach with a different cost from your discard pile\ninto your hand. (2/2)"
					result = effects.may_choose_one_of(instruction_text,player,assemble,ai_hint.BEST)
					if result != None:
						result.pop_self()
						player.hand.contents.append(result)
		return 0

#done
class per_degaton(card_frame.card):
	name = "Per Degaton"
	vp = 1
	cost = 5
	ctype = cardtype.VILLAIN
	text = "+2 Power\nDiscard any number of cards from your hand.\n+1 Power for each card you discard or have\ndiscarded this turn."
	image = "crossover_1/images/cards/Per Degaton 5.jpg"

	def trigger(self,ttype,data,player,active,immediate):
		if globe.DEBUG:
			print("test",self.name,flush=True)
		if trigger.test(not immediate,\
						trigger.DISCARD, \
						self.trigger, \
						player,ttype) \
				and data[0].name == "Punch":
			if globe.DEBUG:
				print("active",self.name,flush=True)
			player.played.plus_power(1)
	
	def play_action(self,player):
		player.played.plus_power(2)
		instruction_text = "Discard any number of cards from your hand.\n+1 Power for each card you discard or have\ndiscarded this turn."
		if len(player.hand.contents) > 0:
			result = effects.choose_however_many(instruction_text,player,player.hand.contents,ai_hint.IFBAD)
			if result != None:
				for c in result:
					player.discard_a_card(c)
		total_power = 2
		for c in player.discarded_this_turn:
			total_power += 1
		player.triggers.append(self.trigger)
		player.played.plus_power(total_power)
		return 0

#done
class scythe(card_frame.card):
	name = "Scythe"
	vp = 1
	cost = 3
	ctype = cardtype.VILLAIN
	text = "+2 Power"
	attack = True
	attack_text = "Attack:: Each foe gains a Weakness unless\nthey reveals a Starter from his hand."
	image = "crossover_1/images/cards/Scythe 3.jpg"
	
	def play_action(self,player):
		player.played.plus_power(2)
		self.attack_action(player)
		return 0

	def attack_action(self,by_player):
		for p in globe.boss.players:
			if p != by_player and effects.attack(p,self,by_player):
				has_starter = False
				for c in p.hand.contents:
					if c.ctype_eq(cardtype.STARTER):
						has_starter = True
				if not has_starter:
					p.gain_a_weakness()
		return

#done
class t_spheres(card_frame.card):
	name = "T-Spheres"
	vp = 2
	cost = 6
	ctype = cardtype.EQUIPMENT
	text = "+2 Power\nChoose a card name. Reveal the top three cards of\nyour deck. Put all cards with that name into your\nhand and the rest on top in any order"
	image = "crossover_1/images/cards/T Spheres 6.jpg"
	
	def play_action(self,player):
		player.played.plus_power(2)
		assemble_names = set()
		assemble = []
		grand_assemble = []
		grand_assemble.extend(player.deck.contents)
		grand_assemble.extend(player.under_superhero.contents)
		grand_assemble.extend(player.over_superhero.contents)
		grand_assemble.extend(player.discard.contents)
		grand_assemble.extend(player.hand.contents)
		grand_assemble.extend(player.played.contents)
		for c in grand_assemble:
			if not c.name in assemble_names:
				assemble_names.add(c.name)
				assemble.append(c)
		chosen_name = ""
		if len(assemble) > 0:
			result = effects.choose_one_of("Choose a card name.\nReveal the top three cards of your deck\nand put any cards with that name into\nyour hand.",player,assemble,ai_hint.RANDOM)
			chosen_name = result.name

		revealed = []
		for i in range(3):
			revealing = player.reveal_card(public = False)
			if revealing != None:
				revealing.pop_self()
				revealed.append(revealing)
		if len(revealed) > 0:
			effects.reveal(f"These were on top of {player.persona.name}'s deck",player,revealed)
		for c in revealed.copy():
			if c.name == chosen_name:
				player.hand.contents.append(c)
				revealed.remove(c)
		while len(revealed) > 0:
			result = effects.choose_one_of("Put one of the revealed cards on top of your deck",player,revealed,ai_hint.WORST)
			player.deck.contents.append(result)
			revealed.remove(result)
		return 0

#done
#A rule clarrification says "that is still in play" when the card is moved
class the_hourglass(card_frame.card):
	name = "The Hourglass"
	vp = 1
	cost = 4
	ctype = cardtype.EQUIPMENT
	text = "Choose another card with cost 6 or less you\nplayed this turn. At the end of turn, put that card\ninto your hand. (If it is yours and still in play)"
	image = "crossover_1/images/cards/The Hourglass 4.jpg"
	card_choosen = None
	played_by = None

	def next_turn(self):
		if self.played_by != None \
				and self.card_choosen.owner == self.played_by \
				and (self.card_choosen.find_self()[0] == self.played_by.played \
				or self.card_choosen.find_self()[0] == self.played_by.discard):
			self.played_by.hand.contents.append(self.card_choosen.pop_self())
		else:
			if globe.DEBUG:
				print("The Hourglass could not be found.",flush = True)
		self.card_choosen = None
		self.played_by = None

	
	def play_action(self,player):
		assemble = []
		for c in player.played.contents:
			if c.cost <= 6 and c != self:
				assemble.append(c)
		if len(assemble) > 0:
			result = effects.choose_one_of("Choose a card to have in your hand next turn.",player,assemble,ai_hint.BEST)
			self.played_by = player
			self.card_choosen = result
		return 0


#SVs
class eclipso(card_frame.card):
	name = "Eclipso"
	vp = 7
	cost = 14
	ctype = cardtype.VILLAIN
	owner_type = owners.VILLAINDECK
	text = "You are considered to have the game text of each foe's Super Hero.\nEach foe discards the top card of his deck. You may play each of the\ndiscarded cards this turn, and then return them to their discard piles."
	attack_text = "First Appearance - Attack: Each player discards a card for each Villain in his hand."
	image = "crossover_1/images/cards/Eclipso 14.jpg"
	save_persona = None
	discarded_cards = []
	action = None

	def special_action_click(self,player):
		#if len(self.discarded_cards) > 0:
		result = False
		while result != None and len(self.discarded_cards) > 0:
			result = effects.may_choose_one_of("Choose a card to play",player,self.discarded_cards,ai_hint.BEST)
			if result != None:
				save_place = result.find_self()[0]
				result.pop_self()
				player.play_and_return(result,save_place)
				self.discarded_cards.remove(result)
		if len(self.discarded_cards) == 0:
			player.played.special_options.remove(self.action)

	def play_action(self,player):
		self.discarded_cards = []
		self.save_persona = persona_frame.dispatch(player)
		for p in globe.boss.players:
			if p != player:
				card_to_discard = p.reveal_card(public = False)
				if card_to_discard != None:
					self.discarded_cards.append(card_to_discard)
					p.discard_a_card(card_to_discard)
		if len(self.discarded_cards) > 0:
			self.action = actions.special_action("Eclipso",self.special_action_click)
			player.played.special_options.append(self.action)
		return 0

	def end_of_turn(self):
		self.save_persona.restore()
		self.save_persona = None

	def first_apearance(self):
		for p in globe.boss.players:
			if effects.attack(p,self):
				#effects.reveal(f"This was {p.persona.name}'s hand",p,p.hand.contents)
				num_heros = p.hand.get_count(cardtype.VILLAIN)
				for i in range(num_heros):
					instruction_text = f"You had {num_heros} heros in you hand.  Choose a card to discard ({i+1}/{num_heros})"
					if p.hand.size() > 0:
						choose = effects.choose_one_of(instruction_text,p,p.hand.contents,ai_hint.WORST)
						p.discard_a_card(choose)
		return


#SVs
class gentleman_ghost(card_frame.card):
	name = "Gentleman Ghost"
	vp = 6
	cost = 13
	ctype = cardtype.VILLAIN
	owner_type = owners.VILLAINDECK
	text = "Put all cards with cost 0 from your discard pile into your hand. Then,\nyou may pass a card from your hand into the discard pile of each foe."
	attack_text = "First Appearance - Attack: Each player destroys two different cards with cost 1 or greater in his discard pile."
	image = "crossover_1/images/cards/Gentleman Ghost 13.jpg"
	
	def play_action(self,player):
		for c in player.discard.contents.copy():
			if c.cost == 0:
				c.pop_self()
				player.hand.contents.append(c)

		for p in globe.boss.players:
			if p != player:
				if len(player.hand.contents) > 0:
					instruction_text = f"You may pass a card from your hand into the discard of {p.persona.name}"
					result = effects.may_choose_one_of(instruction_text,player,player.hand.contents,ai_hint.IFBAD)
					if result != None:
						result.pop_self()
						result.set_owner(p)
						p.discard.contents.append(result)

		return 0

	def first_apearance(self):
		for p in globe.boss.players:
			if effects.attack(p,self):
				assemble = []
				for c in p.discard.contents:
					if c.cost >= 1:
						assemble.append(c) 
				if len(assemble) > 0:
					instruction_text = "Destory a card with cost 1 or greater in your discard pile (1/2)."
					result = effects.choose_one_of(instruction_text,p,assemble,ai_hint.WORST)
					result.destroy(p)
					assemble = []
					for c in p.discard.contents:
						#two different cards?
						if c.cost >= 1 and c.name != result.name:
							assemble.append(c)
					if len(assemble) > 0:
						instruction_text = "Destory a card with cost 1 or greater in your discard pile (2/2)."
						result = effects.choose_one_of(instruction_text,p,assemble,ai_hint.WORST)
						result.destroy(p)

		return

class gog(card_frame.card):
	name = "Gog"
	vp = 7
	cost = 15
	ctype = cardtype.VILLAIN
	owner_type = owners.VILLAINDECK
	text = "Stack Ongling:: At the start of each player's turn, he discards a\ncard unless he destroys a card in his discard pile."
	attack_text = "First Appearance - Attack: Each player discards a random\ncard. The player(s) that discarded the card with the highest cost\ndiscard an additional card."
	image = "crossover_1/images/cards/Gog 15.jpg"
	has_stack_ongoing = True

	def stack_ongoing(self,player):
		destroyed_a_card = False
		if len(player.discard.contents) > 0:
			instruction_text = "Stack Ongoing: You may destroy a card in your discard pile.\n(If you do not, you will discard a card)."
			result = effects.may_choose_one_of(instruction_text,player,player.discard.contents,ai_hint.IFBAD)
			if result != None:
				result.destroy(player)
				destroyed_a_card = True

		if not destroyed_a_card:
			if len(player.hand.contents) > 0:
				result = effects.choose_one_of("Stack Ongoing: Discard a card.",player,player.hand.contents,ai_hint.WORST)
				player.discard_a_card(result)
	
	

	def first_apearance(self):
		discarded = {}
		highest_cost = -1
		for p in globe.boss.players:
			if effects.attack(p,self):
				if len(p.hand.contents) > 0:
					card_to_discard = random.choice(p.hand.contents)
					discarded[p] = card_to_discard
					p.discard_a_card(card_to_discard)
					if card_to_discard.cost > highest_cost:
						highest_cost += 1

		for p in discarded:
			if discarded[p].cost == highest_cost:
				p.discard_a_card(random.choice(p.hand.contents))
		return

#done
class icicle(card_frame.card):
	name = "Icicle"
	vp = 5
	cost = 10
	ctype = cardtype.VILLAIN
	owner_type = owners.VILLAINDECK
	text = "+3 Power and choose a foe.\nThat foe flips his super Hero face down until the end of his next turn."
	attack_text = "First Appearance - Attack: Each player gains a Weakness\nfor each Hero in the Line-up."
	image = "crossover_1/images/cards/Icicle 10.jpg"

	#Should not matter if it's immedaite or not
	#preferably i dont run this twise
	def trigger(self,ttype,data,player,active,immediate):
		if globe.DEBUG:
			print("test",self.name,flush=True)
		if trigger.test(not immediate,\
						trigger.END_TURN, \
						self.trigger, \
						player,ttype):
			if globe.DEBUG:
				print("active",self.name,flush=True)
			player.persona.active = True


	def play_action(self,player):
		player.played.plus_power(3)
		instruction_text = "Choose a foe. That foe flips his super Hero face down until the end of his next turn."
		result = effects.choose_a_player(instruction_text,player,includes_self = False,hint = ai_hint.WORST)
		#If their persona is already not active, we dont want to be able to affect it at all
		if result.persona.active:
			result.persona.active = False
			result.triggers.append(self.trigger)
		return 0

	def first_apearance(self):
		heros_in_lineup = globe.boss.lineup.get_count(cardtype.HERO)
		for p in globe.boss.players:
			if effects.attack(p,self):
				for i in range(heros_in_lineup):
					p.gain_a_weakness()
		return


#Done
class kobra(card_frame.card):
	name = "Kobra"
	vp = 6
	cost = 11
	ctype = cardtype.VILLAIN
	owner_type = owners.VILLAINDECK
	text = "Draw four cards, and then discard two of those cards."
	attack_text = "First Appearance - Attack: Each player reveals the\ntop five cards of his deck and discards all cards with cost\n1 or greater. Put the rest back in any order."
	image = "crossover_1/images/cards/Kobra 11.jpg"


	def play_action(self,player):
		player.draw_card(4)
		for i in range(2):
			instruction_text = f"Discard a card. ({i+1}/2)"
			result = effects.choose_one_of(instruction_text,player,player.hand.contents,ai_hint.WORST)
			player.discard_a_card(result)
		return 0

	def first_apearance(self):
		for p in globe.boss.players:
			if effects.attack(p,self):
				revealed = []
				for i in range(5):
					to_reveal = p.reveal_card(public = False)
					if to_reveal != None:
						revealed.append(to_reveal)
						to_reveal.pop_self()
				effects.reveal(f"These were on the top of {p.persona.name}'s deck.",p,revealed)
				for c in revealed.copy():
					if c.cost >= 1:
						#put back into deck so that it is  discarded from a place
						p.deck.contents.append(c)
						p.discard_a_card(c)
						revealed.remove(c)
				while len(revealed) > 0:
					result = effects.choose_one_of("Put cards back on top of your deck",p,revealed,ai_hint.WORST)
					p.deck.contents.append(result)
					revealed.remove(result)
		return

class mordru_the_merciless(card_frame.card):
	name = "Mordru The Merciless"
	vp = 5
	cost = 9
	ctype = cardtype.VILLAIN
	owner_type = owners.VILLAINDECK
	text = "+3 Power\nYou may shuffle all cards with cost 1 or greater from your discard pile into your deck."
	attack_text = "First Appearance - Attack: Each player discards a card\nwith cost 3 or greater."
	image = "crossover_1/images/cards/Mordru The Merciless 9.jpg"


	def play_action(self,player):
		player.played.plus_power(3)
		instruction_text = "Would you like to shuffle all cards from your\ndiscard pile with cost 1 or greater into your deck."
		if effects.ok_or_no(instruction_text,player,self,ai_hint.ALWAYS):
			for c in player.discard.contents.copy():
				if c.cost >= 1:
					c.pop_self()
					player.deck.contents.append(c)
			random.shuffle(player.deck.contents)
		return 0

	def first_apearance(self):
		for p in globe.boss.players:
			if effects.attack(p,self):
				assemble = []
				for c in p.hand.contents:
					if c.cost >= 3:
						assemble.append(c)
				if len(assemble) > 0:
					result = effects.choose_one_of("Choose a card with cost 3 or greater to discard",p,assemble,ai_hint.WORST)
					p.discard_a_card(result)
		return


class solomon_grundy(card_frame.card):
	name = "Solomon Grundy"
	vp = '*'
	cost = 8
	ctype = cardtype.VILLAIN
	owner_type = owners.VILLAINDECK
	text = "+3 Power\nStack Ongoing:: Solomon Frundy can't be defeated unless you played a\nStarter this turn.\nAt the end of the game, Solomon Grundy is worth !VP for each Starter in your deck."
	image = "crossover_1/images/cards/Solomon Grundy 8.jpg"
	has_stack_ongoing = True
	played_starter = False

	def play_action(self,player):
		player.played.plus_power(3)
		return 0

	def trigger(self,ttype,data,player,active,immediate):
		if globe.DEBUG:
			print("test",self.name,flush=True)
		if trigger.test(not immediate,\
						trigger.PLAY, \
						self.trigger, \
						player,ttype) \
				and data[0].ctype_eq(cardtype.STARTER):
			if globe.DEBUG:
				print("active",self.name,flush=True)
			self.played_starter = True
			player.triggers.remove(self.trigger)



	def stack_ongoing(self,player):
		self.played_starter = False
		player.triggers.append(self.trigger)

	#cannot be bought unless a starter has been played
	def buy_action(self,player,bought,defeat):
		if defeat:
			return self.played_starter
		else:
			return True

	def calculate_vp(self,all_cards):
		amount_of_starters = 0
		for c in all_cards:
			#print(len(all_cards),c,all_cards,flush = True)
			#print(c.name,flush = True)
			if c.ctype_eq(cardtype.STARTER):
				amount_of_starters += 1
		return amount_of_starters


class ultra_humanite(card_frame.card):
	name = "Ultra-Humanite"
	vp = 6
	cost = 12
	ctype = cardtype.VILLAIN
	owner_type = owners.VILLAINDECK
	text = "+2 Power\nPut any number of cards from your hand on the bottom of your deck,\nand then draw that many cards."
	attack_text = "First Appearance - Attack: Each player gains two Weakness\ncards and puts them on the bottom of his deck."
	image = "crossover_1/images/cards/Ultra Humanite 12.jpg"


	def play_action(self,player):
		player.played.plus_power(2)
		if len(player.hand.contents) > 0:
			result = effects.choose_however_many("Choose any number of cards to put on the bottom of your deck.\nYou will draw that many cards.",player,player.hand.contents,ai_hint.IFBAD)
			if result != None:
				for c in result:
					c.pop_self()
					player.deck.contents.insert(0,c)
				player.draw_card(len(result))
		return 0

	def first_apearance(self):
		for p in globe.boss.players:
			if effects.attack(p,self):
				for i in range(2):
					if p.gain_a_weakness():
						already_moved = False
						for c in p.discard.contents.copy():
							if not already_moved and c.name == "Weakness":
								c.pop_self()
								p.deck.contents.insert(0,c)
								already_moved = True
		return







