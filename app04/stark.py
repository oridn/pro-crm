from stark.service import v1
from . import models

class RoleConfig(v1.StarkConfig):
    list_display = ['id','title']
v1.site.register(models.Role,RoleConfig)

class DepartmentConfig(v1.StarkConfig):
    list_display = ['id','caption']
v1.site.register(models.Department,DepartmentConfig)

class UserInfoConfig(v1.StarkConfig):
    def display_gender(self,obj=None,is_header=False):
        if is_header:
            return '性别'

        # return obj.gender
        return obj.get_gender_display()

    def display_depart(self,obj=None,is_header=False):
        if is_header:
            return '部门'
        return obj.depart.caption

    def display_roles(self,obj=None,is_header=False):
        if is_header:
            return '角色'

        html = []
        role_list = obj.roles.all()
        for role in role_list:
            html.append(role.title)

        return ",".join(html)

    list_display = ['id','name','email',display_gender,display_depart,display_roles]

    comb_filter = [
        v1.FilterOption('gender',is_choice=True),
        v1.FilterOption('depart',condition={'id__gt':3}),
        v1.FilterOption('roles',True),
    ]
    # 是否显示搜索
    show_search_form = True
    search_fields = ['name__contains', 'email__contains']
    # 批量删除和初始化
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

v1.site.register(models.UserInfo,UserInfoConfig)
