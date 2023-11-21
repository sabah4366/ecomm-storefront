from django.shortcuts import render,get_object_or_404
from django.db.models import Count
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet
from . models import Product,Collection,OrderItem,Review
from . serializers import ProductSerializer,CollectionSerializer,ReviewSerializer


class ProductViewSet(ModelViewSet):
    serializer_class=ProductSerializer

    def get_queryset(self):
        queryset=Product.objects.all()
        collection_id=self.request.query_params.get('collection_id')
        if collection_id is not None:
            queryset=Product.objects.filter(collection_id=collection_id)
        return queryset

    def get_serializer_context(self):
        return {'request':self.request  }
    
    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error':'Product cannot be deleted because it is associated with an order item.'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)
    
#i want  edit destroyy method 
class CollectionViewSet(ModelViewSet):
    serializer_class=CollectionSerializer
    queryset=Collection.objects.annotate(products_count=Count('products')).all()

    def destroy(self, request, *args, **kwargs):

        if Collection.objects.filter(id=kwargs['pk']).count() > 0:
            return Response({'error':'Collection cannot be deleted because it includes one or more products.'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)
    
class ReviewViewSet(ModelViewSet):
    serializer_class=ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id':self.kwargs['product_pk']}
                        

    
