# Review

Voor het schoonmaken van mijn code ben ik aan de slag gegaan door als eerst te kijken wat mij opviel, daar notities van te maken en te kijken hoe ik dat kon verbeteren. De code zelf had niet zo zeer onderdelen waar het te onduidelijk was of te langdradig. Er zaten niet oneindig veel onnodige functies in, maar het was wel veel duidelijker te maken door gebruik te maken van verschillende opties.

## De volgorde van de app features

Als eerste heb ik gekeken naar de volgorde. Alles stond nu op volgorde van wanneer ik elke feature toe had gevoegd. Dat leek mij echter heel erg onduidelijk dus heb ik ervoor gekozen om dit op te delen in “chronologische” volgorde van hoe de gebruiker de functies gaat gebruiken. Als eerst start je met een login, gevolgd met de producten bekijken, waarna er wordt afgerekend. In die hoedanigheid is nu de volgorde volledig aangepast zodat iemand anders de code beter kan begrijpen.

## Kopjes en Comments

Ik heb om die volgorde nog duidelijker te maken elk “onderwerp” een eigen kopje gegeven zodat iemand sneller de feature kan vinden die hij nodig heeft. Daarnaast heb ik comments gewijzigd, weggehaald en toegevoegd. Niet alleen in de `app.py` maar ook in alle HTML's.

## Forms.py

Ik heb een grote aanpassing gedaan in mijn register-feature. Ik heb gebruikgemaakt van een externe map genaamd `forms.py` om de grotere formulieren beter te monitoren zodat hij minder gevoelig zou zijn voor fouten. Register had ik niet zo verwerkt en ik vond dit toch zonde, dus heb besloten deze meer te laten corresponderen met de andere formulieren. Ook de HTML heb ik aangepast zodat deze beter functioneert als een echte website en correspondeert met het nieuwe format. Het komt nu een stuk logischer over.

## Verwijderingen

Ik heb een aantal dingen geschrapt die horen bij features die de site niet hebben gehaald of uiteindelijk helemaal niet meer nodig waren. Voorbeelden waren HTML's die ik niet meer gebruikte, functies die geen nut meer hadden en bootstrap links die ik uiteindelijk niet heb gebruikt.

## Flake 8

Uiteindelijk heb ik Flake 8 gebruikt om een schone code op te leveren. Hier heb ik echter soms genegeerd dat een regel te lang was in verband met dat dat de code niet mooier zou maken indien dit gewijzigd zou worden.
