from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.db.models import Count
from django.http.request import HttpRequest
from django.utils.html import format_html,urlencode
from django.contrib.contenttypes.admin import GenericTabularInline
from django.urls import reverse
from . import models
from tags.models import TaggedItem

class InventoryFilter(admin.SimpleListFilter):
    title='inventory'
    parameter_name='inventory'

    def lookups(self, request, model_admin) :
        return [
            ('<10','Low')
        ]
    def queryset(self, request, queryset: QuerySet) :
        if self.value() == '<10':
            return queryset.filter(inventory__lt=10)

class TagInline(GenericTabularInline):
    autocomplete_fields=['tag']
    model=TaggedItem


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    actions = ['clear_inventory']
    autocomplete_fields=['collection']
    inlines=[TagInline]
    prepopulated_fields={
        'slug':['title']
    }
    list_display=['title','unit_price','inventory_status','collection_title']
    list_editable=['unit_price']
    list_filter=['collection','last_update',InventoryFilter]
    list_per_page=10
    list_select_related=['collection']
    search_fields=['title']

    def collection_title(self,product):
        return product.collection.title

    @admin.display(ordering='inventory')
    def inventory_status(self,product):
        if product.inventory < 10:
            return "Low"
        return 'Ok'
    
    @admin.action(description='Clear inventory')
    def clear_inventory(self,request , queryset):
        updated_count=queryset.update(inventory=0)
        self.message_user(
            request,
            f'{updated_count} products were successfully updated.'
        )
@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_per_page=10
    list_display=['first_name','last_name','membership','orders']
    list_editable=['membership']
    ordering=['first_name','last_name']
    search_fields=['first_name__istartswith','last_name__istartswith']

    # @admin.display(ordering='orders_count')
    def orders(self,customer):
        url=(
            reverse('admin:store_order_changelist')
            + '?'
            + urlencode({
                'customer_id':str(customer.id)
            })
        )
        return format_html('<a href="{}">{}{}<a/>',url,customer.orders,' Orders')
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            orders=Count('order')
        )
    
class OrderItemInline(admin.TabularInline):
    autocomplete_fields=['product']
    model=models.OrderItem
    min_num=1
    extra=0
    max_num=10

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display=['id','placed_at','customer']
    inlines=[OrderItemInline]
    autocomplete_fields=['customer']

@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    autocomplete_fields=['featured_product']
    list_display=['id','title','products_count']
    search_fields=['title']
    
    @admin.display(ordering=['products_count'])
    def products_count(self,collection):
        url=(
            reverse('admin:store_product_changelist') 
            + '?'
            + urlencode({
                'collection_id':str(collection.id)
            })
            )
        
        return format_html('<a href="{}">{} {}<a/>',url,collection.products_count,' Products')
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            products_count=Count('products')
        )
    





