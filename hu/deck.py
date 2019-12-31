from . import cards
from . import persona
import random
from frames import deck_frame


def initialize_supervillains():
	assemble = []
	assemble.append(cards.amazo())
	assemble.append(cards.arkillo())
	assemble.append(cards.black_adam())
	assemble.append(cards.graves())
	assemble.append(cards.hel())
	assemble.append(cards.hector_hammond())
	assemble.append(cards.helspont())
	assemble.append(cards.mongul())
	assemble.append(cards.mr_freeze())
	assemble.append(cards.nekron())
	assemble.append(cards.trigon())
	random.shuffle(assemble)
	assemble.append(cards.vandal_savage())
	return assemble

deck = {
	cards.crimson_whirlwind : 1,
	cards.daughter_of_gotham_city: 2,
	cards.deadman: 2,
	cards.hawkgirl: 2,
	cards.hero_of_the_future: 2,
	cards.jason_blood: 1,
	cards.katana: 4,
	cards.kyle_rayner: 1,
	cards.plastic_man: 3,
	cards.raven:3,
	cards.saint_walker: 2,
	cards.sonic_siren: 2,
	cards.superboy:2,
	cards.warrior_princess:1,
	cards.winged_warrior:1,
	cards.wonder_of_the_knight:1,
	cards.worlds_mightiest_mortal:1,
	cards.black_lantern_corps:2,
	cards.brother_blood: 2,
	cards.deadshot: 2,
	cards.the_demon_etrigan: 1,
	cards.dr_sivana:2,
	cards.granny_goodness:2,
	cards.jervis_tetch:2,
	cards.killer_croc:2,
	cards.larfleeze:2,
	cards.manhunter:6,
	cards.mr_zsasz:2,
	cards.ocean_master:2,
	cards.parasite:2,
	cards.red_lantern_corps:2,
	cards.talon:2,
	cards.canary_cry:3,
	cards.force_field:2,
	cards.power_of_the_green:2,
	cards.shazam:2,
	cards.starbolt:3,
	cards.teleportation:1,
	cards.whirlwind:3,
	cards.batarang:4,
	cards.helmet_of_fate:2,
	cards.legion_flight_ring:4,
	cards.mind_control_hat:1,
	cards.red_lantern_power_ring:1,
	cards.orange_lantern_power_ring:1,
	cards.yellow_lantern_power_ring:1,
	cards.green_lantern_power_ring:1,
	cards.blue_lantern_power_ring:1,
	cards.indigo_tribe_power_ring:1,
	cards.star_sapphire_power_ring:1,
	cards.sciencell:2,
	cards.skeets:3,
	cards.soultaker_sword:3,
	cards.white_lantern_power_battery:1,
	cards.apokolips:1,
	cards.gotham_city:1,
	cards.metropolis:1,
	cards.new_genesis:1,
	cards.oa:1,
}

def initialize_deck():
	assemble = []
	for card,num in deck.items():
		for i in range(num):
			assemble.append(card())
	random.shuffle(assemble)
	return assemble

this_set = deck_frame.deck_set("Heroes Unite set",persona.get_personas,initialize_deck,initialize_supervillains,True)
