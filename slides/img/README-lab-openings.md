# Artwork for the lab-opening decks

Drop image files here under exactly these names and re-run
`python3 course/slides/build_lab_opening.py`. Each one is base64-embedded into
the deck, so the file never has to travel with it. Missing files are simply
skipped: the intro slide renders without artwork.

| File | Woman | What to look for |
|---|---|---|
| `perpetua-felicity-icon.png` ✅ | Perpetua (w08) and Felicity (w09) | Contemporary icon, the two of them embracing. |
| `syncletica-icon.png` ✅ | Amma Syncletica (w01) | Contemporary icon; the scroll reads "light the divine fire within yourself". |
| `theodora-icon.png` ✅ | Amma Theodora (w03) | Byzantine-manner icon with the boy she is said to have raised. |
| `sarah-icon.png` ✅ | Amma Sarah (w04) | **Must say "of the Desert" or "Venerable".** "Righteous Sarah" is Abraham's wife. |
| `macrina-icon.png` ✅ | Macrina the Younger (w12) | Icon of her holding an icon of her three brothers. |
| `marcella-engraving.png` ✅ | Marcella of Rome (w13) | Engraving of the sack of Rome scene, not a portrait. Beware Greek icons of Ἁγία Μαρκέλλα &mdash; that is Markella of Chios, a 14th-c. martyr. Ours is the elderly Roman widow, feast 31 January. |

## Two rules

1. **Nothing generated.** No AI-made faces. These are real people; an invented
   portrait projected in a classroom is a fabrication presented as a fact.
2. **Caption what it is.** Every image carries its date and place in the deck,
   and how long after her death it was made. A 6th-century mosaic of a woman
   who died in 203 is an act of devotion by people three centuries later, not a
   likeness, and students should be able to see that from the slide.

Set the caption text in `WOMEN[...]['credit']` in
`course/slides/build_lab_opening.py`.

## Licensing

Prefer Wikimedia Commons files marked public domain (the artworks are ancient;
what is in copyright is the modern *photograph* of them). The Ravenna mosaic
photo at christianiconography.info is CC BY-NC-SA, which is fine for classroom
use with attribution, but a public-domain Commons photograph is cleaner.
