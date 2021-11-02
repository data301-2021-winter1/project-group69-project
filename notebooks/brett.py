import pandas as pd
import matplotlib.pyplot as plt

decklists = pd.read_json("https://us-central1-tumbledmtg-website.cloudfunctions.net/api/decklists")

"""
def get_mana_value(decklists):
    values = []
    bodies = decklists['cards']
    for body in bodies:
        count = 0
        mv = 0
        for line in body.split("\n"):
            if len(line) < 5:
                continue
            card = cards[cards['name'] == line.split(";")[1]]
            if card['cmc'].size > 0 and "Land" not in str(card['type']):
                mv += (int(card['cmc'].iloc[0]) * int(line.split(';')[0]))
                count += int(line.split(';')[0])
        values.append(mv/count)
    return pd.Series(values)
    """

"""
cards = (   
    pd.DataFrame(data.data,columns=data.feature_names)
    .rename(columns={"color_intensity": "ci"})
    .assign(color_filter=lambda x: np.where((x.hue > 1) & (x.ci > 7), 1, 0))
    .loc[lambda x: x['alcohol']>14]
    .sort_values("alcohol", ascending=False)
    .reset_index(drop=True)
    .loc[:, ["alcohol", "ci", "hue"]]
)
"""

def get_star_count(cards):
    values = []
    something = decklists.loc[lambda decklist: decklist['stars'] > 0]
    names = cards["name"]
    for name in names:
        score = 0
        for index,decklist in something.iterrows():
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
            #board_ratio = "{:.2%}".format(board_ratio)
        values.append(board_ratio)
    return pd.Series(values)
                
def clean_cards(cards):
    return (
        cards
            .assign(star_score=get_star_count)
            .assign(board_ratio=get_board_ratio)
            .loc[lambda card: ~card['type'].str.contains('Basic')]
            .drop(columns=['pt', 'set', 'tablerow', 'text', 'tags', 'related', 'layout', 'side', 'manacost'], axis=1)
            .sort_values("star_score", ascending=True)
            )