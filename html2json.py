#!/bin/env python
import json
import urllib2
import sys
import re
import time
headers = {'User-Agent':'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_2 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8H7 Safari/6533.18.5' };
class TCParser():
    def __init__(self):
        self.reset();

    def reset(self):
        self.prefix="http://m.baidu.com/l=3/tc?srd=1&nextpage=1&dict=30&tc_source=1&src=";
        self.pagelist = [];
        self.urllist = [];

    def dumpjson(self):
        html  = json.dumps(self.pagelist,ensure_ascii=False).encode('UTF-8');
        html = re.sub("<img[^>]*src=([^\s\"\\\]+)[^>]*>",lambda x:"<img class = 'pic' src="+urllib2.unquote(x.group(1))+">",html)
        html = re.sub("<span[^>]+>","<span>",html)
        print html 
        return;

    def json2file(self):
        if (len(self.pagelist)<1):
            return False;
        prefix="data/"+str(int(time.time()));
        i=0;
        header = '<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"><link href = "css/common.css" type="text/css" rel="stylesheet"></head><body>';
        tail = '<script src = js/common.js></script></body></html>';
        while i<len(self.pagelist):
            file = open(prefix+"_"+str(i+1)+".html","w");
            file.write(header);
            page = self.pagelist[i];
            title = json.dumps(page["title"],ensure_ascii=False).encode('UTF-8').strip('"');
            content = json.dumps(page["content"],ensure_ascii=False).encode('UTF-8').strip('"');
            content= re.sub("<img[^>]*src=([^\s\"\\\]+)[^>]*>",lambda x:"<img class = 'pic' src="+urllib2.unquote(x.group(1))+">",content)
            content = re.sub("<span[^>]+>","<span>",content)
            file.write("<div id = 'title'>" + title + "</div>\n");
            file.write("<div id = 'content'>" + content + "</div>\n");
            file.write(tail);
            i+=1;

    def parseBlock(self,block,page):
        if("func_type" in block.keys() and block["func_type"] == "TITLE"):
            page["title"]=block["data_value"]

        if(block["type"] == "VIRTUAL_CONTENT_TEXT"):
            page["content"]=block["data_value"]["content"][0]["data_value"];


    def getData(self,url):
        req = urllib2.Request(self.prefix+urllib2.quote(url),None,headers);
        try:
            response = urllib2.urlopen(req,timeout=15);
        except:
            return {};
        the_page = response.read();
        #print the_page;
        try:
            s = json.loads(the_page);
        except:
            return {};
        response.close();
        #if("offline" not in s.keys()):
        #    return {};
        if("page_type" not in s.keys() or s["page_type"] != "PAGE_TYPE_NEWS_CONTENT"):
            return {};
        return s["blocks"];

    def getURLList(self,url):
        json_data = self.getData(url);
        if (len(json_data)<1):
            return False;
        hasAdd = False;
        i=0;
        while i <len(json_data):
            block=json_data[i];
            if(block["type"] == "PAGE_TURNING" and block["data_value"]["pt_type"] == "1"):
                pt=block;
                j=0;
                while j < len(pt["data_value"]["pt_link"]):
                    self.urllist.append(pt["data_value"]["pt_link"][j]["link"]);
                    hasAdd = True;
                    j+=1;
            i+=1;
        if(not hasAdd):
            self.urllist.append(url);
         
    def process(self,url):
        self.getURLList(url);
        i=0;
        while i < len(self.urllist):
            self.parseURL(self.urllist[i]);
            i+=1;

    def parseURL(self,url):
        json_data = self.getData(url);
        if (len(json_data)<1):
            return False;
        page = {};
        page["url"] = url;
        i=0;
        while i <len(json_data):
            self.parseBlock(json_data[i],page);
            i+=1;
        self.pagelist.append(page);
        return True;

if (len(sys.argv)>1):
    url = sys.argv[1];
else:
    url="http://news.qiyue.com/yule/bagua/20140403/213931.html";

np = TCParser();
np.process(url);
np.dumpjson();
np.json2file();

