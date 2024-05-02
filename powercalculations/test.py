"""
def examine(lijst, partiele_oplossing):
    if sorted(lijst) == sorted(partiele_oplossing):
        return ACCEPT
    # Als er een getal tweemaal voorkomt in de partiële oplossing,
    # dan leidt deze niet meer tot een oplossing.
    if len(partiele_oplossing) > len(set(partiele_oplossing)): # een set bevat ieder element één keer.
        return ABANDON
    return CONTINUE


# Het uitbreiden van partiele_oplossing met de elementen uit de gegeven lijst.
def extend(lijst, partiele_oplossing):
    partial_solutions = []
    for n in lijst:
        partial_solutions.append(partiele_oplossing + [n])
    return partial_solutions


def solve(lijst, partiele_oplossing=None):
    if partiele_oplossing is None:
        partiele_oplossing = [] #Deze ietwat rare constructie gebruiken we om defaultwaarden voor lijsten, sets en
                                # dicts te kunnen maken. De reden hiervoor is dat je je defaultwaarde niet tijdens
                                # runtime wilt kunnen aanpassen. Voor meer uitleg kan je kijken naar het addendum
                                # onderaan.
    exam = examine(lijst, partiele_oplossing)
    # Als De oplossing volledig is en nog steeds klopt, kan dit teruggegeven worden.
    if exam == ACCEPT:
        return [partiele_oplossing]
    # Als de oplossing nog niet volledig is, maar wel kan:
    elif exam != ABANDON:
        oplossing = []
        for part in extend(lijst, partiele_oplossing):
            # Elke uitgebreide partiele oplossing wordt ook apart opgelost om te checken of deze gebruikt kan worden.
            rec_opl = solve(lijst, part)
            if rec_opl is not None:
                for o in rec_opl:
                    oplossing.append(o)
        return oplossing
    # Aangezien niets wordt teruggegeven aan de functie, wordt None automatisch teruggegeven.
"""

string="hallo"
for i in string:
    print(i)