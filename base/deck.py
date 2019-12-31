from . import cards
from . import persona
import random
from frames import deck_frame


def initialize_supervillains():
	assemble = []
	assemble.append(cards.the_anti_monitor())
	assemble.append(cards.atrocitus())
	assemble.append(cards.black_manta())
	assemble.append(cards.brainiac())
	assemble.append(cards.captain_cold())
	assemble.append(cards.darkseid())
	assemble.append(cards.deathstroke())
	assemble.append(cards.the_joker())
	assemble.append(cards.lex_luther())
	assemble.append(cards.parallax())
	assemble.append(cards.sinestro())
	random.shuffle(assemble)
	#assemble.append(cards.the_joker())
	assemble.append(cards.ras_al_ghul())
	return assemble

deck = {cards.aquamans_trident: 3,
		cards.bane: 2,
		cards.the_batmobile: 3,
		cards.the_bat_signal: 3,
		cards.bizarro: 1,
		cards.blue_beetle: 1,
		cards.bulletproof: 3,
		cards.the_cape_and_cowl: 3,
		cards.catwoman: 3,
		cards.cheetah: 2,
		cards.clayface: 2,
		cards.the_dark_knight: 1,
		cards.doomsday: 2,
		cards.the_emerald_knight: 1,
		cards.fastest_man_alive: 1,
		cards.gorilla_grodd: 2,
		cards.green_arrow: 3,
		cards.green_arrows_bow: 3,
		cards.harley_quinn: 2,
		cards.heat_vision: 3,
		cards.high_tech_hero: 3,
		cards.jonn_jonzz: 1,
		cards.kid_flash: 4,
		cards.king_of_atlantis: 1,
		cards.lasso_of_truth: 3,
		cards.lobo: 1,
		cards.the_man_of_steel: 1,
		cards.mera: 2,
		cards.nth_metal: 4,
		cards.the_penguin: 2,
		cards.poison_ivy: 2,
		cards.power_ring: 3,
		cards.princess_diana_of_themyscira: 1,
		cards.the_riddler: 2,
		cards.robin: 3,
		cards.scarecrow: 2,
		cards.solomon_grundy: 2,
		cards.starro: 1,
		cards.suicide_squad: 6,
		cards.super_speed: 4,
		cards.super_strength: 3,
		cards.super_girl: 2,
		cards.swamp_thing: 2,
		cards.two_face: 2,
		cards.utility_belt: 3,
		cards.x_ray_vision: 3,
		cards.zatanna_zatara: 2,
		cards.arkham_asylum: 1,
		cards.the_batcave: 1,
		cards.fortress_of_solitude: 1,
		cards.titans_tower: 1,
		cards.the_watchtower: 1,
		}

def initialize_deck():
	assemble = []
	for card,num in deck.items():
		for i in range(num):
			assemble.append(card())
	random.shuffle(assemble)
	for i in range(6):
		assemble.append(cards.solomon_grundy())
	return assemble


this_set = deck_frame.deck_set("Base set",persona.get_personas,initialize_deck,initialize_supervillains,True)

