from django import forms
from app01 import models


class RegForm(forms.Form):
    username = forms.CharField(max_length=8,min_length=3,label='用户名',error_messages={
                                'max_length':'用户名最长8位',
                                'min_length':'用户名最少3位',
                                'required':'用户名不能为空',
    },widget=forms.TextInput(attrs={'class':'form-control'}))
    password = forms.CharField(max_length=8, min_length=3, label='密码', error_messages={
        'max_length': '密码最长8位',
        'min_length': '密码最少3位',
        'required': '密码不能为空',
    }, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(max_length=8, min_length=3, label='确认密码', error_messages={
        'max_length': '确认密码最长8位',
        'min_length': '确认密码最少3位',
        'required': '确认密码不能为空',
    }, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='邮箱',error_messages={
                            'invalid':'邮箱格式错误',
                            'required':'邮箱不能为空'
    },widget=forms.EmailInput(attrs={"class":'form-control'}))

    # 局部钩子 校验用户名是否已存在
    def clean_username(self):
        username = self.cleaned_data.get('username')
        user = models.UserInfo.objects.filter(username=username).first()
        if user:
            self.add_error('username','用户名已存在')
        else:
            return username

    # 全局钩子 校验密码是否一致
    def clean(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if not password == confirm_password:
            self.add_error('confirm_password','两次密码不一致')
        else:
            return self.cleaned_data
