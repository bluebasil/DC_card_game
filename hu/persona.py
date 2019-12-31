from constants import cardtype
import effects
from constants import ai_hint
import globe
from frames import persona_frame
from frames import actions
from constants import trigger


def get_personas():
	return [batgirl(),black_canary(),booster_gold(),hawkman(),nightwing(),red_tornado(),shazam(),starfire()]



class batgirl(persona_frame.persona):
	name = "Batgirl"
	text = "Once during each of your turns, you may discard a Punch card.  If you do, draw a card."
	image = "hu/images/personas/Batgirl MC.jpg"
	action = None

	def special_action_click(self,player):
		#We must ensure that we are doing this on our turn
		if player.pid == globe.boss.whose_turn:
			for c in self.player.hand.contents:
				if c.name == "Punch" and self.action in self.player.played.special_options:
					self.player.discard_a_card(c)
					self.player.draw_card(from_card = False)
					self.player.played.special_options.remove(self.action)
					return True
		return False


	def ready(self):
		if self.active:
			self.action = actions.special_action("Batgirl",self.special_action_click)
			self.player.played.special_options.append(self.action)

	#If there is more than a 50% chance of getting a card that does anything,
	def ai_is_now_a_good_time(self):
		total_left = 0
		for c in self.player.deck.contents:
			if c.cost > 0:
				total_left += 1
		if total_left/(len(self.player.deck.contents)+1) > 0.5:
			if self.action in self.player.played.special_options:
				return self.special_action_click(self.player)
			#return self.any_time()
		return False

class black_canary(persona_frame.persona):
	name = "Black Canary"
	text = "+1 Power for each different Villain you play during your turn."
	image = "hu/images/personas/Black Canary HU MC.jpg"
	
	def ai_overvalue(self,card):
		if card.ctype_eq(cardtype.VILLAIN):
			return persona_frame.overvalue()
		return 0

	def trigger(self,ttype,data,player,active,immediate):
		if globe.DEBUG:
			print("test",self.name,flush=True)
		if trigger.test(not immediate,\
						trigger.PLAY, \
						self.trigger, \
						player,ttype,active) \
				and data[0].ctype_eq(cardtype.VILLAIN):
			if globe.DEBUG:
				print("active",self.name,flush=True)
			already_played = False
			for c in self.player.played.played_this_turn:
				if data[0] != c and data[0].name == c.name:
					already_played = True
			if not already_played:
				player.played.plus_power(1)


	def ready(self):
		self.player.triggers.append(self.trigger)


class booster_gold(persona_frame.persona):
	name = "Booster Gold"
	text = "+1 Power for each Defense card you play during your turn.  When you avoid an attack, draw a card."
	image = "hu/images/personas/Booster Gold MC.jpg"
	
	def ai_overvalue(self,card):
		if card.defense:
			return persona_frame.overvalue()
		return 0

	def triggerDE(self,ttype,data,player,active,immediate):
		if globe.DEBUG:
			print("test",self.name,flush=True)
		if trigger.test(not immediate,\
						trigger.PLAY, \
						self.triggerDE, \
						player,ttype,active) \
				and data[0].defense:
			if globe.DEBUG:
				print("active",self.name,flush=True)
			player.played.plus_power(1)

	def triggerAA(self,ttype,data,player,active,immediate):
		if globe.DEBUG:
			print("test",self.name,flush=True)
		if trigger.test(not immediate,\
						trigger.AVOIDED_ATTACK, \
						self.triggerAA, \
						player,ttype,active):
			if globe.DEBUG:
				print("active",self.name,flush=True)
			player.draw_card(from_card = False)


	def ready(self):
		self.player.triggers.append(self.triggerAA)

	def reset(self):
		self.player.triggers.append(self.triggerDE)

class hawkman(persona_frame.persona):
	name = "Hawkman"
	text = "+1 Power for each Hero you play during your turn."
	image = "hu/images/personas/Hawkman MC.jpg"

	def ai_overvalue(self,card):
		if card.ctype_eq(cardtype.HERO):
			return persona_frame.overvalue()
		return 0

	def trigger(self,ttype,data,player,active,immediate):
		if globe.DEBUG:
			print("test",self.name,flush=True)
		if trigger.test(not immediate,\
						trigger.PLAY, \
						self.trigger, \
						player,ttype,active) \
				and data[0].ctype_eq(cardtype.HERO):
			if globe.DEBUG:
				print("active",self.name,flush=True)
			player.played.plus_power(1)

	def ready(self):
		self.player.triggers.append(self.trigger)

class nightwing(persona_frame.persona):
	name = "Nightwing"
	text = "The first time you play an Equipment during your turn, +1 Power.\n The second time you play an Equipment during your turn, draw a card."
	image = "hu/images/personas/Nightwing MC.jpg"

	def ai_overvalue(self,card):
		if card.ctype_eq(cardtype.EQUIPMENT):
			return persona_frame.overvalue()
		return 0

	def trigger(self,ttype,data,player,active,immediate):
		if globe.DEBUG:
			print("test",self.name,flush=True)
		if trigger.test(not immediate,\
						trigger.PLAY, \
						self.trigger, \
						player,ttype,active) \
				and data[0].ctype_eq(cardtype.EQUIPMENT):
			if globe.DEBUG:
				print("active",self.name,flush=True)
			number_played = 0
			for c in self.player.played.played_this_turn:
				if c.ctype_eq(cardtype.EQUIPMENT):
					number_played += 1
			if number_played == 1:
				player.played.plus_power(1)
			elif number_played == 2:
				player.draw_card(from_card = False)
				player.triggers.remove(self.trigger)
			
	def ready(self):
		self.player.triggers.append(self.trigger)



class red_tornado(persona_frame.persona):
	name = "Red Tornado"
	text = "Once during each of your turns, if there are four or more different card types in your discard pile, +2 Power."
	image = "hu/images/personas/Red Tornado MC.jpg"
	accounted_for = False
	action = None

	def get_typecount(self):
		return {cardtype.HERO:self.player.deck.get_count(cardtype.HERO) + self.player.discard.get_count(cardtype.HERO) + 1, \
						cardtype.VILLAIN:self.player.deck.get_count(cardtype.VILLAIN) + self.player.discard.get_count(cardtype.VILLAIN) + 1, \
						cardtype.SUPERPOWER:self.player.deck.get_count(cardtype.SUPERPOWER) + self.player.discard.get_count(cardtype.SUPERPOWER) + 1, \
						cardtype.EQUIPMENT:self.player.deck.get_count(cardtype.EQUIPMENT) + self.player.discard.get_count(cardtype.EQUIPMENT) + 1}

	def ai_overvalue(self,card):
		card_types = self.get_typecount()
		all_relevant = sum(list(card_types.values()))
		#print("MAKE SURE NONE OF THESE ARE 0",card.ctype,all_relevant,flush=True)
		if card.ctype in card_types:
			return 0.25/(card_types[card.ctype]/all_relevant) - 1
		return 0


	def special_action_click(self,player):
		#We must ensure that we are doing this on our turn
		if player.pid == globe.boss.whose_turn:
			card_types = set()
			for c in player.discard.contents:
				card_types.update(c.get_ctype())
			if len(card_types) >= 4:
				player.played.plus_power(2)
				player.played.special_options.remove(self.action)
				return True
		return False


	def ready(self):
		if self.active:
			self.action = actions.special_action("Red Tornado",self.special_action_click)
			self.player.played.special_options.append(self.action)


	#If there is more than a 50% chance of getting a card that does anything,
	def ai_is_now_a_good_time(self):
		if self.action in self.player.played.special_options:
			return self.special_action_click(self.player)


class shazam(persona_frame.persona):
	name = "Shazam"
	text = "You may pay 4 Power, If you do, gain the top card of the main deck.  You may put it on top of your deck or into your discard pile."
	image = "hu/images/personas/Shazam MC.jpg"
	action = None


	def special_action_click(self,player):
		#We must ensure that we are doing this on our turn
		if player.pid == globe.boss.whose_turn:
			if self.player.played.power >= 4:
				self.player.played.power -= 4
				card = globe.boss.main_deck.contents[-1]
				instruction_text = f"Would you like to put {card.name} on top of your deck?"
				result = effects.ok_or_no(instruction_text,self.player,card,ai_hint.ALWAYS)
				card = globe.boss.main_deck.contents.pop()
				card.set_owner(self.player)
				if result:
					self.player.deck.add(card)
				else:
					self.player.gain(card)
				return True
		return False


	def ready(self):
		if self.active:
			self.action = actions.special_action("Shazam",self.special_action_click)
			self.player.played.special_options.append(self.action)

	#IDK, never?
	def ai_is_now_a_good_time(self):

		return False



class starfire(persona_frame.persona):
	name = "Starfire"
	text = "Once during each of your turns, if there are no Super Powers in the Line-up, draw a card."
	image = "hu/images/personas/Starfire HU MC.jpg"
	action = None

	def ai_overvalue(self,card):
		if card.ctype_eq(cardtype.SUPERPOWER):
			return persona_frame.overvalue()
		return 0


	def special_action_click(self,player):
		#We must ensure that we are doing this on our turn
		if player.pid == globe.boss.whose_turn:
			if globe.boss.lineup.get_count(cardtype.SUPERPOWER) == 0:
				self.player.draw_card(from_card = False)
				player.played.special_options.remove(self.action)
				return True
		return False


	def ready(self):
		if self.active:
			self.action = actions.special_action("Starfire",self.special_action_click)
			self.player.played.special_options.append(self.action)


	#If there is more than a 50% chance of getting a card that does anything,
	def ai_is_now_a_good_time(self):
		if self.action in self.player.played.special_options:
			return self.special_action_click(self.player)

