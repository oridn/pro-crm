#!usr/bin/env python
# -*- coding:utf-8 -*-
from django.forms import ModelForm
from django.shortcuts import render,HttpResponse,redirect
from django.utils.safestring import mark_safe
from stark.service import v1
from crm import models
from django.conf.urls import url

class DepartmentConfig(v1.StarkConfig):
    list_display = ["title","code"]
    edit_link = ["title"]   #自定制链接，指定字段可编辑

    # 重写get_list_display(),因为父类有这个方法，如果这里不写就会继承父类的，写了就优先执行自己的
    def get_list_display(self):
        result = []

        result.extend(self.list_display)
        result.insert(0,v1.StarkConfig.checkbox)
        result.append(v1.StarkConfig.edit)
        result.append(v1.StarkConfig.delete)

        return result

v1.site.register(models.Department,DepartmentConfig)

class UserInfoConfig(v1.StarkConfig):
    edit_link = ["name"]

    def depart_dispaly(self,obj=None,is_header=False):
        if is_header:
            return "所属部门"
        return obj.depart.title

    def get_model_form_class(self):
        '''自定义ModelForm'''
        class MyModelForm(ModelForm):
            class Meta:
                model = models.UserInfo
                fields = "__all__"
                error_messages = {
                    "name":{"required":"姓名不能为空"},
                    "username":{"required":"用户名不能为空"},
                    "password":{"required":"密码不能为空"},
                    "email":{"required":"邮箱不能为空","invalid":"邮箱格式不正确"},
                    "depart":{"required":"用户名不能不选",},
                }
        return MyModelForm

    list_display = ["name","username","email",depart_dispaly]

    # comb_filter = [
    #     v1.FilterOption("depart",val_func_name=lambda x: x.code,),
    # ]  #分组搜索
    #
    # def delete_view(self, request,nid, *args, **kwargs):
    #     '''重写视图函数'''
    #     if request.method=="GET":
    #         return render(request,"stark/delete_view.html",{"quxiao_url":self.get_list_url()})
    #     else:
    #         self.model_class.objects.filter(pk=nid).delete()
    #         return redirect(self.get_list_url())

v1.site.register(models.UserInfo,UserInfoConfig)

class CourseConfig(v1.StarkConfig):
    list_display = ["name"]
    edit_link = ["name"]
    show_actions =True  #显示actions

    def mutil_delete(self,request):
        if request.method =="POST":
            pk_list = request.POST.getlist("pk")
            print(pk_list,"000")
            self.model_class.objects.filter(id__in=pk_list).delete()

    mutil_delete.short_desc = "批量删除"
    def init_func(self):
        pass
    init_func.short_desc = "初始化"
    actions = [mutil_delete,init_func]   #actios操作


    search_fields = ["name__contains"]   #按照name搜索
    show_search_form = True

v1.site.register(models.Course,CourseConfig)

class SchoolConfig(v1.StarkConfig):
    list_display = ["title"]
    edit_link = ["title"]

v1.site.register(models.School,SchoolConfig)

class ClassListConfig(v1.StarkConfig):
    def teachers_display(self,obj=None,is_header=False):
        if is_header:
            return "任教老师"
        user_list = obj.teachers.all()
        html = []
        for i in user_list:
            html.append(i.name)
        return ','.join(html)

    def display_graduate_date(self,obj=None,is_header=False):
        if is_header:
            return "结业日期"
        return '' if not obj.graduate_date else obj.graduate_date

    def  display_memo(self,obj=None,is_header=False):
        if is_header:
            return "说明"
        return '' if not obj.memo else obj.memo

    def course_semester(self,obj=None,is_header=False):
        if is_header:
            return "课程（班级）"
        return "%s(%s期)"%(obj.course,obj.semester)

    #列举这个班级的人数
    def num(self,obj=None,is_header=False):
        if is_header:
            return "人数"
        print(obj.student_set.all().count())
        return obj.student_set.all().count()
    list_display = ["school",course_semester,num,"price","start_date",display_graduate_date,teachers_display,"tutor"]
    edit_link = ["school"]
v1.site.register(models.ClassList,ClassListConfig)

class CustomerConfig(v1.StarkConfig):
    def display_gender(self,obj=None,is_header=False):
        if is_header:
            return "性别"
        return obj.get_gender_display()
    def display_education(self,obj=None,is_header=False):
        if is_header:
            return "学历"
        return obj.get_education_display()

    def display_status(self, obj=None, is_header=False):
        if is_header:
            return '状态'
        return obj.get_status_display()
    def recode(self, obj=None, is_header=False):
        if is_header:
            return "跟进记录"
        return mark_safe("<a href='/index/crm/consultrecord/?customer=%s'>查看跟进记录</a>" %(obj.pk,))

    def display_course(self,obj=None, is_header=False):
        if is_header:
            return "咨询课程"
        course_list = obj.course.all()
        html = []
        for item in course_list:
            temp = "<a style='display:inline-block;padding:3px 5px;border:1px solid blue;margin:2px;' href='/stark/crm/customer/%s/%s/dc/'>%s X</a>" %(obj.pk,item.pk,item.name)
            html.append(temp)
        return mark_safe("".join(html))
    def extra_urls(self):
        # 由于没有路径，我们可以额外的增加一个路径,重新走一个delete_course视图
        app_model_name = (self.model_class._meta.app_label, self.model_class._meta.model_name)
        urlpatterns =[
            url(r'^(\d+)/(\d+)/dc/$', self.wrap(self.delete_course), name="%s_%s_delete" % app_model_name)
        ]
        return urlpatterns
    def delete_course(self, request,customer_id,course_id):
        '''
        删除当前用户感兴趣的课程
        :param request:
        :param customer_id:
        :param course_id:
        :return:
        '''
        customer_obj = self.model_class.objects.filter(pk=customer_id).first()
        customer_obj.course.remove(course_id)
        return redirect(self.get_list_url())

    list_display = ["qq","name","graduation_school",display_course,display_gender,display_status,display_education,recode]
    edit_link = ["name","graduation_school"]
    search_fields = ["name__contains"]
    show_search_form = True
    show_actions = True
    # 组合搜索
    comb_filter = [
        v1.FilterOption("gender",is_choice=True),
        v1.FilterOption('status',is_choice=True),
    ]
v1.site.register(models.Customer, CustomerConfig)
class ConsultRecordConfig(v1.StarkConfig):
    def customer_display(self,obj=None,is_header=False):
        if is_header:
            return "所咨询客户"
        return obj.customer.name
    list_display = [customer_display,"consultant","date","note"]
    comb_filter = [
        v1.FilterOption("customer"),
    ]   #组合搜索默认不显示，但是却又筛选的功能

    def change_views(self, request,*args, **kwargs):
        customer = request.GET.get('customer')
        # session中获取当前用户ID
        current_login_user_id = 6
        ct = models.Customer.objects.filter(consultant=current_login_user_id, id=customer).count()
        if not ct:
            return HttpResponse('无权访问.')
        return super(ConsultRecordConfig,self).change_view(request, *args, **kwargs)
v1.site.register(models.ConsultRecord,ConsultRecordConfig)

#  上课记录
class CourseRecordConfig(v1.StarkConfig):
    list_display = ['class_obj','day_num']
    edit_link = ['class_obj']
v1.site.register(models.CourseRecord,CourseRecordConfig)





