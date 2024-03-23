# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CarsItem(scrapy.Item):

    car_price = scrapy.Field()
    url = scrapy.Field()
    motorizacao = scrapy.Field()
    carroceria = scrapy.Field()
    km_andado = scrapy.Field()
    combustivel = scrapy.Field()
    cambio = scrapy.Field()
    cor = scrapy.Field()
    ano = scrapy.Field()
    marca_carro = scrapy.Field()
    nome_carro = scrapy.Field()
    altura = scrapy.Field()
    largura = scrapy.Field()
    comprimento = scrapy.Field()
    peso = scrapy.Field()
    tanque = scrapy.Field()
    entre_eixos = scrapy.Field()
    porta_malas = scrapy.Field()
    ocupantes = scrapy.Field()
    direcao = scrapy.Field()