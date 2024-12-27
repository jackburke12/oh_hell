


def partition(lst, start, num_elements):
    return lst[start:num_elements]

def determine_bid(hand, trump_card, is_dealer):
    bid = 0
    if trump_card.suit != 'no_trump':
        for card in hand:
            if card.suit == trump_card.suit:
                bid += 1
    else: 
        for card in hand:
            if card.value >= 10:
                bid += 1
    return bid

def find_high_bidder(current_player):
    high_bid = 0
    high_bidder = None
    starting_player = current_player
    while current_player.next_player != starting_player:
        if current_player.bid > high_bid:
            high_bid = current_player.bid
            high_bidder = current_player
        next_player = current_player.next_player
        current_player = next_player
    if current_player.bid > high_bid:
        high_bidder = current_player
    return high_bidder

def determine_card_to_play(current_player, cards_and_players):
    #currently unused, but should be useful when improving this logic. Player may wish to play a lower card than what was led if 
    # remaining tricks to take == 0, or if the number of high cards in their hand is greater than their remaining tricks to take
    remaining_tricks_to_take = current_player.bid - current_player.tricks_won
    #handle case where player is leading. Should add logic telling players what to lead. Right now, a random card is led
    if len(cards_and_players) == 0:
        return current_player.hand.pop()
    #check if player has the leading suit in their hand. If they do, return the first card whose suit matches the leading suit.
    #Need to add logic so that player chooses the best card of the leading suit, not just the first one that appears
    else:
        suit_led = cards_and_players[0][1].suit
        card = check_if_suit_in_hand(current_player, suit_led)
        if card:
            return card
        else:
            return current_player.hand.pop()

def determine_trick_winner(cards_played, trump_card):
    high_card = cards_played[0][1]
    High_card_player = cards_played[0][0]

    for player, card in cards_played:
        if card.suit == trump_card.suit:
            if high_card.suit == trump_card.suit:
                if high_card.compare(card) < 0:
                    high_card = card
                    High_card_player = player
            else:
                high_card = card
                High_card_player = player
        else:
            if high_card.suit == card.suit:
                if high_card.compare(card) < 0:
                    high_card = card
                    High_card_player = player
    return High_card_player

def check_if_suit_in_hand(player, suit_led):
    for card in player.hand:
        if card.suit == suit_led:
            card1 = card
            player.hand.remove(card)
            return card1
    return None

def unzip_card_played(player_and_card_tuple):
    return (player_and_card_tuple[0].name,player_and_card_tuple[1].id)

def unzip_cards_played_trick(cards_played_trick):
    cards_played_trick_unzipped = []
    for card_played in cards_played_trick:
        cards_played_trick_unzipped.append(unzip_card_played(card_played))
    return cards_played_trick_unzipped