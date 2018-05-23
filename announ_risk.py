import re
import csv
from database import  Database
import datetime


class ConnRisk():
    def __init__(self):
        print()

    csv_contents = csv.reader(open('announ_content.csv', 'r'))
    csv_risk = csv.reader(open('announ_risk_keywords.csv', 'r'))


    def get_json(self, csv_contents):
        contents = []
        for row in csv_contents:
            content = {}
            content['id'] = int(row[1])
            content['content'] = row[6].strip('\t\n')
            contents.append(content)
        print('公告数量：', len(contents))
        return contents

    def get_riskdict(self, csv_risk):
        risk_dict = {}
        for row in csv_risk:
            risk_dict[row[0]] = row[1:]
        #print(risk_dict)       #{'业绩风险': ['净利润,增长|增加', '交易细节未披露|未披露'], '违法违规': ['同比增长|同比下降', '交易细节未披露']}
        print('风险类型数量为：', len(risk_dict), '风险类型为：', risk_dict.keys())    #风险类型数量为： 2 风险类型为： dict_keys(['业绩风险', '违法违规'])
        return risk_dict



    def get_risklabel(self, contents, risk_dict):  #传入数据(目前为批量，后来要修改为单个)
        double_id = []
        texts = []
        for i in range(len(contents)):
        #for i in range(1000):
            text = contents[i]   #取出第i篇新闻；是一个字典，存储的有id，content, stoc_id, counts
            content = text['content']
            for key, value in risk_dict.items():#遍历风险类型
                flag = False
                right_labels = str(value[0]).split(';')   #元素是等价的    ['承诺,未|超期|延期|豁免', '致歉|道歉']
                del_labels = str(value[1]).split(',')     #['交易细节未披露|未披露', '世纪天鸿']
                #print('保留的正则：', right_labels, '删除的正则：', del_labels)

                #right_labels中元素是等同的，只有有一个满足即可
                for i in range(len(right_labels)):
                    right_label = str(right_labels[i]).split(',')  #将要同时含有几个关键字的那些关键字分割开
                    count = 0  #看最终是否能同时匹配上那几个关键字
                    for j in range(len(right_label)):
                        right_pattern = re.compile('%s' % (right_label[j]))
                        if right_pattern.search(content):
                            count += 1
                    if count == len(right_label):  #只要right_labels中有一个元素满足，就可以中止循环了
                        flag = True
                        break

                if flag:
                    #并行的几个删除的正则表达式，一旦有一个匹配不上，则继续往下进行
                    for k in range(len(del_labels)):
                        #print(del_labels[k])
                        if not del_labels[k]:
                            flag = False
                        else:
                            del_pattern = re.compile('%s' % (del_labels[k]))
                            if not del_pattern.search(content):
                                flag = False
                    if not flag:
                        for item in texts:  ##若此新闻之前已匹配上其他风险，则将risk添加一个元素
                            if item['id'] == text['id'] and text['id'] != None:
                                item['risk'].extend([key])
                                if item['id'] not in double_id:
                                    double_id.append(item['id'])
                                flag = True
                        if not flag:
                            jre = {}
                            jre['id'] = text['id']
                            jre['risk'] = [key]
                            jre['content'] = content
                            texts.append(jre)
                            #print(type(key))
        print("匹配多个风险标签的新闻数量为:", len(double_id), "具体id为:", double_id)
        return texts

    def run(self, contents):

        db = Database()
        db.connect('announce_connect_keywords')

        for i in range(len(contents)):
            data = contents[i]
            sql_insert = 'INSERT INTO announce_conn_risk(id, content) VALUES (%s, %s)'
            db.execute(sql_insert, [data['id'], data['content']])
        db.close()


    # def run(self, texts):
    #
    #     db = Database()
    #     db.connect('announce_connect_keywords')
    #
    #     for i in range(len(texts)):
    #         data = texts[i]
    #         #sql_update = """update announce_conn_risk set risk = "%s" where id = %d""" %(str(data['risk']), int(data['id']))
    #         #sql_update = """update announce_conn_risk set risk = "%s" where id = '1204822535'""" % (str(data['risk']))
    #         #db.execute(sql_update)
    #
    #     db.close()


if __name__ == '__main__':
    CR = ConnRisk()
    contents = CR.get_json(CR.csv_contents)
    # print(contents)
    # risk_dict = CR.get_riskdict(CR.csv_risk)
    # texts = CR.get_risklabel(contents, risk_dict)
    # print("匹配上风险的公告数量为:", len(texts))
    # print("具体情况为:", texts)
    CR.run(contents)

