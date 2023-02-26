import codecs as co
import markdown as md
import re,sys,os,shutil,time

class MdToEpub():
    def __init__(self):
        self.setting={}
    def escape_illgal_chars(self,txt):
        replace_dict={ '\\':'＼', '*':'＊', '_':'＿', '{':'｛', '}':'｝', '[':'［', ']':'］', '(':'（', ')':'）', '#':'＃', '+':'＋', '-':'－', '.':'．', '!':'！' }
        tmp_txt=txt
        replace_ls=['\\','*','_','{','}','[',']','(',')','#','+','-','.','!']
        for j in replace_ls:
            tmp_txt=tmp_txt.replace(j,replace_dict[j])
        return tmp_txt
    
    #創建目錄，如果目錄不存在
    def mkdir_if_not_exists(self,out_dir):
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
            print(f"\t{out_dir} Created!")
        else:
            print(f"\t{out_dir} Existed!")
    #刪除目錄，包含目錄裡面的所有檔案
    def delete_folder(self,dir_path):
        shutil.rmtree(dir_path, ignore_errors=True)
        print(f"\tDeleted '{dir_path}' directory successfully")
    
    #取得目錄裡面的所有圖像列表，傳回值為list
    def get_img_list(self,source_dir,img_type=['jpg','png']):
        if os.path.exists(source_dir):
            img_type_str_lower=""
            for i in img_type:
                img_type_str_lower+=(i).lower()
            myimages = []
            dirFiles = os.listdir(source_dir)
            dirFiles.sort()
            sorted(dirFiles)
            for files in dirFiles:
                if (files.split('.')[-1].lower() in img_type_str_lower) and '.db' not in files:
                    myimages.append(files)
            return myimages
        else:
            print(f"\t{source_dir} directory is a ghost! abort get img list ")
            return None
    
    def gent_htm_from_md(self,source,temp,filename):
        fo = co.open(source+filename, mode="r", encoding="utf-8")
        fr = fo.read()
        # call escape_illgal_chars()
        fr=re.sub(r"([^`]{1})(`)([^`]{1}.*?[^`]{1})(`)([^`]{1})",r"\1『\3』\5",fr,re.DOTALL)
        ls=re.findall("```.*?```",fr,re.DOTALL)
        #print(len(ls))
        for i  in ls:
            subtxt=i
            start=fr.find(i)
            start2=start+len(subtxt)
            fr=fr[:start]+'<pre>'+i.replace('`','')+'</pre>'+fr[start2:]
        
        #fr = re.sub(r"^(```)([^`]*)(```)$",r"<pre>\2</pre>",fr,re.DOTALL)
        #fr = fr.replace('{','&lbrace;').replace('}','&rbrace;')
        #header_txt=re.findall(r"^# [^\n]*",fr,re.DOTALL)[0][2:].replace("\r","").replace("\n","")
        header_txt = filename
        ht = md.markdown(fr)
        out = co.open(temp+filename.replace(".md",".htm"), "w+", encoding="utf-8", errors="xmlcharrefreplace")
        out.write(ht)
        return header_txt
    
    def add_headline_num_to_htm(self,htm_url,header_txt,css_loc):
        css_txt=open(css_loc,'r',encoding='utf-8').read()
        tmp_header="""<?xml version='1.0' encoding='utf-8'?>
    <html xmlns="http://www.w3.org/1999/xhtml" lang="zh" class="calibre" xml:lang="zh">
    <head>
        <title>"""+header_txt+"""</title>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
        <style>"""+css_txt+"""
        </style>
    </head>
    <body class="calibre1">
    """
        tmp_footer="""
    </body>
    </html>
    """
        #print(htm_url)
        ls=[i.replace('\n','') for i in open(htm_url,'r',encoding='utf-8').readlines() if i!='\n']
        headline_count=0
        headline_ls=[]
        tmp_htm=""
        used_img_ls=[]
        for i in range(0,len(ls)):
            if ls[i].find("src=\"images/")!=-1:
                ls[i]=ls[i].replace("src=\"images/","src=\"")
                used_img_ls.append(re.findall("src=\"([^\"]*)\"",ls[i])[0])
            if re.match("^<h1>",ls[i]) or re.match("^<h2>",ls[i]):
                headline_ls.append(ls[i].replace("\n","")[4:-5])
                #ls[i]=(ls[i][:3]+" id='toc_"+str(headline_count)+"'>"+ls[i][4:]+"\n")
                tmp_htm+=(ls[i][:3]+" id='toc_"+str(headline_count)+"'>"+ls[i][4:]+"\n")
                headline_count+=1
                #print(ls[i])
            elif re.match("^\d\. ",ls[i]):
                tmp_htm+='<br />'+ls[i].replace("code>","pre>")+"\n"
            else:
                tmp_htm+=ls[i].replace("code>","pre>")+"\n"
        tmp_htm=tmp_htm.replace("<pre>\n","<pre>")
        with open(htm_url,'w+',encoding='utf-8') as hf:
            hf.write(tmp_header+tmp_htm+tmp_footer)
        #print('ADD_HEADLINE_NUM_TO_HTM OKAY!')
        return headline_ls,used_img_ls

    def fix_table_view(self,htm_url):
        with open(htm_url,'r',encoding='utf-8') as f:
            source = f.read()
        ls = re.findall("<p>[^\|]*\|.*?\n.*?<\/p>",source,re.DOTALL)
        #print('fix_table_view ls: ',ls)
        for i  in ls:
            subtxt=i
            start=source.find(i)
            start2=start+len(subtxt)
            source=source[:start]+'<table>'+self.fix_table_view_sub(i)+'</table>'+source[start2:]
        with open(htm_url,'w+',encoding='utf-8') as f:
             f.write(source)

    def fix_table_view_sub(self,tr_txt):
        tmp_txt = tr_txt.replace('<p>','').replace('</p>','')
        output = ""
        ls = tmp_txt.split('\n')
        row_mode = 'th'
        for i in ls:
            if i.find(':---')!=-1:
                row_mode = 'td'
                continue
            output += '<tr>'
            for j in i.split('|'):
                output += f"<{row_mode}>{j}</{row_mode}>"
            output += '</tr>'
        return output

    def gent_ncx_from_htm(self,htm_fname,tmp_folder,book_name,h_text_ls):
        htm_fname1= htm_fname if htm_fname.find("\\")==-1 else htm_fname.split("\\")[-1]
        doc_title=book_name
        ncx_header=f"""<?xml version='1.0' encoding='utf-8'?>
    <ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1" xml:lang="zh">
    <head>
        <meta name="dtb:depth" content="2"/>
        <meta name="dtb:generator" content="calibre (6.11.0)"/>
        <meta name="dtb:totalPageCount" content="0"/>
        <meta name="dtb:maxPageNumber" content="0"/>
    </head>
    <docTitle>
        <text>{book_name}</text>
    </docTitle>
    <navMap>
    """
        ncx_footer="</navMap></ncx>"
        ncx_body=""
        for i in range(0,len(h_text_ls)):
            htm_fname_fix= (f"#toc_{i}" if i>0 else "")
            ncx_body+=f"""    <navPoint id="num_{i+1}" playOrder="{i+1}">
        <navLabel>
            <text>{h_text_ls[i]}</text>
        </navLabel>
        <content src="{htm_fname1}{htm_fname_fix}"/>
        </navPoint>
    """
        with open(tmp_folder+"toc.ncx","w+",encoding="utf-8") as f:
            f.write(ncx_header+ncx_body+ncx_footer)
    
    def read_book_dict(self,book_dict_url):
        return dict([i.replace('\n','').replace('\\\\','\\').split('\t') for i in open(book_dict_url,'r',encoding='utf-8').readlines() if i!='\n'])
    
    def gent_content_opf(self,htm_fname,ncx_fname,opf_fname,book_name,author_name,img_ls):
        img_item_txt=""
        img_item_txt+="<item id=\"cover\" href=\"cover-image.png\" media-type=\"image/png\"/>"
        for i in range(1,len(img_ls)+1):
            if 'cover-image.png' not in img_ls[i-1]:
                img_item_txt+=f"    <item id=\"imgid{i}\" href=\"{img_ls[i-1]}\" media-type=\"image/{'png' if 'png' in img_ls[i-1] else 'jpg'}\"/>\n"
        htm_fname1= htm_fname if htm_fname.find("\\")==-1 else htm_fname.split("\\")[-1]
        opf_txt=f"""<?xml version='1.0' encoding='utf-8'?>
    <package xmlns="http://www.idpf.org/2007/opf" unique-identifier="uuid_id" version="2.0">
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
        <dc:title>{book_name}</dc:title>
        <dc:creator opf:role="aut" opf:file-as="{author_name}">{author_name}</dc:creator>
        <dc:language>zh</dc:language>
        <meta name="calibre:author_link_map" content="{book_name}"/>
        <meta name="calibre:title_sort" content="{book_name}"/>
        <meta name="cover" content="cover"/>
    </metadata>
    <manifest>
        <item href="{ncx_fname}" id="ncx" media-type="application/x-dtbncx+xml"/>
        <item id="id" href="{htm_fname1}" media-type="application/xhtml+xml"/>
    {img_item_txt}
    </manifest>
    <spine toc="ncx">
        <itemref idref="id"/>
        </spine>
    <guide>
        <reference type="cover" title="Cover" href="cover-image.png"/>
    </guide>
    </package>
    """
        #print(opf_txt)
        with open(opf_fname,"w+",encoding="utf-8") as f:
            f.write(opf_txt)
    
    def gen_epub(self,convert_url,opf_url,epub_url):
        os.system('cmd /c "'+convert_url+' '+opf_url+' '+epub_url+' --pretty-print "')
        print("GENT EPUB OK!")
    
    def main(self):
        self.setting=self.read_book_dict('resource\\setting.txt')
        print(self.setting['fileName'])
        self.mkdir_if_not_exists(self.setting['TEMP_DIR_ROOT'])
        self.mkdir_if_not_exists(self.setting['EPUB_DIR_ROOT'])
        
        img_ls=self.get_img_list(self.setting['IMAGES_DIR_ROOT'])
        #print(img_ls)
        # 將 SOURCE/images/ 所有圖檔複制到 TEMP/
        if img_ls != None and len(img_ls)>0: #####
            for i in img_ls:
                shutil.copyfile(self.setting['IMAGES_DIR_ROOT']+i, self.setting['TEMP_DIR_ROOT']+i)
        # step1: md 2 htm save to temp
        header_txt=self.gent_htm_from_md(self.setting['SOURCE_DIR_ROOT'].strip(),self.setting['TEMP_DIR_ROOT'].strip(),self.setting['fileName'].strip())
        headline_ls,used_img_ls=self.add_headline_num_to_htm(self.setting['TEMP_DIR_ROOT'].strip()+self.setting['fileName'].strip().replace(".md",".htm"),header_txt,self.setting['CSS_LOC'].strip())
        self.fix_table_view(self.setting['TEMP_DIR_ROOT'].strip()+self.setting['fileName'].strip().replace(".md",".htm"))
        #print(headline_ls)
        self.gent_ncx_from_htm(self.setting['TEMP_DIR_ROOT'].strip()+self.setting['fileName'].strip().replace(".md",".htm"),self.setting['TEMP_DIR_ROOT'].strip(),self.setting['bookName'].strip(),headline_ls)
        self.gent_content_opf(self.setting['TEMP_DIR_ROOT'].strip()+self.setting['fileName'].strip().replace(".md",".htm"),self.setting['ncx_fname'].strip(),self.setting['TEMP_DIR_ROOT'].strip()+self.setting['opf_fname'].strip(),self.setting['bookName'].strip(),self.setting['author'].strip(),used_img_ls)
        
        self.gen_epub(self.setting['EBOOK_ENGINE'].strip(),self.setting['TEMP_DIR_ROOT'].strip()+self.setting['opf_fname'].strip(),self.setting['EPUB_DIR_ROOT'].strip()+self.setting['fileName'].replace(".md",".epub").strip())
        #remove all files in TEMP when finished
        self.delete_folder(self.setting['TEMP_DIR_ROOT'].strip())
#if __name__ == "__main__": main()

