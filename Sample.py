import io
import json
import urllib
import urllib2

from HTMLParser import HTMLParser


#def add_json_data(args):
#    with io.open('Sample.json', mode='r', encoding='utf-8') as feedsjson:
#        data = json.load(feedsjson)
#        print (data)
#    with io.open('Sample.json', mode='a+', encoding='utf-8') as feedsjson:
#        data = json.load(feedsjson)
#        entry = {}
#        entry['numComplaints'] = args.numComplaints
#        entry['areaCode'] = args.areaCode
#        entry['phoneNumber'] = args.phoneNumber
#        entry['comments'] = args.comments
#        json.dump(entry, data)
#        print (data)

class MyFancyHTMLParser(HTMLParser):
  def __init__(self):
      HTMLParser.__init__(self)
      self.numcomFound = False
      self.phoneFound = False
      self.commentFound = False
      self.buf = ""
      self.level = 0
      self.data = ""
      self.idx = 0
      self.i = 0
      self.elementdata = {}

  def fetch_url(self, url) :
      request = urllib2.Request(url)
      response = urllib2.urlopen(request)
      html = response.read()
      response.close()
      return (html)
      #self.feed (html)

  def get_area_code(self, data):
      if data[0] == "(":
      # Need to remove the parenthesis around area code
          data = data.replace("(", "")
          data = data.replace(")", "")

      # Get area code
      number = (data[:3])
      return number

  def handle_starttag(self, tag, attrs):
      # Number of Comment/Reports
      if tag == "div" and ("class", "oos_previewSide") in attrs:
          self.numcomFound = True
      elif self.numcomFound:
          self.level += 1

      # Phone Number
      if tag == "h4" and ("class", "oos_previewHeader") in attrs:
          self.phoneFound = True
      elif self.phoneFound:
          self.level += 1

      # The Comment
      if tag == "div" and ("class", "oos_previewBody") in attrs:
          self.commentFound = True
      elif self.commentFound:
          self.level += 1

  def handle_endtag(self, tag):
      if self.numcomFound or self.phoneFound or self.commentFound:
          self.level -= 1

          # Handle end of the number of comments field
          if (self.level == 0) and self.numcomFound:
              self.numcomFound = False
              if (self.idx == 0):
                  self.idx += 1
                  self.data = "numberOfComplaints: " + self.buf
              else:
                  self.data = (self.data + ", ") + "numberOfComplaints: " + self.buf
              self.buf = ""

          # Handle the end of the phone number and calculate the area code field
          if (self.level == 0) and self.phoneFound:
              self.phoneFound = False
              areacode= self.get_area_code(self.buf)
              self.data = (self.data + ", ") + "areaCode: " + areacode
              self.data = (self.data + ", ") + "phoneNumber: " + self.buf
              self.buf = ""

          # Handle the end of the comments field
          if (self.level == 0) and self.commentFound:
              self.commentFound = False
              self.buf = self.buf.strip("kdxyiun2 6s,so,ltz,fz")
              self.data = (self.data + ", ") + "comments: " + self.buf
              self.elementdata[self.i] = self.data
              print(self.elementdata[self.i])
              self.i += 1
              self.buf = ""
              self.data = ""
              self.idx = 0

  def handle_data(self, data):
      if self.numcomFound or self.phoneFound or self.commentFound:
          self.buf += data


if __name__ == '__main__':
    # Get data from site
    ScrubData = MyFancyHTMLParser()
    myHtml = ScrubData.fetch_url("https://s3.us-east-2.amazonaws.com/gsd-auth-callinfo/callnotes.html")
    ScrubData.feed(myHtml)

    # Convert to JSON
    with io.open('Challenge.json', mode='a+', encoding='utf-8') as datafeed:
        json.dumps([], datafeed)


