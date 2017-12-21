from django.shortcuts import HttpResponse,render,redirect
from django.utils.safestring import mark_safe
from django.conf.urls import url
from stark.service import v1
from app01 import models
from django.forms import ModelForm
class UserInfoModelForm(ModelForm):
    class Meta:
        model = models.UserInfo
        fields = '__all__'
        error_messages = {
            'name':{
                'required':'用户名不能为空'
            }
        }

class UserInfoConfig(v1.StarkConfig):

    list_display = ['id','name','email','pwd']

    show_add_btn = True

    model_form_class = UserInfoModelForm

    show_search_form = True
    search_fields = ['name__contains', 'email__contains']


    show_actions = True

    def multi_del(self,request):
        pk_list = request.POST.getlist('pk')
        self.model_class.objects.filter(id__in=pk_list).delete()
        # return HttpResponse('删除成功')
        return redirect("http://www.baidu.com")
    multi_del.short_desc = "批量删除"

    def multi_init(self,request):
        pk_list = request.POST.getlist('pk')
        #self.model_class.objects.filter(id__in=pk_list).delete()
        # return HttpResponse('删除成功')
        #return redirect("http://www.baidu.com")
    multi_init.short_desc = "初始化"

    actions = [multi_del, multi_init]


v1.site.register(models.UserInfo,UserInfoConfig) # UserInfoConfig(UserInfo,)



















class RoleConfig(v1.StarkConfig):

    list_display = ['id','name']
v1.site.register(models.Role,RoleConfig) # StarkConfig(Role)



class HostModelForm(ModelForm):
    class Meta:
        model = models.Host
        fields = ['id','hostname','ip','port']
        error_messages = {
            'hostname':{
                'required':'主机名不能为空',
            },
            'ip':{
                'required': 'IP不能为空',
                'invalid': 'IP格式错误',
            }

        }



class HostConfig(v1.StarkConfig):
    def ip_port(self,obj=None,is_header=False):
        if is_header:
            return '自定义列'
        return "%s:%s" %(obj.ip,obj.port,)

    list_display = ['id','hostname','ip','port',ip_port]
    # get_list_display

    show_add_btn = True
    # get_show_add_btn

    model_form_class = HostModelForm
    # get_model_form_class


    def extra_url(self):
        urls = [
            url('^report/$',self.report_view)
        ]
        return urls

    def report_view(self,request):
        return HttpResponse('自定义报表')

    def delete_view(self,request,nid,*args,**kwargs):
        if request.method == "GET":
            return render(request,'my_delete.html')
        else:
            self.model_class.objects.filter(pk=nid).delete()
            return redirect(self.get_list_url())


v1.site.register(models.Host,HostConfig)
