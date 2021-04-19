'''
用户账户相关功能:注册,短信,登录,注销
'''
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from web.forms.account import RegisterModelForm,SendSmsForm


def register(request):
    '''注册'''
    if request.method == 'GET':
        form = RegisterModelForm()
        return render(request, 'web/register.html', {'form': form})

    form = RegisterModelForm(data=request.POST)
    if form.is_valid():
        #验证通过,写入数据库,form.save()比较简单,自动剔除表单中有但是数据库中没有的字段
        #密码要是密文
        form.save()
        return JsonResponse({'status':True, 'data':"/login/"})

    return JsonResponse({'status':False, 'error': form.errors})

def send_sms(request):
    #发送短信
    mobile_phone = request.GET.get('mobile_phone')
    tpl = request.GET.get('tpl') #register/login
    form = SendSmsForm(request, data=request.GET)
    #只是校验手机号:不能为空,格式是否正确
    if form.is_valid():
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'error': form.errors})













