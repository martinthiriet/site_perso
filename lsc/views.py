import json
from django.shortcuts import render,HttpResponse, redirect
from django.http import JsonResponse
from .models import Camdata as cd

# Create your views here.
def camplot(request):
    id=request.GET.get('id')
    data=cd.objects.filter(id=id)
    if len(data)!=1:
        return HttpResponse("Error: Something went wrong: not a single matching brainmap", status=400)
    data=data[0]
# <#a>1<a#><#t>Title<t#><#d>Description<d#><#id><id#>
    val_list=[]
    title_list=[]
    description_list=[]
    link_list=[]
    for line in data.data.split("\n"):
        val_list.append(float(line.split('<#a>')[1].split('<a#>')[0].replace(',','.')))
        title_list.append(line.split('<#t>')[1].split('<t#>')[0])
        description_list.append(line.split('<#d>')[1].split('<d#>')[0])
        link=line.split('<#id>')[1].split('<id#>')[0]
        if link=='':
            link=str(id)
        link_list.append('?id='+link)
        
    descriptions = "<#>".join(description_list)
    titles = "<#>".join(title_list)

    context = {
        'camtitle':data.title,
        'val_list': json.dumps(val_list),
        'title_list': json.dumps(titles, ensure_ascii=False),
        'description_list': json.dumps(descriptions, ensure_ascii=False),
        'link_list': json.dumps(str(link_list).replace("'",'')),
        'unit': json.dumps(data.unit, ensure_ascii=False),
        'id':id
    }

    return render(request, "camplot.html", context)

def camlist(request):
    data=cd.objects.all()
    return render(request, "camlist.html", {'data':data})


def sources(request):
    id=request.GET.get('id')
    data=cd.objects.filter(id=id)
    if len(data)!=1:
        return HttpResponse("Error: Something went wrong: not a single matching brainmap", status=400)
    data=data[0]
    return render(request, "sources.html", {'sources':data.sources,'title':data.title,'id':id})
