# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import re
from itemadapter import ItemAdapter


class CarsScrapePipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Remove some weird keys from car_price
        val_price = adapter.get('car_price')
        adapter['car_price'] = float(re.search(r'\d+\.?\d*', val_price).group(0).replace('.', ''))

        return item
