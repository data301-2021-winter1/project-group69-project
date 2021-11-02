import pandas as pd

cards = pd.read_json("https://us-central1-tumbledmtg-website.cloudfunctions.net/api/cards")

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


def get_type(decklists, card_type):
    lands = [] 
    bodies = decklists['cards']
    for body in bodies:
        count = 0
        lines = body.split("\n")
        for line in lines:
            if len(line) < 5:
                continue
            card = cards[cards['name'] == line.split(";")[1]]
            if card_type in str(card['type']):
                count += int(line.split(';')[0])
        lands.append(count)
    return pd.Series(lands)


def get_cards(decklists):
    series = [] 
    bodies = decklists['body']
    for body in bodies:
        newbody = ""
        lines = body.split("\n")
        for line in lines:
            if line[0:2] != "//" and len(line.split(' ')) > 1:
                i = 0
                if line[0:2] == "SB":
                    i = 1
                words = line.split(" ")
                newbody += (words[i] + ";" + " ".join(words[i+1:]) + "\n")
        series.append(newbody)
    return pd.Series(series) 
    

def get_color(x, num):
    colors = []
    for i in range(x['colors'].size):
        colors.append(x['colors'].iloc[i][num])
    return pd.Series(colors)


def clean_decklists():
    return (
        pd.read_json("https://us-central1-tumbledmtg-website.cloudfunctions.net/api/decklists")
            .assign(cards=get_cards)
            .assign(lands=lambda x: get_type(x,"Land"))
            .assign(sorcery=lambda x: get_type(x,"Sorcery"))
            .assign(enchant=lambda x: get_type(x,"Enchantment"))
            .assign(creature=lambda x: get_type(x,"Creature"))
            .assign(mv=get_mana_value)
            .assign(white=lambda x: get_color(x,0))
            .assign(blue=lambda x: get_color(x,1))
            .assign(black=lambda x: get_color(x,2))
            .assign(red=lambda x: get_color(x,3))
            .assign(green=lambda x: get_color(x,4))
            .loc[lambda x: x['duplex'] != True]
            .drop(columns=['duplex','decklistId','author','uploadId','title','createdAt','description','body','colors'], axis=1)
            .sort_values('stars', ascending=False)
        )

