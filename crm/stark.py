#!usr/bin/env python
# -*- coding:utf-8 -*-
from django.forms import ModelForm
from django.shortcuts import render,HttpResponse,redirect
from django.utils.safestring import mark_safe
from stark.service import v1
from crm import models
from django.conf.urls import url
from django.urls import reverse
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
    list_display = ['name','username','email','depart']
    edit_link = ['name']
    comb_filter = [
        v1.FilterOption('depart',text_func_name=lambda x:str(x),val_text_func_name=lambda x:x.code)
        # v1.FilterOption('depart')
    ]

    search_fields = ['name__contains','email__contains']
    show_search_form = True

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
            return '性别'
        return obj.get_gender_display()

    def display_education(self,obj=None,is_header=False):
        if is_header:
            return '学历'
        return obj.get_education_display()

    def display_course(self,obj=None,is_header=False):
        if is_header:
            return '咨询课程'
        course_list = obj.course.all()
        html = []
        # self.request.GET
        # self._query_param_key
        # 构造QueryDict
        # urlencode()
        for item in course_list:
            temp = "<a style='display:inline-block;padding:3px 5px;border:1px solid blue;margin:2px;' href='/stark/crm/customer/%s/%s/dc/'>%s X</a>" %(obj.pk,item.pk,item.name)
            html.append(temp)

        return mark_safe("".join(html))

    def display_status(self,obj=None,is_header=False):
        if is_header:
            return '状态'
        return obj.get_status_display()

    def record(self,obj=None,is_header=False):
        if is_header:
            return '跟进记录'
        # /stark/crm/consultrecord/?customer=11
        return mark_safe("<a href='/stark/crm/consultrecord/?customer=%s'>查看跟进记录</a>" %(obj.pk,))

    list_display = ['qq','name',display_gender,display_education,display_course,display_status,record]
    edit_link = ['qq']

    def delete_course(self,request,customer_id,course_id):
        """
        删除当前用户感兴趣的课程
        :param request:
        :param customer_id:
        :param course_id:
        :return:
        """
        customer_obj = self.model_class.objects.filter(pk=customer_id).first()
        customer_obj.course.remove(course_id)
        # 跳转回去时，要保留原来的搜索条件
        return redirect(self.get_list_url())

    def extra_url(self):
        app_model_name = (self.model_class._meta.app_label, self.model_class._meta.model_name,)
        patterns = [
            url(r'^(\d+)/(\d+)/dc/$', self.wrap(self.delete_course), name="%s_%s_dc" %app_model_name),
        ]
        return patterns
    search_fields = ['qq','name']
    show_search_form = True
    comb_filter = {
        v1.FilterOption('gender',is_choice=True),
        v1.FilterOption('status',is_choice=True),

    }
v1.site.register(models.Customer,CustomerConfig)


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

    def extra_url(self):
        app_model_name = (self.model_class._meta.app_label, self.model_class._meta.model_name,)
        url_list = [
            url(r'^(\d+)/score_list/$', self.wrap(self.score_list), name="%s_%s_score_list" % app_model_name),
        ]
        return url_list

    def score_list(self,request,record_id):
        """
        :param request:
        :param record_id:老师上课记录ID
        :return:
        """

        if request.method == "GET":
            # 方式一
            # study_record_list = models.StudyRecord.objects.filter(course_record_id=record_id)
            # score_choices = models.StudyRecord.score_choices
            # return render(request,'score_list.html',{'study_record_list':study_record_list,'score_choices':score_choices})
            # 方式二
            from django.forms import Form
            from django.forms import fields
            from django.forms import widgets

            # class TempForm(Form):
            #     score = fields.ChoiceField(choices=models.StudyRecord.score_choices)
            #     homework_note = fields.CharField(widget=widgets.Textarea())
            data = []
            study_record_list = models.StudyRecord.objects.filter(course_record_id=record_id)
            for obj in study_record_list:
                # obj是对象
                TempForm = type('TempForm',(Form,),{
                    'score_%s' %obj.pk:fields.ChoiceField(choices=models.StudyRecord.score_choices),
                    'homework_note_%s' %obj.pk: fields.CharField(widget=widgets.Textarea())
                })
                data.append({'obj':obj,'form':TempForm(initial={'score_%s' %obj.pk:obj.score,'homework_note_%s' %obj.pk:obj.homework_note})})
            return render(request, 'stark/score_list.html',
                          {'data': data})
        else:
            data_dict = {}
            for key,value in request.POST.items():
                if key == "csrfmiddlewaretoken":
                    continue
                name,nid = key.rsplit('_',1)
                if nid in data_dict:
                    data_dict[nid][name] = value
                else:
                    data_dict[nid] = {name:value}

            for nid,update_dict in data_dict.items():
                models.StudyRecord.objects.filter(id=nid).update(**update_dict)

            return redirect(request.path_info)

    def kaoqin(self,obj=None,is_header=False):
        if is_header:
            return '考勤'

        return mark_safe("<a href='/stark/crm/studyrecord/?course_record=%s'>查看考勤记录</a>" %obj.pk)

    def display_score_list(self,obj=None,is_header=False):
        if is_header:
            return '成绩录入'
        from django.urls import reverse
        rurl = reverse("stark:crm_courserecord_score_list",args=(obj.pk,))
        return mark_safe("<a href='%s'>成绩录入</a>" %rurl)

    list_display = ['class_obj','day_num',kaoqin,display_score_list]

    show_actions = True
v1.site.register(models.CourseRecord,CourseRecordConfig)

# 学习记录
class StudyRecordConfig(v1.StarkConfig):
    def display_record(self,obj=None,is_header=None):
        if is_header:
            return '出勤'
        return obj.get_record_display()

    def action_checked(self, request):
        pass

    action_checked.short_desc = "已签到"

    def action_vacate(self, request):
        pass

    action_vacate.short_desc = "请假"

    def action_late(self, request):
        pass

    action_late.short_desc = "迟到"

    def action_noshow(self, request):
        pk_list = request.POST.getlist('pk')
        models.StudyRecord.objects.filter(id__in=pk_list).update(record='noshow')

    action_noshow.short_desc = "缺勤"

    def action_leave_early(self, request):
        pass

    action_leave_early.short_desc = "早退"

    actions = [action_checked, action_vacate, action_late, action_noshow, action_leave_early]


    show_actions = True
    show_add_btn = False
    edit_link = ['course_record']
    list_display = ['course_record', 'student', display_record]
    comb_filter = [
        v1.FilterOption('course_record')
    ]
v1.site.register(models.StudyRecord,StudyRecordConfig)



class StudentConfig(v1.StarkConfig):
    list_display = ['customer','class_list','emergency_contract']
v1.site.register(models.Student,StudentConfig)




