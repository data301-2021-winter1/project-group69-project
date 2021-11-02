import pandas as pd
import matplotlib.pyplot as plt

decklists = pd.read_json("https://us-central1-tumbledmtg-website.cloudfunctions.net/api/decklists")

def get_star_count(cards):
    values = []
    decks = decklists.loc[lambda decklist: decklist['stars'] > 0]
    names = cards["name"]
    for name in names:
        score = 0
        for index,decklist in decks.iterrows():
            for line in decklist['body'].split("\n"):
                words = line.split(' ')
                if words[0].isnumeric():
                    if " ".join(words[1:]) == name:
                        score += int(words[0])*int(decklist['stars'])
                elif words[0] == "SB:":
                    if " ".join(words[2:]) == name:
                        score += int(words[1])*int(decklist['stars'])
        values.append(score)
    return pd.Series(values)

def get_board_ratio(cards):
    values = []
    names = cards["name"]
    for name in names:
        maindeckcount = 0
        sideboardcount = 0
        for index,decklist in decklists.iterrows():
            for line in decklist['body'].split("\n"):
                words = line.split(' ')
                if words[0].isnumeric():
                    if " ".join(words[1:]) == name:
                        maindeckcount += int(words[0])
                elif words[0] == "SB:":
                     if " ".join(words[2:]) == name:
                            sideboardcount += int(words[1])
        board_ratio = 0
        if (maindeckcount + sideboardcount) == 0:
            board_ratio = float("NaN")
        else:
            board_ratio = maindeckcount / (maindeckcount + sideboardcount)
        values.append(board_ratio)
    return pd.Series(values)
                
def clean_cards():
    return (
        pd.read_json("https://us-central1-tumbledmtg-website.cloudfunctions.net/api/cards")
            .assign(star_score=get_star_count)
            .assign(board_ratio=get_board_ratio)
            .loc[lambda card: ~card['type'].str.contains('Basic')]
            .drop(columns=['pt', 'set', 'tablerow', 'text', 'tags', 'related', 'layout', 'side', 'manacost'], axis=1)
            .sort_values("star_score", ascending=True)
            )