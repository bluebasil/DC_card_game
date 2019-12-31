from constants import option
from constants import ai_hint
import time
import random
import globe
from constants import cardtype
from frames import actions

view = None
def set_view(vi):
	global view
	view = vi


#import view
class controler:
	#boss = None
	player = None

	def __init__(self,player,invisible = None):
		#self.boss = boss
		self.player = player

	def choose_persona(self,persona_list):
		return persona_list[0]

	# Choose to end turn or play any cards
	def turn(self):
		#This is where turn logic goes
		return True

	def may_defend(self, options, attacking_card, attacking_player = None):
		return (option.OK,0)

	def choose_one_of(self,instruction_text,player,cards,hint):
		#base on hint
		return [0]

	def may_choose_one_of(self,instruction_text,player,cards,hint):
		#base on hint
		return [option.NO]

	#def may_put_on_top(self,instruction_text):
	#	return [option.OK]

	def ok_or_no(self,instruction_text,player,card,hint):
		return [option.NO]

	#No responce needed
	def reveal(self,instruction_text,player,cards):
		return

	def choose_even_or_odd(self,instruction_text,player):
		return [option.EVEN]

	def choose_a_player(self,instruction_text,player,options,hint):
		return 0

		min(self.player.pid,len(options)-1)

	#NO,HAND,DISCARD
	#def may_destroy_card_in_hand_or_discard(self):
	#	return (option.NO,-1)

	#only OK or CANNOT are accepted
	#def discard_a_card(self):
	#	return (option.OK,0)

	#NO,OK
	#def may_play_one_of_these_cards(self,cards):
	#	return (option.NO,-1)

	#NO,OK
	#def may_destroy_card_in_discard(self):
	#	return (option.NO,-1)

	def choose_however_many(self,instruction_text,player,cards,hint = None):
		return [option.NO]


class human_view(controler):

	def await_turn(self,process):
		#print(globe.bus.display,flush=True)
		#try:
		print("Waiting for player input...",flush = True)
		while True:
			#print(len(globe.bus.on_bus),flush = True)
			if len(globe.bus.on_bus) > 0:
				result = process()
				if result != None:
					return result
			time.sleep(0.1)
		#except Exception as e:
		#	print("ERRROROROROR:", e)

	def turn(self):
		globe.bus.clear()
		def process():
			current = globe.bus.read()
			if current.header == "card":

				#hand to play
				if current.content in self.player.hand.contents:
					self.player.play_c(current.content)
					globe.bus.clear()

				#lineup to buy
				if current.content in globe.boss.lineup.contents:
					self.player.buy_c(current.content)
					globe.bus.clear()

				#kick to buy
				if current.content in globe.boss.kick_stack.contents:
					self.player.buy_kick()
					globe.bus.clear()

				#sv to buy
				if current.content in globe.boss.supervillain_stack.contents:
					self.player.buy_supervillain()
					globe.bus.clear()

			if current.header == "button":

				#hand to play
				if current.content == actions.ENDTURN:
					globe.bus.clear()
					return True

				if type(current.content) == actions.special_action:
					self.player.click_action(current.content)
					#.click_action(self.player)
					globe.bus.clear()

		self.await_turn(process)

	def choose_persona(self,persona_list):
		globe.bus.clear()
		text = f"Who would you like to play as?"
		options = []
		for i in persona_list:
			options.append(i)
		#try:
		globe.bus.query(text,None,options)
		#except Exception as e:
		#	print("ERROR", e)
		def process():
			current = globe.bus.read()
			if current.header == "card":

				#hand to play
				if current.content in persona_list:
					return current.content


		choosen = self.await_turn(process)
		return choosen

	def may_defend(self, options, attacking_card, attacking_player = None):
		globe.bus.clear()
		text = f"You are getting attacked by {attacking_card.name}\n{attacking_card.attack_text}.\nWould you like to defend?"
		#try:
		options.insert(0,option.NO)
		globe.bus.query(text,attacking_card,options)
		#except Exception as e:
		#	print("ERROR", e)

		
		def process():
			current = globe.bus.read()
			if current.header == "card":
				#hand to play
				if current.content in options:
					globe.bus.clear()
					return (option.OK,options.index(current.content))

			if current.header == "button":

				#hand to play
				if current.content == option.NO:
					globe.bus.clear()
					return (option.NO,-1)
		
		return self.await_turn(process)

	def choose_one_of(self,instruction_text,player,cards,hint):
		options = cards
		globe.bus.clear()
		text = instruction_text
		#try:
		globe.bus.query(text,None,cards)
		#except Exception as e:
		#	print("ERRORR", e)

		
		def process():
			current = globe.bus.read()
			if current.header == "card":
				#hand to play
				if current.content in options:
					globe.bus.clear()
					return [options.index(current.content)]


		
		return self.await_turn(process)
		#base on hint
		#return [0]

	def may_choose_one_of(self,instruction_text,player,cards,hint):
		options = [option.NO]
		options.extend(cards)
		globe.bus.clear()
		text = instruction_text
		#try:
		globe.bus.query(text,None,options)
		#except Exception as e:
		#	print("ERROR", e)

		
		def process():
			current = globe.bus.read()
			if current.header == "card":
				#hand to play
				if current.content in options:
					globe.bus.clear()
					return [option.OK,cards.index(current.content)]

			if current.header == "button":

				#hand to play
				if current.content == option.NO:
					globe.bus.clear()
					return [option.NO]
		
		return self.await_turn(process)

	def ok_or_no(self,instruction_text,player,card,hint):
		options = [option.NO,option.OK]
		globe.bus.clear()
		text = instruction_text
		#try:
		globe.bus.query(text,card,options)
		#except Exception as e:
		#	print("ERROR", e)

		
		def process():
			current = globe.bus.read()
			if current.header == "button":
				if current.content == option.NO or current.content == option.OK:
					globe.bus.clear()
					return [current.content]

		return self.await_turn(process)


	#No responce needed
	def reveal(self,instruction_text,player,cards):
		options = [option.DONE]
		options.extend(cards)
		globe.bus.clear()
		text = instruction_text
		#try:
		globe.bus.query(text,None,options)
		#except Exception as e:
		#	print("ERROR", e)

		def process():
			current = globe.bus.read()
			if current.header == "button":
				if current.content == option.DONE:
					globe.bus.clear()
					return [current.content]

		return self.await_turn(process)


	def choose_even_or_odd(self,instruction_text,player):
		options = [option.ODD,option.EVEN]
		globe.bus.clear()
		text = instruction_text
		#try:
		globe.bus.query(text,None,options)
		#except Exception as e:
		#	print("ERROR", e)

		def process():
			current = globe.bus.read()
			if current.header == "button":
				if current.content == option.EVEN or current.content == option.ODD:
					globe.bus.clear()
					return [current.content]

		return self.await_turn(process)

	def choose_a_player(self,instruction_text,player,options,hint = None):
		globe.bus.clear()
		text = instruction_text
		globe.bus.query(text,None,options)

		def process():
			current = globe.bus.read()
			if current.header == "card":
				#hand to play
				if current.content in options:
					globe.bus.clear()
					return options.index(current.content)

		return self.await_turn(process)


	def choose_however_many(self,instruction_text,player,cards,hint = None):
		assemble = [option.OK]
		assemble_started = False
		while True:
			options = [option.DONE]
			for c in cards:
				if c not in assemble:
					options.append(c)
			globe.bus.clear()
			text = instruction_text
			#try:
			globe.bus.query(text,None,options)
			#except Exception as e:
			#	print("ERROR", e)

			
			def process():
				current = globe.bus.read()
				if current.header == "card":
					#hand to play
					if current.content in options:
						globe.bus.clear()
						return current.content

				if current.header == "button":

					#hand to play
					if current.content == option.DONE:
						globe.bus.clear()
						return option.DONE
			
			result = self.await_turn(process)
			if result == option.DONE and not assemble_started:
				return [option.NO]
			elif result == option.DONE:
				for i in range(1,len(assemble)):
					assemble[i] = cards.index(assemble[i])
				return assemble
			else:
				assemble_started = True
				assemble.append(result)


		#return [option.NO]


def get_input():
	global view
	x = input().split(" ")
	#try:
	if x[0] == "back":
		view.print_board()
	elif x[0] == "destroyed":
		view.print_destroyed()
	elif x[0] == "discard":
		if len(x) == 1:
			view.print_discard()
		else:
			try:
				intx = int(x[1])
				view.print_discard(intx)
			except:
				print("?")
	elif x[0] == "help":
		print("back, discard, others discard, help, ok, no, or a #")
	elif x[0] == "deck":
		if len(x) == 1:
			view.print_deck()
		else:
			try:
				intx = int(x[1])
				view.print_deck(intx)
			except:
				print("?")
	elif x[0] == "hand":
		if len(x) == 1:
			print("?")
		else:
			try:
				intx = int(x[1])
				view.print_hand(intx)
			except:
				print("?")
	elif x[0] == "play":
		if len(x) == 1:
			print("?")
		else:
			try:
				intx = int(x[1])
				view.print_played(intx)
			except:
				print("?")
	elif x[0] == "under":
		if len(x) == 1:
			print("?")
		else:
			try:
				intx = int(x[1])
				view.print_under(intx)
			except:
				print("?")
	elif x[0] == "actions":
		view.print_actions()
	else:
		return x
	return get_input()








class human(controler):
	global view
	def state_name(self):
		print(f" - {self.player.pid} - {self.player.persona.name} - ")

	def turn(self):
		view.print_board()
		print(f"{self.player.pid}'s Turn!")
		while True:
			x = get_input()
			if x[0] == "end":
				return
			#print(int(x))
			#try:
			if x[0] == "buy":
				result = False
				if x[1] == "sv":
					result = self.player.buy_supervillain()
					view.print_power()
				elif x[1] == "kick":
					result = self.player.buy_kick()
					view.print_power()
				else:
					safe = True
					intx = -1
					try:
						intx = int(x[1])
					except:
						print("?")
						safe = False
					if safe:
						result = self.player.buy(int(x[1]))
						view.print_board()
				if not result:
					print("COULD NOT BUY")
			elif x[0] == "action":
				safe = True
				intx = -1
				try:
					intx = int(x[1])
				except:
					safe = False
					print("?")
				if safe:
					self.player.played.special_options[intx].click_action(self.player)
					print("clicked")

			elif x[0] == "sh":
				result = self.player.persona.any_time()
			else:
				safe = True
				intx = -1
				try:
					intx = int(x[0])
				except:
					print("?")
					safe = False
				if safe:
					if intx < 0 or intx >= self.player.hand.size():
						print("Err: Not a valid card")
					else:
						self.player.play(intx)
						view.print_board()
				else:
					print("?")
			#except Exception as e:
			#	print("?", e)
			#except:
			#	print("?")

	def choose_persona(self,persona_list):
		print("Who would you like to be?")
		for i,p in enumerate(persona_list):
			print(f"{i} {p.name}: {p.text}")
		x = get_input()
		try:
			intx = int(x[0])
		except:
			print("?")
			return self.choose_persona(persona_list)
		return persona_list[intx]


	def may_defend(self, options, attacking_card, attacking_player = None):
		global view
		self.state_name()
		print(f"!{self.player.pid}! may_defend")
		print(f"{attacking_card.name}'s attack: {attacking_card.attack_text}.")
		view.print_custom(options)
		x = get_input()
		if x[0] == "no":
			return (option.NO,-1)
		elif x[0] == "ok":
			intx = -1
			try:
				intx = int(x[1])
			except:
				print("?")
				return self.may_defend(options,attacking_card,attacking_player)
			return (option.OK,intx)
		else:
			print("?")
			return self.may_defend(options,attacking_card,attacking_player)

	def choose_one_of(self,instruction_text,player,cards,hint):
		self.state_name()
		global view
		print(f"{instruction_text}  ( '0' / '2' )")
		view.print_custom(cards)
		print(instruction_text)
		x = get_input()
		intx = -1
		try:
			intx = int(x[0])
		except:
			print("?")
			return self.choose_one_of(instruction_text,player,cards,hint)
		return [intx]

	def may_choose_one_of(self,instruction_text,player,cards,hint):
		self.state_name()
		global view
		print(f"{instruction_text} ('no' / 'ok 2')")
		view.print_custom(cards)
		print(instruction_text)
		x = get_input()
		if x[0] == "no":
			return [option.NO]
		elif x[0] == "ok":
			intx = -1
			safe = True
			try:
				intx = int(x[1])
			except:
				print("?")
				safe = False
			if safe:
				return [option.OK,intx]
		print("??")
		return self.may_choose_one_of(instruction_text,player,cards,hint)

	def ok_or_no(self,instruction_text,player,card,hint):
		self.state_name()
		global view
		print(f"{instruction_text} ('ok / 'no')")
		if card != None:
			view.print_card(card)
			print(instruction_text)
		x = get_input()
		if x[0] == "ok":
			return [option.OK]
		elif x[0] == "no":
			return [option.NO]
		else:
			print("?")
			return self.ok_or_no(instruction_text,player,card,hint)

	def reveal(self,instruction_text,player,cards):
		self.state_name()
		global view
		print(instruction_text, flush = True)
		view.print_custom(cards)
		time.sleep(3)
		return

	def choose_even_or_odd(self,instruction_text,player):
		self.state_name()
		print(f"{instruction_text} ('even'/'odd')")
		x = get_input()
		if x[0] == "even":
			return [option.EVEN]
		elif x[0] == "odd":
			return [option.ODD]
		else:
			return choose_even_or_odd(instruction_text,player)

	def choose_a_player(self,instruction_text,player,options):
		self.state_name()
		print(instruction_text)
		for i,p in enumerate(options):
			print(f"{i} - {p.persona.name}")
		x = get_input()
		intx = -1
		try:
			intx = int(x[0])
		except:
			print("?")
			return self.choose_a_player(instruction_text,player,options)
		return [intx]


	def choose_however_many(self,instruction_text,player,cards,hint = None):
		print(f"{instruction_text} (Example: 'no', or 'ok 0 2 3')")
		x = get_input()
		if x[0] == "no":
			return [option.NO]
		elif x[0] == "ok":
			assemble = [option.OK]
			for r in x[1:]:
				safe = True
				intx = -1
				try:
					intx = int(r)
				except:
					print("?")
					safe = False
				if not safe:
					print(f"Unknown # {r}")
					return self.choose_however_many(self,instruction_text,player,cards,hint)
				assemble.append(intx)
			return assemble
		print("?")
		return self.choose_however_many(self,instruction_text,player,cards,hint)



class cpu(controler):
	#sleep length between actions
	slti = 0
	invisible = False

	def __init__(self,player,invisible = False):
		#self.boss = boss
		self.player = player
		self.invisible = invisible
		self.slti = globe.TIME_BETWEEN_CPU_MOVES

	def display_thought(self,text,long = False,quick = True):
		if not self.invisible:
			print(text, flush = True)
			if not quick:
				time.sleep(self.slti)
				if long:
					time.sleep(self.slti)

	def sort_by_cost(self,card):
		if card.name == "Weakness":
			return -2
		if card.name == "Vunerability":
			return -1
		#if card.name == "Punch":
		return card.cost + self.player.persona.ai_overvalue(card)

	def sort_by_play_order(self,card):
		if card.name == "Weakness":
			return 500
		if card.name == "Vunerability":
			return 750
		if card.name == "Punch":
			return 250
		if card.ctype_eq(cardtype.LOCATION):
			return -1
		return card.cost

	def choose_persona(self,persona_list):
		return random.choice(persona_list)

	# Choose to end turn or play any cards
	def turn(self):
		global view
		if not self.invisible:
			view.print_board()
		self.display_thought(f"Begining of AI {self.player.pid}'s turn",quick = False)
		self.player.hand.contents.sort(key = self.sort_by_play_order)

		self.player.persona.ai_is_now_a_good_time()
		
		while self.player.hand.size() > 0:
			size_check = self.player.hand.size()
			self.display_thought(f"AI {self.player.pid}-{self.player.persona.name} is going to play a {self.player.hand.contents[0].name} (total power = {self.player.played.power})",quick = False)
			self.player.play(0)
			if size_check - 1 != self.player.hand.size():
				self.display_thought("(Differtent cards than expected)",quick = False)
				self.player.hand.contents.sort(key = self.sort_by_play_order)
			self.player.persona.ai_is_now_a_good_time()

		self.display_thought(f"AI {self.player.pid}-{self.player.persona.name} has {self.player.played.power} power!",quick = False)
		if globe.boss.supervillain_stack.size() > 0 and self.player.buy_supervillain():
			self.display_thought(f"AI {self.player.pid}-{self.player.persona.name} is buying the supervillain! ({self.player.played.power} power left)",True,quick = False)
		assemble = []
		for c in globe.boss.lineup.contents:
			assemble.append(c)
		assemble.sort(key = self.sort_by_cost)
		#Tries to buy everything from most to least expensive
		while len(assemble) > 0:
			test = assemble.pop()
			if self.player.buy_c(test):
				self.display_thought(f"AI {self.player.pid}-{self.player.persona.name} bought {test.name} ({self.player.played.power} power left)",True,quick = False)
		while self.player.played.power >= 3 and globe.boss.kick_stack.size() > 0:
			self.player.buy_kick()
			self.display_thought(f"AI {self.player.pid}-{self.player.persona.name} bought a kick ({self.player.played.power} power left)",True,quick = False)

		return

	def may_defend(self, options, attacking_card, attacking_player = None):
		self.display_thought(f"AI {self.player.pid}-{self.player.persona.name} choose to defend with {options[0]}")
		return (option.OK,0)


	def choose_one_of(self,instruction_text,player,cards,hint):
		cards.sort(key = self.sort_by_cost)
		self.display_thought(f"AI {self.player.pid}-{self.player.persona.name} got:{instruction_text}")
		if hint == ai_hint.BEST:
			self.display_thought(f"AI {self.player.pid}-{self.player.persona.name} choose {cards[-1].name}")
			return [len(cards)-1]
		elif hint == ai_hint.WORST:
			self.display_thought(f"AI {self.player.pid}-{self.player.persona.name} choose {cards[0].name}")
			return [0]
		elif hint == ai_hint.RANDOM:
			return [random.randint(0,len(cards)-1)]
		self.display_thought(f"AI {self.player.pid}-{self.player.persona.name} choose {cards[0].name}")
		return [0]

	def may_choose_one_of(self,instruction_text,player,cards,hint):
		cards.sort(key = self.sort_by_cost)
		self.display_thought(f"AI {self.player.pid}-{self.player.persona.name} got:{instruction_text}")
		if len(cards) == 0:
			return [option.NO]
		if hint == ai_hint.BEST and cards[-1].cost >= 3:
			self.display_thought(f"AI {self.player.pid}-{self.player.persona.name} choose {cards[-1].name}")
			return [option.OK,len(cards)-1]
		elif hint == ai_hint.WORST and cards[0].cost <= 2:
			self.display_thought(f"AI {self.player.pid}-{self.player.persona.name} choose {cards[0].name}")
			return [option.OK,0]
		elif hint == ai_hint.IFBAD and cards[0].cost <= 3:
			self.display_thought(f"AI {self.player.pid}-{self.player.persona.name} choose {cards[0].name}")
			return [option.OK,0]
		elif hint == ai_hint.RANDOM:
			return [option.OK,random.randint(0,len(cards)-1)]
		else:
			self.display_thought(f"AI {self.player.pid}-{self.player.persona.name} choose not to so")
			return [option.NO]
		

	def ok_or_no(self,instruction_text,player,card,hint):
		self.display_thought(f"AI {self.player.pid}-{self.player.persona.name} got:{instruction_text}")
		if hint == ai_hint.ALWAYS:
			self.display_thought(f"AI {self.player.pid}-{self.player.persona.name} choose to do so")
			return [option.OK]
		elif hint == ai_hint.IFBAD and card.cost > 1:
			self.display_thought(f"AI {self.player.pid}-{self.player.persona.name} choose NOT to do so")
			return [option.NO]
		elif hint == ai_hint.NEVER:
			self.display_thought(f"AI {self.player.pid}-{self.player.persona.name} choose NOT to do so")
			return [option.NO]
		elif card != None and hint == ai_hint.IFGOOD:
			if card.cost >= 4:
				self.display_thought(f"AI {self.player.pid}-{self.player.persona.name} choose to do so")
				return [option.OK]
			else:
				self.display_thought(f"AI {self.player.pid}-{self.player.persona.name} choose NOT to do so")
				return [option.NO]
		else:
			self.display_thought(f"AI {self.player.pid}-{self.player.persona.name} choose to do so (by default)")
			return [option.OK]

	def choose_a_player(self,instruction_text,player,options,hint):
		if hint == ai_hint.BEST:
			if self.player in options:
				return options.index(self.player)
			else:
				return random.randint(0,len(options) - 1)
		elif hint == ai_hint.WORST:
			if self.player in options:
				choose = random.randint(0,len(options) - 1)
				if choose >= options.index(self.player):
					choose += 1
				return choose
			else:
				return random.randint(0,len(options) - 1)
		else:
			return random.randint(0,len(options) - 1)

		

	def choose_however_many(self,instruction_text,player,cards,hint):
		if hint == ai_hint.IFBAD:
			choose = [option.OK]
			for i,c in enumerate(cards):
				if c.cost <= 4:
					choose.append(i)
			if len(choose) > 1:
				return choose
		return [option.NO]




class cpu_greedy(cpu):

	# Choose to end turn or play any cards
	def turn(self):
		global view
		if not self.invisible:
			view.print_board()
		self.display_thought(f"Begining of AI {self.player.pid}'s turn",quick = False)
		self.player.hand.contents.sort(key = self.sort_by_play_order)
		
		while self.player.hand.size() > 0:
			size_check = self.player.hand.size()
			self.display_thought(f"AI {self.player.pid}-{self.player.persona.name} is going to play a {self.player.hand.contents[0].name} (total power = {self.player.played.power})",quick = False)
			self.player.play(0)
			if size_check - 1 != self.player.hand.size():
				self.display_thought("(Differtent cards than expected)",quick = False)
				self.player.hand.contents.sort(key = self.sort_by_play_order)

		self.display_thought(f"AI {self.player.pid}-{self.player.persona.name} has {self.player.played.power} power!",quick = False)
		if globe.boss.supervillain_stack.size() > 0 and self.player.played.power >= globe.boss.supervillain_stack.contents[-1].cost:
			self.player.buy_supervillain()
			self.display_thought(f"AI {self.player.pid}-{self.player.persona.name} is buying the supervillain! ({self.player.played.power} power left)",quick = False)
		assemble = []
		for c in globe.boss.lineup.contents:
			assemble.append(c)
		assemble.sort(reverse = True,key = self.sort_by_cost)
		#Tries to buy everything from most to least expensive
		while len(assemble) > 0:
			test = assemble.pop()
			if self.player.buy_c(test):
				self.display_thought(f"AI {self.player.pid}-{self.player.persona.name} bought {test.name} ({self.player.played.power} power left)",quick = False)
		while self.player.played.power >= 3 and globe.boss.kick_stack.size() > 0:
			self.player.buy_kick()
			self.display_thought(f"AI {self.player.pid}-{self.player.persona.name} bought a kick ({self.player.played.power} power left)",quick = False)

		return