# Tietokantasovellus

Harjoitustyön aiheena on sovellus, jonka avulla on mahdollista hoitaa verkkokauppaa harjoittavan yrityksen tilausten käsittely, laskutus sekä varastosaldojen ylläpito. Jokainen sovelluksen käyttäjä on joko työntekijä tai asiakas.

Sovellus on laadittu Helsingin yliopiston kevään 2022 kurssille [Aineopintojen harjoitustyö: Tietokantasovellus](https://hy-tsoha.github.io/materiaali/).

## Heroku

Sovellusta voi käyttää [Herokussa](https://vast-coast-44980.herokuapp.com/). Kirjautumiseen voi käyttää seuraavia tunnuksia:

|    Rooli   | Käyttäjätunnus |  Salasana  |
| :--------- | :------------- | :--------- |
| asiakas    | `customer`     | `qXd9Y8ok` |
| työntekijä | `admin`        | `op33RfQ4` |

## Ominaisuudet

### Toimivat

* Kaikki käyttäjät voivat kirjautua sisään ja ulos.
* Asiakkaat voivat luoda itselleen uuden tunnuksen. 
* Asiakkaat voivat tarkastella tuotteiden tietoja.
* Työntekijät voivat lisätä uusia tuotteita ja muokata olemassaolevien tuotteiden tietoja (esim. tuotekuvaukset, hinnat, varastosaldot).

### Vielä puuttuvat

* Asiakkaat voivat tehdä uusia tilauksia, joita työntekijät voivat selailla ja käsitellä.
* Asiakkaat voivat tarkastella ja päivittää omia yhteystietojaan.
* Asiakkaat voivat katsella aiempia tilauksiaan ja laskujaan.
* Työntekijät voivat lähettää uusia laskuja sekä tarkastella kaikkia lähetettyjä laskuja. Työntekijät pystyvät myös lähettämään maksumuistutuksia ja merkitsemään laskuja maksetuiksi.
* Työntekijät voivat tarkastella toteutuneita myyntejä esimerkiksi tuotteen, ajankohdan tai asiakkaan mukaan.
* Järjestelmä huolehtii automaattisesti siitä, että tuotteiden varastosaldot ovat ajan tasalla sekä siitä, että tuotteita ei voi tilata enempää kuin niitä on varastossa.
* Työntekijät voivat lisätä työntekijän oikeuksia muille käyttäjille.

## Työn edistyminen

### Välipalautus 2

Tässä vaiheessa olen priorisoinut sovelluksen perustoiminnallisuuksia. Esimerkiksi sovelluksen ulkoasu on askeettinen, koska sivuja ei vielä ole muotoiltu CSS:llä. Lisäksi koodia jaetaan useampaan tiedostoon myöhemmissä vaiheissa.