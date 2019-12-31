from constants import option
import globe
from constants import cardtype
from constants import ai_hint
from constants import trigger

"""
effects.py is the intercafe bettween the cointroelrs (player and/or ai's) and the cards
Cards call different an effects function when a choice has to be made by a player
These functions then ask the coresponding controler, who then returns a result.
The result is then verified, and a program friendly answer is returned

The common uses for effects is:
attack (where a choice to defend if possible is implied)
choose a player
choose a card  (from a provided list of cards)
may choose a card (same as choose a card except the player can choose none)
ok or no (Boolean questions)
even or odd (This is a special one for the riddler.  Maybe i should alloe ok_or_no to cover this)
choose_however_many (allows the player to choose from none to all of the cards listed)
reveal.  This is a special one, as it dosnt actaully ask a question, but just reveals somehting to a player,
	Like what was in an opponents hand, or what was on top of their deck, ect.
"""

# deprecited.  i guess i forgot about .copy()
def new_assemble(list):
	assemble = []
	for i in list:
		assemble.append(i)
	return assemble

def ensure_int(i):
	if not type(i) is int:
		print("ERR: not an integer")
		return False
	else:
		return True

#depreciated
def attack_all(card):
	total_hit = 0
	for p in globe.boss.players:
		if attack(p,card):
			total_hit += 1
	return total_hit

#Returns true if hit by attack
def attack(player,card,by_player = None,avoid_twise = False):
	if by_player != None:
		#Triggers that dosn't affect the parent code return None
		#if the trigger wants to override this attack, it returns
		#True or False
		result = trigger.all(trigger.ATTACKING,[player,card],by_player,first_result = True)
		if result != None:
			return result

	# Looks for any avalable defense cards
	assemble = []
	for c in player.hand.contents:
		if c.defence:
			assemble.append(c)
	for c in player.ongoing.contents:
		if c.defence:
			assemble.append(c)

	# If there are any defense cards, ask the defender if they would like to use one of them
	if len(assemble) > 0:
		result = player.controler.may_defend(assemble,card,by_player)
		if result[0] == option.OK:
			if not ensure_int(result[1]):
				return attack(player,card,by_player)
			elif result[1] < 0 or result[1] >= len(assemble):
				print("Err: invalid number")
				return attack(player,card,by_player)
			else:
				#Attack avoided
				assemble[result[1]].defend(attacker = by_player, defender = player)
				#avoid twise, like in crossover 2's deadshot
				if avoid_twise:
					return attack(player,card,by_player,avoid_twise = False)
				else:
					#If you avoid the attack but not twise when nessesary (crossover 2's deadshot)
					#do you get to trigger your avoided attack abilities?
					#player.persona.avoided_attack(assemble[result[1]])
					#sent to the defending player
					trigger.all(trigger.AVOIDED_ATTACK,[by_player,card,assemble[result[1]]],player,first_result = True)
					return False
		elif result[0] == option.NO:
			if by_player != None:
				#Sent to the attacking player
				result = trigger.all(trigger.FAILED_TO_AVOID,[player,card],by_player,first_result = True)
				#by_player.persona.failed_to_avoid_power()

			return True
		else:
			print("Err: responce")
			return attack(player,card,by_player)
	else:
		if by_player != None:
			result = trigger.all(trigger.FAILED_TO_AVOID,[player,card],by_player,first_result = True)
			#by_player.persona.failed_to_avoid_power()
		return True

def choose_a_player(instruction_text,player,includes_self = True,hint = ai_hint.WORST):
	assemble = []
	for i,p in enumerate(globe.boss.players):
		if p != player or includes_self:
			assemble.append(p.persona)

	result = player.controler.choose_a_player(instruction_text,player,assemble,hint)
	if globe.DEBUG:
		print("choose_a_player",result)
	if not ensure_int(result):
		return choose_a_player(instruction_text,player,includes_self)
	elif result < 0 or result >= len(assemble):
		print(f"ERR: invalid number. max:{len(assemble)-1}")
		return choose_a_player(instruction_text,player,includes_self)
	return assemble[result].player

def choose_one_of(instruction_text,player,cards,hint = ai_hint.WORST):
	result = player.controler.choose_one_of(instruction_text,player,cards,hint)
	if globe.DEBUG:
		print("choose_one_of",result)
	if not ensure_int(result[0]):
		return choose_one_of(instruction_text,player,cards)
	elif result[0] < 0 or result[0] >= len(cards):
		print(f"ERR: invalid number. max:{len(cards)-1}")
		return choose_one_of(instruction_text,player,cards)
	return cards[result[0]]

def may_choose_one_of(instruction_text,player,cards,hint = ai_hint.BEST):
	if len(cards) == 0:
		return None
	result = player.controler.may_choose_one_of(instruction_text,player,cards,hint)
	if globe.DEBUG:
		print("may_choose_one_of",result)
	if result[0] == option.NO:
		return None
	elif result[0] == option.OK:
		if not ensure_int(result[1]):
			return may_choose_one_of(instruction_text,player,cards,hint)
		elif result[1] < 0 or result[1] >= len(cards):
			print(f"ERR: invalid number. max:{len(cards)-1}")
			return may_choose_one_of(instruction_text,player,cards,hint)
		return cards[result[1]]
	else:
		print(f"ERR: invalid responce code")
		return may_choose_one_of(instruction_text,player,cards,hint)


def ok_or_no(instruction_text,player,card = None,hint = ai_hint.IFBAD):
	result = player.controler.ok_or_no(instruction_text,player,card,hint)
	if globe.DEBUG:
		print("ok_or_no",result)
	if result[0] == option.OK:
		return True
	elif result[0] == option.NO:
		return False
	else:
		print(f"ERR: invalid responce code")
		return ok_or_no(instruction_text,player,hint)

def reveal(reveal_text,player,cards):
	for p in globe.boss.players:
		p.controler.reveal(reveal_text,player,cards)

#True for even
def choose_even_or_odd(instruction_text,player):
	result = player.controler.choose_even_or_odd(instruction_text,player)
	if globe.DEBUG:
		print("choose_even_or_odd",result)
	if result[0] == option.EVEN:
		return True
	if result[0] == option.ODD:
		return False
	else:
		return choose_even_or_odd(instruction_text,player)

# depreciated
# (no/hand/disccard, if hand or discard: #)
def may_destroy_card_in_hand_or_discard(player):
	result = player.controler.may_destroy_card_in_hand_or_discard()
	if globe.DEBUG:
		print("may_destroy_card_in_hand_or_discard",result)
	if len(result) != 2:
		print("ERR: not 2 attributes")
		return may_destroy_card_in_hand_or_discard(player)
	if result[0] == option.NO:
		return (option.NO,)
	elif result[0] == option.HAND or result[0] == option.DISCARD:
		if not ensure_int(result[1]):
			return may_destroy_card_in_hand_or_discard(player)
		elif result[0] == option.HAND and (result[1] < 0 or result[1] >= player.hand.size()):
			print(f"ERR: invalid number. max:{player.hand.size()-1}")
			return may_destroy_card_in_hand_or_discard(player)
		elif result[0] == option.DISCARD and (result[1] < 0 or result[1] >= player.discard.size()):
			print(f"ERR: invalid number. max:{player.discard.size()-1}")
			return may_destroy_card_in_hand_or_discard(player)
		card_to_destroy = None
		if result[0] == option.HAND:
			card_to_destroy = player.hand.contents.pop(result[1])
		else:
			card_to_destroy = player.discard.contents.pop(result[1])
		card_to_destroy.destroy()
		return (result[0],card_to_destroy)
	else:
		print(f"ERR: invalid responce code: {result[0]}")
		return may_destroy_card_in_hand_or_discard(player)


def choose_however_many(instruction_text,player,cards,hint):
	result = player.controler.choose_however_many(instruction_text,player,cards,hint = ai_hint.IFBAD)
	if globe.DEBUG:
		print("choose_however_many",result)
	if result[0] == option.NO:
		return None
	elif result[0] == option.OK:
		assemble = []
		for r in result[1:]:
			#print("FJFHJFHFHFHF",r)
			if not ensure_int(r):
				print(f"ERR: invalid symbol {r}.")
				return choose_however_many(instruction_text,player,cards,hint)
			elif r < 0 or r >= len(cards):
				print(f"ERR: invalid number {r}. max:{len(cards)-1}")
				return choose_however_many(instruction_text,player,cards,hint)
			assemble.append(cards[r])
		return assemble
	else:
		print(f"ERR: invalid responce code: {result[0]}")
		return choose_however_many(instruction_text,player,cards,hint)

