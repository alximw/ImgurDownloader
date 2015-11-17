#!/usr/bin/python
 
 
import requests
import sys,os
from bs4 import BeautifulSoup
 
CHUNK_SIZE = 4096

def download_file(path,url):
    bytes = 0
    files = 0
    #print url+']'
    server_response = requests.get(url)
    try:
        if server_response.status_code == 200:
            if not os.path.exists(path):
                os.makedirs(path)
 
            file_path = path+url[url.rfind("/"):]
            #print file_path
 
            with open(file_path,'wb') as f:
                files +=1
                for chunk in server_response.iter_content(CHUNK_SIZE):
                    bytes += len(chunk)
                    f.write(chunk)
                f.close()
    except Exception as e:
        print 'Problems downloading file...(requests/openfile crashed)'
        os.rmdir(path)
    return (bytes,files)
 
 
def download_from_imgur(path,url):
 
    bytes = 0
    files = 0
    print '[triying to download: '+url
    if 'http://i.imgur.com/' in url:
        #direct link to picture
        downloaded_bytes,downloaded_files=download_file(path,url)
        bytes+=downloaded_bytes
        files+=downloaded_files
 
    elif 'http://imgur.com/a/' in url:
        #album link 
        #download album page
        print "album"
        server_response = requests.get(url,allow_redirects=False)
 
        if server_response.status_code == 200:
            link_list=[]
            page_source = server_response.text
            #parse web with bs4
            soup = BeautifulSoup(page_source)
            head = soup.html.head
            metas = head.findAll('meta', {"property":'og:image'})
            if metas:
                for meta in metas:
                    if 'jpg' in meta.get('content'):
                        link_list.append(meta.get('content'))
 
            if len(link_list) > 0:
                for link in link_list:
                    downloaded_bytes,downloaded_files=download_file(path,link)
                    bytes+=downloaded_bytes
                    files+=downloaded_files
 
    elif 'http://imgur.com/' in url:
        #album with 1 pic only
 
        server_response = requests.get(url,allow_redirects = False)
        if server_response.status_code == 200:
            page_source = server_response.text
            soup = BeautifulSoup(page_source)
            pic_url = soup.select('.image img')[0]
            pic_url = pic_url['src']
            if pic_url.startswith('//'):
                pic_url = pic_url.replace('//','http://')
            if '?' in pic_url:
                pic_url = pic_url[:pic_url.find('?')]
            file_path = path
            downloaded_bytes,downloaded_files=download_file(file_path,pic_url)
            bytes+=downloaded_bytes
            files+=downloaded_files
 
    return (bytes,files)
 
 
 
def main(argv):
 
    if argv > 2:
        bytes, files = download_from_imgur(argv[2],argv[1])
    else:
        bytes, files = download_from_imgur('',argv[1])
 
 
    if bytes < 1024:
        print "Downloaded "+str(bytes)+" bytes in "+str(files)+" files"
    elif bytes > 1024 and bytes < 1024*1024:
        size = round(float(bytes)/1024,2)
        print "Downloaded "+str(size)+" KB in "+str(files)+" files"
    elif bytes > 1024*1024:
        size = round(float(bytes)/(1024*1024),2)
        print "Downloaded "+str(size)+" MB in "+str(files)+" files"
 
if __name__== '__main__':
    main(sys.argv)