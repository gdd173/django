import random

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from utils.tencent.sms import send_sms_single
from utils.encrypt import md5
from web import models
from django_redis import get_redis_connection

class RegisterModelForm(forms.ModelForm):
    mobile_phone = forms.CharField(
        label= '手机号',
        validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', '手机号格式错误'),])
    password = forms.CharField(
        label= '密码',
        min_length=8,
        max_length=64,
        error_messages={
            'min_length':"密码长度不能小于8个字符",
            'max_length':"密码长度不能大于64个字符"
        },
        widget=forms.PasswordInput())
    confirm_password = forms.CharField(
        label="确认密码",
        min_length=8,
        max_length=64,
        error_messages={
            'min_length': "密码长度不能小于8个字符",
            'max_length': "密码长度不能大于64个字符"
        },
        widget=forms.PasswordInput())
    code = forms.CharField(
        label='验证码',
        widget= forms.TextInput()
    )
    class Meta:
        model = models.UserInfo
        # fields = '__all__'#默认展示所有,依次是models里的字段,modelform里的字段
        #页面展示字段按照列表中的顺序
        fields = ['username', 'email', 'password', 'confirm_password','mobile_phone', 'code']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            #name 拿的是 mobile_phone password等字段
            #field拿的是forms.CharField()中的对象
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = '请输入%s'% field.label

    #用户名校验
    def clean_username(self):
        username = self.cleaned_data['username']

        exists = models.UserInfo.objects.filter(username=username)
        if exists:
            raise ValidationError('用户已存在')
            # self.add_error('username','用户名已存在')
        return username
    #邮箱校验
    def clean_email(self):
        email = self.cleaned_data['email']

        exists = models.UserInfo.objects.filter(email=email)
        if exists:
            raise ValidationError('邮箱已存在')
        return email

    def clean_password(self):
        pwd = self.cleaned_data['password']
        #加密&返回
        return md5(pwd)

    def clean_confirm_password(self):
        pwd = self.cleaned_data['password']
        confirm_pwd = md5(self.cleaned_data['confirm_password'])
        if pwd != confirm_pwd:
            raise ValidationError("两次密码不一致")
        return confirm_pwd

    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data['mobile_phone']
        exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone)
        if exists:
            raise ValidationError("手机号已注册")
        return mobile_phone

    def clean_code(self):
        code = self.cleaned_data["code"]#用户输入的验证码
        mobile_phone = self.cleaned_data['mobile_phone']
        if not mobile_phone:
            return code

        conn = get_redis_connection()
        redis_code = conn.get(mobile_phone) #根据手机号获取的存放在redis中的验证码
        if not redis_code:
            raise ValidationError("验证码失效或未发送,请重新发送")

        redis_str_code = redis_code.decode("utf-8")#redis中的验证码是byte形式

        if code.strip() != redis_str_code: #有可能用户输入的时候两边带空格
            raise ValidationError('验证码错误,请重新发送')
        return code

#只做表单验证,和数据库无关,所以继承自forms.Form
class SendSmsForm(forms.Form):
    mobile_phone = forms.CharField(label='手机号', validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', '手机号格式错误'),])
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_mobile_phone(self):
        # 手机号校验的钩子
        mobile_phone = self.cleaned_data['mobile_phone']

        #判断短信模板是否有问题
        tpl = self.request.GET.get('tpl')
        template_id = settings.TENCENT_SMS_TEMPLATE.get(tpl)
        if not template_id:
            raise ValidationError('短信模板错误')

        #校验数据库中是否已有手机号
        exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        if exists:
            raise ValidationError('手机号已存在')

        #发短信
        code = random.randrange(1000,9999)
        sms = send_sms_single(mobile_phone, template_id, [code,])
        if sms['result'] != 0:
            raise ValidationError('短信发送失败, {}'.format(sms['errmsg']))

        #验证码写入redis(django_redis)
        conn = get_redis_connection()
        conn.set(mobile_phone, code, ex = 60)
        return mobile_phone




