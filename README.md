# Tietokantasovellus

Harjoitustyön aiheena on sovellus, jonka avulla on mahdollista hoitaa verkkokauppaa harjoittavan yrityksen tilausten käsittely, laskutus sekä varastosaldojen ylläpito. Jokainen sovelluksen käyttäjä on joko työntekijä tai asiakas.

Sovellus on laadittu Helsingin yliopiston kevään 2022 kurssille [Aineopintojen harjoitustyö: Tietokantasovellus](https://hy-tsoha.github.io/materiaali/).

## Heroku

Sovellusta voi käyttää [Herokussa](https://vast-coast-44980.herokuapp.com/). Kirjautumiseen voi käyttää seuraavia tunnuksia:

|    Rooli    | Käyttäjätunnus |  Salasana  |
| :---------- | :------------- | :--------- |
| asiakas     | `customer`     | `qXd9Y8ok` |
| työntekijä  | `admin`        | `op33RfQ4` |

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