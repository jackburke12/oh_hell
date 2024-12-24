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
            print(player.name)
            for i in range(num_cards):
                player.add_to_hand(self.deck.pop())
                print(player.hand)
    
    def get_trump_card(self):
        return self.deck.pop()

    #reset the deck to get a new, unshuffled deck to start each hand.
    def reset(self):
        self.deck = copy.deepcopy(self.deck_backup)

class Game:
    game_deck = Deck()
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
    scores = {}
    plays = {}
    results = {}
    tricks_won = {}
    bids = {}

    def __init__(self, player_list):
        if len(player_list) == 5 or len(player_list) == 4:
            self.total_hands = 10
        elif len(player_list) == 6:
            self.total_hands = 8
        else:
            print("Games must have 4, 5, or 6 players.")
        self.num_players = len(player_list)
        self.player_list = player_list 
        self.hand_number = self.total_hands
        self.tricks_left = self.hand_number
        self.dealer = random.choice(self.player_list)
        self.dealer.is_dealer = True
        self.first_bidder = self.dealer.next_player

        self.cards_played = []

    def play_hand(self,hand_number,updown):
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
            self.current_player.make_bid(self.trump, self.total_bids, self.hand_number)
            next_player = self.current_player.next_player
            self.total_bids += self.current_player.bid
            self.current_player = next_player

        self.current_player.make_bid(self.trump, self.total_bids, self.hand_number)

        #find_high_bidder is working fine, bids are not being made. Understandable
        #determine first bidder
        self.first_bidder = find_high_bidder(self.first_bidder)
        self.current_player = self.first_bidder
        self.last_player = self.current_player.previous_player
        #bids made, first player set to high bidder
        #play #tricks = hand number. 10 tricks are played for hand 10, 9 tricks for hand 9...

        while self.tricks_left > 0:
            #each player chooses a card to play, plays it, then play moves to the next player
            #exit loop when you get to the last player
            while self.current_player != self.last_player:
                card = determine_card_to_play(self.current_player)
                self.cards_played.append((self.current_player,card))
                next_player = self.current_player.next_player
                self.current_player = next_player
            
            #last player chooses a card and plays it
            self.cards_played.append((self.current_player,determine_card_to_play(self.current_player)))

            #first player for next hand becomes trick winner. Last player is player behind trick winner
            self.current_player = determine_trick_winner(self.cards_played)
            self.last_player = self.current_player.previous_player
            self.current_player.tricks_won += 1
            self.tricks_left -= 1

        self.hand_number -= 1
        self.game_deck.reset()
        self.cards_played = []
        self.total_bids = 0
        next_dealer = self.dealer.next_player
        next_dealer.is_dealer = True
        self.dealer = next_dealer
        self.first_bidder = self.dealer.next_player


        #score hand
        for player in self.player_list:
            if player.bid == player.tricks_won:
                player.hand_score = 5 + player.tricks_won
            else:
                player.hand_score = 0
            self.scores[player] = player.hand_score
            self.tricks_won[player] = player.tricks_won
            self.bids[player] = player.bid

        #store results
        self.results[str(hand_number)+updown] = {'cards_played':self.cards_played, 'hand_scores':self.scores,
                                            'tricks_won':self.tricks_won, 'bids':self.bids}
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

class Simulator:
    def __init__(self, player_list):
        self.game = Game(player_list)

    def play_game(self):
        for i in range(10, 0, -1):
            self.game.play_hand(i, "down")
        
        for i in range(2,11,1):
            self.game.play_hand(i, "up")

        print(self.game.results)


class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.bid = 0
        self.next_player = None
        self.previous_player = None
        self.is_dealer = False
        self.tricks_won = 0
        self.hand_score = 0

    def add_to_hand(self,card):
        self.hand.append(card)

    def update_next_player(self, next_player, previous_player):
        self.next_player = next_player
        self.previous_player = previous_player
    
    def make_bid(self, trump_card, total_bids, total_tricks):
        self.bid = determine_bid(self.hand, trump_card, self.is_dealer)
        print(self.bid)
        ##need to add logic to adjust bid if dealer
        if self.is_dealer and total_bids == total_tricks:
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

sim1 = Simulator([player1,player2,player3,player4,player5])
sim1.play_game()