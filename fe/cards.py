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
from constants import trigger

#Done
class amanda_waller(card_frame.card):
	name = "Amanda Waller"
	vp = 1
	cost = 4
	ctype = cardtype.HERO
	text = "You may destroy a card in your hand or discard pile.\nIf it's a Villain, +Power equal to it's cost.\nIf you choose not to, +2 Power."
	image = "fe/images/cards/Amanda Waller.jpg"
	
	def play_action(self,player):
		#effects.may_destroy_card_in_hand_or_discard(player)
		collection = player.hand.contents.copy()
		collection.extend(player.discard.contents)
		instruction_text = "You may destroy a card in your hand or discard pile.\nIf it's a Villain, +Power equal to it's cost.\nIf you choose not to, +2 Power."
		card_to_destroy = effects.may_choose_one_of(instruction_text,player,collection,ai_hint.IFBAD)
		if card_to_destroy == None:
			player.played.plus_power(2)
			return 0
		else:
			card_to_destroy.destroy(player)
			if card_to_destroy.ctype_eq(cardtype.VILLAIN):
				player.played.plus_power(card_to_destroy.cost)
				return 0
		return 0

#Done
class atomica(card_frame.card):
	name = "Atomica"
	vp = 1
	cost = 3
	ctype = cardtype.VILLAIN
	text = "You may destroy a non-Villain card in your hand or discard pile. If its cost is 1 or greater, gain 1 VP."
	image = "fe/images/cards/Atomica 3.jpg"
	
	def play_action(self,player):
		#effects.may_destroy_card_in_hand_or_discard(player)
		assemble = []
		for c in player.hand.contents:
			if not c.ctype_eq(cardtype.VILLAIN):
				assemble.append(c)
		for c in player.discard.contents:
			if not c.ctype_eq(cardtype.VILLAIN):
				assemble.append(c)
		instruction_text = "You may destroy a card in your hand or discard pile.\nIf it's a Villain, +Power equal to it's cost.\nIf you choose not to, +2 Power."
		card_to_destroy = effects.may_choose_one_of(instruction_text,player,assemble,ai_hint.IFBAD)
		if card_to_destroy != None:
			card_to_destroy.destroy(player)
			if card_to_destroy.cost >= 1:
				player.gain_vp(1)
		return 0

#Done
class bizarro_power(card_frame.card):
	name = "Bizarro Power"
	vp = -1
	cost = 6
	ctype = cardtype.SUPERPOWER
	text = "+4 Power and gain a Weakness."
	attack = True
	attack_text = "Attack:: Each foe gains a Weakness"
	image = "fe/images/cards/Bizarro Power.jpg"
	
	def play_action(self,player):
		player.played.plus_power(4)
		player.gain_a_weakness()
		self.attack_action(player)
		return 0

	def attack_action(self,by_player):
		for p in globe.boss.players:
			if p != by_player and effects.attack(p,self,by_player):
				p.gain_a_weakness()
		return


#Done
class broadsword(card_frame.card):
	name = "Broadsword"
	vp = 2
	cost = 6
	ctype = cardtype.EQUIPMENT
	text = "+2 Power and choose a foe."
	attack = True
	attack_text = "Attack:: Destroy a card with cost 1,2, or 3 in that\nfoe's discard pile."
	image = "fe/images/cards/Broadsword.jpg"
	
	def play_action(self,player):
		player.played.plus_power(2)
		self.attack_action(player)
		return 0

	def attack_action(self,by_player):
		#r(instruction_text,player,includes_self = True):
		player = effects.choose_a_player("Choose a player to destroy a cost 1,2, or 3 card from their discard",by_player,False)
		if effects.attack(player,self,by_player):
			assemble = []
			for c in player.discard.contents:
				if c.cost >= 1 and c.cost <= 3:
					assemble.append(c)
			if len(assemble) > 0:
				result = effects.choose_one_of(f"destroy a cost 1,2, or 3 card from {player.persona.name}'s' discard.",by_player,assemble,hint = ai_hint.BEST)
				result.destroy(by_player)
		return

#Done
class catwoman(card_frame.card):
	name = "Catwoman"
	vp = 1
	cost = 3
	ctype = cardtype.HERO
	text = "+1 Power and choose a foe."
	attack = True
	attack_text = "Attack:: Steal 1 VP from that foe"
	image = "fe/images/cards/Catwoman 3 Fe.jpg"
	
	def play_action(self,player):
		player.played.plus_power(1)
		self.attack_action(player)
		return 0

	def attack_action(self,by_player):
		#r(instruction_text,player,includes_self = True):
		player = effects.choose_a_player("Choose a player to steal 1 VP from",by_player,includes_self = False)
		if effects.attack(player,self,by_player):
			if player.vp >= 1:
				player.vp -= 1
				by_player.gain_vp(1)
		return

#Done
class cold_gun(card_frame.card):
	name = "Cold Gun"
	vp = 1
	cost = 2
	ctype = cardtype.EQUIPMENT
	text = "+1 Power\nYou may put a Frozen token on a card in the Line-up.\nIf you do, remove it at the start of your next turn."
	image = "fe/images/cards/Cold Gun 2.jpg"
	play_time = []
	
	#I could use triggers and buy actions to remove the global
	#frozen attributes
	#But i have not done that yet, and graphicly there are advantages this way
	def play_action(self,player):
		player.played.plus_power(1)
		instruction_text = "You may put a Frozen token on a card in the Line-up"
		result = effects.may_choose_one_of(instruction_text,player,globe.boss.lineup.contents,ai_hint.RANDOM)
		if result != None:
			result.frozen.append(player.pid)
		return 0

#Done
class commissioner_gordon(card_frame.card):
	name = "Commissioner Gordon"
	vp = 1
	cost = 2
	ctype = cardtype.HERO
	defense = True
	text = "+1 Power.  Defense: You may discard this card to avoid an Attack.  If you do, gain 1 VP."
	image = "fe/images/cards/Commissioner Gordon.jpg"
	
	def play_action(self,player):
		player.played.plus_power(1)
		return 0

	def defend(self,attacker = None,defender = None):
		self.owner.discard_a_card(self)
		self.owner.gain_vp(1)
		return

#Done
class constructs_of_fear(card_frame.card):
	name = "Constructs Of Fear"
	vp = 2
	cost = 7
	ctype = cardtype.SUPERPOWER
	text = "+3 Power"
	attack = True
	attack_text = "Attack:: Each foe discards two cards."
	image = "fe/images/cards/Constructs of Fear.jpg"
	
	def play_action(self,player):
		player.played.plus_power(3)
		self.attack_action(player)
		return 0

	def attack_action(self,by_player):
		for p in globe.boss.players:
			if p != by_player and effects.attack(p,self,by_player):
				for i in range(2):
					if len(p.hand.contents) > 0:
						result = effects.choose_one_of(f"Choose a card to discard. ({i+1}/2)",p,p.hand.contents,ai_hint.WORST)
						p.discard_a_card(result)
		return

class cosmic_staff(card_frame.card):
	name = "Cosmic Staff"
	vp = 1
	cost = 5
	ctype = cardtype.EQUIPMENT
	defense = True
	text = "+2 Power.  Defense: You may discard this card to avoid an Attack.  If you do, gain the bottom of the main deck."
	image = "fe/images/cards/Cosmic Staff.jpg"
	
	def play_action(self,player):
		player.played.plus_power(2)
		return 0

	def defend(self,attacker = None,defender = None):
		self.owner.discard_a_card(self)
		if len(globe.boss.main_deck.contents) > 0:
			self.owner.gain(globe.boss.main_deck.contents[0])
		return

class deathstorm(card_frame.card):
	name = "Deathstorm"
	vp = '10*'
	cost = 4
	ctype = cardtype.VILLAIN
	text = "You may destroy a card in your hand.\nAt the end of the game, this card is worth 10VP minus 1VP fewer for each\ncard in excess of 20 in your deck. (Minimum 0)"
	image = "fe/images/cards/Deathstorm.jpg"
	
	def play_action(self,player):
		instruction_text = "You may destroy a card in your hand."
		result = effects.may_choose_one_of(instruction_text,player,player.hand.contents,ai_hint.IFBAD)
		if result != None:
			result.destroy(player)
		return 0

	def calculate_vp(self,all_cards):
		return max(0,10 - max(0,(len(all_cards)-20)))

class despero(card_frame.card):
	name = "Despero"
	vp = 2
	cost = 6
	ctype = cardtype.VILLAIN
	text = "Draw two cards and choose a foe."
	attack = True
	attack_text = "Attack:: That foe discards a card with cost 1 or greater"
	image = "fe/images/cards/Despero.jpg"
	
	def play_action(self,player):
		player.draw_card(2)
		self.attack_action(player)
		return 0

	def attack_action(self,by_player):
		player = effects.choose_a_player("Choose a player to force to discard a cards costing 1 or greater.",by_player,False)
		if effects.attack(player,self,by_player):
			assemble = []
			for c in player.hand.contents:
				if c.cost >= 1:
					assemble.append(c)
			if len(assemble) > 0:
				result = effects.choose_one_of(f"Choose a card to discard.",player,assemble,ai_hint.WORST)
				player.discard_a_card(result)
		return


class dr_light(card_frame.card):
	name = "Dr. Light"
	vp = 1
	cost = 3
	ctype = cardtype.HERO
	text = "Draw a card and choose a foe."
	attack = True
	attack_text = "Attack:: That foe puts a Location he controls into his discard pile."
	image = "fe/images/cards/Dr Light.jpg"
	
	def play_action(self,player):
		player.draw_card()
		self.attack_action(player)
		return 0

	def attack_action(self,by_player):
		player = effects.choose_a_player("Choose a player to force to discard a location they control",by_player,includes_self = False,hint = ai_hint.RANDOM)
		if effects.attack(player,self,by_player):
			assemble = []
			for c in player.ongoing.contents:
				if c.ctype_eq(cardtype.LOCATION):
					assemble.append(c)
			if len(assemble) > 0:
				result = effects.choose_one_of(f"Choose a location to discard.",player,assemble,ai_hint.WORST)
				player.discard_a_card(result)
		return



class element_woman(card_frame.card):
	name = "Element Woman"
	vp = 1
	cost = 4
	ctype = cardtype.HERO
	text = "+2 Power\nWhile you own or are playing this card, it is also a Super Power, Equipment, and Villain."
	image = "fe/images/cards/Element Woman.jpg"
	being_played = False
	
	def play_action(self,player):
		player.played.plus_power(2)
		self.being_played = True
		return 0

	def get_ctype(self):
		if self.owner == None and not self.being_played:
			return super().get_ctype()
		else:
			return [cardtype.HERO,cardtype.SUPERPOWER,cardtype.EQUIPMENT,cardtype.VILLAIN]

	def ctype_eq(self,ctype):
		if self.owner == None and not self.being_played:
			return super().ctype_eq(ctype)
		else:
			if ctype == cardtype.SUPERPOWER or ctype == cardtype.EQUIPMENT or ctype == cardtype.VILLAIN or ctype == self.ctype:
				return True
			else:
				return False

	def end_of_turn(self):
		self.being_played = False
		return

	def destroy(self,by_player):
		self.being_played = False
		super().destroy(by_player)



#Done
class emperor_penguin(card_frame.card):
	name = "Emperor Penguin"
	vp = 0
	cost = 1
	ctype = cardtype.VILLAIN
	text = "When you destroy this card in any zone, gain 2 VPs."
	image = "fe/images/cards/Emperor Penguin.jpg"
	
	def destroy(self,player_responsible):
		player_responsible.gain_vp(2)
		super().destroy(player_responsible)



class expert_marksman(card_frame.card):
	name = "Expert Marksman"
	vp = 1
	cost = 3
	ctype = cardtype.SUPERPOWER
	text = "You may destroy a non-Super Power card in\nyour hand or discard pile. If its cost is 1 or\n greater, gain 1 VP."
	image = "fe/images/cards/Expert Marksman.jpg"
	
	def play_action(self,player):
		assemble = []
		for c in player.hand.contents:
			if not c.ctype_eq(cardtype.SUPERPOWER):
				assemble.append(c)
		for c in player.discard.contents:
			if not c.ctype_eq(cardtype.SUPERPOWER):
				assemble.append(c)
		if len(assemble) > 0:
			result = effects.may_choose_one_of(self.text,player,assemble,ai_hint.IFBAD)
			if result != None and result.cost >= 1:
				player.gain_vp(1)
		return 0


class firestorm_matrix(card_frame.card):
	name = "Firestorm Matrix"
	vp = 2
	cost = 7
	ctype = cardtype.EQUIPMENT
	text = 'Play the top card of your deck. If its cost is 5 or less, you may\ndestroy this card. If you do, leave the card you played in fromt\nof you for the rest of the game and it has: "Ongoing: You may\nplay this card once during each of your turns.\n(At the end of the game, destroy it.)"'
	image = "fe/images/cards/Firestorm Matrix.jpg"


	
	def play_action(self,player):
		drawn = player.reveal_card(public = False)
		if drawn != None:
			player.played.play(drawn.pop_self())
			if drawn.cost <= 5:
				instruction_text = "Would you like to destroy the Firestorm Matrix and make this card ongoing?"
				if effects.ok_or_no(instruction_text,player,drawn,hint = ai_hint.IFGOOD):
					self.destroy(player)
					player.ongoing.contents.append(drawn.pop_self())
					#Here comes the scary stuff

					def firestorm_special_action_click(player,actual_self = drawn):
						#print("SPECIAL ACTION CLICK",actual_self.name,flush=True)
						if actual_self.action in player.played.special_options:
							player.played.special_options.remove(actual_self.action)
							backup_play_action = actual_self.play_action
							actual_self.play_action = actual_self.original_play_action
							player.played.play(actual_self)
							player.played.contents.remove(actual_self)
							actual_self.play_action = backup_play_action

					def replace_play_action(player,actual_self = drawn):
						#print("REPLACE PLAY ACTION",actual_self.name,flush=True)
						actual_self.action = actions.special_action(f"Firestorm-{actual_self.name}",actual_self.firestorm_special_action_click)
						player.played.special_options.append(actual_self.action)
						return 0
					drawn.original_play_action = drawn.play_action
					drawn.firestorm_special_action_click = firestorm_special_action_click
					drawn.play_action = replace_play_action
		return 0

#DOne
class firestorm(card_frame.card):
	name = "Firestorm"
	vp = 2
	cost = 6
	ctype = cardtype.HERO
	text = 'Put the top card of your deck on your Super-Villain.\nThis card has the game text of each card on you\nSuper-Villain this turn.\n(At the end of the game, destroy those cards.)'
	image = "fe/images/cards/Firestorm.jpg"
	currently_played_by = None

	def play_action(self,player):
		#print(player,"AHAHAHAHAH")
		self.currently_played_by = player
		drawn = player.reveal_card(public = False)
		if drawn != None:
			player.over_superhero.contents.append(drawn.pop_self())
		#Should i remove the owner?
		total = 0
		assemble = player.over_superhero.contents.copy()
		for c in assemble:
			save_owner = c.owner
			c.set_owner(self.owner)
			total += c.play_action(player)
			#location = self.find_self()
			self.firestorm_find_and_replace(c,save_owner)
			#print(c.name,"firesotrm is ",self.find_self())
			#if self in player.ongoing.contents:
			#	location[0].contents.insert(location[1],self.pop_self())
			#put's locations and other cards back
			#if c not in player.over_superhero.contents:
			#	c.pop_self()
			#	player.over_superhero.contents.append(c)
		return total

	def get_ctype(self):
		if self.currently_played_by != None:
			temp_ctype = set()
			temp_ctype.add(self.ctype)
			assemble = self.currently_played_by.over_superhero.contents.copy()
			for c in assemble:
				temp_ctype.add(c.get_ctype())
			return temp_ctype
		else:
			return [self.ctype]

	def ctype_eq(self,ctype):
		if self.currently_played_by != None:
			are_they_equal = self.ctype == ctype
			assemble = self.currently_played_by.over_superhero.contents.copy()
			for c in assemble:
				are_they_equal = are_they_equal or c.ctype_eq(ctype)
			return are_they_equal
		else:
			return self.ctype == ctype

	def end_of_turn(self):
		if self.currently_played_by != None:
			assemble = self.currently_played_by.over_superhero.contents.copy()
			for c in assemble:
				save_owner = c.owner
				c.set_owner(self.owner)
				c.end_of_turn()
				self.firestorm_find_and_replace(c,save_owner)
			self.currently_played_by = None
		return

	def firestorm_find_and_replace(self,c,save_owner):
		
		#If it changed owners
		self.owner = c.owner
		#but give back original card
		c.set_owner(save_owner)
		if c not in self.currently_played_by.over_superhero.contents:
			location = c.find_self()
			#Firestorm cannot be made ongoing
			#Firestorm cannot be taken out of the destroyed pile
			if location[0].name != "Ongoing" and self.find_self()[0].name != "Destroyed":
				self.pop_self()
				location[0].contents.insert(location[1],self)
			self.currently_played_by.over_superhero.contents.append(c.pop_self())

	def destroy(self,by_player):
		self.currently_played_by = None
		super().destroy(by_player)


class giant_growth(card_frame.card):
	name = "Giant Growth"
	vp = 1
	cost = 2
	ctype = cardtype.SUPERPOWER
	text = "+2 Power"
	image = "fe/images/cards/Giant Growth.jpg"
	
	def play_action(self,player):
		return 2


class giganta(card_frame.card):
	name = "Giganta"
	vp = 1
	cost = 4
	ctype = cardtype.VILLAIN
	text = "+4 Power if there are no cards with cost 3 or\nless in your discard pile.\nOtherwise, +2 Power."
	image = "fe/images/cards/Giganta.jpg"
	
	def play_action(self,player):
		card_exists = False
		for c in player.discard.contents:
			if c.cost <= 3:
				player.played.plus_power(2)
				return 0
		player.played.plus_power(4)
		return 0

class grid(card_frame.card):
	name = "Grid"
	vp = 1
	cost = 2
	ctype = cardtype.VILLAIN
	text = "+1 Power\nYou may put a Villain or Equipment with cost 5 or\nless from your discard pile on top of your deck."
	image = "fe/images/cards/Grid.jpg"
	
	def play_action(self,player):
		player.played.plus_power(1)
		assemble = []
		for c in player.discard.contents:
			if c.cost <= 5 and (c.ctype_eq(cardtype.VILLAIN) or c.ctype_eq(cardtype.EQUIPMENT)):
				assemble.append(c)
		if len(assemble) > 0:
			instruction_text = "You may put a Villain or Equipment with cost 5 or\nless from your discard pile on top of your deck."
			result = effects.may_choose_one_of(instruction_text,player,assemble,ai_hint.BEST)
			if result != None:
				player.deck.contents.append(result.pop_self())
		return 0

class insanity(card_frame.card):
	name = "Insanity"
	vp = 1
	cost = 2
	ctype = cardtype.SUPERPOWER
	text = "If this is the first card you play this turn, each player passes a\ncard in his hand to the hand of the player on his left.\nDefense: You may discard this card to avoid an Attack. If you do,\nyou may put a card from your hand or discard pile into the\nattacker's hand."
	image = "fe/images/cards/Insanity.jpg"
	defense = True
	
	def play_action(self,player):
		if len(player.played.played_this_turn) == 0:
			cards_to_pass = []
			instruction_text = "Choose a card to pass to the hand of the player to your left."
			for p in globe.boss.players:
				if len(p.hand.contents) > 0:
					cards_to_pass.append(effects.choose_one_of(instruction_text,p,p.hand.contents,ai_hint.WORST))
					#Alerts any relevant persona powers (harly quin)
					p.persona.card_pass_power()
				else:
					cards_to_pass.append(None)
			for i,p in enumerate(globe.boss.players):
				current = cards_to_pass[i-1]
				if current != None:
					current.pop_self()
					current.set_owner(p)
					p.hand.contents.append(current)
		return 0



	def defend(self,defender = None,attacker = None):
		self.owner.discard_a_card(self)
		if attacker != None:
			assemble = []
			assemble.extend(self.owner.hand.contents)
			assemble.extend(self.owner.discard.contents)
			if len(assemble) > 0:
				instruction_text = f"You may put a card from your hand or discard pile into {attacker.persona.name}'s hand"
				result = effects.may_choose_one_of(instruction_text,self.owner,assemble,ai_hint.WORST)
				if result != None:
					result.pop_self()
					result.set_owner(attacker)
					attacker.hand.contents.append(result)
		return

class invulnerable(card_frame.card):
	name = "Invulnerable"
	vp = 1
	cost = 3
	ctype = cardtype.SUPERPOWER
	text = "+1 Power\nDefense: When you are attacked, you may reveal this card\nfrom your hand. If you do, you may discard it or destroy a\nVulnerability in your hand or discard pile to avoid\nan Attack"
	image = "fe/images/cards/Invulnerable.jpg"
	defense = True
	
	def play_action(self,player):
		player.played.plus_power(1)
		return 0

	def defend(self,defender = None,attacker = None):
		assemble = []
		for c in self.owner.hand.contents:
			if c.name == "Vulnerability":
				assemble.append(c)
		for c in self.owner.discard.contents:
			if c.name == "Vulnerability":
				assemble.append(c)
		if len(assemble) > 0:
			instruction_text = f"You may destroy a vunerability in your hand or discard pile.\nIf you choose not to, this card will be discarded."
			result = effects.may_choose_one_of(instruction_text,self.owner,assemble,ai_hint.RANDOM)
			if result != None:
				result.destroy(self.owner)
				return
		self.owner.discard_a_card(self)
		return


class johnny_quick(card_frame.card):
	name = "Johnny Quick"
	vp = 1
	cost = 2
	ctype = cardtype.VILLAIN
	text = "Draw a card"
	image = "fe/images/cards/Johnny Quick.jpg"
	
	def play_action(self,player):
		player.draw_card()
		return 0


class mallet(card_frame.card):
	name = "Mallet"
	vp = 1
	cost = 4
	ctype = cardtype.EQUIPMENT
	text = "Reveal the top card of your deck. Draw it or\npass it to any player's discard pile"
	image = "fe/images/cards/Mallet.jpg"
	
	def play_action(self,player):
		top_card = player.reveal_card()
		if top_card != None:
			instruction_text = f"Would you like to draw this card? If not, pass it to any players discard pile."
			if effects.ok_or_no(instruction_text,player,top_card,hint = ai_hint.IFGOOD):
				player.draw_card()
			else:
				instruction_text = f"Which players discard pile would you like to pass the {top_card.name} to?"
				result = effects.choose_a_player(instruction_text,player,includes_self = True,hint = ai_hint.WORST)
				top_card.pop_self()
				top_card.set_owner(result)
				result.discard.contents.append(top_card)
				player.persona.card_pass_power()
		return 0


class man_bat_serum(card_frame.card):
	name = "Man-Bat Serum"
	vp = 1
	cost = 3
	ctype = cardtype.EQUIPMENT
	text = "+Power equal to your VPs.\nIf you have 5 or more VPs, destroy this card\nat the end of your turn."
	image = "fe/images/cards/Man Bat Serum.jpg"
	destroy_by = None
	
	def play_action(self,player):
		self.destroy_by = None
		if player.vp >= 5:
			self.destroy_by = player
		player.played.plus_power(player.vp)
		return 0


	def end_of_turn(self):
		if self.destroy_by != None:
			self.destroy(self.destroy_by)
		return


class man_bat(card_frame.card):
	name = "Man-Bat Serum"
	vp = 1
	cost = 3
	ctype = cardtype.VILLAIN
	text = "+2 Power\nDefense: You may discard this card to avoid an Attack\nif you do, steal 1VP from the attacker."
	image = "fe/images/cards/Man Bat.jpg"
	defense = True
	
	def play_action(self,player):
		player.played.plus_power(2)
		return 0


	def defend(self,defender = None,attacker = None):
		#print(self.owner,defender,attacker,"THOSE ARE THE PPL")
		self.owner.discard_a_card(self)
		if attacker != None and attacker.vp > 0:
			self.owner.vp += 1
			attacker.vp -= 1
		return

class owlman(card_frame.card):
	name = "Owlman"
	vp = 2
	cost = 6
	ctype = cardtype.VILLAIN
	text = "You may destroy an Equipment in the Line-up.\n+1 Power for each different Equipment in the destroyed pile."
	image = "fe/images/cards/Owlman.jpg"
	
	def play_action(self,player):
		assemble = []
		for c in globe.boss.lineup.contents:
			if c.ctype_eq(cardtype.EQUIPMENT):
				assemble.append(c)
		if len(assemble) > 0:
			instruction_text = "You may destroy an Equipment in the Line-up."
			result = effects.may_choose_one_of(instruction_text,player,assemble,ai_hint.RANDOM)
			if result != None:
				result.destroy(player)
		unique_equipment = set()
		for c in globe.boss.destroyed_stack.contents:
			if c.ctype_eq(cardtype.EQUIPMENT):
				unique_equipment.add(c.name)
		player.played.plus_power(len(unique_equipment))
		return 0

class pandora(card_frame.card):
	name = "Pandora"
	vp = 2
	cost = 7
	ctype = cardtype.HERO
	text = "Add the top card of the main deck to the Line-Ip.\n\n+1 Power for each different cost among cards in the Line-Up."
	image = "fe/images/cards/Pandora.jpg"
	
	def play_action(self,player):
		card_to_add = globe.boss.main_deck.draw()
		if card_to_add != None:
			card_to_add.set_owner(owners.LINEUP)
			globe.boss.lineup.add(card_to_add)
		unique_cost = set()
		for c in globe.boss.lineup.contents:
			unique_cost.add(c.cost)
		player.played.plus_power(len(unique_cost))
		return 0

class pandoras_box(card_frame.card):
	name = "Pandora's Box"
	vp = 1
	cost = 2
	ctype = cardtype.EQUIPMENT
	text = "Reveal the top card of the main deck. Add\ncards from the main deck to the Line-Up\nequal to the revealed card's cost."
	image = "fe/images/cards/Pandoras Box.jpg"
	
	def play_action(self,player):
		if len(globe.boss.main_deck.contents) > 0:
			revealed_card = globe.boss.main_deck.contents[-1]
			effects.reveal("This was on top of the main deck.",player,[revealed_card])
			for i in range(revealed_card.cost):
				adding = globe.boss.main_deck.draw()
				if adding != None:
					adding.set_owner(owners.LINEUP)
					globe.boss.lineup.contents.append(adding)

		return 0

class phantom_stranger(card_frame.card):
	name = "Phantom Stranger"
	vp = '10*'
	cost = 5
	ctype = cardtype.HERO
	text = "You may destroy a card in your hand and you may destroy\na card in your discard pile.\nAt the end of the game this card is worth 10VP  minus 1VP for each\ncard with cost 0 in your deck. (Minimum 0.)"
	image = "fe/images/cards/Phantom Stranger.jpg"
	
	def play_action(self,player):
		if len(player.hand.contents) > 0:
			instruction_text = "You may destroy a card in your hand."
			result = effects.may_choose_one_of(instruction_text,player,player.hand.contents,ai_hint.IFBAD)
			if result != None:
				result.destroy(player)
		if len(player.discard.contents) > 0:
			instruction_text = "You may destroy a card in your discard pile."
			result = effects.may_choose_one_of(instruction_text,player,player.discard.contents,ai_hint.IFBAD)
			if result != None:
				result.destroy(player)
		return 0


	def calculate_vp(self,all_cards):
		count = 0
		for c in all_cards:
			if c.cost == 0:
				count += 1
		return max(0,10-count)

class power_armor(card_frame.card):
	name = "Power Armor"
	vp = 3
	cost = 8
	ctype = cardtype.EQUIPMENT
	text = "+3 Power\nDefense: You may reveal this card from your hand to\navoid an Attack. If you do, you may destroy a card in\nyour hand or discard pile."
	image = "fe/images/cards/Power Armor.jpg"
	defense = True
	
	def play_action(self,player):
		player.played.plus_power(3)
		return 0


	def defend(self,defender = None,attacker = None):
		assemble = []
		assemble.extend(self.owner.hand.contents)
		assemble.extend(self.owner.discard.contents)
		if len(assemble) > 0:
			instruction_text = "You may destroy a card in your hand or discard pile."
			result = effects.may_choose_one_of(instruction_text,self.owner,assemble,ai_hint.IFBAD)
		return

class power_drain(card_frame.card):
	name = "Power Drain"
	vp = 1
	cost = 4
	ctype = cardtype.SUPERPOWER
	text = "+2 Power and choose a foe."
	attack = True
	attack_text = "Attack:: That foe reveals his hand. Choose one\ncard revealed this way to be discarded."
	image = "fe/images/cards/Power Drain.jpg"
	
	def play_action(self,player):
		player.played.plus_power(2)
		self.attack_action(player)
		return 0

	def attack_action(self,by_player):
		player = effects.choose_a_player("Choose a foe to attack",by_player,includes_self = False)
		if effects.attack(player,self,by_player) and len(player.hand.contents) > 0:
			instruction_text = f"Choose a card to be discarded from {player.persona.name}'s hand"
			result = effects.choose_one_of(instruction_text,by_player,player.hand.contents,ai_hint.BEST)
			player.discard_a_card(result)
		return


class power_girl(card_frame.card):
	name = "Power Girl"
	vp = 2
	cost = 5
	ctype = cardtype.HERO
	text = "+3 Power"
	image = "fe/images/cards/Power Girl.jpg"
	
	def play_action(self,player):
		player.played.plus_power(3)
		return 0



class power_ring(card_frame.card):
	name = "Power Ring"
	vp = 2
	cost = 6
	ctype = cardtype.VILLAIN
	text = "You may destroy a HERO in the Line-up.\n+1 Power for each different HERO in the destroyed pile."
	image = "fe/images/cards/Power Ring 6.jpg"
	
	def play_action(self,player):
		assemble = []
		for c in globe.boss.lineup.contents:
			if c.ctype_eq(cardtype.HERO):
				assemble.append(c)
		if len(assemble) > 0:
			instruction_text = "You may destroy an Hero in the Line-up."
			result = effects.may_choose_one_of(instruction_text,player,assemble,ai_hint.RANDOM)
			if result != None:
				result.destroy(player)
		unique_hero = set()
		for c in globe.boss.destroyed_stack.contents:
			if c.ctype_eq(cardtype.HERO):
				unique_hero.add(c.name)
		player.played.plus_power(len(unique_hero))
		return 0

class royal_flush_gang(card_frame.card):
	name = "Royal Flush Glang"
	vp = 0
	cost = 5
	ctype = cardtype.VILLAIN
	text = "Draw two cards, and then discard two cards.\nGain 1 VP for each other Royal Flush Gang\nyou have played this turn."
	image = "fe/images/cards/Royal Flush Gang.jpg"
	
	def play_action(self,player):
		player.draw_card(2)
		for i in range(2):
			if len(player.hand.contents) > 0:
				instruction_text = f"Choose a card to discard ({i+1}/2)"
				result = effects.choose_one_of(instruction_text,player,player.hand.contents,ai_hint.WORST)
				player.discard_a_card(result)

		count = 0
		for c in player.played.played_this_turn:
			if c != self and c.name == "Royal Flush Glang":
				count += 1
		player.gain_vp(count)
		return 0


class secret_society_communicator(card_frame.card):
	name = "Secret Society Communicator"
	vp = 1
	cost = 4
	ctype = cardtype.EQUIPMENT
	text = "You may destroy a card in your hand or discard\npile. If it's a Hero, +Power equal to its cost.\nIf you choose not to, +2 Power"
	image = "fe/images/cards/Secret Society Communicator.jpg"
	
	def play_action(self,player):
		assemble = []
		assemble.extend(player.hand.contents)
		assemble.extend(player.discard.contents)
		if len(assemble) > 0:
			result = effects.may_choose_one_of(self.text,player,assemble,ai_hint.IFBAD)
			if result != None:
				result.destroy(player)
				if result.ctype_eq(cardtype.HERO):
					player.played.plus_power(result.cost)
				return 0
		player.played.plus_power(2)
		return 0

class sledgehammer(card_frame.card):
	name = "Sledgehammer"
	vp = 1
	cost = 3
	ctype = cardtype.EQUIPMENT
	text = "You may destroy a non-Equipment card in\nyour hand or discard pile. If its cost is 1 or\ngreater, gain 1VP."
	image = "fe/images/cards/Sledgehammer.jpg"
	
	def play_action(self,player):
		assemble = []
		for c in player.hand.contents:
			if not c.ctype_eq(cardtype.EQUIPMENT):
				assemble.append(c)
		for c in player.discard.contents:
			if not c.ctype_eq(cardtype.EQUIPMENT):
				assemble.append(c)
		if len(assemble) > 0:
			result = effects.may_choose_one_of(self.text,player,assemble,ai_hint.IFBAD)
			if result != None:
				result.destroy(player)
				if result.cost >= 1:
					player.gain_vp(1)
		return 0


class stargirl(card_frame.card):
	name = "Stargirl"
	vp = 1
	cost = 4
	ctype = cardtype.HERO
	text = "+2 Power\nDefense: You may discard this card to avoid an Attack.  if you\ndo, draw a card and put a card with cost 1 or greater from the\ndestroyed pile on the bottom of the main deck."
	image = "fe/images/cards/Star Girl.jpg"
	defense = True
	
	def play_action(self,player):
		player.played.plus_power(2)
		return 0


	def defend(self,defender = None,attacker = None):
		self.owner.discard_a_card(self)
		self.owner.draw_card()
		assemble = []
		for c in globe.boss.destroyed_stack.contents:
			if c.cost >= 1:
				assemble.append(c)
		if len(assemble) > 0:
			instruction_text = "Put a card with cost 1 or greater on the bottom of the main deck."
			result = effects.choose_one_of(instruction_text,self.owner,assemble,ai_hint.RANDOM)
			result.pop_self()
			result.set_owner(owners.MAINDECK)
			globe.boss.main_deck.contents.insert(0,result)
		return


class steel(card_frame.card):
	name = "Steel"
	vp = 1
	cost = 3
	ctype = cardtype.HERO
	text = "You may destroy a non-Hero card in\nyour hand or discard pile. If its cost is 1 or\ngreater, gain 1VP."
	image = "fe/images/cards/Steel.jpg"
	
	def play_action(self,player):
		assemble = []
		for c in player.hand.contents:
			if not c.ctype_eq(cardtype.HERO):
				assemble.append(c)
		for c in player.discard.contents:
			if not c.ctype_eq(cardtype.HERO):
				assemble.append(c)
		if len(assemble) > 0:
			result = effects.may_choose_one_of(self.text,player,assemble,ai_hint.IFBAD)
			if result != None:
				result.destroy(player)
				if result.cost >= 1:
					player.gain_vp(1)
		return 0


class steve_trevor(card_frame.card):
	name = "Steve Trevor"
	vp = 0
	cost = 1
	ctype = cardtype.HERO
	text = "When you destroy this card in any zone, draw\ntwo cards, and then discard a card."
	image = "fe/images/cards/Steve Trevor.jpg"
	
	def destroy(self,player_responsible):
		player_responsible.draw_card(2)
		assemble = player_responsible.hand.contents.copy()
		if self in assemble:
			assemble.remove(self)
		result = effects.choose_one_of("Choose a card to discard",player_responsible,assemble,ai_hint.WORST)
		player_responsible.discard_a_card(result)
		super().destroy(player_responsible)


class super_intellect(card_frame.card):
	name = "Super Intellect"
	vp = 1
	cost = 4
	ctype = cardtype.SUPERPOWER
	text = "You may destroy a card in your hand or discard\npile. If it's an Equipment, +Power equal to its cost.\nIf you choose not to, +2 Power"
	image = "fe/images/cards/Super Intellect.jpg"
	
	def play_action(self,player):
		assemble = []
		assemble.extend(player.hand.contents)
		assemble.extend(player.discard.contents)
		if len(assemble) > 0:
			result = effects.may_choose_one_of(self.text,player,assemble,ai_hint.IFBAD)
			if result != None:
				result.destroy(player)
				if result.ctype_eq(cardtype.EQUIPMENT):
					player.played.plus_power(result.cost)
				return 0
		player.played.plus_power(2)
		return 0


class superwoman(card_frame.card):
	name = "Superwoman"
	vp = 3
	cost = 7
	ctype = cardtype.VILLAIN
	text = "You may destroy a VILLAIN in the Line-up.\n+1 Power for each different Villain in the\ndestroyed pile."
	image = "fe/images/cards/Superwoman.jpg"
	
	def play_action(self,player):
		assemble = []
		for c in globe.boss.lineup.contents:
			if c.ctype_eq(cardtype.VILLAIN):
				assemble.append(c)
		if len(assemble) > 0:
			instruction_text = "You may destroy an Villain in the Line-up."
			result = effects.may_choose_one_of(instruction_text,player,assemble,ai_hint.RANDOM)
			if result != None:
				result.destroy(player)
		unique_villain = set()
		for c in globe.boss.destroyed_stack.contents:
			if c.ctype_eq(cardtype.VILLAIN):
				unique_villain.add(c.name)
		player.played.plus_power(len(unique_villain))
		return 0


class the_blight(card_frame.card):
	name = "The Blight"
	vp = 1
	cost = 4
	ctype = cardtype.VILLAIN
	text = "You may destroy a card in your hand or discard\npile. If it's a Super Power, +Power equal to its cost.\nIf you choose not to, +2 Power"
	image = "fe/images/cards/The Blight.jpg"
	
	def play_action(self,player):
		assemble = []
		assemble.extend(player.hand.contents)
		assemble.extend(player.discard.contents)
		if len(assemble) > 0:
			result = effects.may_choose_one_of(self.text,player,assemble,ai_hint.IFBAD)
			if result != None:
				result.destroy(player)
				if result.ctype_eq(cardtype.SUPERPOWER):
					player.played.plus_power(result.cost)
				return 0
		player.played.plus_power(2)
		return 0


class transmutation(card_frame.card):
	name = "Transmutation"
	vp = 1
	cost = 5
	ctype = cardtype.SUPERPOWER
	text = "Destroy a card in your hand or discard pile and gain 1\nVP.  You may gain a card from the Line-Up of equal or\nlesser cost than the card destroyed this way."
	image = "fe/images/cards/Transmutation.jpg"
	
	def play_action(self,player):
		assemble = []
		assemble.extend(player.hand.contents)
		assemble.extend(player.discard.contents)
		player.gain_vp(1)
		if len(assemble) > 0:
			result = effects.choose_one_of(self.text,player,assemble,ai_hint.RANDOM)
			result.destroy(player)
			assemble = []
			for c in globe.boss.lineup.contents:
				if c.cost <= result.cost:
					assemble.append(c)
			result = effects.may_choose_one_of(f"you may gain a card from the lineup of cost {result.cost} or less",player,assemble,ai_hint.BEST)
			if result != None:
				player.gain(result)
		return 0


class ultra_strength(card_frame.card):
	name = "Ultra ultra_strength"
	vp = 3
	cost = 9
	ctype = cardtype.SUPERPOWER
	text = "+3 Power and draw two cars."
	image = "fe/images/cards/Ultra Strength.jpg"
	
	def play_action(self,player):
		player.played.plus_power(3)
		player.draw_card(2)
		return 0


class ultraman(card_frame.card):
	name = "Ultraman"
	vp = 3
	cost = 8
	ctype = cardtype.VILLAIN
	text = "You may destroy a card in the Line-up.\n+1 Power for each different Super Power in the destroyed pile."
	image = "fe/images/cards/Ultraman.jpg"
	
	def play_action(self,player):
		if len(globe.boss.lineup.contents) > 0:
			instruction_text = "You may destroy a card in the Line-up."
			result = effects.may_choose_one_of(instruction_text,player,globe.boss.lineup.contents,ai_hint.RANDOM)
			if result != None:
				result.destroy(player)
		unique_superpower= set()
		for c in globe.boss.destroyed_stack.contents:
			if c.ctype_eq(cardtype.SUPERPOWER):
				unique_superpower.add(c.name)
		player.played.plus_power(len(unique_superpower))
		return 0


class venom_injector(card_frame.card):
	name = "Venom Injector"
	vp = 0
	cost = 1
	ctype = cardtype.EQUIPMENT
	text = "When you destroy this card in any zone, +2 Power."
	image = "fe/images/cards/Venom Injector 1.jpg"
	
	def destroy(self,player_responsible):
		player_responsible.played.plus_power(2)
		super().destroy(player_responsible)



class vibe(card_frame.card):
	name = "Vibe"
	vp = 1
	cost = 2
	ctype = cardtype.HERO
	text = "+1 Power\nYou may put a Hero or Super Power with cost 5 or\nless from your discard pile on top of your deck."
	image = "fe/images/cards/Vibe.jpg"
	
	def play_action(self,player):
		player.played.plus_power(1)
		assemble = []
		for c in player.discard.contents:
			if c.cost <= 5 and (c.ctype_eq(cardtype.HERO) or c.ctype_eq(cardtype.SUPERPOWER)):
				assemble.append(c)
		if len(assemble) > 0:
			instruction_text = "You may put a Hero or Super Power with cost 5 or\nless from your discard pile on top of your deck."
			result = effects.may_choose_one_of(instruction_text,player,assemble,ai_hint.BEST)
			if result != None:
				player.deck.contents.append(result.pop_self())
		return 0


class word_of_power(card_frame.card):
	name = "Word Of Power"
	vp = 0
	cost = 1
	ctype = cardtype.SUPERPOWER
	text = "When you destroy this card in any zone, you\npay 4 less to defeat Super Heros this turn."
	image = "fe/images/cards/Word of Power.jpg"

	def trigger(self,ttype,data,player,active,immediate):
		if globe.DEBUG:
			print("test",self.name,flush=True)
		if trigger.test(immediate,\
						trigger.PRICE, \
						self.trigger, \
						player,ttype) \
				and data[1].owner_type == owners.VILLAINDECK:
			if globe.DEBUG:
				print("active",self.name,flush=True)
			return data[0] - 4
	
	def destroy(self,player_responsible):
		player.triggers.append(self.trigger)
		super().destroy(player_responsible)


####LOCATIONS

class belle_reve(card_frame.card):
	name = "Belle Reve"
	vp = 1
	cost = 5
	ctype = cardtype.LOCATION
	text = "Ongoing: +1 Power for each Villain you play."
	image = "fe/images/cards/Belle Reve.jpg"
	ongoing = True

	def trigger(self,ttype,data,player,active,immediate):
		if globe.DEBUG:
			print("test",self.name,flush=True)
		if trigger.test(not immediate,\
						trigger.PLAY, \
						self.trigger, \
						player,ttype) \
				and data[0].ctype_eq(cardtype.VILLAIN):
			if globe.DEBUG:
				print("active",self.name,flush=True)
			player.played.plus_power(1)

	
	
	def play_action(self,player):
		if self not in player.ongoing.contents:
			player.ongoing.add(self.pop_self())
		player.triggers.append(self.trigger)
		return 0

class blackgate_prison(card_frame.card):
	name = "Blackgate Prison"
	vp = 1
	cost = 4
	ctype = cardtype.LOCATION
	text = "Ongoing: Once during each of your turns, reveal the top\ncard of your deck.  If it's a Vulnerability or\nWeakness, destroy it and gain 1 VP."
	image = "fe/images/cards/Blackgate Prison.jpg"
	ongoing = True
	action = None

	def special_action_click(self,player):
		revealed = player.reveal_card()
		if revealed != None and revealed.name == "Vulnerability" or revealed.name == "Weakness":
			revealed.destroy(player)
			player.gain_vp(1)
		player.played.special_options.remove(self.action)
	
	
	def play_action(self,player):
		if self not in player.ongoing.contents:
			player.ongoing.add(self.pop_self())
		#player.played.card_mods.append(self.location_mod)
		self.action = actions.special_action("Blackgate\n  Prison",self.special_action_click)
		player.played.special_options.append(self.action)
		return 0

class central_city(card_frame.card):
	name = "Central City"
	vp = 1
	cost = 5
	ctype = cardtype.LOCATION
	text = "Ongoing: +1 Power for each non-Kick Super Power you play."
	image = "fe/images/cards/Central City.jpg"
	ongoing = True

	def trigger(self,ttype,data,player,active,immediate):
		if globe.DEBUG:
			print("test",self.name,flush=True)
		if trigger.test(not immediate,\
						trigger.PLAY, \
						self.trigger, \
						player,ttype) \
				and data[0].ctype_eq(cardtype.SUPERPOWER) \
				and data[0].name != "Kick":
			if globe.DEBUG:
				print("active",self.name,flush=True)
			player.played.plus_power(1)
	
	
	def play_action(self,player):
		if self not in player.ongoing.contents:
			player.ongoing.add(self.pop_self())
		player.triggers.append(self.trigger)
		return 0

class earth_3(card_frame.card):
	name = "Earth-3"
	vp = 1
	cost = 6
	ctype = cardtype.LOCATION
	text = "Ongoing: Once during each of your turns, reveal the top\ncard of your deck.  If it's a Punch or\nWeakness, destroy it and gain 1 VP."
	image = "fe/images/cards/Earth 3.jpg"
	ongoing = True
	action = None

	def special_action_click(self,player):
		revealed = player.reveal_card()
		if revealed != None and revealed.name == "Punch":
			revealed.destroy(player)
			player.gain_vp(1)
		player.played.special_options.remove(self.action)
	
	
	def play_action(self,player):
		if self not in player.ongoing.contents:
			player.ongoing.add(self.pop_self())
		#player.played.card_mods.append(self.location_mod)
		self.action = actions.special_action("Earth-3",self.special_action_click)
		player.played.special_options.append(self.action)
		return 0

class happy_harbor(card_frame.card):
	name = "Happy Harbor"
	vp = 1
	cost = 5
	ctype = cardtype.LOCATION
	text = "Ongoing: +1 Power for each Hero you play."
	image = "fe/images/cards/Happy Harbor.jpg"
	ongoing = True

	def trigger(self,ttype,data,player,active,immediate):
		if globe.DEBUG:
			print("test",self.name,flush=True)
		if trigger.test(not immediate,\
						trigger.PLAY, \
						self.trigger, \
						player,ttype) \
				and data[0].ctype_eq(cardtype.HERO):
			if globe.DEBUG:
				print("active",self.name,flush=True)
			player.played.plus_power(1)
	
	
	def play_action(self,player):
		if self not in player.ongoing.contents:
			player.ongoing.add(self.pop_self())
		player.triggers.append(self.trigger)
		return 0

class star_labs(card_frame.card):
	name = "S.T.A.R. Labs"
	vp = 1
	cost = 5
	ctype = cardtype.LOCATION
	text = "Ongoing: +1 Power for each Equipment you play."
	image = "fe/images/cards/Star Labs.jpg"
	ongoing = True

	def trigger(self,ttype,data,player,active,immediate):
		if globe.DEBUG:
			print("test",self.name,flush=True)
		if trigger.test(not immediate,\
						trigger.PLAY, \
						self.trigger, \
						player,ttype) \
				and data[0].ctype_eq(cardtype.EQUIPMENT):
			if globe.DEBUG:
				print("active",self.name,flush=True)
			player.played.plus_power(1)
	
	
	def play_action(self,player):
		if self not in player.ongoing.contents:
			player.ongoing.add(self.pop_self())
		player.triggers.append(self.trigger)
		return 0




#SuperVillains
class aquaman(card_frame.card):
	name = "Aquaman"
	vp = 6
	cost = 11
	ctype = cardtype.HERO
	owner_type = owners.VILLAINDECK
	text = "You may put up to three cards from your discard pile on top of your\ndeck. If you choose not to, +3 Power."
	image = "fe/images/cards/Aquaman 11.jpg"
	attack_text = "First Appearance - Attack:: Each player puts four cards with\ncost 0 from his discard pile on top of his deck. If you put none\nthere, gain a Weakness."
	
	def play_action(self,player):
		number_put = 0
		#Initialize it to something other than None
		result = False
		while result != None and number_put < 3:
			#print("Loop1",flush = True)
			if len(player.discard.contents) > 0:
				instruction_text = f"You may put a card from your discard pile on top of your deck.\nIf you choose not to put any, +3 Power. ({number_put+1}/3)"
				result = effects.may_choose_one_of(instruction_text,player,player.discard.contents,ai_hint.IFGOOD)
				if result != None:
					number_put += 1
					result.pop_self()
					player.deck.contents.append(result)
			else:
				result = None
		if number_put == 0:
			player.played.plus_power(3)
		return 0


	def first_apearance(self):
		for p in globe.boss.players:
			if effects.attack(p,self):
				assemble = []
				for c in p.discard.contents:
					if c.cost == 0:
						assemble.append(c)
				if len(assemble) != 0:
					for i in range(4):
						if len(assemble) != 0:
							instruction_text = f"Put a card of cost 0 from your discard ontop of your deck ({i+1}/4)"
							result = effects.choose_one_of(instruction_text,p,assemble,ai_hint.BEST)
							result.pop_self()
							assemble.remove(result)
							p.deck.contents.append(result)
				else:
					p.gain_a_weakness()
		return


class batman(card_frame.card):
	name = "Batman"
	vp = 6
	cost = 11
	ctype = cardtype.HERO
	owner_type = owners.VILLAINDECK
	text = "You may play up to three Equipment with cost 6 or less from the\ndestroyed pile, and then put them on the bottom of the main deck.\nIf you choose not to, +3 Power."
	image = "fe/images/cards/Batman 11.jpg"
	attack_text = "First Appearance - Attack:: Each player destroys an Equipment in\nhis hand or discard pile. If you cannot, gain a Weakness."
	
	def play_action(self,player):
		assemble = []
		for c in globe.boss.destroyed_stack.contents:
			if c.ctype_eq(cardtype.EQUIPMENT) and c.cost <= 6:
				assemble.append(c)


		number_put = 0
		#Initialize it to something other than None
		result = False
		while result != None and number_put < 3:
			#print("Loop2",flush = True)
			if len(assemble) > 0:
				instruction_text = f"You may up to three Equipment of cost 6 or less from the destroyed pile. If you choose to play none, +3 Power ({number_put+1}/3)"
				result = effects.may_choose_one_of(instruction_text,player,assemble,ai_hint.IFGOOD)
				if result != None:
					number_put += 1
					#I should make a better play and return function
					player.played.play(result.pop_self())
					assemble.remove(result)
					result.pop_self()
					result.set_owner(owners.MAINDECK)
					globe.boss.main_deck.insert(0,result)
					assemble.remove(result)
			else:
				result = None
		if number_put == 0:
			player.played.plus_power(3)
		return 0


	def first_apearance(self):
		for p in globe.boss.players:
			if effects.attack(p,self):
				assemble = []
				for c in p.hand.contents:
					if c.ctype_eq(cardtype.EQUIPMENT):
						assemble.append(c)
				for c in p.discard.contents:
					if c.ctype_eq(cardtype.EQUIPMENT):
						assemble.append(c)
				if len(assemble) != 0:
					instruction_text = f"Destroy an Equipment in your hand or discard pile."
					result = effects.choose_one_of(instruction_text,p,assemble,ai_hint.WORST)
					result.destroy(p)
				else:
					p.gain_a_weakness()
		return



class constantine(card_frame.card):
	name = "Constantine"
	vp = 5
	cost = 10
	ctype = cardtype.HERO
	owner_type = owners.VILLAINDECK
	text = "Reveal the top three cards of your deck. Draw one, destroy one, and put\none on top of your deck. Gain VPs equal to the destroyed cards VP value."
	image = "fe/images/cards/Constantine 10.jpg"
	attack_text = "First Appearance - Attack:: Each player loses 3VPs. If you have\nnone to lose, gain a Weakness."
	
	def play_action(self,player):
		assemble = []
		for i in range(3):
			to_add = player.reveal_card(public = False)
			if to_add != None:
				assemble.append(to_add)
				#I take the card off to get fresh cards properly (the shuffling the discard pile if neccessary)
				player.deck.contents.pop()
		# I put the cards back, otherwise they cannot be destroyed because they cannot be found, +the last card has to go back anyways
		if len(assemble) > 0:
			player.deck.contents.extend(assemble)
			effects.reveal(f"These were the top 3 cards on {player.persona.name}'s deck",player,assemble)
			result = effects.choose_one_of("Choose one of these to draw.",player,assemble,ai_hint.BEST)
			assemble.remove(result)
			result.pop_self()
			player.hand.contents.append(result)
		if len(assemble) > 0:
			result = effects.choose_one_of("Choose one of these to destroy.  You will gain the destroyed costs VP value.",player,assemble,ai_hint.WORST)
			vp_to_gain = result.vp
			#Ive seen conflicting ruling on wether 10* is 10 or 3
			if isinstance(vp_to_gain, str):
				vp_to_gain = 3
			#if vp_to_gain == '*':
			#	vp_to_gain = 3
			#elif isinstance(vp_to_gain, str):
			#	vp_to_gain = vp_to_gain.replace('*','')
			#	try:
			#		vp_to_gain = int(vp_to_gain)
			#	except:
			#		if globe.DEBUG:
			#			print(f"Error converting {vp_to_gain} to an int, defaulting to 3.")
			#		vp_to_gain = 3
			else:
				vp_to_gain = result.vp
			player.gain_vp(vp_to_gain)
			result.destroy(player)
		#The last card stays on the top of the deck
		return 0


	def first_apearance(self):
		for p in globe.boss.players:
			if effects.attack(p,self):
				if p.vp == 0:
					p.gain_a_weakness()
				else:
					p.vp = max(0,p.vp-3)
		return


class cyborg(card_frame.card):
	name = "Cyborg"
	vp = 5
	cost = 10
	ctype = cardtype.HERO
	owner_type = owners.VILLAINDECK
	text = "+2 Power for each Super Power and Equipment you play or have\nplayed this turn."
	image = "fe/images/cards/Cyborg 10.jpg"
	attack_text = "First Appearance - Attack:: Each player discards a Super\nPower and an Equipment. If you discard no cards, gain a Weakness."


	def trigger(self,ttype,data,player,active,immediate):
		if globe.DEBUG:
			print("test",self.name,flush=True)
		if trigger.test(not immediate,\
						trigger.PLAY, \
						self.trigger, \
						player,ttype) \
				and (data[0].ctype_eq(cardtype.SUPERPOWER) \
				or data[0].ctype_eq(cardtype.EQUIPMENT)):
			if globe.DEBUG:
				print("active",self.name,flush=True)
			player.played.plus_power(2)

	def play_action(self,player):
		so_far_power = 0
		for c in player.played.played_this_turn:
			if c.ctype_eq(cardtype.SUPERPOWER) \
					or c.ctype_eq(cardtype.EQUIPMENT):
				so_far_power += 2
		player.played.plus_power(so_far_power)
		player.triggers.append(self.trigger)
		return 0


	def first_apearance(self):
		for p in globe.boss.players:
			if effects.attack(p,self):
				card_discarded = False
				assemble = []
				for c in p.hand.contents:
					if c.ctype_eq(cardtype.SUPERPOWER):
						assemble.append(c)
				if len(assemble) > 0:
					result = effects.choose_one_of("Discard a Super Power",p,assemble,ai_hint.WORST)
					card_discarded = True

				assemble = []
				for c in p.hand.contents:
					if c.ctype_eq(cardtype.EQUIPMENT):
						assemble.append(c)
				if len(assemble) > 0:
					result = effects.choose_one_of("Discard a Super Power",p,assemble,ai_hint.WORST)
					card_discarded = True

				if not card_discarded:
					p.gain_a_weakness()
		return


class green_arrow(card_frame.card):
	name = "Green Arrow"
	vp = 5
	cost = 9
	ctype = cardtype.HERO
	owner_type = owners.VILLAINDECK
	text = "When you play this card, leave it in front of you for the rest of the game.\nOngoing: Punch cards your play have an additional +1 Power."
	image = "fe/images/cards/Green Arrow 9.jpg"
	attack_text = "First Appearance - Attack:: Each player discards two Punch\ncards. For each Punch you fail ti discard, gain a Weakness."

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
			player.played.plus_power(1)
	
	
	def play_action(self,player):
		if self not in player.ongoing.contents:
			player.ongoing.add(self.pop_self())
		player.triggers.append(self.trigger)
		return 0

	def first_apearance(self):
		for p in globe.boss.players:
			if effects.attack(p,self):
				assemble = []
				for c in p.hand.contents:
					if c.name == "Punch":
						assemble.append(c)
				discarded = 0
				while len(assemble) > 0 and discarded < 2:
					#print("Loop3",flush = True)
					p.discard_a_card(assemble.pop())
					discarded += 1
				while discarded < 2:
					#print("Loop4",flush = True)
					p.gain_a_weakness()
					discarded += 1
		return


class green_lantern(card_frame.card):
	name = "Green Lantern"
	vp = 6
	cost = 11
	ctype = cardtype.HERO
	owner_type = owners.VILLAINDECK
	text = "You may play up to three Heros with a cost of 6 or less\nfrom the destroyed pile,\nand then put them on the bottom of the main deck.\nIf you choose not to, +3 Power"
	image = "fe/images/cards/Green Lantern.jpg"
	attack_text = "First Appearance - Attack:: Each player destroys a Hero in his hand or discard pile. If you cannot, gain a Weakness"
	
	def play_action(self,player):
		assemble = []
		for c in globe.boss.destroyed_stack.contents:
			if c.ctype_eq(cardtype.HERO) and c.cost <= 6:
				assemble.append(c)


		number_put = 0
		#Initialize it to something other than None
		result = False
		while result != None and number_put < 3:
			#print("Loop5",flush = True)
			if len(assemble) > 0:
				instruction_text = f"You may up play to three Heros of cost 6 or less from the destroyed pile. If you choose to play none, +3 Power ({number_put+1}/3)"
				result = effects.may_choose_one_of(instruction_text,player,assemble,ai_hint.IFGOOD)
				if result != None:
					number_put += 1
					#I should make a better play and return function
					player.played.play(result.pop_self())
					result.pop_self()
					result.set_owner(owners.MAINDECK)
					globe.boss.main_deck.contents.insert(0,result)
					assemble.remove(result)
			else:
				result = None
		if number_put == 0:
			player.played.plus_power(3)
		return 0


	def first_apearance(self):
		for p in globe.boss.players:	
			if effects.attack(p,self):
				assemble = []
				for c in p.hand.contents:
					if c.ctype_eq(cardtype.HERO):
						assemble.append(c)
				for c in p.discard.contents:
					if c.ctype_eq(cardtype.HERO):
						assemble.append(c)
				if len(assemble) != 0:
					instruction_text = f"Destroy a Hero in your hand or discard pile."
					result = effects.choose_one_of(instruction_text,p,assemble,ai_hint.WORST)
					result.destroy(p)
				else:
					p.gain_a_weakness()
		return


class martian_manhunter(card_frame.card):
	name = "Martian Manhunter 12"
	vp = 6
	cost = 12
	ctype = cardtype.HERO
	owner_type = owners.VILLAINDECK
	text = "+2 Power for each Hero and Villain you play or have\nplayed this turn."
	image = "fe/images/cards/Martian Manhunter 12.jpg"
	attack_text = "First Appearance - Attack:: Each player discards a\nHero and a Villain. If you discard no cards, gain a Weakness."
	
	def trigger(self,ttype,data,player,active,immediate):
		if globe.DEBUG:
			print("test",self.name,flush=True)
		if trigger.test(not immediate,\
						trigger.PLAY, \
						self.trigger, \
						player,ttype) \
				and (data[0].ctype_eq(cardtype.HERO) \
				or data[0].ctype_eq(cardtype.VILLAIN)):
			if globe.DEBUG:
				print("active",self.name,flush=True)
			player.played.plus_power(2)

	def play_action(self,player):
		so_far_power = 0
		for c in player.played.played_this_turn:
			if c.ctype_eq(cardtype.HERO) or c.ctype_eq(cardtype.VILLAIN):
				so_far_power += 2
		player.played.plus_power(so_far_power)
		player.triggers.append(self.trigger)
		return 0


	def first_apearance(self):
		for p in globe.boss.players:
			if effects.attack(p,self):
				card_discarded = False
				assemble = []
				for c in p.hand.contents:
					if c.ctype_eq(cardtype.HERO):
						assemble.append(c)
				if len(assemble) > 0:
					result = effects.choose_one_of("Discard a Hero",p,assemble,ai_hint.WORST)
					p.discard_a_card(result)
					card_discarded = True

				assemble = []
				for c in p.hand.contents:
					if c.ctype_eq(cardtype.VILLAIN):
						assemble.append(c)
				if len(assemble) > 0:
					result = effects.choose_one_of("Discard a Villain",p,assemble,ai_hint.WORST)
					p.discard_a_card(result)
					card_discarded = True

				if not card_discarded:
					p.gain_a_weakness()
		return


class shazam(card_frame.card):
	name = "Shazam"
	vp = 6
	cost = 12
	ctype = cardtype.HERO
	owner_type = owners.VILLAINDECK
	text = "Gain the top two cards of the main deck, play them, and then\ndestroy one of them. (Its effects remain)."
	image = "fe/images/cards/Shazam 12.jpg"
	attack_text = "First Appearance - Attack:: Each player puts a card with\ncost 5 or greater from his hand or discard pile on the bottom of\nthe main deck. If you cannot, gain a Weakness."
	
	def play_action(self,player):
		assemble = []
		#Step 1, gain the top 2 cards of the main deck
		for i in range(2):
			new_card = globe.boss.main_deck.reveal()
			if new_card != None:
				player.gain(new_card)
				assemble.append(new_card)
		#Step 2, play them
		for c in assemble:
			if c.find_self()[0] == player.discard:
				player.played.play(c.pop_self())
		#step 3, destroy one of them
		if len(assemble) > 0:
			result = effects.choose_one_of("Destroy one of the cards that you just gained.",player,assemble,ai_hint.WORST)
			result.destroy(player)
		return 0


	def first_apearance(self):
		for p in globe.boss.players:
			if effects.attack(p,self):
				assemble = []
				for c in p.hand.contents:
					if c.cost >= 5:
						assemble.append(c)
				for c in p.discard.contents:
					if c.cost >= 5:
						assemble.append(c)
				if len(assemble) > 0:
					result = effects.choose_one_of("Choose a card to put on the bottom of the main deck.",p,assemble,ai_hint.WORST)
					result.set_owner(owners.MAINDECK)
					result.pop_self()
					globe.boss.main_deck.contents.insert(0,result)
				else:
					p.gain_a_weakness()
		return


class superman(card_frame.card):
	name = "Superman"
	vp = 6
	cost = 13
	ctype = cardtype.HERO
	owner_type = owners.VILLAINDECK
	text = "You may play up to three Super Powers from the destroyed pile, and then\nput them on the bottom of the main deck. If you choose not to, +4 Power."
	image = "fe/images/cards/Superman 13.jpg"
	attack_text = "First Appearance - Attack:: Each player destroys a Super\nPower in his hand or discard pile. If you cannot, gain two Weakness cards."
	
	def play_action(self,player):
		assemble = []
		for c in globe.boss.destroyed_stack.contents:
			if c.ctype_eq(cardtype.SUPERPOWER):
				assemble.append(c)
		#Initialize to anything but None
		result = True
		num_played = 0
		while result != None and num_played < 3:
			#print("Loop6",flush = True)
			instruction_text = f"You may play a Super Power from the destroyed pile,\nand then put on the bottom of the main deck. ({num_played+1}/3)"
			result = effects.may_choose_one_of(instruction_text,player,assemble,ai_hint.BEST)
			if result != None:
				num_played += 1
				player.played.play(result.pop_self())
				assemble.remove(result)
				result.set_owner(owners.MAINDECK)
				result.pop_self()
				globe.boss.main_deck.contents.insert(0,result)
		if num_played == 0:
			player.played.plus_power(4)
		return 0


	def first_apearance(self):
		for p in globe.boss.players:
			if effects.attack(p,self):
				assemble = []
				for c in p.hand.contents:
					if c.ctype_eq(cardtype.SUPERPOWER):
						assemble.append(c)
				for c in p.discard.contents:
					if c.ctype_eq(cardtype.SUPERPOWER):
						assemble.append(c)
				if len(assemble) > 0:
					result = effects.choose_one_of("Destroy a Super Power from your hand or discard pile",p,assemble,ai_hint.WORST)
					result.destroy(p)
				else:
					for i in range(2):
						p.gain_a_weakness()
		return

class swamp_thing(card_frame.card):
	name = "Swamp Thing"
	vp = 5
	cost = 9
	ctype = cardtype.HERO
	owner_type = owners.VILLAINDECK
	text = "+2 Power for each Location in play."
	image = "fe/images/cards/Swamp Thing 9.jpg"
	attack_text = "First Appearance - Attack:: Each player puts a\nLocation he controls into his discard pile. If you\ncannot, gain a Weakness."
	
	def play_action(self,player):
		locations_in_play = 0
		for p in globe.boss.players:
			for c in p.ongoing.contents:
				if c.ctype_eq(cardtype.LOCATION):
					locations_in_play += 1
		player.played.plus_power(locations_in_play*2)
		return 0


	def first_apearance(self):
		for p in globe.boss.players:
			if effects.attack(p,self):
				assemble = []
				for c in p.ongoing.contents:
					if c.ctype_eq(cardtype.LOCATION):
						assemble.append(c)
				if len(assemble) > 0:
					result = effects.choose_one_of("discard a location you control",p,assemble,ai_hint.WORST)
					p.discard_a_card(result)
				else:
					p.gain_a_weakness()
		return

class the_flash(card_frame.card):
	name = "The Flash"
	vp = 4
	cost = 8
	ctype = cardtype.HERO
	owner_type = owners.VILLAINDECK
	text = "Draw three cards, and then discard a card."
	image = "fe/images/cards/The Flash 8.jpg"
	
	def play_action(self,player):
		player.draw_card(3)
		result = effects.choose_one_of("Choose a card to discard",player,player.hand.contents,ai_hint.WORST)
		player.discard_a_card(result)
		return 0

class wonder_woman(card_frame.card):
	name = "Wonder Woman"
	vp = 6
	cost = 11
	ctype = cardtype.HERO
	owner_type = owners.VILLAINDECK
	text = "You may play up to three Villains from the destroyed pile, and then\nput them on the bottom of the main deck. If you choose not to, +3 Power."
	image = "fe/images/cards/Wonder Woman 11.jpg"
	attack_text = "First Appearance - Attack:: Each player destroys a Villain in his\nhand or discard pile. If you cannot, gain a Weakness."
	
	def play_action(self,player):
		assemble = []
		for c in globe.boss.destroyed_stack.contents:
			if c.ctype_eq(cardtype.VILLAIN) and c.cost <= 6:
				assemble.append(c)
		#Initialize to anything but None
		result = True
		num_played = 0
		while result != None and num_played < 3:
			#print("Loop0",flush = True)
			instruction_text = f"You may play a Villain from the destroyed pile,\nand then put on the bottom of the main deck. ({num_played+1}/3)"
			result = effects.may_choose_one_of(instruction_text,player,assemble,ai_hint.BEST)
			if result != None:
				num_played += 1
				player.played.play(result.pop_self())
				assemble.remove(result)
				result.set_owner(owners.MAINDECK)
				result.pop_self()
				globe.boss.main_deck.contents.insert(0,result)
		if num_played == 0:
			return 3
		return 0


	def first_apearance(self):
		for p in globe.boss.players:
			if effects.attack(p,self):
				assemble = []
				for c in p.hand.contents:
					if c.ctype_eq(cardtype.VILLAIN):
						assemble.append(c)
				for c in p.discard.contents:
					if c.ctype_eq(cardtype.VILLAIN):
						assemble.append(c)
				if len(assemble) > 0:
					result = effects.choose_one_of("Destroy a Villain from your hand or discard pile",p,assemble,ai_hint.WORST)
					result.destroy(p)
				else:
					p.gain_a_weakness()
		return