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
    def __init__(self):
        self.deck = []
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
                player.add_to_hand(self.deck.pop())
    
    def get_trump_card(self):
        return self.deck.pop()

    #reset the deck to get a new, unshuffled deck to start each hand.
    def reset(self):
        self.deck = copy.deepcopy(self.deck_backup)

class Game:
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
        self.current_player = self.first_bidder
        self.last_player = self.current_player.previous_player
        self.trump = None
        self.high_bidder = None
        self.total_bids = 0
        self.cards_played_trick = []
        self.game_deck = Deck()

        self.bids = {}
        self.cards_played_hand = {}
        self.tricks_won = {}
        self.scores = {}
        self.results = {}

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

        exit = True
        first = self.current_player
        while exit:
            self.current_player.make_bid(self.trump, self.total_bids, self.hand_number)
            next_player = self.current_player.next_player
            self.total_bids += self.current_player.bid
            self.current_player = next_player
            if self.current_player == first:
                exit = False

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

            exit = True
            first = self.current_player
            while exit:
                card = determine_card_to_play(self.current_player, self.cards_played_trick)
                self.cards_played_trick.append((self.current_player,card))
                next_player = self.current_player.next_player
                self.current_player = next_player
                if self.current_player == first:
                    exit = False

            #first player for next hand becomes trick winner. Last player is player behind trick winner
            self.current_player = determine_trick_winner(self.cards_played_trick, self.trump)
            self.last_player = self.current_player.previous_player
            self.current_player.tricks_won += 1

            self.cards_played_hand[self.tricks_left] = []

            for player, card in self.cards_played_trick:
                self.cards_played_hand[self.tricks_left].append((player.name,card.id))

            self.tricks_left -= 1
            #empty the cards played for the trick list after saving
            self.cards_played_trick = []

        #dealer for this hand is no longer the dealer
        self.dealer.is_dealer = False
        #Next hand will use one fewer card
        self.hand_number -= 1
        #reset the game deck to 52 cards
        self.game_deck.reset()
        #reset total bids to 0
        self.total_bids = 0
        #set dealer to player to the left of current dealer
        next_dealer = self.dealer.next_player
        next_dealer.is_dealer = True
        self.dealer = next_dealer
        #set first_bidder to left of dealer
        self.first_bidder = self.dealer.next_player

        #score hand
        for player in self.player_list:
            if player.bid == player.tricks_won:
                player.hand_score = 5 + player.tricks_won
            else:
                player.hand_score = 0
            self.scores[player.name] = player.hand_score
            self.tricks_won[player.name] = player.tricks_won
            self.bids[player.name] = player.bid

        #store results
        self.results[str(hand_number)+updown] = {'cards_played':self.cards_played_hand, 'hand_scores':self.scores,
                                            'tricks_won':self.tricks_won, 'bids':self.bids}

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