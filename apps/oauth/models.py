from django.db import models
from utils.models import BaseModel
# Create your models here.

class QQUser(BaseModel):

    user = models.ForeignKey("user.User",on_delete=models.CASCADE,verbose_name='用户')
    openid = models.CharField(db_index=True,max_length=40,verbose_name='openid') #db_index 创建索引

    class Meta:
        db_table = 'tb_oauth_qq'
        verbose_name = 'QQ登录用户数据'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user.username