from django.shortcuts import render,redirect

HOST_LIST = []

for i in range(1,924):
    HOST_LIST.append("c%s.com" %i )
from utils.pager import Pagination
def hosts(request):

    pager_obj = Pagination(request.GET.get('page',1),len(HOST_LIST),request.path_info,request.GET)
    host_list = HOST_LIST[pager_obj.start:pager_obj.end]
    # host_list = models.Host.objects.all()[pager_obj.start:pager_obj.end]

    # condition_dict = {}
    # source=2&status=2&gender=2&consultant=1&page=1
    # for k,v in request.GET.items():
    #     if k == 'page':
    #         continue
    #     condition_dict[k] = v
    # host_list = models.Host.objects.filter(**condition_dict)[pager_obj.start:pager_obj.end]

    html = pager_obj.page_html()


    list_condition = request.GET.urlencode()
    # print(list_condition)
    from django.http import QueryDict # request.GET
    # params = QueryDict(mutable=True)

    # request.GET是一个QueryDict类型，
    # 默认不可修改，request.GET._mutable = True
    # request.GET.urlencode() 用于讲k,v构造成URL格式字符串
    # request.GET['page'] = 666

    # _list_filter=page%3D5%26id__gt%3D4
    params = QueryDict(mutable=True)
    params['_list_filter'] = request.GET.urlencode()
    list_condition = params.urlencode()

    return render(request,'hosts.html',{'host_list':host_list,"page_html":html,'list_condition':list_condition})

USER_LIST = []

for i in range(1,302):
    USER_LIST.append("bb%s" %i )

def users(request):
    pager_obj = Pagination(request.GET.get('page', 1), len(USER_LIST),request.path_info,request.GET)
    user_list = USER_LIST[pager_obj.start:pager_obj.end]
    html = pager_obj.page_html()
    return render(request, 'users.html', {'user_list': user_list, "page_html": html})


def edit_host(request,pk):
    if request.method == "GET":
        return render(request,'edit_host.html')
    else:
        # 修改成功 /hosts/?page=5&id__gt=4
        url = "/hosts/?%s" %(request.GET.get('_list_filter'))
        return redirect(url)






















