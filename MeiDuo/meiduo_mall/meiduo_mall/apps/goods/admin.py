# from django.contrib import admin
# from . import models
# # Register your models here.
# admin.site.register(models.GoodsCategory)
# admin.site.register(models.GoodsChannel)
# admin.site.register(models.Goods)
# admin.site.register(models.Brand)
# admin.site.register(models.GoodsSpecification)
# admin.site.register(models.SpecificationOption)
# admin.site.register(models.SKU)
# admin.site.register(models.SKUSpecification)
# admin.site.register(models.SKUImage)
from django.contrib import admin

# Register your models here.

from goods import models

#保存商品，修改了商品需要生成静态文件
class SKUAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(obj.id)

#保存商品，修改了商品需要生成静态文件
class SKUSpecificationAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(obj.sku.id)

    def delete_model(self, request, obj):
        sku_id = obj.sku.id
        obj.delete()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(sku_id)

#保存商品，修改了商品需要生成静态文件
class SKUImageAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(obj.sku.id)

        # 设置SKU默认图片
        sku = obj.sku
        if not sku.default_image_url:
            sku.default_image_url = obj.image.url
            sku.save()

    def delete_model(self, request, obj):
        sku_id = obj.sku.id
        obj.delete()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(sku_id)




#商品分类列表被修改需要生成静态文件
class GoodsCategoryAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()
        from celery_tasks.html.tasks import generate_static_list_search_html
        generate_static_list_search_html.delay()



    def delete_model(self, request, obj):
        obj.delete()
        from celery_tasks.html.tasks import generate_static_list_search_html
        generate_static_list_search_html.delay()




admin.site.register(models.GoodsCategory,GoodsCategoryAdmin)
admin.site.register(models.GoodsChannel)
admin.site.register(models.Goods)
admin.site.register(models.Brand)
admin.site.register(models.GoodsSpecification)
admin.site.register(models.SpecificationOption)
admin.site.register(models.SKU, SKUAdmin)
admin.site.register(models.SKUSpecification, SKUSpecificationAdmin)
admin.site.register(models.SKUImage, SKUImageAdmin)
