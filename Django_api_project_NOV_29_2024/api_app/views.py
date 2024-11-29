from rest_framework import generics
from .models import Item
from .serializers import ItemSerializer

# List all items or create a new item
class ItemListCreate(generics.ListCreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

# Retrieve, update or delete an item
class ItemRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

# Partial update for an item (PATCH)
class ItemPartialUpdate(generics.UpdateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
