# Het Nomino Project

![homepage](/static/uploads/homepage.png)

## David Verboom - Het nomino project

Mijn vader is al jaren bezig met het oplossen van zijn probleem. Hij probeert zijn producten al langere tijd op Etsy te verkopen, maar zijn account verdwijnt tussen de menigte en tevergeefs heeft hij nog geen producten kunnen verkopen. Hij wilde heel graag dat ik een basis kon maken voor een gepersonaliseerde site. De basis is inmiddels gemaakt en nu kunnen wij samen kijken naar een gepersonaliseerd platform waarop hij zijn producten kan verkopen.

### Instructies

1. Installeer de volgende applicaties:

pip install -r requirements.txt

2. Zet een database op in Postgres door de volgende commando’s uit te voeren:

psql -U postgres:
- CREATE DATABASE mydatabase;
- \q
- export DATABASE_URL="postgresql://davidverboom:123456789@localhost/mydatabase"
- python3 create.py

3. API-key van Stripe koppelen:

![Stripe Afbeelding](/static/uploads/stripe.png)

export STRIPE_PUBLISHABLE_KEY="de publishable key"
export STRIPE_SECRET_KEY="de secret key"

4. Run de `app.py`:

flask run

De code in de map `main.js` in `static` is direct overgenomen van Michael Herman op de site [testdriven.io](https://testdriven.io/blog/flask-stripe-tutorial/).

![product Afbeelding](/static/uploads/product.png)

Alle afbeeldingen zijn afkomstig van het account NominoNL op Etsy.com:
[https://www.etsy.com/nl/shop/NominoNL?ref=shop-header-name&listing_id=883457845&from_page=listing](https://www.etsy.com/nl/shop/NominoNL?ref=shop-header-name&listing_id=883457845&from_page=listing)

De visuele weergave van de webshop is te zien met de volgende link:
[https://youtu.be/CnYrKM8i3AE](https://youtu.be/CnYrKM8i3AE)



