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



#DOne
class aquamans_trident(card_frame.card):
	name = "Auquaman's Trident"
	vp = 1
	cost = 3
	ctype = cardtype.EQUIPMENT
	text = "+2 Power\nYou may put any one card you buy or gain this turn on top of your deck."
	image = "base/images/cards/Aquamans_Trident.jpeg"

	def trigger(self,ttype,data,player,active,immediate):
		if globe.DEBUG:
			print("test",self.name,flush=True)
		if trigger.test(immediate,\
						trigger.GAIN_CARD, \
						self.trigger, \
						player,ttype) \
				and data[0] == False \
				and effects.ok_or_no(f"Would you like to put {data[1].name} on top of your deck?",player,data[1],ai_hint.ALWAYS):
			if globe.DEBUG:
				print("active",self.name,flush=True)
			player.deck.contents.append(data[1])
			player.triggers.remove(self.trigger)
			return True
	
	def play_action(self,player):
		player.played.plus_power(2)
		used = False
		for c in player.gained_this_turn:
			if not used and c in player.discard.contents and effects.ok_or_no(f"Would you like to put {c.name} into your hand?-",player,c,ai_hint.ALWAYS):
				#player.gain_redirect.remove(player.hand)
				player.hand.add(c.pop_self())
				used = True
		if not used:
			#player.gain_redirect.append(self.trident_redirect)
			player.triggers.append(self.trigger)
		#player.gain_redirect.append(player.deck)
		return 0

#Done
class bane(card_frame.card):
	name = "Bane"
	vp = 1
	cost = 4
	ctype = cardtype.VILLAIN
	text = "+2 Power"
	attack = True
	attack_text = "Attack:: Each foe chooses and discards a card."
	image = "base/images/cards/Bane_4.jpeg"
	
	def play_action(self,player):
		player.played.plus_power(2)
		self.attack_action(player)
		return 0

	def attack_action(self,by_player):
		for p in globe.boss.players:
			if p != by_player and effects.attack(p,self,by_player):
				#effects.discard_a_card(p)
				if len(p.hand.contents) > 0:
					result = effects.choose_one_of("Choose a card to discard.",p,p.hand.contents,ai_hint.WORST)
					p.discard_a_card(result)
		return


#done
class the_batmobile(card_frame.card):
	name = "The Batmobile"
	vp = 1
	cost = 2
	ctype = cardtype.EQUIPMENT
	text = "If this is the first card you play this turn, discard your hand and draw 5 cards.  Otherwise, +1 Power"
	image = "base/images/cards/Batmobile_2.jpeg"
	
	def play_action(self,player):
		if len(player.played.played_this_turn) == 1:
			player.discard_hand()
			player.draw_card(5)
		else:
			player.played.plus_power(1)
		return 0

#done
class the_bat_signal(card_frame.card):
	name = "The Bat-Signal"
	vp = 1
	cost = 5
	ctype = cardtype.EQUIPMENT
	text = "+1 Power.  Put a Hero from your discard pile into your hand."
	image = "base/images/cards/The_Bat_Signal.jpeg"
	
	def play_action(self,player):
		instruction_text = "Choose a Hero from you discard pile to put into your hand"
		assemble = []
		for c in player.discard.contents:
			if c.ctype_eq(cardtype.HERO):
				assemble.append(c)
		if len(assemble) > 0:
			choosen = effects.choose_one_of(instruction_text,player,assemble,ai_hint.BEST)
			#if choosen != None
			player.hand.add(choosen.pop_self())
		player.played.plus_power(1)
		return 0

#TODO: test vp
class bizarro(card_frame.card):
	name = "Bizzaro"
	vp = 1
	cost = 7
	ctype = cardtype.VILLAIN
	text = "+3 Power.  At the end of the game, this card is worth 2 VP's for each Weakness in your deck."
	image = "base/images/cards/Bizarro_7.jpeg"
	
	def play_action(self,player):
		player.played.plus_power(3)
		return 0

	def calculate_vp(self,all_cards):
		count = 0
		for c in all_cards:
			if c.ctype_eq(cardtype.WEAKNESS):
				count += 1
		return 2*count + 1

#Done
class blue_beetle(card_frame.card):
	name = "Blue Beetle"
	vp = 2
	cost = 6
	ctype = cardtype.HERO
	defense = True
	text = "+3 Power.  Defense: You may reveal this card from your hand to avoid an Attack. (It stays in your hand)"
	image = "base/images/cards/Blue_Beetle.jpeg"
	
	def play_action(self,player):
		player.played.plus_power(3)
		return 0

	def defend(self,attacker = None,defender = None):
		return

#Done
class bulletproof(card_frame.card):
	name = "Bulletproof"
	vp = 1
	cost = 4
	ctype = cardtype.SUPERPOWER
	defense = True
	text = "+2 Power.  Defense: You may discard this card to avoid an Attack.  If you do, draw a card and you may destroy a card in your discard pile."
	image = "base/images/cards/Bulletproof.jpeg"
	
	def play_action(self,player):
		player.played.plus_power(2)
		return 0

	def defend(self,attacker = None,defender = None):
		self.owner.discard_a_card(self)
		self.owner.draw_card()
		#This effdect does it, but be carefull
		#effects.may_destroy_card_in_hand_or_discard(self.owner)


		instruction_text = f"You may destroy a card in your discard pile"
		card_to_destroy = effects.may_choose_one_of(instruction_text,self.owner,self.owner.discard.contents,ai_hint.IFBAD)
		if card_to_destroy != None:
			card_to_destroy.destroy(self.owner)
		return

#Done
class the_cape_and_cowl(card_frame.card):
	name = "The Cape and Cowl"
	vp = 1
	cost = 4
	ctype = cardtype.EQUIPMENT
	defense = True
	text = "+2 Power.  Defense: You may discard this card to avoid an Attack.  If you do, draw two cards."
	image = "base/images/cards/The_Cape_and_Cowl.jpeg"
	
	def play_action(self,player):
		player.played.plus_power(2)
		return 0

	def defend(self,attacker = None,defender = None):
		self.owner.discard_a_card(self)
		self.owner.draw_card(2)
		return

#done
class catwoman(card_frame.card):
	name = "Catwoman"
	vp = 1
	cost = 2
	ctype = cardtype.HERO
	text = "+2 Power"
	image = "base/images/cards/Catwoman_2.jpeg"
	
	def play_action(self,player):
		player.played.plus_power(2)
		return 0

#Done
class cheetah(card_frame.card):
	name = "Cheetah"
	vp = 1
	cost = 2
	ctype = cardtype.VILLAIN
	text = "Gain any card with cost 4 or less from the Line-Up."
	image = "base/images/cards/Cheetah_2.jpeg"
	
	def play_action(self,player):
		instruction_text = "Choose a one of these to gain from the Line-Up"
		assemble = []
		for c in globe.boss.lineup.contents:
			if c.cost <= 4 and len(c.frozen) == 0:
				assemble.append(c)
		if len(assemble) > 0:
			choosen = effects.choose_one_of(instruction_text,player,assemble,ai_hint.BEST)
			#if choosen != None
			player.gain(choosen)
		return 0

#Done
class clayface(card_frame.card):
	name = "Clayface"
	vp = 1
	cost = 4
	ctype = cardtype.VILLAIN
	text = "Choose a card you played this turn.  Play it again this turn.  (Effects and Power generated the first time you played it remain.)"
	image = "base/images/cards/Clayface_4.jpeg"
	
	def play_action(self,player):
		instruction_text = "Choose a card that you have already played to play again"
		assemble = []
		#Should i be able to play cards in toher people hands on on their decks, or in the destroyed pile, or in my dack...
		#Cannot play the last card played...because whatever card that was caused clayface to play in the first place
		#creates an infinite loop (firestor/clayface example)
		for c in player.played.contents:
			if c.name != "Clayface" and c != player.played.played_this_turn[-1]:
				assemble.append(c)
		if len(assemble) > 0:
			choosen = effects.choose_one_of(instruction_text,player,assemble,ai_hint.BEST)
			player.played.play(choosen)
			#To avoid it being in the played list twise
			#This is suposed to only remove 1 instance of the element
			player.played.contents.remove(choosen)
		return 0

#Done
class the_dark_knight(card_frame.card):
	name = "The Dark Knight"
	vp = 1
	cost = 5
	ctype = cardtype.HERO
	text = "+2 Power.  Gain all Equipment in the Line-Up.  Then, if you play or have gained Catwoman this turn, you may put a card you bought or gained this turn into your hand."
	image = "base/images/cards/Dark_Knight.jpeg"

	def trigger(self,ttype,data,player,active,immediate):
		if globe.DEBUG:
			print("test - DK",self.name,flush=True)
		if trigger.test(immediate,trigger.GAIN_CARD,self.trigger,player,ttype) \
				and data[0] == False \
				and effects.ok_or_no(f"Would you like to put {data[1].name} into your hand?",player,data[1],ai_hint.ALWAYS):
			if globe.DEBUG:
				print("active - DK",self.name,flush=True)
			player.hand.contents.append(data[1])
			player.triggers.remove(self.trigger)
			return True

	def catwoman_catchup(self,player):
		assemble = []
		for c in player.gained_this_turn:
			if c in player.discard.contents:
				assemble.append(c)
		if len(assemble) > 0:
			result = effects.may_choose_one_of("Would you like to put a card you gined this turn, into your hand?",player,assemble,ai_hint.BEST)
			if result != None:
				player.hand.add(result.pop_self())
				return True
		return False

	def triggerCW(self,ttype,data,player,active,immediate):
		if globe.DEBUG:
			print("test - CW",self.name,flush=True)
		if trigger.test(not immediate,\
						trigger.PLAY, \
						self.triggerCW, \
						player,ttype) \
				and data[0].name == "Catwoman":
			if globe.DEBUG:
				print("active - CW",self.name,flush=True)
			player.triggers.remove(self.triggerCW)
			if not self.catwoman_catchup(player):
				player.triggers.append(self.trigger)
	
	def play_action(self,player):
		player.played.plus_power(2)
		assemble = []
		for c in globe.boss.lineup.contents:
			if c.ctype_eq(cardtype.EQUIPMENT):
				assemble.append(c)
		for c in assemble:
			player.gain(c)

		catwoman_triggered = False
		for c in player.played.played_this_turn:
			if c.name == "Catwoman":
				catwoman_triggered = True
		for c in player.gained_this_turn:
			if c.name == "Catwoman":
				catwoman_triggered = True

		if catwoman_triggered and not self.catwoman_catchup(player):
			player.triggers.append(self.trigger)
		elif not catwoman_triggered:
			player.triggers.append(self.triggerCW)
		return 0

#Done
class doomsday(card_frame.card):
	name = "Doomsday"
	vp = 2
	cost = 6
	ctype = cardtype.VILLAIN
	text = "+4 Power"
	image = "base/images/cards/Doomsday.jpeg"
	
	def play_action(self,player):
		player.played.plus_power(4)
		return 0

#Done
class the_emerald_knight(card_frame.card):
	name = "The Emerald Knight"
	vp = 1
	cost = 5
	ctype = cardtype.HERO
	text = "Remove an Equipment, Hero, or Super Power from the Line-Up.  Play it, then return it to the Line-Up at the end of your turn."
	played_card = None
	image = "base/images/cards/Emerald_Knight.jpeg"
	
	def play_action(self,player):
		instruction_text = "Choose one of these from the line up, play it, then return it at the end of the turn"
		assemble = []
		for c in globe.boss.lineup.contents:
			if c.ctype_eq(cardtype.EQUIPMENT) or c.ctype_eq(cardtype.HERO) or c.ctype_eq(cardtype.SUPERPOWER):
				assemble.append(c)
		if len(assemble) > 0:
			choosen = effects.choose_one_of(instruction_text,player,assemble,ai_hint.BEST)
			self.played_card = choosen
			choosen.pop_self()
			player.played.play(choosen)
		return 0
#This may be a better way to do it, but its currently being done by checking the cards owner and returning it there
	#def end_of_turn(self):
	#	if self.played_card != None:
	#		globe.boss.lineup.add(self.played_card.pop_self())
	#	return

#Done
class fastest_man_alive(card_frame.card):
	name = "The Fastest Man Alive"
	vp = 1
	cost = 5
	ctype = cardtype.HERO
	text = "Draw two cards"
	image = "base/images/cards/The_Fastest_Man_Alive.jpeg"
	
	def play_action(self,player):
		player.draw_card(2)
		return 0

#Done
class gorilla_grodd(card_frame.card):
	name = "Grorilla Grodd"
	vp = 2
	cost = 5
	ctype = cardtype.VILLAIN
	text = "+3 Power"
	image = "base/images/cards/Gorilla_Grodd.jpeg"
	
	def play_action(self,player):
		player.played.plus_power(3)
		return 0

#TODO: need testing calculating vp
class green_arrow(card_frame.card):
	name = "Green Arrow"
	vp = '*'
	cost = 5
	ctype = cardtype.HERO
	text = "+2 Power\nAt the end of the game, if you have four or more other Heroes in your deck, this card is worth 5 VPs."
	image = "base/images/cards/Green_Arrow.jpeg"
	
	def play_action(self,player):
		player.played.plus_power(2)
		return 2

	def calculate_vp(self,all_cards):
		count = 0
		for c in all_cards:
			if c.ctype_eq(cardtype.HERO):
				count += 1
		if count > 4:
			return 5
		else:
			return 0

#Done
class green_arrows_bow(card_frame.card):
	name = "Green Arrow's Bow"
	vp = 1
	cost = 4
	ctype = cardtype.EQUIPMENT
	text = "+2 Power.  Super-Villains cost you 2 less to defeat this turn."
	image = "base/images/cards/Green_Arrows_Bow.jpeg"

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
			return data[0] - 2
	
	def play_action(self,player):
		player.played.plus_power(2)
		player.triggers.append(self.trigger)
		return 0

#Done
class harley_quinn(card_frame.card):
	name = "Harley Quinn"
	vp = 1
	cost = 2 
	ctype = cardtype.VILLAIN
	text = "+1 Power"
	attack = True
	attack_text = "Attack: Each foe puts a Punch or Vulnerability from his discard pile on top of his deck."
	image = "base/images/cards/Harley_Quinn_2.jpeg"
	
	def play_action(self,player):
		player.played.plus_power(1)
		self.attack_action(player)
		return 0

	def attack_action(self,by_player):
		for p in globe.boss.players:
			if p != by_player and effects.attack(p,self,by_player):
				assemble = []
				for c in p.discard.contents:
					if c.name == "Punch" or c.name == "Vunerability":
						assemble.append(c)
				if len(assemble) > 0:
					result = effects.choose_one_of("Choose punch or Vunerability from your discard to put on top of your deck",p,assemble,hint = ai_hint.BEST)
					p.deck.add(result.pop_self())
		return
#done
class heat_vision(card_frame.card):
	name = "Heat Vision"
	vp = 2
	cost = 6
	ctype = cardtype.SUPERPOWER
	text = "+3 Power\nYou may destory a card in your hand or discard pile."
	image = "base/images/cards/Heat_Vision.jpeg"
	
	def play_action(self,player):
		player.played.plus_power(3)
		#effects.may_destroy_card_in_hand_or_discard(player)
		collection = player.hand.contents.copy()
		collection.extend(player.discard.contents)
		instruction_text = f"You may destroy a card in your hand or discard pile"
		card_to_destroy = effects.may_choose_one_of(instruction_text,player,collection,ai_hint.IFBAD)
		if card_to_destroy != None:
			card_to_destroy.destroy(player)

		return 0

#Done
class high_tech_hero(card_frame.card):
	name = "High-Tech HERO"
	vp = 1
	cost = 3
	ctype = cardtype.HERO
	text = "If you have played a Super Power or Equipment this turn, +3 Power.\nOtherwise, +1 Power."
	image = "base/images/cards/High_Tech_Hero.jpeg"
	
	def play_action(self,player):
		if player.played.get_count(cardtype.SUPERPOWER) > 0 \
				or player.played.get_count(cardtype.EQUIPMENT) > 0:
			player.played.plus_power(3)
		else:
			player.played.plus_power(1)
		return 0

#Done
class jonn_jonzz(card_frame.card):
	name = "J'onn J'onzz"
	vp = 2
	cost = 6
	ctype = cardtype.HERO
	text = "Play the top card of the Super-Villain stack, then return it to the stack.  (The First Appearance - Attack does not happen.)"
	image = "base/images/cards/Jonn_Jonzz.jpeg"
	
	def play_action(self,player):
		top_of_sv = globe.boss.supervillain_stack.contents.pop()
		player.played.play(top_of_sv)
		top_of_sv.pop_self()
		#player.played.contents.remove(top_of_sv)
		globe.boss.supervillain_stack.add(top_of_sv)
		return 0

#Done
class kid_flash(card_frame.card):
	name = "Kid Flash"
	vp = 1
	cost = 2
	ctype = cardtype.HERO
	text = "Draw a card"
	image = "base/images/cards/Kid_Flash_2.jpeg"
	
	def play_action(self,player):
		player.draw_card()
		return 0

#done
class king_of_atlantis(card_frame.card):
	name = "King of Atlantis"
	vp = 1
	cost = 5
	ctype = cardtype.HERO
	text = "You may destroy a card in your discard pile.  If you do, +3 Power.  Otherwise, +1 Power"
	image = "base/images/cards/King_of_Atlantis.jpeg"
	
	def play_action(self,player):
		#choice = effects.may_destroy_card_in_discard(player)

		instruction_text = f"You may destroy a card in your discard pile"
		card_to_destroy = effects.may_choose_one_of(instruction_text,player,player.discard.contents,ai_hint.IFBAD)

		if card_to_destroy == None:
			player.played.plus_power(1)
		else:
			card_to_destroy.destroy(player)
			player.played.plus_power(3)
		return 0

#Done
class lasso_of_truth(card_frame.card):
	name = "Lasso of Truth"
	vp = 1
	cost = 2
	ctype = cardtype.EQUIPMENT
	defense = True
	text = "+1 Power\nDefence:: You may discard this card to avoid an Attack.  If you do, draw a card."
	image = "base/images/cards/Lasso_of_Truth.jpeg"
	
	def play_action(self,player):
		player.played.plus_power(1)
		return 0

	def defend(self,attacker = None,defender = None):
		self.owner.discard_a_card(self)
		self.owner.draw_card()
		return

#Done
class lobo(card_frame.card):
	name = "Lobo"
	vp = 2
	cost = 7
	ctype = cardtype.VILLAIN
	text = "+3 Power.  You may destroy up to two cards in your hand and/or discard pile."
	image = "base/images/cards/Lobo.jpeg"
	
	def play_action(self,player):
		player.played.plus_power(3)
		collection = player.hand.contents.copy()
		collection.extend(player.discard.contents)
		instruction_text = f"You may destroy a card in your hand or discard pile (1/2)"
		card_to_destroy = effects.may_choose_one_of(instruction_text,player,collection,ai_hint.IFBAD)
		if card_to_destroy != None:
			card_to_destroy.destroy(player)
			collection = player.hand.contents.copy()
			collection.extend(player.discard.contents)
			instruction_text = f"You may destroy a card in your hand or discard pile (2/2)"
			card_to_destroy = effects.may_choose_one_of(instruction_text,player,collection,ai_hint.IFBAD)
			if card_to_destroy != None:
				card_to_destroy.destroy(player)
		return 0

#Done
class the_man_of_steel(card_frame.card):
	name = "The Man of Steel"
	vp = 3
	cost = 8
	ctype = cardtype.HERO
	text = "+3 Power.  Put all Super Powers from your discard pile into your hand."
	image = "base/images/cards/Man_of_Steel.jpeg"
	
	def play_action(self,player):
		player.played.plus_power(3)
		assemble = []
		for c in player.discard.contents:
			if c.ctype_eq(cardtype.SUPERPOWER):
				assemble.append(c)
		for c in assemble:
			player.hand.add(c.pop_self())
		return 0

#Done
class mera(card_frame.card):
	name = "Mera"
	vp = 1
	cost = 3
	ctype = cardtype.HERO
	text = "If your discard pile is empty, +4 Power.  Otherwise, +2 Power."
	image = "base/images/cards/Mera.jpeg"
	
	def play_action(self,player):
		if player.discard.size() == 0:
			player.played.plus_power(4)
		else:
			player.played.plus_power(2)
		return 0

#Done
class nth_metal(card_frame.card):
	name = "Nth Metal"
	vp = 1
	cost = 3
	ctype = cardtype.EQUIPMENT
	text = "+1 Power.  Look at the top of your deck.  You may destroy it."
	image = "base/images/cards/Nth_Metal.jpeg"
	
	def play_action(self,player):
		top_card = player.reveal_card(public = False)
		if top_card != None and effects.ok_or_no(f"A {top_card.name} is on top of your deck, would you like to destroy it? (ok/no)",player,top_card,ai_hint.IFBAD):
			top_card.destroy(player)
		return 0

#DOne
class the_penguin(card_frame.card):
	name = "The Penguin"
	vp = 1
	cost = 3
	ctype = cardtype.VILLAIN
	text = "Draw two cards, then choose and discard two cards from your hand."
	image = "base/images/cards/The_Penguin.jpeg"
	
	def play_action(self,player):
		player.draw_card(2)
		for i in range(2):
			if len(player.hand.contents) > 0:
				result = effects.choose_one_of("Choose a card to discard.",player,player.hand.contents,ai_hint.WORST)
				player.discard_a_card(result)
		return 0

#Done
class poison_ivy(card_frame.card):
	name = "Poison Ivy"
	vp = 1
	cost = 3
	ctype = cardtype.VILLAIN
	text = "+1 Power"
	attack = True
	attack_text = "Attack:: Each foe discards the top card of his deck.  If its cost is 1 or greater, that player gains a Weakness."
	image = "base/images/cards/Poison_Ivy_3.jpeg"
	
	def play_action(self,player):
		player.played.plus_power(1)
		self.attack_action(player)
		return 0

	def attack_action(self,by_player):
		for p in globe.boss.players:
			if p != by_player and effects.attack(p,self,by_player):
				card_to_discard = p.reveal_card(public = False)
				if card_to_discard != None:
					p.discard_a_card(card_to_discard)
					if card_to_discard.cost >= 1:
						p.gain_a_weakness()
		return


#Done
class power_ring(card_frame.card):
	name = "Power Ring"
	vp = 1
	cost = 3
	ctype = cardtype.EQUIPMENT
	text = "Reveal the top card of your deck.  If its cost is 1 or greater, +3 Power.  Otherwise, +2 Power."
	image = "base/images/cards/Power_Ring_3.jpeg"
	
	def play_action(self,player):
		top_card = player.reveal_card()
		if top_card != None and top_card.cost >= 1:
			player.played.plus_power(3)
		else:
			player.played.plus_power(1)
		return 0

#Done
class princess_diana_of_themyscira(card_frame.card):
	name = "Princess Diana of Themyscira"
	vp = 2
	cost = 7
	ctype = cardtype.HERO
	text = "Gain all Villains with cost 7 or less in the Line-Up."
	image = "base/images/cards/Princess_Diana_of_Themyscira.jpeg"
	
	def play_action(self,player):
		assemble = []
		for c in globe.boss.lineup.contents:
			if c.ctype_eq(cardtype.VILLAIN) and c.cost <= 7:
				assemble.append(c)
		for c in assemble:
			player.gain(c)
		return 0

#done
class the_riddler(card_frame.card):
	name = "The Riddler"
	vp = 1
	cost = 3
	ctype = cardtype.VILLAIN
	text = "type 'riddle' to pay 3 Power.  If you do, gain the top card of the main deck.  Use this ability any number of times this turn.  If you choose not to, +1 Power instead"
	image = "base/images/cards/The_Riddler.jpeg"
	
	def special_action_click(self,player):
		if globe.boss.main_deck.size() > 0 and player.played.power >= 3:
			player.played.power -= 3
			player.gain(globe.boss.main_deck.contents[-1])

	def play_action(self,player):
		#player.played_riddler = True
		if effects.ok_or_no(f"Would you like to use the riddler ability?",player,self,ai_hint.NEVER):
			player.played.special_options.append(actions.special_action("Riddle",self.special_action_click))
		else:
			player.played.plus_power(1)
		return 0



#done
class robin(card_frame.card):
	name = "Robin"
	vp = 1
	cost = 3
	ctype = cardtype.HERO
	text = "+1 Power.  Put an Equipment from your discard pile into your hand."
	image = "base/images/cards/Robin_3.jpeg"
	
	def play_action(self,player):
		player.played.plus_power(1)
		instruction_text = "Choose an Equipment from you discard pile to put into your hand"
		assemble = []
		for c in player.discard.contents:
			if c.ctype_eq(cardtype.EQUIPMENT):
				assemble.append(c)
		if len(assemble) > 0:
			choosen = effects.choose_one_of(instruction_text,player,assemble,ai_hint.BEST)
			#if choosen != None
			player.hand.add(choosen.pop_self())
		return 0

#Attack
class scarecrow(card_frame.card):
	name = "Scarecrow"
	vp = 1
	cost = 5
	ctype = cardtype.VILLAIN
	text = "+2 Power."
	attack = True
	attack_text = "Attack: Each foe gains a Weakness."
	image = "base/images/cards/Scarecrow_5.jpeg"
	
	def play_action(self,player):
		player.played.plus_power(2)
		self.attack_action(player)
		return 0

	def attack_action(self,by_player):
		for p in globe.boss.players:
			if p != by_player and effects.attack(p,self,by_player):
				p.gain_a_weakness()
		return

#done
class solomon_grundy(card_frame.card):
	name = "Solomon Grundy"
	vp = 2
	cost = 6
	ctype = cardtype.VILLAIN
	text = "When you buy or gain this Villain, you may put him on top of your deck.  +3 Power."
	image = "base/images/cards/Solomon_Grundy.jpeg"
	
	def play_action(self,player):
		player.played.plus_power(3)
		return 0

	def trigger(self,ttype,data,player,active,immediate):
		if globe.DEBUG:
			print("test",self.name,flush=True)
		if trigger.test(immediate,\
						trigger.GAIN_CARD, \
						self.trigger, \
						player,ttype) \
				and data[1] == self \
				and data[0] == False \
				and effects.ok_or_no(f"Would you like to put {data[1].name} on top of your deck?",player,data[1],ai_hint.ALWAYS):
			if globe.DEBUG:
				print("active",self.name,flush=True)
			player.deck.contents.append(data[1])
			player.triggers.remove(self.trigger)
			return True

	#def solomon_grundy_redirect(self,player,card):
	#	if card.name == "Solomon Grundy" and effects.ok_or_no(f"Would you like to put {card.name} on top of your deck?-",player,card,ai_hint.ALWAYS):
	#		return (True,player.deck)
	#	return (False,None)

	def buy_action(self,player,bought,defeat):
		#player.gain_redirect.append(self.solomon_grundy_redirect)
		player.triggers.append(self.trigger)
		#Assume that card can be bought
		return True


#done
class starro(card_frame.card):
	name = "Starro"
	vp = 2
	cost = 7
	ctype = cardtype.VILLAIN
	text = ""
	attack = True
	attack_text = "Attack: Each foe discards the top card of his deck.  You may play each non-Location discarded this way this turn."
	image = "base/images/cards/Starro.jpeg"
	
	def play_action(self,player):
		self.attack_action(player)
		return 0

	def attack_action(self,by_player):
		for p in globe.boss.players:
			if p != by_player and effects.attack(p,self,by_player):
				card_to_discard = p.reveal_card(public = False)
				if card_to_discard != None:
					p.discard_a_card(card_to_discard)
					if not card_to_discard.ctype_eq(cardtype.LOCATION):
						result = effects.ok_or_no(f"Would you like to play a {card_to_discard.name}?",by_player,card_to_discard,ai_hint.ALWAYS)
						if result:
							by_player.played.play(card_to_discard.pop_self())
		return

#test vp
class suicide_squad(card_frame.card):
	name = "Suicide Squad"
	vp = '*'
	cost = 4
	ctype = cardtype.VILLAIN
	text = "+2 Power\nIf you already played two other Suicide Squad cards this turn, each foe discards his hand.\nAt the end of the game, this card is worth 1 VP for each Suiside Squad in your deck."
	image = "base/images/cards/Suicide_Squad.jpeg"
	
	def play_action(self,player):
		player.played.plus_power(2)
		count = 0
		for c in player.played.contents:
			if c.name == "Suicide Squad":
				count += 1
		#This card has been played
		if count >= 3:
			for p in globe.boss.players:
				if p != player:
					p.discard_hand()
		return 0
		# Suidide ability needed

	def calculate_vp(self,all_cards):
		count = 0
		for c in all_cards:
			if c.name == "Suicide Squad":
				count += 1
		return count

#done
class super_speed(card_frame.card):
	name = "Super Speed"
	vp = 1
	cost = 3
	ctype = cardtype.SUPERPOWER
	defense = True
	text = "Draw a card.  Defense: You may discard this card to avoid an Attack.  If you do, draw two cards."
	image = "base/images/cards/Super_Speed.jpeg"
	
	def play_action(self,player):
		player.draw_card()
		return 0

	def defend(self,attacker = None,defender = None):
		self.owner.discard_a_card(self)
		self.owner.draw_card(2)
		return

#Done
class super_strength(card_frame.card):
	name = "Super Strength"
	vp = 2
	cost = 7
	ctype = cardtype.SUPERPOWER
	text = "+5 Power"
	image = "base/images/cards/Super_Strength.jpeg"
	
	def play_action(self,player):
		player.played.plus_power(5)
		return 0

#done
class super_girl(card_frame.card):
	name = "Super Girl"
	vp = 1
	cost = 4
	ctype = cardtype.HERO
	text = "You may put a Kick card from the Kick stack into your hand."
	image = "base/images/cards/Supergirl.jpeg"
	
	def play_action(self,player):
		if globe.boss.kick_stack.size() > 0 and \
				effects.ok_or_no("Would you like to gain a kick into your hand?",player,None,hint = ai_hint.ALWAYS):
			new_kick = globe.boss.kick_stack.contents.pop()
			new_kick.set_owner(player)
			player.hand.add(new_kick)
		return 0

#done
class swamp_thing(card_frame.card):
	name = "Swamp Thing"
	vp = 1
	cost = 4
	ctype = cardtype.HERO
	text = "If you control a Location, +5 Power.  Otherwise, +2 Power."
	image = "base/images/cards/Swamp_Thing.jpeg"
	
	def play_action(self,player):
		for c in player.ongoing.contents:
			if c.ctype_eq(cardtype.LOCATION):
				player.played.plus_power(5)
				return 0
		player.played.plus_power(2)
		return 0

#Test
class two_face(card_frame.card):
	name = "Two-Face"
	vp = 1
	cost = 2
	ctype = cardtype.VILLAIN
	text = "+1 Power.  Choose even or odd, then reveal the top card of your deck.  If its cost matches your choice, draw it.  If not, discard it. (0 is even.)"
	image = "base/images/cards/Two_Face.jpeg"
	
	def play_action(self,player):
		player.played.plus_power(1)
		choose_even = effects.choose_even_or_odd("Choose even or odd, then reveal the top card of your deck.  If its cost matches your choice, draw it.  If not, discard it.",player)
		
		on_top = player.reveal_card()
		if on_top != None:
			if on_top.cost%2 == 0:
				card_is_even = True
			else:
				card_is_even = False
			if card_is_even == choose_even:
				player.draw_card()
			else:
				player.discard_a_card(on_top)

		return 0

#TODO: need testing calculating vp
class utility_belt(card_frame.card):
	name = "utility_belt"
	vp = '*'
	cost = 5
	ctype = cardtype.EQUIPMENT
	text = "+2 Power\nAt the end of the game, if you have four or more other Equipment in your deck, this card is worth 5 VPs."
	image = "base/images/cards/Utility_Belt.jpeg"
	
	def play_action(self,player):
		player.played.plus_power(2)
		return 0

	def calculate_vp(self,all_cards):
		count = 0
		for c in all_cards:
			if c.ctype_eq(cardtype.EQUIPMENT):
				count += 1
		if count > 4:
			return 5
		else:
			return 0


#TODO: allow to place back on top of players deck
class x_ray_vision(card_frame.card):
	name = "X-Ray Vision"
	vp = 1
	cost = 3
	ctype = cardtype.SUPERPOWER
	text = "Each foe reveals the top card of his deck. You may play one of the non-Location cards revealed this eay this turn, then return it to the top of it's owner's deck."
	image = "base/images/cards/Xray_Vision.jpeg"
	
	def play_action(self,player):
		#effects.x_ray_vision_reveal(player)
		assemble = []
		for p in globe.boss.players:
			if p != player:
				top_card = p.reveal_card()
				if top_card != None:
					if not top_card.ctype_eq(cardtype.LOCATION):
						assemble.append(top_card)
		if len(assemble) > 0:
			result = effects.may_choose_one_of("You may play of of the revealed cards.\nIt will then go back ontop of the players deck.",player,assemble,ai_hint.BEST)
			if result != None:
				result.pop_self()
				player.play_and_return(result,result.owner.deck)
		return 0

#test
class zatanna_zatara(card_frame.card):
	name = "Zatanna Zatara"
	vp = 1
	cost = 4
	ctype = cardtype.HERO
	text = "+1 Power.  You may put up to two cards from your discard pile on the bottom of your deck."
	image = "base/images/cards/Zatanna_Zatara.jpeg"
	
	def play_action(self,player):
		player.played.plus_power(1)
		instruction_text = "You may choose a card from your dicard pile to go on the bottom of your deck('no' or 'ok 0')"
		for i in range(2):
			result = effects.may_choose_one_of(instruction_text,player,player.discard.contents,hint = ai_hint.BEST)
			if result != None:
				player.deck.contents.insert(0,result.pop_self())
		return 0

#Locations
class arkham_asylum(card_frame.card):
	name = "Arkham Asylum"
	vp = 1
	cost = 5
	ctype = cardtype.LOCATION
	text = "Ongoing: When you play your first Villain on each of your turns, draw a card."
	image = "base/images/cards/Arkham_Asylum.jpeg"
	ongoing = True

	#def arkham_mod(self,card,player):
	#	if card.ctype_eq(cardtype.VILLAIN) and self.arkham_mod in player.played.card_mods:
	#		player.played.card_mods.remove(self.arkham_mod)
	#		player.draw_card()
	#	return 0

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
			player.draw_card()
			player.triggers.remove(self.trigger)
			return True
	
	
	def play_action(self,player):
		if self in player.ongoing.contents:
			#player.played.card_mods.append(self.arkham_mod)
			player.triggers.append(self.trigger)
		else:
			player.ongoing.add(self.pop_self())

			already_played = False
			for c in player.played.played_this_turn:
				if c.ctype_eq(cardtype.VILLAIN):
					already_played = True
			if not already_played:
				#player.played.card_mods.append(self.arkham_mod)
				player.triggers.append(self.trigger)
		return 0

class the_batcave(card_frame.card):
	name = "The Batcave"
	vp = 1
	cost = 5
	ctype = cardtype.LOCATION
	text = "Ongoing: When you play your first Equipment on each of your turns, Draw a card."
	image = "base/images/cards/The_Batcave.jpeg"
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
			player.draw_card()
			player.triggers.remove(self.trigger)
			return True


	def play_action(self,player):
		if self in player.ongoing.contents:
			player.triggers.append(self.trigger)
		else:
			player.ongoing.add(self.pop_self())

			already_played = False
			for c in player.played.played_this_turn:
				if c.ctype_eq(cardtype.EQUIPMENT):
					already_played = True
			if not already_played:
				player.triggers.append(self.trigger)
		return 0

class fortress_of_solitude(card_frame.card):
	name = "Fortress of Solitude"
	vp = 1
	cost = 5
	ctype = cardtype.LOCATION
	text = "Ongoing: When you play your first Super Power on each of your turns, draw a card."
	image = "base/images/cards/Fortress_of_Solitude.jpeg"
	ongoing = True

	def trigger(self,ttype,data,player,active,immediate):
		if globe.DEBUG:
			print("test",self.name,flush=True)
		if trigger.test(not immediate,\
						trigger.PLAY, \
						self.trigger, \
						player,ttype) \
				and data[0].ctype_eq(cardtype.SUPERPOWER):
			if globe.DEBUG:
				print("active",self.name,flush=True)
			player.draw_card()
			player.triggers.remove(self.trigger)
			return True
	
	
	def play_action(self,player):
		if self in player.ongoing.contents:
			player.triggers.append(self.trigger)
		else:
			player.ongoing.add(self.pop_self())

			already_played = False
			for c in player.played.played_this_turn:
				if c.ctype_eq(cardtype.SUPERPOWER):
					already_played = True
			if not already_played:
				player.triggers.append(self.trigger)
		return 0

class titans_tower(card_frame.card):
	name = "Titans Tower"
	vp = 1
	cost = 5
	ctype = cardtype.LOCATION
	text = "Ongoing: When you play your first card with cost 2 or 3 on each of your turns, draw a card."
	image = "base/images/cards/Titans_Tower.jpeg"
	ongoing = True

	def trigger(self,ttype,data,player,active,immediate):
		if globe.DEBUG:
			print("test",self.name,flush=True)
		if trigger.test(not immediate,\
						trigger.PLAY, \
						self.trigger, \
						player,ttype) \
				and (data[0].cost == 2 or data[0].cost == 3):
			if globe.DEBUG:
				print("active",self.name,flush=True)
			player.draw_card()
			player.triggers.remove(self.trigger)
			return True

	
	def play_action(self,player):
		if self in player.ongoing.contents:
			player.triggers.append(self.trigger)
		else:
			player.ongoing.add(self.pop_self())

			already_played = False
			for c in player.played.played_this_turn:
				if c.cost == 2 or c.cost == 3:
					already_played = True
			if not already_played:
				player.triggers.append(self.trigger)
		return 0

class the_watchtower(card_frame.card):
	name = "The Watchtower"
	vp = 1
	cost = 5
	ctype = cardtype.LOCATION
	text = "Ongoing: When you play your first hero on each of your turns, draw a card."
	image = "base/images/cards/The_Watchtower.jpeg"
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
			player.draw_card()
			player.triggers.remove(self.trigger)
			return True
	
	
	def play_action(self,player):
		if self in player.ongoing.contents:
			player.triggers.append(self.trigger)
		else:
			player.ongoing.add(self.pop_self())

			already_played = False
			for c in player.played.played_this_turn:
				if c.ctype_eq(cardtype.HERO):
					already_played = True
			if not already_played:
				#if player == self.owner:
				player.triggers.append(self.trigger)
		return 0



#SuperVillains
class ras_al_ghul(card_frame.card):
	name = "Ra's Al Ghul"
	vp = 4
	cost = 8
	ctype = cardtype.VILLAIN
	owner_type = owners.VILLAINDECK
	text = "+3 Power\nAt the end of your turn, put this card on the bottom of its owners deck before drawing a new hand."
	image = "base/images/cards/Ras Al Ghul 8.jpg"
	
	def play_action(self,player):
		player.played.plus_power(3)
		return 0

	def end_of_turn(self):
		if self.owner != None:
			self.pop_self()
			self.owner.deck.contents.insert(0,self)
		return

#test fa
class the_anti_monitor(card_frame.card):
	name = "The Anti-Monitor"
	vp = 6
	cost = 12
	ctype = cardtype.VILLAIN
	owner_type = owners.VILLAINDECK
	text = "+2 Power.\n Destroy any number of cards in the Line-Up, then replace them."
	attack_text = "First Appearance - Attack:: Each player reveals his hand, chooses a card with cost 1 or greater from it, and adds that card to the Line-Up."
	image = "base/images/cards/The Anti-Monitor.jpg"
	
	def play_action(self,player):
		player.played.plus_power(2)
		instruction_text = "Choose any number of cards in the lineup to destroy"
		choosen = effects.choose_however_many(instruction_text,player,globe.boss.lineup.contents,ai_hint.IFBAD)
		if choosen != None:
			#print(len(choosen),"FHGFGFHFGHFH")
			for c in choosen:
				c.destroy(player)
				card_to_add = globe.boss.main_deck.draw()
				if card_to_add != None:
					globe.boss.lineup.add(card_to_add)
		return 0

	def first_apearance(self):
		instruction_text = "Choose a card with cost 1 or greater to add to the lineup"
		for p in globe.boss.players:
			if effects.attack(p,self):
				assemble = []
				for c in p.hand.contents:
					if c.cost >= 1:
						assemble.append(c)
				if len(assemble) > 0:
					card_to_give = effects.choose_one_of(instruction_text,p,assemble,ai_hint.WORST)
					card_to_give.pop_self()
					card_to_give.set_owner(owners.LINEUP)
					globe.boss.lineup.add(card_to_give)
		return

#done
class atrocitus(card_frame.card):
	name = "Atrocitus"
	vp = 5
	cost = 10
	ctype = cardtype.VILLAIN
	owner_type = owners.VILLAINDECK
	text = "+2 Power.\n Destroy up to two cards in your discard pile."
	attack_text = "First Appearance - Attack:: Each player puts a random card from his hand under his Super Hero.  When this Villain is defeated, put each of those cards on top of it's owner's deck."
	image = "base/images/cards/Atrocitus 10.jpg"
	
	def play_action(self,player):
		player.played.plus_power(2)
		card_to_destroy = True
		for i in range(2):
			#This way we only ask the seccond time if the first was ok
			if card_to_destroy:
				instruction_text = f"You may destroy a card from your discard pile ({i+1}/2)"
				card_to_destroy = effects.may_choose_one_of(instruction_text,player,player.discard.contents,ai_hint.IFBAD)
				if card_to_destroy != None:
					card_to_destroy.destroy(player)
		return 0

	def first_apearance(self):
		for p in globe.boss.players:
			if effects.attack(p,self) and p.hand.size() > 0:
				selected_card = random.choice(p.hand.contents)
				p.under_superhero.add(selected_card.pop_self())
		return

	def buy_action(self,player,bought,defeat):
		#If cards are under the persona for other reasons, re-gaining this card should not free them
		if defeat:
			for p in globe.boss.players:
				for c in p.under_superhero.contents:
					p.deck.add(c.pop_self())
		return True

#done
class black_manta(card_frame.card):
	name = "Black Manta"
	vp = 4
	cost = 8
	ctype = cardtype.VILLAIN
	owner_type = owners.VILLAINDECK
	text = "+3 Power and draw a card."
	attack_text = "First Appearance - Attack:: Each player discards the top card of his deck.  If you discarded a card with cost 1 or more, choose one: Destroy it, or discard your hand."
	image = "base/images/cards/Black Manta 8.jpg"
	
	def play_action(self,player):
		player.played.plus_power(3)
		player.draw_card()
		return 0

	def first_apearance(self):
		for p in globe.boss.players:
			if effects.attack(p,self):
				discarded = p.reveal_card(public = False)
				if discarded != None:
					p.discard_a_card(discarded)
					if discarded.cost >= 1:
						instruction_text = f"Would you like to destroy this card?  If not, you hand will be discarded."
						if effects.ok_or_no(instruction_text,p,card = discarded,hint = ai_hint.IFBAD):
							discarded.destroy(p)
						else:
							p.discard_hand()
		return

#done
class brainiac(card_frame.card):
	name = "Brainiac"
	vp = 6
	cost = 11
	ctype = cardtype.VILLAIN
	owner_type = owners.VILLAINDECK
	text = "Each foe reveals a random card from his hand. Play each revealed non-Location."
	attack_text = "First Appearance - Attack:: Each player chooses two cards from his hand and puts them on the table face down.  Shuffle all of the chosen cards face down, then deal two back to each player at random."
	image = "base/images/cards/Brainiac 11.jpg"
	
	def play_action(self,player):
		for p in globe.boss.players:
			if p != player and p.hand.size() > 0:
				card_to_play = random.choice(p.hand.contents)
				effects.reveal(f"This was in {p.pid}-{p.persona.name}'s hand",player,[card_to_play])
				if not card_to_play.ctype_eq(cardtype.LOCATION):
					player.play_and_return(card_to_play.pop_self(), p.hand)
		return 0

	def first_apearance(self):
		cards_to_shuffle = []
		participating_players = []
		for p in globe.boss.players:
			participating_players.append(p)	
			for i in range(2):
				instruction_text = f"Choose a card from your hand to be dealt to each player. ({i+1}/2)"
				if p.hand.size() > 0:
					cards_to_shuffle.append(effects.choose_one_of(instruction_text,p,p.hand.contents,ai_hint.WORST).pop_self())
		random.shuffle(cards_to_shuffle)
		for i in range(2):
			for p in participating_players:
				if len(cards_to_shuffle) > 0:
					added_card = cards_to_shuffle.pop()
					added_card.set_owner(p)
					p.hand.add(added_card)
		return

#done
class captain_cold(card_frame.card):
	name = "Captain Cold"
	vp = 5
	cost = 9
	ctype = cardtype.VILLAIN
	owner_type = owners.VILLAINDECK
	text = "+2 Power, and an additional +1 Power for each foe with a Hero in his discard pile."
	attack_text = "First Appearance - Attack:: Each player flips his Super Hero face down until this Villain is defeated."
	image = "base/images/cards/Captain Cold 9.jpg"
	
	def play_action(self,player):
		power = 2
		for p in globe.boss.players:
			if p != player:
				if p.discard.get_count(cardtype.HERO) > 0:
					power += 1
		player.played.plus_power(power)
		return 0

	def first_apearance(self):
		for p in globe.boss.players:
			if effects.attack(p,self):
				p.persona.active = False
		return

	def buy_action(self,player,bought,defeat):
		if defeat:
			for p in globe.boss.players:
				p.persona.active = True
		return True

#done
class darkseid(card_frame.card):
	name = "Darkseid"
	vp = 6
	cost = 11
	ctype = cardtype.VILLAIN
	owner_type = owners.VILLAINDECK
	text = "You may destroy two cards in your hand.\n If you do, +5 Power.  Otherwise, +3 Power."
	attack_text = "First Appearance - Attack:: Each player discards two cards unless he reveals a Villain from his hand."
	image = "base/images/cards/Darkseid 11.jpg"
	
	def play_action(self,player):
		instruction_text = f"You may destroy 2 cards in your hand, if you do, +5 Power, +3 power otherwise (1/2)"
		assemble = player.hand.contents.copy()
		card1 = effects.may_choose_one_of(instruction_text,player,assemble,hint = ai_hint.IFBAD)
		if card1 != None:
			instruction_text = f"You may destroy 2 cards in your hand, if you do, +5 Power, +3 power otherwise (2/2).  If you do not choose a second card, no cards will be destroyed."
			assemble.remove(card1)
			card2 = effects.may_choose_one_of(instruction_text,player,assemble,hint = ai_hint.IFBAD)
			if card2 != None:
				card1.destroy(player)
				card2.destroy(player)
				player.played.plus_power(5)
				return 0
		player.played.plus_power(3)
		return 0

	def first_apearance(self):
		for p in globe.boss.players:
			if effects.attack(p,self):
				has_villain = False
				for c in p.hand.contents:
					if c.ctype_eq(cardtype.VILLAIN):
						#Reveal card
						has_villain = True
				if not has_villain:
					for i in range(2):
						instruction_text = f"Discard 2 cards from your hand ({i+1}/2)"
						if p.hand.size() > 0:
							card_to_discard = effects.choose_one_of(instruction_text,p,p.hand.contents,hint = ai_hint.WORST)
							p.discard_a_card(card_to_discard)
		return

#done
class deathstroke(card_frame.card):
	name = "Deathstroke"
	vp = 5
	cost = 9
	ctype = cardtype.VILLAIN
	owner_type = owners.VILLAINDECK
	text = "You may gain a Hero or Villain from the Line-Up.\n If you choose not to, +3 Power."
	attack_text = "First Appearance - Attack:: Each player reveals his hand and destroys a Hero, Super Power or Equipment in his hand or discard pile."
	image = "base/images/cards/Deathstroke 9.jpg"
	
	def play_action(self,player):
		instruction_text = f"You may choose to gain a hero or villain from the lineup.  If you choose not to, +3 Power"
		assemble = []
		for c in globe.boss.lineup.contents:
			if c.ctype_eq(cardtype.VILLAIN) or c.ctype_eq(cardtype.HERO):
				assemble.append(c)
		if len(assemble) > 0:
			choosen = effects.may_choose_one_of(instruction_text,player,assemble,hint = ai_hint.BEST)
			if choosen != None:
				choosen.set_owner(player)
				player.discard_a_card(choosen)
				return 0
		player.played.plus_power(3)
		return 0
			

	def first_apearance(self):
		instruction_text = "destroy a hero, superpower, or equipment in your hand or discard pile"
		for p in globe.boss.players:
			if effects.attack(p,self):
				assemble = []
				for c in p.hand.contents:
					if c.ctype_eq(cardtype.HERO) or c.ctype_eq(cardtype.SUPERPOWER) or c.ctype_eq(cardtype.EQUIPMENT):
						assemble.append(c)
				for c in p.discard.contents:
					if c.ctype_eq(cardtype.HERO) or c.ctype_eq(cardtype.SUPERPOWER) or c.ctype_eq(cardtype.EQUIPMENT):
						assemble.append(c)
				if len(assemble) > 0:
					card_to_destroy = effects.choose_one_of(instruction_text,p,assemble,hint = ai_hint.WORST)
					card_to_destroy.destroy(p)



class the_joker(card_frame.card):
	name = "The Joker"
	vp = 5
	cost = 10
	ctype = cardtype.VILLAIN
	owner_type = owners.VILLAINDECK
	text = "+2 Power and each foe chooses: He discards a random card, or you draw a card."
	attack_text = "First Appearance - Attack:: Each player puts a card from his hand into the discard pile of the player on\nhis left.  If the card you received has a cost of 1 or greater, gain a Weakness"
	image = "base/images/cards/The Joker 10.jpg"
	
	def play_action(self,player):
		instruction_text = f"You may choose to discard a card, if you do not, {player.pid}-{player.persona.name} will draw a card."
		for p in globe.boss.players:
			if p != player:
				choosen = effects.may_choose_one_of(instruction_text,p,p.hand.contents,hint = ai_hint.IFBAD)
				if choosen == None:
					player.draw_card()
				else:
					p.discard_a_card(choosen)
		player.played.plus_power(2)
		return 0

	def first_apearance(self):
		instruction_text = "Choose a card to go into the discard pile of the player on your left"
		cards_to_shuffle = []
		participating_players = []
		for p in globe.boss.players:
			#print(p.persona.name,flush=True)
			if effects.attack(p,self):
				if p.hand.size() > 0:
					card_to_give = effects.choose_one_of(instruction_text,p,p.hand.contents,hint = ai_hint.WORST)
					cards_to_shuffle.append(card_to_give)
					participating_players.append(p)
		if len(cards_to_shuffle) > 0:
			for i,p in enumerate(participating_players):
				card_recived = cards_to_shuffle[i-1]
				card_recived.set_owner(p)
				p.discard_a_card(card_recived)
				if card_recived.cost > 0:
					p.gain_a_weakness()
				
		return

class lex_luther(card_frame.card):
	name = "Lex Luther"
	vp = 5
	cost = 10
	ctype = cardtype.VILLAIN
	owner_type = owners.VILLAINDECK
	text = "Draw three cards."
	attack_text = "First Appearance - Attack:: Each player gains a Weakness for each Villain in the Line-Up."
	image = "base/images/cards/Lex Luthor 10.jpg"
	
	def play_action(self,player):
		player.draw_card(3)
		return 0

	def first_apearance(self):
		villains_in_lineup = globe.boss.lineup.get_count(cardtype.VILLAIN)
		for p in globe.boss.players:
			if effects.attack(p,self):
				for i in range(villains_in_lineup):
					p.gain_a_weakness()
		return

class parallax(card_frame.card):
	name = "Parallax"
	vp = 6
	cost = 12
	ctype = cardtype.VILLAIN
	owner_type = owners.VILLAINDECK
	text = "Double your Power this turn."
	attack_text = "First Appearance - Attack:: Each player reveals his hand and discards all cards with cost 2 or less."
	image = "base/images/cards/Parallax 12.jpg"
	
	def play_action(self,player):
		player.played.parallax_double()
		return 0

	def first_apearance(self):
		for p in globe.boss.players:
			if effects.attack(p,self):
				assemble = effects.new_assemble(p.hand.contents)
				for c in assemble:
					if c.cost <= 2:
						p.discard_a_card(c)
		return

class sinestro(card_frame.card):
	name = "Sinestro"
	vp = 5
	cost = 10
	ctype = cardtype.VILLAIN
	owner_type = owners.VILLAINDECK
	text = "Reveal the top card of the main deck.  If it's a Hero, +3 Power and then destroy it.  Otherwise, put it in your hand."
	attack_text = "First Appearance - Attack: Each player reveals his hand and discards a card for each Hero revealed this way."
	image = "base/images/cards/Sinestro 10.jpg"
	
	def play_action(self,player):
		effects.reveal("This was on top of the main deck",player,[globe.boss.main_deck.contents[-1]])
		if len(globe.boss.main_deck.contents) > 0 and globe.boss.main_deck.contents[-1].ctype_eq(cardtype.HERO):
			globe.boss.main_deck.contents[-1].destroy(player)
			player.played.plus_power(3)
			return 0
		else:
			new_card = globe.boss.main_deck.contents.pop()
			#ownership change
			new_card.set_owner(player)
			player.hand.add(new_card)
			return 0

	def first_apearance(self):
		for p in globe.boss.players:
			if effects.attack(p,self):
				effects.reveal(f"This was {p.persona.name}'s hand",p,p.hand.contents)
				num_heros = p.hand.get_count(cardtype.HERO)
				for i in range(num_heros):
					instruction_text = f"You had {num_heros} heros in you hand.  Choose a card to discard ({i+1}/{num_heros})"
					if p.hand.size() > 0:
						choose = effects.choose_one_of(instruction_text,p,p.hand.contents,ai_hint.WORST)
						p.discard_a_card(choose)
		return



