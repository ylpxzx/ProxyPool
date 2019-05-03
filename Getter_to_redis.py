from storage_redis import RedisClient
from get_module import Crawler
POOL_UPPER_THRESHOLD=10000
import sys

class Getter():
    def __init__(self):
        self.redis=RedisClient()
        self.crawler=Crawler()

    def is_over_threshold(self):
        """
        判断是否达到了代理池限制
        :return:
        """
        if self.redis.count()>=POOL_UPPER_THRESHOLD:
            return True
        else:
            return False
    def run(self):
        print('获取器开始执行')
        if not self.is_over_threshold():
            for callback_label in range(self.crawler.__CrawlFuncCount__):
                callback=self.crawler.__CrawlFunc__[callback_label]
                proxies=self.crawler.get_proxies(callback)
                sys.stdout.flush()#在Linux系统下，必须加入sys.stdout.flush()才能一秒输一个数字;在Windows系统下，加不加sys.stdout.flush()都能一秒输出一个数字
                for proxy in proxies:
                    self.redis.add(proxy)