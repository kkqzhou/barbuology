import numpy as np
import cv2
import pyautogui
import sys

from sewar.full_ref import mse
from time import sleep

import matplotlib.pyplot as plt

def screenshot(filename='C:\\Users\\kkqzh\\Python Files\\for_fun\\barbu\\shot.png'):
    image = pyautogui.screenshot()
       
    # since the pyautogui takes as a 
    # PIL(pillow) and in RGB we need to 
    # convert it to numpy array and BGR 
    # so we can write it to the disk
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
       
    # writing it to the disk using opencv
    cv2.imwrite(filename, image)
    return image

def get_mse(img, card_text):
    card = plt.imread('cards/' + card_text + '.png')[:,:,:3]
    return mse(img, card)

def get_cards_str(card_texts, sep='  ', custom_annotations=None):
    grouped_cards = [
        sorted([x for x in card_texts if x[0] == suit_text], key=lambda z: -card_text_to_num[z[:2]])
        for suit_text in 'cdsh'
    ]
    return sep.join([
        ''.join([x[1].upper() for x in lst]) + \
        ' [' + (str(len(lst)) if custom_annotations is None else custom_annotations[i]) + ']'
        for i, lst in enumerate(grouped_cards)])

SEATS_SHORT_TO_ORDINAL = {'S': 0, 'W': 1, 'N': 2, 'E': 3}
ORDINAL_TO_SEATS_SHORT = {y: x for x, y in SEATS_SHORT_TO_ORDINAL.items()}
leader_ordinal = SEATS_SHORT_TO_ORDINAL[sys.argv[1].upper()]

calibration_r, calibration_c = 138, 1085


SEATS = {0: 'SS', 1: 'WW', 2: 'NN', 3: 'EE'}
SEATS_TO_ORDINAL = {y: x for x, y in SEATS.items()}
cards_played = {'SS': [], 'WW': [], 'NN': [], 'EE': []}
may_have_suit = {'c': set(range(4)), 'd': set(range(4)), 's': set(range(4)), 'h': set(range(4))}
num_to_card_text = dict(enumerate([x + y for x in 'cdsh' for y in '23456789tjqka']))
card_text_to_num = {y: x for x, y in num_to_card_text.items()}
remaining_cards = set(card_text_to_num)
old_remaining_cards_len = len(remaining_cards)

while True:
    screenshot()
    img = plt.imread('C:\\Users\\kkqzh\\Python Files\\for_fun\\barbu\\shot.png')
    h, w = 94, 70
    card_images = {
        'SS': img[calibration_r+556:calibration_r+556+h,calibration_c-38:calibration_c-38+w,:3],
        'WW': img[calibration_r+496:calibration_r+496+h,calibration_c-118:calibration_c-118+w,:3],
        'NN': img[calibration_r+436:calibration_r+436+h,calibration_c-38:calibration_c-38+w,:3],
        'EE': img[calibration_r+496:calibration_r+496+h,calibration_c+42:calibration_c+42+w,:3]
    }

    for i in range(4):
        player_ordinal = (leader_ordinal + i) % 4
        seat = SEATS[player_ordinal]
        player_card = card_images[seat]
        _match = []
        for card_text in card_text_to_num:
            _match.append((get_mse(player_card, card_text), card_text))
            
        card_mse, matched_card = sorted(_match)[0]
        fine_matches = {'da'}
        if matched_card not in remaining_cards or (
            card_mse > 0.07 and matched_card not in fine_matches or card_mse > 0.025 and matched_card in fine_matches):
            print(matched_card, card_mse)
            break

        if player_ordinal == leader_ordinal:
            leader_suit = matched_card[0]
            cards_played[seat].append(matched_card + '*')
        elif matched_card[0] != leader_suit:
            cards_played[seat].append(matched_card + "'")
            if player_ordinal in may_have_suit[leader_suit]:
                may_have_suit[leader_suit].remove(player_ordinal)
        else:
            cards_played[seat].append(matched_card + ' ')
        remaining_cards.remove(matched_card)

    if len(remaining_cards) < old_remaining_cards_len:  
        old_remaining_cards_len = len(remaining_cards)
        print('\n'*3)
        for seat, x in cards_played.items():
            print(seat + ' ' * (5-len(seat)), ''.join(x))
            print(get_cards_str(x, custom_annotations=['C', 'D', 'S', 'H']))
            print()
            
        print()
        print('remaining (' + str(len(remaining_cards)) + '):')
        remaining_cards_annotations = [
            suit_text.upper() + ' ' + ''.join([ORDINAL_TO_SEATS_SHORT[x] for x in sorted(player_ordinals)])
            for suit_text, player_ordinals in may_have_suit.items()
        ]
        print(get_cards_str(remaining_cards, sep='\n', custom_annotations=remaining_cards_annotations))

    assert len(cards_played['EE']) == len(cards_played['NN']) == len(cards_played['WW']) == len(cards_played['SS'])
    if len(cards_played['EE']) > 0:
        played_in_leader_suit = [
            (seat, played[-1]) for seat, played in cards_played.items() if played[-1][0] == leader_suit
        ]
        leader_seat = sorted(played_in_leader_suit, key=lambda x: card_text_to_num[x[1][:2]])[-1][0]
        leader_ordinal = SEATS_TO_ORDINAL[leader_seat]

    sleep(1)