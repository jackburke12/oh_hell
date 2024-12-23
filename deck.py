import random
import copy
from util import partition, determine_bid, find_high_bidder, determine_card_to_play, determine_trick_winner

class Card:
    def __init__(self, id, suit, name, value):
        self.id = id
        self.suit = suit
        self.name = name
        self.value = value

    def compare(self, card2):
        if self.value >= card2.value:
            return 1
        elif self.value < card2.value:
            return -1
        else:
            return 0

class Deck:
    deck = []
    deck_backup = []

    def __init__(self):
        self.deck.clear()
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
    
    def shuffle(self):
        random.shuffle(self.deck)

    def deal(self, players, num_cards):
        for player in players:
            for i in range(num_cards):
                player.add_to_hand(self.pop())
    
    def get_trump_card(self):
        return self.deck.pop()

    #reset the deck to get a new, unshuffled deck to start each hand.
    def reset(self):
        self.deck = copy.deepcopy(self.deck_backup)

class Game:
    game_deck = Deck()
    num_players = 0
    player_list = []
    cards_played = []
    current_player = None
    last_player = None
    trump = None
    first_bidder = None
    high_bidder = None
    dealer = None
    tricks_left = None
    hand_number = None
    total_hands = None
    total_bids = 0
    plays = {}

    def __init__(self, player_list):
        if len(player_list) == 5 or len(player_list) == 4:
            self.total_hands = 10
        elif len(player_list) == 6:
            self.total_hands = 8
        else:
            print("Games must have 4, 5, or 6 players.")
        self.num_players = len(player_list)
        self.player_list = player_list 
        self.tricks_left = self.hand_number
        self.hand_number = self.total_hands
        self.dealer = random.choice(self.player_list)
        self.first_bidder = self.dealer.next_player

    def play_hand(self,hand_number):
        self.hand_number = hand_number
        self.tricks_left = hand_number

        self.game_deck.shuffle()
        self.game_deck.deal(self.player_list, self.hand_number)
        self.trump = self.game_deck.get_trump_card()
        if self.trump.value == 14:
            self.trump.suit = "no_trump"
        
        #bid loop
        self.current_player = self.first_bidder

        while self.current_player != self.dealer:
            self.current_player.make_bid(self.trump)
            next_player = self.current_player.next_player
            self.total_bids += self.current_player.bid
            self.current_player = next_player

        self.current_player.make_bid(self.trump)

        #determine first bidder
        self.first_bidder = find_high_bidder(self.first_bidder)
        self.current_player = self.first_bidder
        self.last_player = self.current_player.previous_player
        #bids made, first player set to high bidder
        #play the trick
        while self.current_player != self.last_player:
            card = determine_card_to_play(self.current_player)
            self.cards_played.append((self.current_player,card))
            next_player = self.current_player.next_player
            self.current_player = next_player
        
        self.cards_played.append((self.current_player,determine_card_to_play(self.current_player)))

        #check that all values are set/reset correctly
        self.current_player = determine_trick_winner(self.cards_played)
        self.current_player.tricks_won += 1
        self.hand_number -= 1
        self.game_deck.reset()

    def simulate_game(self):
        #play hands 10-1 loop
            #create deck
            #shuffle deck
            #deal cards
            #determine trump card
            #bid loop
                #first bidder bids
                #last bid must fit condition total bids != total tricks
            #determine first player
            #play cards loop
                #determine trick winner
            #save trick results
            #score hand
            #update dealer

        #play hands 2-10
        for i in range(self.total_hands, 0, -1):
            play_hand(i)
        
        #for i in range(1, self.total_hands, 1):
            play_hand(i)

        
class Player:
    name = ""
    hand = []
    bid = None
    next_player = None
    previous_player = None
    is_dealer = False
    tricks_won = 0

    def __init__(self, name):
        self.name = name

    def add_to_hand(self,card):
        self.hand.append(card)

    def update_next_player(self, next_player, previous_player):
        self.next_player = next_player
        self.previous_player = previous_player
    
    def make_bid(self, trump_suit, total_bids, tricks_left):
        self.bid = determine_bid(self.hand, trump_suit, self.is_dealer)
        ##need to add logic to adjust bid if dealer
        if self.is_dealer and total_bids == tricks_left:
            self.bid += 1
    
player1 = Player("Jack")
player2 = Player("Kelly")
player3 = Player("Tim")
player4 = Player("Mom")
player5 = Player("Dad")

player1.update_next_player(player2, player5)
player2.update_next_player(player3, player1)
player3.update_next_player(player4, player2)
player4.update_next_player(player5, player3)
player5.update_next_player(player1, player4)