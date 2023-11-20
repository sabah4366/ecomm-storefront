from rest_framework import serializers
from . models import Product,Collection
from decimal import Decimal

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Collection
        fields=['id','title','products_count']
    products_count=serializers.IntegerField(read_only=True)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields=['id','title','unit_price','description','slug','inventory','price_with_tax','collection']
    price_with_tax=serializers.SerializerMethodField(method_name='calculate_tax')
    #1st this is for title of the collection
    # collection=serializers.StringRelatedField()
    #2nd this is for the nested serializer
    # collection=CollectionSerializer()
    #3rd hyperlinked connection
    collection=serializers.PrimaryKeyRelatedField(
        queryset=Collection.objects.all(),
        
    )


    def calculate_tax(self,product:Product):
        return product.unit_price * Decimal(1.1)