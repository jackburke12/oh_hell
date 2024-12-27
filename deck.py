import random
import copy
import pandas as pd
from util import partition, determine_bid, find_high_bidder, determine_card_to_play, determine_trick_winner, unzip_card_played, unzip_cards_played_trick

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
    def __init__(self, player_names):
        self.player_list = []
        for name in player_names:
            self.player_list.append(Player(name))

        first = self.player_list[0]
        last = self.player_list[-1]

        for i, player in enumerate(self.player_list):
            if player == first:
                player.update_next_player(self.player_list[i+1],last)
            elif player == last:
                player.update_next_player(first,self.player_list[i-1])
            else:
                player.update_next_player(self.player_list[i+1],self.player_list[i-1])

        if len(player_names) == 5 or len(player_names) == 4:
            self.total_hands = 10
        elif len(player_names) == 6:
            self.total_hands = 8
        else:
            print("Games must have 4, 5, or 6 players.")
        self.num_players = len(player_names)
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
        self.play_data = []

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

        self.cards_played_hand[self.hand_number] = []

        #bids made, first player set to high bidder
        #play #tricks = hand number. 10 tricks are played for hand 10, 9 tricks for hand 9...
        while self.tricks_left > 0:
            #each player chooses a card to play, plays it, then play moves to the next player
            #exit loop when you get to the last player
            exit = True
            first = self.current_player
            while exit:
                card = determine_card_to_play(self.current_player, self.cards_played_trick)
                #add card to list of cards played this trick
                self.cards_played_trick.append((self.current_player,card))
                #add card to dict of cards played this hand
                self.cards_played_hand[self.hand_number].append((self.current_player.name,card.id))
                #after card is chosen, add all data informing that decision to the "play_data" list of dicitonaries
                self.play_data.append(copy.deepcopy({"card_played":card.id,"hand_result":pd.NA, "player": self.current_player.name, "trump_card":self.trump.id,
                                       "card_led":unzip_card_played(self.cards_played_trick[0]), "player_bid":self.current_player.bid,
                                       "player_tricks_taken":self.current_player.tricks_won,"player_hand":self.current_player.get_hand(),
                                       "total_bids":self.total_bids, "total_tricks_taken":self.hand_number-len(self.current_player.hand)-1,
                                       "all_cards_played":self.cards_played_hand, "hand_number":self.hand_number,
                                       "cards_played_trick":unzip_cards_played_trick(self.cards_played_trick),
                                       }))

                #add data from each card played as a tuple to the self.play_data list
                #(card played, player, trump card id, card led, player bid, player tricks taken,
                #player hand, all bids, all tricks taken, all tricks remaining, all cards played,
                #hand number, cards played this trick, hand_result)

                next_player = self.current_player.next_player
                self.current_player = next_player
                if self.current_player == first:
                    exit = False

            #first player for next hand becomes trick winner. Last player is player behind trick winner
            self.current_player = determine_trick_winner(self.cards_played_trick, self.trump)
            self.last_player = self.current_player.previous_player
            self.current_player.tricks_won += 1

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


        #score hand and reset tricks won
        for player in self.player_list:
            for observation in self.play_data:
                if observation["player"] == player.name and player.bid == player.tricks_won and observation['hand_number'] == self.hand_number + 1:
                    observation["hand_result"] = 1             

            if player.bid == player.tricks_won:
                #update player hand score if player made bid
                player.hand_score = 5 + player.tricks_won
                #for each row in play_data list, update result if player made their bid

            else:
                player.hand_score = 0
            self.scores[player.name] = player.hand_score
            player.running_score += player.hand_score
            self.tricks_won[player.name] = player.tricks_won
            self.bids[player.name] = player.bid
            player.tricks_won = 0
        
        #store results
        self.results[str(hand_number)+updown] = {'cards_played':self.cards_played_hand, 'hand_scores':self.scores,
                                            'tricks_won':self.tricks_won, 'bids':self.bids}
        self.cards_played_hand = {}
        self.scores = {}
        self.tricks_won = {}
        self.bids = {}

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
        self.running_score = 0

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
    
    def get_hand(self):
        return [card.id for card in self.hand]

class Simulator:
    def play_game(self, player_names):
        self.game = Game(player_names)
        for i in range(10, 0, -1):
            self.game.play_hand(i, "down")
        
        for i in range(2,11,1):
            self.game.play_hand(i, "up")

        for player in self.game.player_list:
            print(f'{player.name}: {player.running_score}')
    def export_hands_played(self):
        return self.game.results
    
    def export_cards_played(self):
        return self.game.play_data

sim = Simulator()
sim.play_game(["Jack","Kelly","Tim","Mom","Dad"])

df = pd.DataFrame([sim.export_hands_played()])

df = pd.DataFrame(sim.export_cards_played())

save_path = r'output.csv'
df.to_csv(save_path)
# gamedata = []

# for i in range(10):
#     sim = Simulator()
#     sim.play_game([player1,player2,player3,player4,player5])
#     df = pd.DataFrame(sim.export_results())
#     gamedata.append(df)

# df = pd.concat(gamedata)

# print(df.head())