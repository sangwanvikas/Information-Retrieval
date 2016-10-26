# coding=utf-8
import sys
from HTMLParser import HTMLParser

# create a subclass and override the handler methods
class MyHTMLParser(HTMLParser):
    df =""
    # def handle_starttag(self, tag, attrs):
    #     print "Encountered a start tag:", tag
    # def handle_endtag(self, tag):
    #     print "Encountered an end tag :", tag
    def handle_data(self, data):
        MyHTMLParser.df = MyHTMLParser.df + " " + data

    def GetParsedContentFromHtml(self, email):
        parser = MyHTMLParser()
        MyHTMLParser.df = ""
        try:
            parser.feed(email)
            return MyHTMLParser.df
        except:
            print "vikassssssss"
            return ''


