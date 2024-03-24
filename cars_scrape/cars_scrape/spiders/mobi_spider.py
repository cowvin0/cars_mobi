import scrapy
import re
import time
from scrapy.http import Request
from ..items import CarsItem


class CarsSpider(scrapy.Spider):
    name = "mobi"
    allowed_domains = ["mobiauto.com.br"]

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.closed()

    def __init__(self, *args, **kwargs):
        super(CarsSpider, self).__init__(*args, **kwargs)
        self.start_urls = ["https://www.mobiauto.com.br/comprar/carros/al-maceio"]

    def start_requests(self):
        for page in range(1, 53):
            yield Request(
                url=self.start_urls[0] + f'/pagina-{page}',
                meta=dict(
                    dont_redirect=True,
                    handle_httpstatus_list=[302, 308]
                ),
                callback=self.parse_page
            )

    async def parse_page(self, response):

        possible_classes = [
            response.xpath('//a[@class="mui-style-xsroma"]/@href').getall(),
            response.xpath('//a[@class="css-xsroma"]/@href').getall()
            ]

        possible_classes = [diff_zero for diff_zero in possible_classes if len(diff_zero) != 0]

        for url in possible_classes[0]:

            yield Request(
                url="https://www.mobiauto.com.br" + url,
                meta=dict(
                    dont_redirect=True,
                    handle_httpstatus_list=[302, 308],
                    playwright=True,
                    playwright_include_page=True,
                    errback=self.errback
                ),
                callback=self.parse_auto_items
            )

    async def parse_auto_items(self, response):
        page = response.meta['playwright_page']
        car_item = CarsItem()

        await page.evaluate(r'''
                            var elements = document.querySelectorAll('.MuiAccordionSummary-content.MuiAccordionSummary-contentGutters.css-17o5nyn, .MuiAccordionSummary-content.MuiAccordionSummary-contentGutters.mui-style-17o5nyn');
                            Array.from(elements).forEach(element => element.click());
                            ''')

        await page.wait_for_timeout(5000)

        car_details = await page.evaluate('''() => {
            var names = document.querySelectorAll(".MuiAccordionSummary-content.Mui-expanded.MuiAccordionSummary-contentGutters.css-17o5nyn");
            var details = document.querySelectorAll(".MuiCollapse-wrapperInner.MuiCollapse-vertical.mui-style-8atqhb");
            names = Array.from(names).map(a => a.textContent);
            details = Array.from(details).map(a => a.textContent);

            var keywordDict = {};
            names.forEach((key, index) => {
                keywordDict[key] = details[index];
            })

            return keywordDict;
        }''')

        all_previous_info = response.xpath('//div[@class="mui-style-1n2g6aq"]//text()').getall()
        car_price = response.xpath('//p[@class="mui-style-h31tor"]/text()').get()
        marca_carro = response.xpath('//h1[@class="mui-style-4ato1b"]//text()').getall()

        await page.close()

        mecanica = car_details['Mecânica']
        dimensao = car_details['Dimensões']
        all_previous_info = {all_previous_info[i]: all_previous_info[i + 1] for i in range(len(all_previous_info) - 1)}
        url = response.url
        carroceria = all_previous_info['Carroceria'] if 'Carroceria' in all_previous_info else None
        km_andado = all_previous_info['KM'] if 'KM' in all_previous_info else None
        combustivel = all_previous_info['Combustível'] if 'Combustível' in all_previous_info else None
        cambio = all_previous_info['Câmbio'] if 'Câmbio' in all_previous_info else None
        cor = all_previous_info['Cor'] if 'Cor' in all_previous_info else None
        ano = all_previous_info['Ano'] if 'Ano' in all_previous_info else None
        nome_carro = ''.join(marca_carro)

        dict_list = {
            'velocidade_maxima': re.search(r'Velocidade máxima \(km/h\).+?/ (\d+) \(G\)', mecanica),
            'consumo': re.search(r'Consumo cidade \(km\/l\)(?:N\/C|\d+\.\d+) \(E\) \/ (\d+\.\d+) \(G\)', mecanica),
            'direcao': re.search(r'Direção([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+)', mecanica),
            'motorizacao': re.search(r'Motorização([\d.]+)', mecanica),
            'altura': re.search(r'Altura \(mm\)(\d+)', dimensao),
            'largura': re.search(r'Largura \(mm\)(\d+)', dimensao),
            'comprimento': re.search(r'Comprimento \(mm\)(\d+)', dimensao),
            'peso': re.search(r'Peso \(kg\)(\d+)', dimensao),
            'tanque': re.search(r'Tanque \(L\)(\d+)', dimensao),
            'entre_eixos': re.search(r'Entre-eixos \(mm\)(\d+)', dimensao),
            'porta_malas': re.search(r'Porta-Malas \(L\)(\d+)', dimensao),
            "ocupantes": re.search(r'Ocupantes(\d+)', dimensao),
        }

        for var_name, value in dict_list.items():
            if value:
                item = value.group(1)
                try:
                    car_item[var_name] = float(item)
                except:
                    car_item[var_name] = item
            else:
                car_item[var_name] = value

        car_item['car_price'] = car_price
        car_item['url'] = url
        car_item['carroceria'] = carroceria
        car_item['km_andado'] = float(km_andado) if km_andado else km_andado
        car_item['combustivel'] = combustivel
        car_item['cambio'] = cambio
        car_item['cor'] = cor
        car_item['ano'] = ano
        car_item['marca_carro'] = marca_carro[0]
        car_item['nome_carro'] = nome_carro

        yield car_item
