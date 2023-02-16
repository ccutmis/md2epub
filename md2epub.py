import codecs as co
import markdown as md
import re,sys,os,shutil,time

def escape_illgal_chars(txt):
    replace_dict={ '\\':'＼', '*':'＊', '_':'＿', '{':'｛', '}':'｝', '[':'［', ']':'］', '(':'（', ')':'）', '#':'＃', '+':'＋', '-':'－', '.':'．', '!':'！' }
    tmp_txt=txt
    replace_ls=['\\','*','_','{','}','[',']','(',')','#','+','-','.','!']
    for j in replace_ls:
        tmp_txt=tmp_txt.replace(j,replace_dict[j])
    return tmp_txt

#創建目錄，如果目錄不存在
def mkdir_if_not_exists(out_dir):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
        print(f"\t{out_dir} Created!")
    else:
        print(f"\t{out_dir} Existed!")
#刪除目錄，包含目錄裡面的所有檔案
def delete_folder(dir_path):
    shutil.rmtree(dir_path, ignore_errors=True)
    print(f"\tDeleted '{dir_path}' directory successfully")

#取得目錄裡面的所有圖像列表，傳回值為list
def get_img_list(source_dir,img_type=['jpg','png']):
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

def gent_htm_from_md(source,temp,filename):
    fo = co.open(source+filename, mode="r", encoding="utf-8")
    fr = fo.read()
    # call escape_illgal_chars()
    fr=re.sub(r"([^`]{1})(`)([^`]{1}.*?[^`]{1})(`)([^`]{1})",r"\1『\3』\5",fr,re.DOTALL)
    ls=re.findall("```.*?```",fr,re.DOTALL)
    print(len(ls))
    for i  in ls:
        subtxt=i
        start=fr.find(i)
        start2=start+len(subtxt)
        fr=fr[:start]+'<pre>'+i.replace('`','')+'</pre>'+fr[start2:]
    
    #fr = re.sub(r"^(```)([^`]*)(```)$",r"<pre>\2</pre>",fr,re.DOTALL)
    #fr = fr.replace('{','&lbrace;').replace('}','&rbrace;')
    #header_txt=re.findall(r"^# [^\n]*",fr,re.DOTALL)[0][2:].replace("\r","").replace("\n","")
    header_txt = filename #####
    ht = md.markdown(fr)
    out = co.open(temp+filename.replace(".md",".htm"), "w+", encoding="utf-8", errors="xmlcharrefreplace")
    out.write(ht)
    return header_txt

def add_headline_num_to_htm(htm_url,header_txt,css_loc):
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
    print('ADD_HEADLINE_NUM_TO_HTM OKAY!')
    return headline_ls,used_img_ls
    

def gent_ncx_from_htm(htm_fname,tmp_folder,book_name,h_text_ls):
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

def read_book_dict(book_dict_url):
    if not os.path.exists(book_dict_url): #找不到 setting file
        cwd = os.getcwd()
        cwd=cwd.replace("\\",'\\\\')
        tmp_dict={}
        tmp_dict['fileName'] = "md2epub使用教學.md"
        tmp_dict['bookName'] = "md2epub使用教學"
        tmp_dict['author'] = "Your Name"
        tmp_dict['EBOOK_ENGINE'] = "C:\\Calibre2\\ebook-convert.exe"
        tmp_dict['SOURCE_DIR_ROOT'] = cwd+r"\\SOURCE\\"
        tmp_dict['TEMP_DIR_ROOT'] = cwd+r"\\TEMP\\"
        tmp_dict['RESULT_DIR_ROOT'] = cwd+r"\\RESULT\\"
        tmp_dict['EPUB_DIR_ROOT'] = cwd+r"\\EPUB\\"
        tmp_dict['IMAGES_DIR_ROOT'] = cwd+r"\\SOURCE\\images\\"
        tmp_dict['CSS_LOC'] = cwd+r"\\stylesheet.css"
        tmp_dict['ncx_fname'] = "toc.ncx"
        tmp_dict['opf_fname'] = "book-metadata.opf"
        write_str="fileName	"+(tmp_dict['fileName'])+"\nbookName	"+(tmp_dict['bookName'])+"\nauthor	"+(tmp_dict['author'])+"\nEBOOK_ENGINE	"+(tmp_dict['EBOOK_ENGINE'])+"\nSOURCE_DIR_ROOT	"+(tmp_dict['SOURCE_DIR_ROOT'])+"\nTEMP_DIR_ROOT	"+(tmp_dict['TEMP_DIR_ROOT'])+"\nRESULT_DIR_ROOT	"+(tmp_dict['RESULT_DIR_ROOT'])+"\nEPUB_DIR_ROOT	"+(tmp_dict['EPUB_DIR_ROOT'])+"\nIMAGES_DIR_ROOT	"+(tmp_dict['IMAGES_DIR_ROOT'])+"\nCSS_LOC	"+(tmp_dict['CSS_LOC'])+"\nncx_fname	"+(tmp_dict['ncx_fname'])+"\nopf_fname	"+(tmp_dict['opf_fname'])+"\n"
        with open(book_dict_url,'w+',encoding='utf-8') as f:
            f.write(write_str)
        return tmp_dict
    else:
        return dict([i.replace('\n','').replace('\\\\','\\').split('\t') for i in open(book_dict_url,'r',encoding='utf-8').readlines() if i!='\n'])

def gent_content_opf(htm_fname,ncx_fname,opf_fname,book_name,author_name,img_ls):
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

def gen_epub(convert_url,opf_url,epub_url):
    os.system('cmd /c "'+convert_url+' '+opf_url+' '+epub_url+' --pretty-print "')
    print("GENT EPUB OK!")

def main():
    setting=read_book_dict('resource\\setting.txt')
    print(setting['fileName'])
    mkdir_if_not_exists(setting['TEMP_DIR_ROOT'])
    mkdir_if_not_exists(setting['EPUB_DIR_ROOT'])
    
    img_ls=get_img_list(setting['IMAGES_DIR_ROOT'])
    #print(img_ls)
    # 將 SOURCE/images/ 所有圖檔複制到 TEMP/
    if img_ls != None and len(img_ls)>0:
        if img_ls != None and len(img_ls)>0: #####
            for i in img_ls:
                shutil.copyfile(setting['IMAGES_DIR_ROOT']+i, setting['TEMP_DIR_ROOT']+i)
    # step1: md 2 htm save to temp
    header_txt=gent_htm_from_md(setting['SOURCE_DIR_ROOT'].strip(),setting['TEMP_DIR_ROOT'].strip(),setting['fileName'].strip())
    headline_ls,used_img_ls=add_headline_num_to_htm(setting['TEMP_DIR_ROOT'].strip()+setting['fileName'].strip().replace(".md",".htm"),header_txt,setting['CSS_LOC'].strip())
    #print(headline_ls)
    gent_ncx_from_htm(setting['TEMP_DIR_ROOT'].strip()+setting['fileName'].strip().replace(".md",".htm"),setting['TEMP_DIR_ROOT'].strip(),setting['bookName'].strip(),headline_ls)
    gent_content_opf(setting['TEMP_DIR_ROOT'].strip()+setting['fileName'].strip().replace(".md",".htm"),setting['ncx_fname'].strip(),setting['TEMP_DIR_ROOT'].strip()+setting['opf_fname'].strip(),setting['bookName'].strip(),setting['author'].strip(),used_img_ls)
    
    gen_epub(setting['EBOOK_ENGINE'].strip(),setting['TEMP_DIR_ROOT'].strip()+setting['opf_fname'].strip(),setting['EPUB_DIR_ROOT'].strip()+setting['fileName'].replace(".md",".epub").strip())
    #remove all files in TEMP when finished
    delete_folder(setting['TEMP_DIR_ROOT'].strip())
if __name__ == "__main__": main()

