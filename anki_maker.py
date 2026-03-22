import genanki
import random


def anki_maker(pairs, deck_name, output_filename):

    MODEL = genanki.Model(
        random.randrange(1 << 30, 1 << 31),
        'QA Model',
        fields=[
            {'name': 'Question'},
            {'name': 'Answer'},
        ],
        templates=[{
            'name': 'Card',
            'qfmt': '{{Question}}',
            'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
        }]
    )

    deck = genanki.Deck(random.randrange(1 << 30, 1 << 31), 'DECK NAME')

     
    for pair in pairs:
        note = genanki.Note(
            model=MODEL,
            fields=[pair["front"], pair["back"]]
        )
        deck.add_note(note)
    
    genanki.Package(deck).write_to_file(output_filename + '.apkg')