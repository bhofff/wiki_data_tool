'''
Created on Jul 17, 2019

@author: Brandon Hoffmann
'''


def init(term, directory):
    import json
    import urllib.request
    import urllib.parse
    import requests
    import os
    from html.parser import HTMLParser

    class MLStripper(HTMLParser):
        def __init__(self):
            self.reset()
            self.strict = False
            self.convert_charrefs= True
            self.fed = []
        def handle_data(self, d):
            self.fed.append(d)
        def get_data(self):
            return ''.join(self.fed)
    
    def strip_tags(html):
        s = MLStripper()
        s.feed(html)
        return s.get_data()
    
    url = 'https://en.wikipedia.org/w/api.php?'
    url_titles = url + urllib.parse.urlencode({
        'action': 'query',
        'format': 'json',
        'prop': 'images',
        'imlimit': "80",
        'titles': term,
        })
    data_titles = requests.get(url_titles).json()
    
    
    pageID = list(data_titles['query']['pages'].keys())[0]
    titles = data_titles['query']['pages'][pageID]['images']
    imagecount = len(titles)
    
    
    def createfolder(name):
        #create folder
        path = directory + name
        try:  
            os.mkdir(path)
        except OSError:  
            print ("Creation of the directory %s failed" % path)
            print('directory already exists or path not valid')
        else:  
            print ("Successfully created the directory %s " % path)
        return('done')
    
    def geturls(name, j):
        #get image URLs
        url_urls = url + urllib.parse.urlencode({
        'action': 'query',
        'format': 'json',
        'prop': 'imageinfo',
        'iiprop': 'url',
        'titles': name,
        })
        data_urls = requests.get(url_urls).json()
        imageurl = data_urls['query']['pages'][list(data_urls['query']['pages'].keys())[0]]['imageinfo'][0]['url']
        #download images
        if imageurl[-4:] == '.jpg':
            ext = '.jpg'
        elif imageurl[-4:] == '.png':
            ext = '.png'
        elif imageurl[-4:] == '.svg':
            ext = '.svg'
        elif imageurl[-4:] == 'webm':
            ext = '.webm'
        else:
            ext = '.png'
        urllib.request.urlretrieve(imageurl, directory + term + '/' + str(j) + ext)
        #get description strings
        url_desc = url + urllib.parse.urlencode({
        'action': 'query',
        'format': 'json',
        'prop': 'imageinfo',
        'iiprop': 'extmetadata',
        'titles': name,
        })
        data_desc = requests.get(url_desc).json()
        if 'ImageDescription' in data_desc['query']['pages'][list(data_desc['query']['pages'].keys())[0]]['imageinfo'][0]['extmetadata']:
            desc = data_desc['query']['pages'][list(data_desc['query']['pages'].keys())[0]]['imageinfo'][0]['extmetadata']['ImageDescription']['value']
        else:
            print('Error: Image ' + str(j) + ext + ' does not have description. ' + str(j) + '.txt will read "N/A"');
            desc = 'N/A';
        #download descriptions
        desc = strip_tags(desc)
        f = open(directory + term + '/' + str(j) + '.txt','w+', encoding='utf-8')
        f.write(desc)
        f.close()
        return('done')
    
    
    def getmain(name):
        #get main body text &exintro
        url_main = url + 'format=json&action=query&prop=extracts&exlimit=max&excontinue&explaintext&' + urllib.parse.urlencode({'titles': name})
        data_main = requests.get(url_main).json()
        main = data_main['query']['pages'][list(data_titles['query']['pages'].keys())[0]]['extract']#.replace(/(\r\n|\n|\r)/gm,"")
        #download main
        f = open(directory + term + '/main.txt','w+', encoding='utf-8')
        f.write(main)
        f.close()
        return('done')
    
    #triggers
    if imagecount > 0:
        createfolder(term)
        for i in range(0, imagecount):
            #filter unwanted results
            imagename = titles[i]['title']
            if imagename[slice(9)] == 'File:Wiki':
                imagecount = i - 1
                break
            else:
                geturls(imagename, i)
        print(str(imagecount) + ' files created')
        getmain(term)
            
