# Tietokantasovellus

Harjoitustyön aiheena on sovellus, jonka avulla on mahdollista hoitaa verkkokauppaa harjoittavan yrityksen tilausten käsittely, laskutus sekä varastosaldojen ylläpito. Jokainen sovelluksen käyttäjä on joko työntekijä tai asiakas.

Sovellus on laadittu Helsingin yliopiston kevään 2022 kurssille [Aineopintojen harjoitustyö: Tietokantasovellus](https://hy-tsoha.github.io/materiaali/).

## Ominaisuudet

### Toimivat

* Kaikki käyttäjät voivat kirjautua sisään ja ulos.
* Asiakkaat voivat luoda itselleen uuden tunnuksen. 
* Asiakkaat voivat tarkastella tuotteiden tietoja.
* Työntekijät voivat lisätä uusia tuotteita ja muokata olemassaolevien tuotteiden tietoja (esim. tuotekuvaukset, hinnat, varastosaldot).
* Asiakkaat voivat tarkastella ja päivittää omia yhteystietojaan, ja työntekijät voivat päivittää asiakkaiden yhteystietoja.
* Asiakkaat voivat lisätä tuotteita ostoskoriin ja tehdä ostoskoriin lisätyistä tuotteista uuden tilauksen.
* Työntekijät voivat selailla ja käsitellä tilauksia.
* Asiakkaat voivat selailla aiempia tilauksiaan.
* Järjestelmä huolehtii automaattisesti siitä, että tuotteiden varastosaldot ovat ajan tasalla sekä siitä, että tuotteita ei voi tilata enempää kuin niitä on varastossa.
* Työntekijät voivat lisätä työntekijän oikeuksia muille käyttäjille.

### Jatkokehitysideoita

* Toteutuneiden myyntien tarkastelu esimerkiksi tuotteen, ajankohdan tai asiakkaan mukaan
* Laskujen ja maksumuistutusten lähettäminen

## Työn edistyminen

### Välipalautus 2

Tässä vaiheessa olen priorisoinut sovelluksen perustoiminnallisuuksia. Esimerkiksi sovelluksen ulkoasu on askeettinen, koska sivuja ei vielä ole muotoiltu CSS:llä. Lisäksi koodia jaetaan useampaan tiedostoon myöhemmissä vaiheissa.

### Välipalautus 3

Toimintoja on nyt laajennettu, ja suurin osa toiminnallisuuksista on nyt toteutettu. Tietokantataulujen määrä on kasvanut kahdesta kuuteen. Koodia on myös selkiytetty jakamalla sitä useampaan tiedostoon. Ennen lopullista palautusta sovellukseen lisätään vielä loputkin ominaisuudet. Myös sovelluksen ulkoasua parannetaan.

### Lopullinen palautus

Loputkin toiminnallisuudet on lisätty sovellukseen. Tietoturvaa on parannettu lisäämällä käyttäjäoikeuksien tarkistuksia ja estämällä CSRF-haavoittuvuuden hyödyntäminen. Myös ulkoasua on parannettu CSS:n avulla.

## Asentaminen omalle tietokoneelle

### Vaaditut ohjelmistot

* [Python](https://www.python.org/downloads/) (versio 3.8.10 tai uudempi)
* [pip-paketinhallintajärjestelmä](https://pip.pypa.io/en/stable/)
* Pythonin standardikirjastoon kuuluva [venv-kirjasto](https://docs.python.org/3/library/venv.html)
* [Git](https://git-scm.com/downloads/)-versionhallintajärjestelmä
* [PostgreSQL](https://www.postgresql.org/download/)-tietokannan hallintajärjestelmä

### Asennus ja ajaminen paikallisesti

Aloita lataamalla sovelluksen lähdekoodi [zip-tiedostona](https://github.com/valtterikantanen/tsoha/archive/refs/heads/master.zip) tai kloonaa projekti komennolla

```bash
$ git clone https://github.com/valtterikantanen/tsoha.git
```
Luo virtuaaliympäristö ja aktivoi se komennoilla
```bash
$ python3 -m venv venv
$ source venv/bin/activate
```
Asenna sovelluksen riippuvuudet komennolla
```bash
(venv) $ pip install -r requirements.txt
```
Luo tarvittavat tietokantataulut komennolla
```bash
$ psql < schema.sql
```
Palvelimen voi käynnistää komennolla
```bash
(venv) $ flask run
```
Nyt palvelin on käynnissä ja sovellusta voi käyttää osoitteessa `http://127.0.0.1:5000/`.

### Muuta

* Ohjelma olettaa, että tiedostossa `.env` on määritelty tietokannan osoite muuttujassa `DATABASE_URL` sekä salainen avain muuttujassa `SECRET_KEY`.
* Halutessaan tietokantaan voi syöttää myös esimerkkidataa komennolla `psql < example.sql`, mikä poistaa nykyiset taulut ja luo tilalle uudet. Tällöin luodaan myös kaksi käyttäjää, joiden käyttäjätunnukset ja salasanat ovat seuraavat:

|    Rooli    | Käyttäjätunnus |  Salasana  |
| :---------- | :------------- | :--------- |
| asiakas     | `customer`     | `qXd9Y8ok` |
| työntekijä  | `admin`        | `op33RfQ4` |
