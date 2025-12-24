from django.shortcuts import render,HttpResponse, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, Permission, User
from django.contrib.auth import login, logout
from django.conf import settings
from .models import Mapdata as md
from .models import UserObject
import json
import subprocess
import os
import unicodedata
# Create your views here.


def mindmap(request):
    user=request.user
    owner=User.objects.get(username=request.GET.get('owner'))
    title=request.GET.get('title')
    data=md.objects.filter(owner=owner,title=title)
    if len(data)!=1:
        return HttpResponse("Error: Something went wrong: not a single matching brainmap", status=400)
    data=data[0]

    if data.share==True:
        return render(request,"mindmap.html",{"owner":owner,"map_title":data.title,"map_data":json.dumps(data.map_data),"map_path":json.dumps(data.map_path),'MEDIA_URL': settings.MEDIA_URL})
    else :
        if user == owner:
            return render(request,"mindmap.html",{"owner":owner,"map_title":data.title,"map_data":json.dumps(data.map_data),"map_path":json.dumps(data.map_path),'MEDIA_URL': settings.MEDIA_URL})
        else :
            return HttpResponse("Error: Map in private mode", status=400)

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            print(user)
            directory_path = os.path.join(settings.MEDIA_ROOT,'compiled_data', str(user) )
            os.makedirs(directory_path, exist_ok=True)
            return redirect('user')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def custom_logout(request):
    logout(request)
    return render(request,"registration/logout.html")

@login_required
def create_map(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        public_map = request.POST.get('checkbox')
        title = title.replace(" ", "_")
        title = unicodedata.normalize('NFKD', title)
        title = title.encode('ASCII', 'ignore').decode('ASCII')
        map_data = r"<#i>1<i#><#t>Start node<t#>"
        map_path = r"[None, '1', []]"
        map_link = r"None"

        # Check for existing maps with the same title for the current owner
        existing_maps = md.objects.filter(owner=request.user, title=title)

        # If a map with the same title exists, make the title unique
        if existing_maps.exists():
            counter = 1
            new_title = f"{title} {counter}"
            while md.objects.filter(owner=request.user, title=new_title).exists():
                counter += 1
                new_title = f"{title} {counter}"
            title = new_title

        # Create a new Mapdata instance with the unique title
        if public_map == "on":
            public_map = True
        else:
            public_map = False

        md.objects.create(
            owner=request.user,
            title=title,
            map_data=map_data,
            map_path=map_path,
            map_link=map_link,
            share=public_map
        )
        return redirect('user')
    return render(request, 'create_map.html', {})

@login_required
def edit_map(request):
    owner=request.user
    map_name=request.GET.get('map_name')
    existing_maps = md.objects.filter(owner=request.user, title=map_name)[0]


    if existing_maps.share == False:
        val_checked=""
    else:
        val_checked="checked"      

    if request.method == 'POST':
        new_title = request.POST.get('title')
        public_map = request.POST.get('checkbox')
        new_title = new_title.replace(" ", "_")
        new_title = unicodedata.normalize('NFKD', new_title)
        new_title = new_title.encode('ASCII', 'ignore').decode('ASCII')

        if public_map == "on":
            public_map = True
        else:
            public_map = False

        # Check for existing maps with the same title for the current owner
        existing_maps = md.objects.filter(owner=request.user, title=new_title)

        # If a map with the same title exists, make the title unique
        if existing_maps.exists() and map_name != new_title:
            counter = 1
            new_title = f"{new_title} {counter}"
            while md.objects.filter(owner=request.user, title=new_title).exists():
                counter += 1
                new_title = f"{new_title} {counter}"
            new_title = new_title
        
        obj = md.objects.filter(owner=owner,title=map_name)[0]
        obj.title=new_title
        obj.share=public_map
        obj.save()

        # Create a new Mapdata instance with the unique title
        return redirect('user')
    print(val_checked)
    return render(request, 'edit_map.html', {"map_title":map_name,"public":val_checked})

@login_required
def delete_map(request):
    owner=request.user
    map_name=request.GET.get('map_name')
    try:
        obj = md.objects.filter(owner=owner,title=map_name)[0]
        obj.delete()
        return JsonResponse({'status': 'success'})
    except md.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Object not found'}, status=404)

@login_required
def user(request):
    user_objects = md.objects.filter(owner=request.user)
    return render(request, 'user.html', {'user_objects':  user_objects,'user':request.user})

@login_required
def zoom(request):
    user=request.user
    owner=User.objects.get(username=request.GET.get('owner'))
    title=request.GET.get('title')
    data=md.objects.filter(owner=owner,title=title)
    if len(data)!=1:
        return HttpResponse("Error: Something went wrong: not a single matching brainmap", status=400)
    data=data[0]
    return render(request,"zoom.html",{"owner":owner,"map_title":data.title,"map_data":json.dumps(data.map_data),"map_path":json.dumps(data.map_path),'MEDIA_URL': settings.MEDIA_URL})

@login_required
def add_node(request):
    user=request.user
    owner=User.objects.get(username=request.GET.get('owner'))
    title=request.GET.get('title')
    data=md.objects.filter(owner=owner,title=title)
    if len(data)!=1:
        return HttpResponse("Error: Something went wrong: not a single matching brainmap", status=400)
    data=data[0]

    if user == owner:
        return render(request,"add_node.html",{"owner":owner,"map_title":data.title,"map_data":json.dumps(data.map_data),"map_path":json.dumps(data.map_path)})
    else:
        return HttpResponse("Error: you are not the owner of the map", status=400)

@login_required
def edit_node(request):
    user=request.user
    owner=User.objects.get(username=request.GET.get('owner'))
    title=request.GET.get('title')
    data=md.objects.filter(owner=owner,title=title)
    if len(data)!=1:
        return HttpResponse("Error: Something went wrong: not a single matching brainmap", status=400)
    data=data[0]
    if user == owner:
        img_id=request.GET.get('id')
        for line in data.map_data.split("\n"):
            if line.startswith("<#i>"+img_id+"<i#>"):
                if "<#text>" in line:
                    val_checked=""
                else:
                    val_checked="checked"
                return render(request,"edit_node.html",{"owner":owner,"map_title":data.title,"map_data":json.dumps(data.map_data),"map_path":json.dumps(data.map_path),"node_title":line.split("<#t>")[1].split("<t#>")[0].replace("<#n#>","\n").replace("<#text>","").replace("<text#>",""),"node_core":line.split("<t#>")[1].replace("<#n#>","\n").replace("<#text>","").replace("<text#>",""),"val_checked":val_checked})
        return HttpResponse("Error: No id matching for modification", status=400)
    else  :
        return HttpResponse("Error: you are not the owner of the map", status=400)


@csrf_exempt  # Use with caution; consider using Django's CSRF protection
def rebuild_all(request):
    user=request.user
    owner=User.objects.get(username=request.GET.get('owner'))
    title = request.GET.get('title')

    if owner!=user:
        return HttpResponse("Error: you are not the owner of the map", status=400)

    if not title:
        return JsonResponse({'error': 'Title parameter is missing'}, status=400)

    # Sanitize the title to prevent directory traversal
    sanitized_title = os.path.basename(title)
    # Construct the path using os.path.join
    path = os.path.join(settings.MEDIA_ROOT, 'compiled_data', str(owner),sanitized_title)

    try:
        data = md.objects.get(owner=owner, title=sanitized_title)
    except md.DoesNotExist:
        return JsonResponse({'error': 'Data not found'}, status=404)

    try:
        if not os.path.exists(path):
            return JsonResponse({'error': 'Directory does not exist'}, status=404)
        # Change to the directory
        os.chdir(path)
        # List and remove .svg files
        for elt in os.listdir(path):
            if elt.endswith(".svg"):
                os.remove(elt)

        # Process map data
        for line in data.map_data.split("\n"):
            index = line.split("<#i>")[1].split("<i#>")[0]
            old_title = line.split("<#t>")[1].split("<t#>")[0]
            old_core = line.split("<#t>")[1].split("<t#>")[1]
            compile_title_core(index, old_title, old_core, sanitized_title,owner)
        rebuild_path(owner, sanitized_title)

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt  # Use with caution; consider using Django's CSRF protection
def delete_node(request):
    user=request.user
    owner=User.objects.get(username=request.GET.get('owner'))
    title = request.GET.get('title')

    if owner!=user:
        return HttpResponse("Error: you are not the owner of the map", status=400)

    if not title:
        return JsonResponse({'error': 'Title parameter is missing'}, status=400)

    # Sanitize the title to prevent directory traversal
    sanitized_title = os.path.basename(title)

    try:
        data = md.objects.get(owner=owner, title=sanitized_title)
    except md.DoesNotExist:
        return JsonResponse({'error': 'Data not found'}, status=404)

    if request.method == 'DELETE':
        try:
            new_data = json.loads(request.body)
            image_id = new_data.get('id')

            if image_id == "1":
                return JsonResponse({'error': 'Cannot delete node 1'}, status=400)

            sorted_data = []
            for line in data.map_data.split("\n"):
                index = line.split("<#i>")[1].split("<i#>")[0]
                old_title = line.split("<#t>")[1].split("<t#>")[0]
                old_core = line.split("<#t>")[1].split("<t#>")[1]
                if index != image_id:
                    sorted_data.append([index, old_title, old_core])

            new_map_data = ""
            for elt in sorted_data:
                new_map_data += f"<#i>{elt[0]}<i#><#t>{elt[1]}<t#>{elt[2]}\n"
            data.map_data = new_map_data.rstrip()
            data.save()

            # Construct the path using os.path.join
            path = os.path.join(settings.MEDIA_ROOT, 'compiled_data', str(owner),sanitized_title)

            if not os.path.exists(path):
                return JsonResponse({'error': 'Directory does not exist'}, status=404)

            # Change to the directory and remove files
            os.chdir(path)
            try:
                os.remove(f"{image_id}.svg")
                os.remove(f"title-{image_id}.svg")
            except FileNotFoundError:
                pass  # Handle the case where the file does not exist

            rebuild_path(owner, sanitized_title)

            return JsonResponse({'status': 'success'})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid method'}, status=405)

@csrf_exempt  
def compile_add(request):
    user=request.user
    owner=User.objects.get(username=request.GET.get('owner'))
    title = request.GET.get('title')

    if owner!=user:
        return HttpResponse("Error: you are not the owner of the map", status=400)
    
    data=md.objects.filter(owner=owner,title=title)[0]
    if request.method == 'POST':
        try:
            new_data = json.loads(request.body)
            image_id = new_data.get('id')
            node_title = new_data.get('title')
            core = new_data.get('core')
            latex_compiler = new_data.get('latex_compiler')
            if latex_compiler==False:
                node_title="<#text>"+node_title+"<text#>"
                core="<#text>"+core+"<text#>"

            new_id=find_new_id(image_id,owner,title)

            sorted_data = []
            for line in data.map_data.split("\n"):
                index=(line.split("<#i>")[1].split("<i#>")[0])
                old_title=(line.split("<#t>")[1].split("<t#>")[0])
                old_core=(line.split("<#t>")[1].split("<t#>")[1])
                sorted_data.append([index,old_title,old_core])
                if index==image_id :
                    sorted_data.append([new_id,node_title,core])
            
            new_map_data=""
            for elt in sorted_data:
                new_map_data=new_map_data+"<#i>"+elt[0]+"<i#><#t>"+elt[1].replace("\n","<#n#>")+"<t#>"+elt[2].replace("\n","<#n#>")+"\n"
            data.map_data=new_map_data[:-1]
            data.save()

            compile_title_core(new_id,node_title,core,title,owner)
            rebuild_path(owner,title)
            

            return JsonResponse({'status': 'success'})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=405)


@csrf_exempt  
def compile_edit(request):
    user=request.user
    owner=User.objects.get(username=request.GET.get('owner'))
    title = request.GET.get('title')

    if owner!=user:
        return HttpResponse("Error: you are not the owner of the map", status=400)
    
    data=md.objects.filter(owner=owner,title=title)[0]
    if request.method == 'POST':
        try:
            new_data = json.loads(request.body)
            image_id = new_data.get('id')
            node_title = new_data.get('title')
            core = new_data.get('core')
            latex_compiler = new_data.get('latex_compiler')

            if latex_compiler==False:
                node_title="<#text>"+node_title+"<text#>"
                core="<#text>"+core+"<text#>"

            sorted_data = []
            for line in data.map_data.split("\n"):
                index=(line.split("<#i>")[1].split("<i#>")[0])
                if index!=image_id:
                    old_title=(line.split("<#t>")[1].split("<t#>")[0])
                    old_core=(line.split("<#t>")[1].split("<t#>")[1])
                    sorted_data.append([index,old_title,old_core])
                else :
                    sorted_data.append([image_id,node_title,core])
 
            new_map_data=""
            for elt in sorted_data:
                new_map_data=new_map_data+"<#i>"+elt[0]+"<i#><#t>"+elt[1].replace("\n","<#n#>")+"<t#>"+elt[2].replace("\n","<#n#>")+"\n"
            data.map_data=new_map_data[:-1]
            data.save()

            compile_title_core(image_id,node_title,core,title,owner)
            rebuild_path(owner,title)
            

            return JsonResponse({'status': 'success'})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=405)


def find_new_id(old_id,owner,title):
    data=md.objects.filter(owner=owner,title=title)[0]
    index_list = []
    for line in data.map_data.split("\n"):
        index_list.append(line.split("<#i>")[1].split("<i#>")[0])

    same_root_list=[]
    for index in index_list:
        if index.startswith(old_id):
            if len(index.split("_"))>len(old_id.split("_")):
                same_root_list.append(index.split("_")[len(old_id.split("_"))])

    if len(same_root_list)!=0:
        same_root_list=[int(i) for i in list(set(same_root_list))]
        same_root_list=sorted(same_root_list)
        new_id_list=[i+1 for i in range(len(same_root_list)+1)]
        i=0
        while new_id_list[i] in same_root_list:
            i+=1
        new_id=new_id_list[i]
    else :
        new_id=1

    return old_id+"_"+str(new_id)



def compile_title_core(id, node_title, core, title,owner):
    node_title = node_title.replace("<#n#>", "\n")
    core = core.replace("<#n#>", "\n")

    latex_template_title = r"""
\documentclass[margin=0.1cm,varwidth=500px]{standalone}
\usepackage{tikz}
\newcommand{\bottomlinebox}[2][1pt]{%
\tikz[baseline]{
    \node[anchor=base, draw=none, text depth=0pt, inner sep=0, align=center] (t) {#2\\[-0.2cm]};
    \draw[line width=#1] (t.south west) -- (t.south east);
}%
}

\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage{hyperref}

\begin{document}
\Huge
{{{title_content}}}
\end{document}
"""

    text_template_title = r"""
\documentclass[margin=0.1cm,varwidth=500px]{standalone}
\usepackage{tikz}
\newcommand{\bottomlinebox}[2][1pt]{%
\tikz[baseline]{
    \node[anchor=base, draw=none, text depth=0pt, inner sep=0, align=center] (t) {#2\\[-0.2cm]};
    \draw[line width=#1] (t.south west) -- (t.south east);
}%
}

\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage{hyperref}

\begin{document}
\Huge
\begin{verbatim}
{{{title_content}}}
\end{verbatim}
\end{document}
"""

    latex_template = r"""
\documentclass[margin=0.1cm,varwidth=500px]{standalone}
\usepackage{tikz}
\newcommand{\bottomlinebox}[2][1pt]{%
\tikz[baseline]{
    \node[anchor=base, draw=none, text depth=0pt, inner sep=0, align=center] (t) {#2\\[-0.2cm]};
    \draw[line width=#1] (t.south west) -- (t.south east);
}%
}

\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage{hyperref}

\begin{document}
\begin{center}
\bottomlinebox{\Huge  {{{title_content}}}  }
\end{center}

\normalsize
{{{core_content}}}
\end{document}
"""

    text_template = r"""
\documentclass[margin=0.1cm,varwidth=500px]{standalone}
\usepackage{tikz}
\usepackage{verbatimbox}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{fvextra}

\newcommand{\bottomlinebox}[2][1pt]{%
    \tikz[baseline]{
        \node[anchor=base, draw=none, text depth=0pt, inner sep=0, align=center] (t) {#2\\[-0.2cm]};
        \draw[line width=#1] (t.south west) -- (t.south east);
    }%
}

\begin{document}

% Define a verbatim box to capture the content
\begin{myverbbox}{\verbcontent}
{{{title_content}}}
\end{myverbbox}

\begin{center}
    \bottomlinebox{\scalebox{2.5}{\verbcontent}}
\end{center}

\begin{flushleft}
    \begin{Verbatim}[breaklines=true, breaksymbol=]
{{{core_content}}}
    \end{Verbatim}
\end{flushleft}

\end{document}
"""

    latex = "<#text>" not in node_title
    core = core.replace("<#text>", "").replace("<text#>", "")
    node_title = node_title.replace("<#text>", "").replace("<text#>", "")

    # Sanitize the title to prevent directory traversal
    sanitized_title = os.path.basename(title)
    path = os.path.join(settings.MEDIA_ROOT,'compiled_data',str(owner), sanitized_title)

    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

    def compile_latex(template, title_content, core_content=None):
        latex_document = template.replace(r"""{{{title_content}}}""", title_content)
        if core_content:
            latex_document = latex_document.replace(r"""{{{core_content}}}""", core_content)
        tex_path = os.path.join(path, 'latex_code.tex')
        with open(tex_path, 'w') as f:
            f.write(latex_document)

        subprocess.run(['pdflatex', tex_path], check=True, cwd=path)
        pdf_path = os.path.join(path, 'latex_code.pdf')
        svg_path = os.path.join(path, 'latex_code.svg')
        subprocess.run(['pdf2svg', pdf_path, svg_path], check=True, cwd=path)
        return svg_path

    # Compile title
    svg_path = compile_latex(latex_template_title if latex else text_template_title, node_title)
    os.rename(svg_path, os.path.join(path, f"title-{id}.svg"))

    # Compile core if present
    if core:
        svg_path = compile_latex(latex_template if latex else text_template, node_title, core)
        os.rename(svg_path, os.path.join(path, f"{id}.svg"))
    else :
        svg_path = compile_latex(latex_template_title if latex else text_template_title, node_title)
        os.rename(svg_path, os.path.join(path, f"{id}.svg"))

    return True



def rebuild_path(owner,title):
    data=md.objects.filter(owner=owner,title=title)[0]

    index_list = []
    for line in data.map_data.split("\n"):
        index_list.append(line.split("<#i>")[1].split("<i#>")[0])

    path_list=[]
    for index in index_list:
        indexes=index.split("_")
        if len(indexes)==1:
            index_before=None
        else :
            index_before="_".join(indexes[:-1])

        index_list_after=[]
        for post_indexes in index_list:
            if post_indexes.startswith(index) and post_indexes!=index and len(indexes)+1==len(post_indexes.split("_")):
                index_list_after.append(post_indexes)
        path_list.append([index_before,index,index_list_after])
    
    map_path=""
    for line in path_list:
        map_path=map_path+str(line) + '\n'
    data.map_path=map_path[:-1]
    data.save()

    return True 