import asyncio
import aiohttp
import time
import sys
try:
    from aiohttp import ClientError
except:
    from aiohttp import ClientProxyConnectionError as ProxyConnectionError
from Getter_to_redis import RedisClient
from setting import *

class Tester(object):
    def __init__(self):
        self.redis=RedisClient()

    async def test_single_proxy(self,proxy):
        """
        测试单个代理
        :param proxy:
        :return:
        """
        conn=aiohttp.TCPConnector(verify_ssl=False)#防止ssl报错
        async with aiohttp.ClientSession(connector=conn)as session:#创建session
            try:
                if isinstance(proxy,bytes):#判断对象是否是一个已知的类型（字节类型)
                    proxy=proxy.decode('utf-8')
                real_proxy='http://'+proxy
                print('正在测试',proxy)
                async with session.get(TEST_URL,proxy=real_proxy,timeout=15,allow_redirects=False)as response:
                    if response.status in VALID_STATUS_CODES:
                        self.redis.max(proxy)
                        print('代理可用',proxy)
                    else:
                        self.redis.decrease(proxy)
                        print('请求响应码不合法',response.status,'IP',proxy)
            except(ClientError,aiohttp.client_exceptions.ClientConnectorError,asyncio.TimeoutError,AttributeError):
                self.redis.decrease(proxy)
                print('代理请求失败',proxy)

    def run(self):
        """
        测试的主函数
        :return:
        """
        print('测试器开始执行')
        try:
            count=self.redis.count()
            print('当前剩余',count,'个代理')
            for i in range(0,count,BATCH_TEST_SIZE):#第三个参数表示一次批量处理的数量
                start=i
                stop=min(i+BATCH_TEST_SIZE,count)#返回最小的值，当i+BATCH_TEST_SIZE>count时，始终count
                print('正在测试等',start+1,'-',stop,'个代理')
                test_proxies=self.redis.batch(start,stop)#redis的批量读取
                loop=asyncio.get_event_loop()#创建事件循环
                tasks=[self.test_single_proxy(proxy) for proxy in test_proxies]#调用单个测试函数进行测试
                loop.run_until_complete(asyncio.wait(tasks))#等待任务结束
                sys.stdout.flush()
                time.sleep(5)
        except Exception as e:
            print('测试器发生错误',e.args)