import random
import copy
from util import partition

class Card:
    def __init__(self, id, suit, name, value):
        self.id = id
        self.suit = suit
        self.name = name
        self.value = value

    def compare(self, card2):
        if self.value > card2.value:
            return 1
        elif self.value < card2.value:
            return -1
        else:
            return 0

class Deck:
    def __init__(self):
        self.deck = []
        self.deck_backup = []

    def create_deck(self):
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        values = [2,3,4,5,6,7,8,9,10,11,12,13,14]
        names = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
        for suit in suits:
            suit_letter = suit[0].upper()  # First letter of the suit
            for i, value in enumerate(values):
                card_id = f"{names[i][0] if names[i] != '10' else '0'}{suit_letter}" 
                card = Card(card_id, suit, names[i], values[i])
                self.deck.append(card)
        self.deck_backup = copy.deepcopy(self.deck)

    def get_card_ids(self):
        ids = []
        for card in self.deck:
            ids.append(card.id)
        return ids
    
    def shuffle(self):
        random.shuffle(self.deck)

    #deal cards to each player, popping them from the end of the deck. When done, flip over the trump card and save it. Then, reset the deck.
    def deal(self, players, num_cards):
        for player in players:
            for i in range(num_cards):
                player.add_to_hand(self.pop())
    
    def reset(self):
        self.deck = self.deck_backup

class Game:
    num_players = 0

    def __init__(self, num_players = 5):
        self.num_players = num_players

class Player:
    hand = []

    def add_to_hand(self,card):
        self.hand.append(card)

newdeck = Deck()
newdeck.create_deck()
print(newdeck.get_card_ids())
newdeck.shuffle()
print(newdeck.get_card_ids())