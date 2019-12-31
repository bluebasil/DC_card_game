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


class arrows_bow(card_frame.card):
	name = "Arrow's Bow"
	vp = 1
	cost = 3
	ctype = cardtype.EQUIPMENT
	text = "You may put a random card from under your\nSuper Hero into your hand. if you choose not to,\n+2 Power"
	image = "crossover_2/images/cards/Arrows Bow 3.jpg"

	def play_action(self,player):

		if len(player.under_superhero.contents) > 0:
			instruction_text = "Would you like to put a random card from under\nyour superhero and put it into your hand?"
			if effects.ok_or_no(instruction_text,player,self,ai_hint.RANDOM):
				random_card = random.choice(player.under_superhero.contents)
				random_card.pop_self()
				player.hand.contents.append(random_card)
				return 0

		player.played.plus_power(2)
		return 0


class bronze_tiger(card_frame.card):
	name = "Bronze Tiger"
	vp = 2
	cost = 6
	ctype = cardtype.VILLAIN
	text = "+2 Power"
	attack_text = "Attack:: Each foe reveals a card from his hand and puts it\nunder his Super Hero.\nIf one or more foes does not reveal a card with cost 1 or\ngreater, draw two cards."
	image = "crossover_2/images/cards/Bronze Tiger 6.jpg"
	attack = True

	def play_action(self,player):
		player.played.plus_power(2)
		self.attack_action(player)
		return 0

	def attack_action(self,by_player):
		did_not_reveal_costly_card = False
		for p in globe.boss.players:
			if p != by_player and effects.attack(p,self,by_player):
				if len(p.hand.contents) > 0:
					instruction_text = f"Reveal a card to put under your Super Hero.\nIf one or more foes does not reveal a card with cost 1 or\ngreater, {by_player.persona.name} will draw two cards."
					result = effects.choose_one_of(instruction_text,p,p.hand.contents,ai_hint.WORST)
					if not result.cost >= 1:
						did_not_reveal_costly_card = True
					effects.reveal(f"This {result.name} will be under {p.persona.name}'s super hero",p,[result])
					result.pop_self()
					p.under_superhero.contents.append(result)
				else:
					did_not_reveal_costly_card = True
			#This is a rulebook specific ruling.  I had guessed that avoiding that attack did
			#not count towards not revealing a costly card, but the rulebook says it does
			else:
				did_not_reveal_costly_card = True
		if did_not_reveal_costly_card:
			by_player.draw_card(2)
		return


class collapsible_staff(card_frame.card):
	name = "Collapsible Staff"
	vp = 1
	cost = 4
	ctype = cardtype.EQUIPMENT
	text = "Draw a card. Gain all Villains in the Line-Up, and then put them under your Super Hero."
	image = "crossover_2/images/cards/Collapsible Staff 4.jpg"

	
	def play_action(self,player):
		player.draw_card()

		assemble = []
		for c in globe.boss.lineup.contents:
			if c.ctype_eq(cardtype.VILLAIN):
				assemble.append(c)
		for c in assemble:
			player.gain(c)
			c.pop_self()
			player.under_superhero.contents.append(c)
		return 0


class detective_lance(card_frame.card):
	name = "Detective Lance"
	vp = 2
	cost = 6
	ctype = cardtype.HERO
	text = "+3 Power\nName a card, and then look under any one foe's\nSuper Hero. Gain a card with that name from under\nthat Super Hero."
	image = "crossover_2/images/cards/Detective Lance 6.jpg"


	def play_action(self,player):
		player.played.plus_power(3)
		assemble_names = set()
		assemble = []
		grand_assemble = []
		for p in globe.boss.players:
			if p != player:
				grand_assemble.extend(p.deck.contents)
				grand_assemble.extend(p.under_superhero.contents)
				grand_assemble.extend(p.over_superhero.contents)
				grand_assemble.extend(p.discard.contents)
				grand_assemble.extend(p.hand.contents)
		for c in grand_assemble:
			if not c.name in assemble_names:
				assemble_names.add(c.name)
				assemble.append(c)
		chosen_name = ""
		if len(assemble) > 0:
			result = effects.choose_one_of("Choose a card name.\nThen choose a foe and gain a card with that name\nfrom under their Super Hero.",player,assemble,ai_hint.RANDOM)
			chosen_name = result.name

		instruction_text = f"Choose a player that you think has a {chosen_name}\nunder their super hero that you can gain."
		result = effects.choose_a_player(instruction_text,player,includes_self = False,hint = ai_hint.BEST)
		for c in result.under_superhero.contents:
			if c.name == chosen_name:
				player.gain(c)
				#dont want to get multiple
				return 0
		return 0



class explosive_arrow(card_frame.card):
	name = "Explosive Arrow"
	vp = 1
	cost = 2
	ctype = cardtype.EQUIPMENT
	text = "+1 Power and choose a foe"
	attack_text = "Attack:: Destroy a card under that foe's Super Hero,\nand then put this card under your Super Hero."
	image = "crossover_2/images/cards/Explosive Arrow.jpg"
	attack = True

	def play_action(self,player):
		player.played.plus_power(1)
		self.attack_action(player)
		return 0

	def attack_action(self,by_player):
		p = effects.choose_a_player("Choose a player.\nYou will destory a card under that players Super Hero.",by_player,includes_self = False,hint=ai_hint.BEST)
		if effects.attack(p,self,by_player):
			if len(p.under_superhero.contents) > 0:
				result = effects.choose_one_of(f"Choose a card to destory from uder {p.persona.name}'s Superhero",by_player,p.under_superhero.contents,ai_hint.BEST)
				result.destroy(p)
			self.pop_self()
			by_player.under_superhero.contents.append(self)


class huntress(card_frame.card):
	name = "Huntress"
	vp = 1
	cost = 5
	ctype = cardtype.VILLAIN
	text = "+2 Power\nYou may destroy a card in your hand or discaed\npile for each Villain you buy or gain this turn."
	image = "crossover_2/images/cards/Huntress 5.jpg"

	def trigger(self,ttype,data,player,active,immediate):
		if trigger.test(not immediate,\
						trigger.GAIN_CARD, \
						self.trigger, \
						player,ttype) \
				and data[1].ctype_eq(cardtype.VILLAIN):
			assemble = []
			assemble.extend(player.discard.contents)
			assemble.extend(player.hand.contents)
			if len(assemble) > 0:
				result = effects.may_choose_one_of("You may destory a card in your hand or disscard pile.",player,assemble,ai_hint.IFBAD)
				if result != None:
					result.destroy(player)


	def play_action(self,player):
		player.played.plus_power(2)
		player.triggers.append(self.trigger)
		return 0

class laurel_lance(card_frame.card):
	name = "Laurel Lance"
	vp = 1
	cost = 2
	ctype = cardtype.HERO
	text = "You may put a card from you hand under your\nSuper Hero. If you choose not to, you may put a\ncard from under your Super Hero into  your hand."
	image = "crossover_2/images/cards/Laurel Lance 2.jpg"


	def play_action(self,player):
		if len(player.hand.contents) > 0:
			result = effects.may_choose_one_of(self.text,player,player.hand.contents,ai_hint.IFBAD)
			if result != None:
				result.pop_self()
				player.under_superhero.contents.append(result)
			else:
				if len(player.under_superhero.contents) > 0:
					instruction_text = "You may put a card from under your suprhero into your hand."
					result = effects.may_choose_one_of(instruction_text,player,player.under_superhero.contents,ai_hint.BEST)
					if result != None:
						result.pop_self()
						player.hand.contents.append(result)
		return 0

class mirakuru(card_frame.card):
	name = "Mirakuru"
	vp = 1
	cost = 5
	ctype = cardtype.SUPERPOWER
	text = "If this is the first card you play this turn, you may\nput it nad your hand under your Super Hero. If you\ndo, draw four cards.\nOtherwise, draw a card."
	image = "crossover_2/images/cards/Mirakuru 5.jpg"


	def play_action(self,player):
		#If this is the first card played this turn
		if len(player.played.played_this_turn) == 1:
			instruction_text = f"Would you like to put {self.name} and your hand under your Super Hero?"
			if effects.ok_or_no(instruction_text,player,self,ai_hint.RANDOM):
				for c in player.hand.contents.copy():
					c.pop_self()
					player.under_superhero.contents.append(c)
				self.pop_self()
				player.under_superhero.contents.append(self)
				player.draw_card(4)
				return 0
		#Otherwise condition
		player.draw_card()
		return 0

class moira_queen(card_frame.card):
	name = "Moira Queen"
	vp = '*'
	cost = 3
	ctype = cardtype.HERO
	text = "Put the top card of the main deck under your Super Hero.\nAt the end of the game, this is worth 1 VP for each different\ncard under your Super Hero."
	image = "crossover_2/images/cards/Moira Queen 3.jpg"

	def play_action(self,player):
		top_card = globe.boss.main_deck.draw()
		top_card.set_owner(player)
		player.under_superhero.contents.append(top_card)

		return 0


	def calculate_vp(self,all_cards):
		unique_cards = set()
		for c in self.owner.under_superhero.contents:
			unique_cards.add(c.name)
		return len(unique_cards)

class mr_blank(card_frame.card):
	name = "Mr. Blank"
	vp = 1
	cost = 4
	ctype = cardtype.VILLAIN
	text = "+2 Power and choose a foe"
	attack_text = "Attack:: Look at the cards under that foe's Super Hero and put one of them under your Super Hero."
	image = "crossover_2/images/cards/Mr Blank 4.jpg"
	attack = True

	def play_action(self,player):
		player.played.plus_power(2)
		self.attack_action(player)
		return 0

	def attack_action(self,by_player):
		p = effects.choose_a_player("Choose a player.\nYou will put a card from under their Super Hero, under your Super Hero",by_player,includes_self = False,hint=ai_hint.BEST)
		if effects.attack(p,self,by_player):
			if len(p.under_superhero.contents) > 0:
				result = effects.choose_one_of(f"Put one of these cards from {p.persona.name} under your Super Hero.",by_player,p.under_superhero.contents,ai_hint.BEST)
				result.pop_self()
				result.set_owner(by_player)
				by_player.under_superhero.contents.append(result)


class promise_to_a_friend(card_frame.card):
	name = "Promise To A Friend"
	vp = 1
	cost = 3
	ctype = cardtype.SUPERPOWER
	text = "Ongoing: +1 Power and you may not destroy\ncards during your turn."
	image = "crossover_2/images/cards/Promise to a Friend 3.jpg"
	ongoing = True

	#Returning ture stops the destory
	def trigger(self,ttype,data,player,active,immediate):
		if trigger.test(immediate,\
						trigger.DESTROY, \
						self.trigger, \
						player,ttype):
			return True
	
	
	def play_action(self,player):
		player.played.plus_power(1)
		player.triggers.append(self.trigger)
		if not self in player.ongoing.contents:
			player.ongoing.add(self.pop_self())
		return 0


class shado(card_frame.card):
	name = "Shado"
	vp = 1
	cost = 4
	ctype = cardtype.HERO
	defense = True
	text = "+1 Power and draw a card\nDefence:: You may put this card under your Super Hero to\navoid an Attack. If you do, draw two cards and you may put\na card from your hand under your Super Hero."
	image = "crossover_2/images/cards/Shado 4.jpg"
	
	def play_action(self,player):
		player.played.plus_power(1)
		player.draw_card()
		return 0

	def defend(self,attacker = None,defender = None):
		self.pop_self()
		self.owner.under_superhero.contents.append(self)
		self.owner.draw_card(2)
		if len(self.owner.hand.contents) > 0:
			instruction_text = "You may put a card from your hand under your superhero."
			result = effects.may_choose_one_of(instruction_text,self.owner,self.owner.hand.contents,ai_hint.IFBAD)
			if result != None:
				result.pop_self()
				self.owner.under_superhero.contents.append(result)
		return


class verdant(card_frame.card):
	name = "Verdant"
	vp = 2
	cost = 6
	ctype = cardtype.LOCATION
	text = "Ongoing: At the start of each of your turns, you\nmay put a card from your hand under your Super\nHero. If you do, draw a card."
	image = "crossover_2/images/cards/Verdant 6.jpg"
	ongoing = True

	def play_action(self,player):
		if not self in player.ongoing.contents:
			player.ongoing.add(self.pop_self())
		elif len(player.hand.contents) > 0:
			instruction_text = "You may put a card from your hand under your superhero.\nIf you do, draw a card."
			result = effects.may_choose_one_of(instruction_text,player,player.hand.contents,ai_hint.IFBAD)
			if result != None:
				result.pop_self()
				player.under_superhero.contents.append(result)
				player.draw_card()
		return 0

class you_have_failed_this_city(card_frame.card):
	name = "You Have Failed This City"
	vp = 1
	cost = 5
	ctype = cardtype.SUPERPOWER
	text = "+2 Power and choose a foe"
	attack_text = "Attack:: The chosen foe discards a random card."
	image = "crossover_2/images/cards/You Have Failed This City 5.jpg"
	attack = True

	def play_action(self,player):
		player.played.plus_power(2)
		self.attack_action(player)
		return 0

	def attack_action(self,by_player):
		p = effects.choose_a_player("Choose a player.\nThey will discard a random card.",by_player,includes_self = False,hint=ai_hint.BEST)
		if effects.attack(p,self,by_player):
			if len(p.hand.contents) > 0:
				result = random.choice(p.hand.contents)
				p.discard_a_card(result)



#SVs
class brother_blood(card_frame.card):
	name = "Brother Blood"
	vp = 6
	cost = 13
	ctype = cardtype.VILLAIN
	owner_type = owners.VILLAINDECK
	text = "+4 Power and draw a card."
	attack_text = "First Appearance - Attack: Each player reveals the top card\nof the main dekc and puts it under his Super Hero. If it's not a\nSuper Power, discard all c ards with cost 4 or greater."
	image = "crossover_2/images/cards/Brother Blood 13.jpg"
	
	def play_action(self,player):
		player.played.plus_power(4)
		player.draw_card()
		return 0

	def first_apearance(self):
		for p in globe.boss.players:
			if effects.attack(p,self):
				top_card = globe.boss.main_deck.draw()
				effects.reveal(f"This will be under {p.persona.name}'s Super Hero.",p,[top_card])
				top_card.set_owner(p)
				p.under_superhero.contents.append(top_card)
				if not top_card.ctype_eq(cardtype.SUPERPOWER):
					for c in p.hand.contents.copy():
						if c.cost >= 4:
							p.discard_a_card(c)

		return


class china_white(card_frame.card):
	name = "China White"
	vp = 5
	cost = 9
	ctype = cardtype.VILLAIN
	owner_type = owners.VILLAINDECK
	text = "+3 Power and you may destory a card in your hand or discard\npile."
	attack_text = "First Appearance - Attack: Each player reveals the top card\nof the main deck and puts it under his Super Hero. If it's not a\nHero, discard a random card."
	image = "crossover_2/images/cards/China White 9.jpg"
	
	def play_action(self,player):
		player.played.plus_power(3)
		assemble = []
		assemble.extend(player.hand.contents)
		assemble.extend(player.discard.contents)
		if len(assemble) > 0:
			instruction_text = "You may destroy a card in your hand or discard pile"
			result = effects.may_choose_one_of(instruction_text,player,assemble,ai_hint.IFBAD)
			if result != None:
				result.destroy(player)
		return 0

	def first_apearance(self):
		for p in globe.boss.players:
			if effects.attack(p,self):
				top_card = globe.boss.main_deck.draw()
				effects.reveal(f"This will be under {p.persona.name}'s Super Hero.",p,[top_card])
				top_card.set_owner(p)
				p.under_superhero.contents.append(top_card)
				if not top_card.ctype_eq(cardtype.HERO):
					if len(p.hand.contents) > 0:
						result = random.choice(p.hand.contents)
						p.discard_a_card(result)
		return


class count_vertigo(card_frame.card):
	name = "Count Virtigo"
	vp = 6
	cost = 11
	ctype = cardtype.VILLAIN
	owner_type = owners.VILLAINDECK
	text = "Draw three cards and then put one of them under your superhero."
	attack_text = "First Appearance - Attack: Reveal the top two cards of your deck.\nPut one of them under your Super Hero, and put the other under the Super Hero of the player on your left."
	image = "crossover_2/images/cards/Count Vertigo 11.jpg"
	
	def play_action(self,player):
		drawn_cards = player.draw_card(3)
		if len(drawn_cards) > 0:
			instruction_text = "Put one of there under your super hero."
			result = effects.choose_one_of(instruction_text,player,drawn_cards,ai_hint.WORST)
			result.pop_self()
			player.under_superhero.contents.append(result)
		return 0

	def first_apearance(self):
		for p in globe.boss.players:
			if effects.attack(p,self):
				top_cards = []
				for i in range(2):
					next_card = p.reveal_card(public = False)
					if next_card != None:
						next_card.pop_self()
						top_cards.append(next_card)
				if len(top_cards) > 0:
					effects.reveal("There were what {} drew.",p,top_cards)
					to_left = None
					if p.pid + 1 == len(globe.boss.players):
						to_left = globe.boss.players[0]
					else:
						to_left = globe.boss.players[p.pid+1]
					
					instruction_text = f"Choose one to put under your Super Hero,\nthe other will go under {to_left.persona.name}'s Super Hero."
					result = effects.choose_one_of(instruction_text,p,top_cards,ai_hint.BEST)
					p.under_superhero.contents.append(result)
					top_cards.remove(result)
				if len(top_cards) > 0:
					result = top_cards[0]
					result.set_owner(to_left)
					to_left.under_superhero.contents.append(result)
		return


class deadshot(card_frame.card):
	name = "Deadshot"
	vp = 5
	cost = 10
	ctype = cardtype.VILLAIN
	owner_type = owners.VILLAINDECK
	text = "+3 Power. Your next Attack this turn must be avoided twise."
	attack_text = "First Appearance - Attack: Each player reveals the top card\nof the main deck and puts it under his Super Hero. If it's not a\nHero, discard a random card."
	image = "crossover_2/images/cards/Deadshot 10.jpg"

	def trigger(self,ttype,data,player,active,immediate):
		if trigger.test(immediate,\
						trigger.ATTACKING, \
						self.trigger, \
						player,ttype):
			player.triggers.remove(self.trigger)
			return effects.attack(data[0],data[1],by_player = player,avoid_twise = True)

	def play_action(self,player):
		player.played.plus_power(3)
		player.triggers.append(self.trigger)
		return 0

	def first_apearance(self):
		for p in globe.boss.players:
			if effects.attack(p,self):
				top_card = globe.boss.main_deck.draw()
				effects.reveal(f"This will be under {p.persona.name}'s Super Hero.",p,[top_card])
				top_card.set_owner(p)
				p.under_superhero.contents.append(top_card)
				if not top_card.ctype_eq(cardtype.VILLAIN):
					assemble = []
					for c in p.hand.contents:
						if c.cost <= 3:
							assemble.append(c)
					for c in p.discard.contents:
						if c.cost <= 3:
							assemble.append(c)
					if len(assemble) > 0:
						result = effects.choose_one_of("Choose a card with cost 3 or less to discard.",p,assemble,ai_hint.WORST)
						result.destroy(p)
		return


class edward_fyers(card_frame.card):
	name = "Edward Fyers"
	vp = 4
	cost = 8
	ctype = cardtype.VILLAIN
	owner_type = owners.VILLAINDECK
	text = "Ongoing: The first time a card tells you ro draw one or\nmore cards during each of your turns, you may put one\nof the cards drawn this was under your Super Hero."
	image = "crossover_2/images/cards/Edward Fyers 8.jpg"
	ongoing = True

	#Returning ture stops the destory
	#data[1] is from_card
	#data[2] are the cards drawn
	def trigger(self,ttype,data,player,active,immediate):
		if trigger.test(not immediate,\
						trigger.DRAW, \
						self.trigger, \
						player,ttype) \
				and data[1]:
			player.triggers.remove(self.trigger)
			instruction_text = "Would you like to put one drawn cards under your Super Hero?"
			result = effects.may_choose_one_of(instruction_text,player,data[2])
			if result != None:
				result.pop_self()
				player.under_superhero.contents.append(result)

	
	def play_action(self,player):
		if not self in player.ongoing.contents:
			player.ongoing.add(self.pop_self())
			if not player.drawn_card:
				player.triggers.append(self.trigger)
		else:
			player.triggers.append(self.trigger)
		return 0

class isabel_rochev(card_frame.card):
	name = "Isabel Rochev"
	vp = 7
	cost = 14
	ctype = cardtype.VILLAIN
	owner_type = owners.VILLAINDECK
	text = "Choose a player. gain a card from under that player's\nSuper Hero, and then put it into your hand."
	attack_text = "First Appearance - Attack: Each player puts the highest cost card from his hand under his Super Hero."
	image = "crossover_2/images/cards/Isabel Rochev 14.jpg"

	def play_action(self,player):
		instruction_text = "Choose a player to gain a card from under their Super Hero"
		result = effects.choose_a_player(instruction_text,player,includes_self = True,hint = ai_hint.RANDOM)
		if len(result.under_superhero.contents) > 0:
			instruction_text = f"Gain a card from under {result.persona.name}'s Super Hero"
			result = effects.choose_one_of(instruction_text,player,result.under_superhero.contents,ai_hint.BEST)
			player.gain(result)
			result.pop_self()
			player.hand.contents.append(result)
		return 0

	def first_apearance(self):
		for p in globe.boss.players:
			if effects.attack(p,self):
				highest_costs = []
				cost = -1
				for c in p.hand.contents:
					if c.cost > cost:
						cost = c.cost
						highest_costs = [c]
					elif c.cost == cost:
						highest_costs.append(c)
				#Hand is not empty
				if len(highest_costs) > 1:
					instruction_text = "Choose a highest cost to put under your Super Hero."
					result = effects.choose_one_of(instruction_text,p,highest_costs,ai_hint.WORST)
					result.pop_self()
					p.under_superhero.contents.append(result)
		return

class malcolm_merlyn(card_frame.card):
	name = "Malcolm Merlyn"
	vp = 6
	cost = 12
	ctype = cardtype.VILLAIN
	owner_type = owners.VILLAINDECK
	text = "+3 Power. Defense: You may reveal this card from your hand to avoid an Attack."
	attack_text = "First Appearance - Attack: Each player reveals the top card\nof the main deck and puts it under his Super Hero. If it's not a\nHero, discard a random card."
	image = "crossover_2/images/cards/Malcom Merlyn 12.jpg"
	defense = True

	def play_action(self,player):
		player.played.plus_power(3)
		return 0

	def defend(self,attacker = None,defender = None):
		effects.reveal(f"{self.owner.persona.name} defended with this card.",self.owner,[self])
		return

	def first_apearance(self):
		for p in globe.boss.players:
			if effects.attack(p,self):
				top_card = globe.boss.main_deck.draw()
				effects.reveal(f"This will be under {p.persona.name}'s Super Hero.",p,[top_card])
				top_card.set_owner(p)
				p.under_superhero.contents.append(top_card)
				if not top_card.ctype_eq(cardtype.EQUIPMENT):
					p.gain_a_weakness()
		return

class slade_wilson(card_frame.card):
	name = "Slade Wilson"
	vp = 7
	cost = 15
	ctype = cardtype.VILLAIN
	owner_type = owners.VILLAINDECK
	text = ""
	attack_text = "First Appearance - Attack: This Attack cannot be\navoided. Each player destroys six cards with different\ncard types under his Super Hero. For each card type you\nfail to destroy this way, discard a card."
	image = "crossover_2/images/cards/Slade Wilson 15.jpg"

	def first_apearance(self):
		for p in globe.boss.players:
			#Do i still want to trigger the attack function that may trigger other things?
			#if effects.attack(p,self):
			destroyed_types = set()
			for i in range(6):
				assemble = []
				for c in p.under_superhero.contents:
					#If there are overlaps, this card cant be included
					if len(destroyed_types.intersection(set(c.get_ctype()))) == 0:
						assemble.append(c)
				if len(assemble) > 0:
					instruction_text = f"Destroy six cards with different\ncard types under your Super Hero. ({i+1}/6)"
					result = effects.choose_one_of(instruction_text,p,assemble,ai_hint.WORST)
					result.destroy(p)
				elif len(p.hand.contents) > 0:
					instruction_text = f"Discard a card because you ran out of\nvalid cards to destroy under your super hero. ({i+1}/6)"
					result = effects.choose_one_of(instruction_text,p,p.hand.contents,ai_hint.WORST)
					p.discard_a_card(result)
		return