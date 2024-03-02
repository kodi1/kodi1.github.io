import xml.etree.ElementTree as etree
import xml.etree.cElementTree as cetree
import sys
import json
import requests
import gzip
import os
import time
import threading
import datetime
import codecs
import subprocess

epg_url = 'https://epg.cloudns.org/dl.php'
voyo_names = {"bTV" : "bTV", "bTVComedy":"bTV Comedy", "bTVCinema": "bTV Cinema", "bTVAction": "bTV Action", "bTVLady": "bTV Lady",
              "RING": "RING.BG"}
bgtv_names = ["bTVi", "bTV", "bTVComedy", "bTVCinema", "bTVAction", "bTVLady",
              "RING","VoyoCinema", "78TV", "BNT1", "BNT2", "BNT3", "BNT4",
              "Nova", "BulgariaOnAir", "DSTV", "TiankovFolk", "City",
              "Eurocom", "Kanal3"]

class voyo_epg(threading.Thread):
    def __init__(self, workdir, url=epg_url, offset=0, bgtv=None):
        #threading.Thread.__init__(self)
        self.__voyo_set = voyo_names
        self.configure(workdir, url, offset, bgtv)
        self.processing = False

    def configure(self, workdir, url=epg_url, offset=0, bgtv=bgtv_names, hours=24):
        self.__url = url
        self.__offset = offset
        self.__bgchan_set = bgtv
        self.__workdir = workdir
        if len(workdir)>0 and workdir[len(workdir)-1] != '/':
            self.__workdir += '/'
        self.__xmlepg = '{0}epg.xml'.format(self.__workdir)
        self.__xmlbgepg = '{0}bgepg.xml'.format(self.__workdir)
        self.__gzfile = '{0}epg.xml.gz'.format(self.__workdir)
        self.__hours = hours

    def __find_gzip(self):
        for gzbin in ['/bin/gzip', '/usr/bin/gzip', '/usr/local/bin/gzip', '/system/bin/gzip']:
            if os.path.exists(gzbin):
                return gzbin
        return None

    def __download(self, chunk_size=128):
        requests.packages.urllib3.disable_warnings()
        attempt = 0
        while attempt < 5:
            attempt += 1
            try:
                r = requests.get(self.__url, stream=True, allow_redirects=True, verify=False)
                if r.status_code == 200:
                    with open(self.__gzfile, 'wb') as fd:
                        for chunk in r.iter_content(chunk_size=chunk_size):
                            fd.write(chunk)
                    return True
            except Exception as ex:
                return False
        return False

    def __unpack(self):
        try:
            with gzip.GzipFile(self.__gzfile, 'rb') as ingz:
                content = ingz.read()
                with file(self.__xmlepg, 'wb') as outf:
                    outf.write(content)
            os.chdir(curdir)
            return True
        except Exception as ex:
            if os.path.exists(self.__xmlepg):
                os.unlink(self.__xmlepg)
            gzip_binary = self.__find_gzip()
            if gzip_binary != None and len(gzip_binary):
                try:
                    retval = subprocess.call([gzip_binary, '-d', self.__gzfile])
                    return True
                except Exception as e:
                    pass
            return False

    def __adjustTime(self, epgtime):
        offset = self.__offset * 60 * 60
        _epgtime = time.mktime(time.strptime(epgtime.split()[0],'%Y%m%d%H%M%S'))
        _epgtime += offset
        preftime = time.strftime('%Y%m%d%H%M%S', time.localtime(_epgtime))
        return '{0}{1}'.format(preftime, epgtime[14:])

    def __process_xml(self, useCetree=True):
        xml_esc = [
            ('"', '&quot;'),
            ('\'', '&apos;'),
            ('<', '&lt;'),
            ('>', '&gt;'),
            ('&', '&amp;')
        ]
        logos = {}
        epg_dict = {}
        lang = name = licon = u''
        start = stop = title = desc = icon = plang = dlang = u''
        if self.__bgchan_set and len(self.__bgchan_set)>0:
            f = codecs.open(self.__xmlbgepg, 'w', 'utf-8')
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<tv generator-info-name="Bulgarian EPG Project" ')
            f.write('generator-info-url="http://epg.kodibg.org">\n')

        if useCetree:
            interparse = cetree.iterparse(self.__xmlepg, events=("start", "end"))
        else:
            interparse = etree.iterparse(self.__xmlepg, events=("start", "end"))
        for event, element in interparse:
            if event == 'end':
                if element.tag == "channel":
                    ch = element.attrib['id']
                    if ch in self.__voyo_set:
                        logos[self.__voyo_set[ch]] = licon
                    if self.__bgchan_set and len(self.__bgchan_set)>0 and ch in self.__bgchan_set:
                        f.write('  <{0} id="{1}">\n'.format(element.tag, ch))
                        f.write('    <display-name lang="{0}">{1}</display-name>\n'.format(
                            lang, name))
                        f.write('    <icon src="{0}" />\n'.format(licon))
                        f.write('  </channel>\n')
                    ch = licon = lang = name = ''
                elif element.tag == 'display-name':
                    lang = element.attrib['lang']
                    name = element.text
                elif element.tag == 'icon':
                    licon = element.attrib['src']
                elif element.tag == "programme":
                    try:
                        start = self.__adjustTime(element.attrib['start'])
                        stop = self.__adjustTime(element.attrib['stop'])
                        chann = element.attrib['channel']
                        if chann in self.__voyo_set:
                            channel = self.__voyo_set[chann]
                            if not (channel in epg_dict):
                                epg_dict[channel] = []
                            #epg_dict[channel].append((start, stop, title, desc, icon))
                            epg_dict[channel].append((start, stop, title, '', icon))
                        if self.__bgchan_set and len(self.__bgchan_set)>0 and channel in self.__bgchan_set:
                            f.write('  <programme start="{0}" stop="{1}" channel="{2}">\n'.format(
                                start, stop, channel))
                            for c,e in xml_esc:
                                title = title.replace(c, e)
                            f.write(u'    <title lang="{0}">{1}</title>\n'.format(
                                plang, title))
                            if len(desc) > 0:
                                for c,e in xml_esc:
                                    desc = desc.replace(c, e)
                                f.write(u'    <desc lang="{0}">{1}</desc>\n'.format(
                                    dlang, desc))
                            if len(icon) > 0:
                                f.write('    <icon src="{0}" />\n'.format(icon))
                            f.write('  </programme>\n')
                    except:
                        pass
                    start = stop = title = desc = icon = plang = ''
                elif element.tag == 'title':
                    title = element.text
                    #for c,e in xml_esc:
                    #    title = title.replace(c, e)
                    plang = element.attrib['lang']
                elif element.tag == 'desc':
                    desc = element.text
                    #if len(desc) > 0:
                    #    for c,e in xml_esc:
                    #        desc = desc.replace(c, e)
                    dlang = element.attrib['lang']
                elif element.tag == 'icon':
                    icon = element.attrib['src']
        if self.__bgchan_set and len(self.__bgchan_set)>0:
            f.write('</tv>\n')
            f.close()
        return logos, epg_dict

    def __tidyup(self):
        if os.path.exists(self.__gzfile):
            os.unlink(self.__gzfile)
        if os.path.exists(self.__xmlepg):
            os.unlink(self.__xmlepg)

    def __check_file_expired(self, fn, expsec):
        if os.path.exists(fn):
            mtime = os.path.getmtime(fn)
            now = time.time()
            if mtime + expsec > now:
                return False
            else:
                os.unlink(fn)
        return True

    def run(self):
        if len(self.__workdir) == 0:
            return
        self.processing = True
        epg_exists = False
        epgfname = '{0}epg.json'.format(self.__workdir)
        epglock = '{0}epg.lock'.format(self.__workdir)
        logofname = '{0}logos.json'.format(self.__workdir)

        if os.path.exists(epgfname):
            mtime = os.path.getmtime(epgfname)
            now = time.time()
            epg_exists = True

        if self.__check_file_expired(epglock, 300) and self.__check_file_expired(epgfname, self.__hours*60*60):
            with open(epglock, 'w+') as flc:
                flc.write('processing\n')
            if self.__download() and self.__unpack():
                #this to run python implementation of etree if C implementation
                #fails
                try:
                    logodict, epgdict = self.__process_xml()
                except:
                    logodict, epgdict = self.__process_xml(False)
                #logostr = json.dumps(logodict, ensure_ascii=False)
                #with open(logofname, 'w') as f:
                #    f.write(logostr)
                epg_str = json.dumps(epgdict, ensure_ascii=False)
                with codecs.open(epgfname, 'w', 'utf-8') as f:
                    f.write(epg_str)
            self.__tidyup()
            if os.path.exists(epglock):
                os.unlink(epglock)
        self.processing = False


def main():
    epg = voyo_epg('/home/stani/Downloads/')
    epg.start()
    epg.join()
    if os.path.exists('epg.json'):
        with codecs.open('epg.json', 'r', 'utf-8') as f:
            epgs = f.read()
            epgd = json.loads(epgs)
            for e in epgd:
                print('\n==> {0}\n'.format(e))
                eepglst = epgd[e]
                for it in eepglst:
                    print('{0} - {1} {2}'.format(
                        it[0], it[1], it[2].encode('utf-8')))


if __name__ == '__main__':
    main()

