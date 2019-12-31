from constants import cardtype
import effects
from constants import ai_hint
import globe
from frames import persona_frame
from frames import actions
import random
from constants import owners
from constants import trigger

def get_personas():
	return [felicity_smoak(),john_diggle(),oliver_queen(),roy_harper(),sara_lance()]


class felicity_smoak(persona_frame.persona):
	name = "Felicity Smoak"
	text = "If you play two or more Heros during your turn, you may put\nthe top card of the main deck under your Super Hero or put a\ncard from under your Super Hero into your hand."
	image = "crossover_2/images/personas/Felicity Smoak MC.jpg"

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
			hero_count = 0
			for c in self.player.played.played_this_turn:
				if c.ctype_eq(cardtype.HERO):
					hero_count += 1
			if hero_count == 2:
				instruction_text = "Would you like to put a card from the main deck under Felicity Smoak?"
				hint = ai_hint.ALWAYS
				if len(player.under_superhero.contents) > 0:
					hint = ai_hint.NEVER
					instruction_text += "\nif not, put a card from under your superhero\ninto your hand"
				if effects.ok_or_no(instruction_text,player,None,hint):
					top_card = globe.boss.main_deck.draw()
					top_card.set_owner(player)
					player.under_superhero.contents.append(top_card)
				elif len(player.under_superhero.contents) > 0:
					instruction_text = "You may put a card from under your superhero into your hand."
					result = effects.may_choose_one_of(instruction_text,player,player.under_superhero.contents,ai_hint.BEST)

	def ready(self):
		self.player.triggers.append(self.trigger)


class john_diggle(persona_frame.persona):
	name = "John Diggle"
	text = "When you use a Defence to avoid an Attack, you may put that card\nunder your Super Hero. Once during each of your turns, you may put\na Defence card from under your Super Hero on top of your deck."
	image = "crossover_2/images/personas/John Diggle MC.jpg"
	action = None

	def ai_overvalue(self,card):
		if card.defence:
			return persona_frame.overvalue()
		return 0

	def special_action_click(self,player):
		assemble = []
		for c in player.under_superhero.contents:
			if c.defence:
				assemble.append(c)
		if len(assemble) > 0:
			instruction_text = "Would you like to put a defense from under your\nsuper hero, on top of your deck?"
			result = effects.may_choose_one_of(instruction_text,player,assemble,ai_hint.BEST)
			if result != None:
				result.pop_self()
				player.deck.contents.append(result)
				self.player.played.special_options.remove(self.action)
				return True
		return False

	#I don't know if this should be immediate or not, but 
	#To avoid complications, i'll make it immediate
	def trigger(self,ttype,data,player,active,immediate):
		if globe.DEBUG:
			print("test",self.name,flush=True)
		if trigger.test(immediate,\
						trigger.AVOIDED_ATTACK, \
						self.trigger, \
						player,ttype,active):
			if globe.DEBUG:
				print("active",self.name,flush=True)
			instruction_text = f"Would you like to that {data[2].name} on top of your deck?"
			if effects.ok_or_no(instruction_text,player,data[2],ai_hint.ALWAYS) \
					and data[2].owner == player:
				data[2].pop_self()
				player.under_superhero.contents.append(data[2])


	def ready(self):
		if self.active:
			self.action = actions.special_action("John Diggle",self.special_action_click)
			self.player.played.special_options.append(self.action)
	
	def reset(self):
		self.player.triggers.append(self.trigger)

	#If there is more than a 50% chance of getting a card that does anything,
	def ai_is_now_a_good_time(self):
		if self.action in self.player.played.special_options:
			return self.special_action_click(self.player)
		return False

class oliver_queen(persona_frame.persona):
	name = "Oliver Queen"
	text = "At the start of each of youor turns, you may discard a card from your hand\n. If it's an Equipment, you may put it under your Super Hero. if it's\nnot, put a random card from under your Super Hero into your hand."
	image = "crossover_2/images/personas/Oliver Queen MC.jpg"

	def ai_overvalue(self,card):
		if card.ctype_eq(cardtype.EQUIPMENT):
			#Really need equipment
			return persona_frame.overvalue()
		return 0

	def ready(self):
		if self.active:
			if len(self.player.hand.contents) > 0:
				instruction_text = "You may discard a card from your hand]\n. If it's an Equipment, you may put it under your Super Hero. if it's\nnot, put a random card from under your Super Hero into your hand."
				result = effects.may_choose_one_of(instruction_text,self.player,self.player.hand.contents,ai_hint.IFBAD)
				if result != None:
					if result.ctype_eq(cardtype.EQUIPMENT):
						result.pop_self()
						self.player.under_superhero.contents.append(result)
					else:
						if len(self.player.under_superhero.contents) > 0:
							self.player.hand.contents.append(random.choice(self.player.under_superhero.contents).pop_self())


class roy_harper(persona_frame.persona):
	name = "Roy Harper"
	text = "Once during each of your turns, you may put a Super Power from the\nLine-up under your Super Hero. At the start of each of your turns, if\nthere are four or more cards under your Super Hero. +2 Power and\nyou must destroy four cards under your Super Hero."
	image = "crossover_2/images/personas/Roy Harper MC.jpg"
	action = None

	def ai_overvalue(self,card):
		if card.ctype_eq(cardtype.SUPERPOWER):
			return -persona_frame.overvalue()
		return 0

	def special_action_click(self,player):
		assemble = []
		for c in globe.boss.lineup.contents:
			if c.ctype_eq(cardtype.SUPERPOWER):
				assemble.append(c)
		if len(assemble) > 0:
			instruction_text = "Would you like to put a Super Power from the line up under your persona?"
			result = effects.may_choose_one_of(instruction_text,player,assemble,ai_hint.BEST)
			if result != None:
				result.pop_self()
				result.set_owner(player)
				player.under_superhero.contents.append(result)
				player.played.special_options.remove(self.action)
		return False

	def ready(self):
		if self.active:
			if len(self.player.under_superhero.contents) >= 4:
				self.player.played.plus_power(2)
				if len(self.player.under_superhero.contents) > 4:
					for i in range(4):
						instruction_text = f"Choose a card to destroy from under your super hero ({i+1}/4)"
						result = effects.choose_one_of(instruction_text,self.player,self.player.under_superhero.contents)
						result.destroy(self.player)
				else:
					for c in self.player.under_superhero.contents.copy():
						c.destroy(self.player)


			self.action = actions.special_action("Roy Harper",self.special_action_click)
			self.player.played.special_options.append(self.action)


	#If there is more than a 50% chance of getting a card that does anything,
	def ai_is_now_a_good_time(self):
		if self.action in self.player.played.special_options:
			return self.special_action_click(self.player)
		return False

class sara_lance(persona_frame.persona):
	name = "Sara Lance"
	text = "When you buy or gain a Villain in the Line-up, you may put it\nunder your Super Hero. Once during each of your turnss, you may put\na Villain from under your Super Hero on the bottom of your deck."
	image = "crossover_2/images/personas/Sara Lance MC.jpg"
	action = None

	def ai_overvalue(self,card):
		if card.ctype_eq(cardtype.VILLAIN):
			return persona_frame.overvalue()
		return 0

	def trigger(self,ttype,data,player,active,immediate):
		if globe.DEBUG:
			print("test",self.name,flush=True)
		if trigger.test(immediate,\
						trigger.GAIN_CARD, \
						self.trigger, \
						player,ttype,active) \
				and data[1].owner_type == owners.LINEUP \
				and data[1].ctype_eq(cardtype.VILLAIN) \
				and data[0] == False \
				and effects.ok_or_no(f"Would you like to put {data[1].name} under your Super Hero?",player,data[1],ai_hint.ALWAYS):
			if globe.DEBUG:
				print("active",self.name,flush=True)
			player.under_superhero.contents.append(data[1])
			return True

	def special_action_click(self,player):
		assemble = []
		for c in player.under_superhero.contents:
			if c.ctype_eq(cardtype.VILLAIN):
				assemble.append(c)
		if len(assemble) > 0:
			instruction_text = "Would you like to put a Villain from under\nyour super hero on the bottom of your deck?"
			result = effects.may_choose_one_of(instruction_text,player,assemble,ai_hint.BEST)
			if result != None:
				result.pop_self()
				player.deck.contents.insert(0,result)
				self.player.played.special_options.remove(self.action)
				return True
		return False

	def ready(self):
		self.player.triggers.append(self.trigger)
		if self.active:
			self.action = actions.special_action("Sara Lance",self.special_action_click)
			self.player.played.special_options.append(self.action)
		

	def ai_is_now_a_good_time(self):
		if self.action in self.player.played.special_options:
			return self.special_action_click(self.player)
		return False


