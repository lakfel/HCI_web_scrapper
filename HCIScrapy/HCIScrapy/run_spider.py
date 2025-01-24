from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from HCIScrapy.spiders.SDIssuesSpiderSelenium import SdissuesspiderSpider
import time

def run_spider_multiple_times(spider_class, times=5, delay_between_runs=5):
	"""
	Run a spider multiple times with a delay between runs
	
	Args:
		spider_class: The spider class to run
		times: Number of times to run the spider
		delay_between_runs: Delay in seconds between runs
	"""
	process = CrawlerProcess(get_project_settings())
	
	for i in range(times):
		print(f"Starting spider run {i + 1} of {times}")
		process.crawl(spider_class)
		if i < times - 1:  # Don't sleep after the last run
			time.sleep(delay_between_runs)
	
	process.start()

if __name__ == "__main__":  
	run_spider_multiple_times(SdissuesspiderSpider)