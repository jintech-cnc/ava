from django.contrib import admin
from .models import Client, Order, OrderItem, Requisition, RequisitionItem


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('nom', 'email', 'telephone')
    search_fields = ('nom', 'email')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'entrepot', 'statut', 'cree_le')
    list_filter = ('statut', 'entrepot')
    inlines = [OrderItemInline]


class RequisitionItemInline(admin.TabularInline):
    model = RequisitionItem
    extra = 1


@admin.register(Requisition)
class RequisitionAdmin(admin.ModelAdmin):
    list_display = ('id', 'demandeur', 'service', 'statut', 'cree_le')
    list_filter = ('statut',)
    inlines = [RequisitionItemInline]
