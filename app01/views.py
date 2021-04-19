from django.core.validators import RegexValidator
from django.shortcuts import render
from django import forms
# Create your views here.
from app01 import models


class RegisterModelForm(forms.ModelForm):
    mobile_phone = forms.CharField(
        label='手机号',
        validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', '手机号格式错误'), ])
    password = forms.CharField(
        label='密码',
        widget=forms.PasswordInput())
    confirm_password = forms.CharField(
        label="确认密码",
        widget=forms.PasswordInput())
    code = forms.CharField(
        label='验证码',
        widget=forms.TextInput()
    )

    class Meta:
        model = models.UserInfo
        # fields = '__all__'#默认展示所有,依次是models里的字段,modelform里的字段
        # 页面展示字段按照列表中的顺序
        fields = ['username', 'email', 'password', 'confirm_password', 'mobile_phone', 'code']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            # name 拿的是 mobile_phone password等字段
            # field拿的是forms.CharField()中的对象
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = '请输入%s' % field.label


def register(request):
    form = RegisterModelForm()
    return render(request, 'app01/register.html', {'form': form})
