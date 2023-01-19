import json

from django.core.paginator import Paginator

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView

from ads.models import Ad
from users.models import User

PAGE_NUMBER = 4


class AdDetailView(DetailView):
    model = Ad

    def get(self, request, *args, **kwargs):
        ad = self.get_object()
        return JsonResponse(
            {
                "id": ad.id,
                "name": ad.name,
                "author": ad.author.first_name,
                "category": ad.category.name,
                "price": ad.price,
                "description": ad.description,
                "is_published": ad.is_published,
            },
            safe=False
        )


class AdListView(ListView):
    model = Ad
    queryset = Ad.objects.all()

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)

        paginator = Paginator(self.object_list, PAGE_NUMBER)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return JsonResponse(
            {"total": page_obj.paginator.count,
             "num_pages": page_obj.paginator.num_pages,
             "items": [{"id": ad.id,
                        "name": ad.name,
                        "author_id": ad.author_id,
                        "author": ad.author.first_name,
                        "price": ad.price,
                        "description": ad.description,
                        "is_published": ad.is_published,
                        "category_id": ad.category_id,
                        "image": ad.image.url if ad.image else None} for ad in page_obj]}
        )


@method_decorator(csrf_exempt, name="dispatch")
class AdCreateView(CreateView):
    model = Ad
    fields = "__all__"

    def post(self, request, **kwargs):
        data = json.loads(request.body)

        author = get_object_or_404(User, username=data["username"])
        category = get_object_or_404(User, name=data["category"])

        ad = Ad.objects.create(
            name=data["name"],
            author=author,
            price=data["price"],
            description=data["description"],
            is_published=data["is_published"],
            category=category
        )
        return JsonResponse(
            {
                "id": ad.id,
                "name": ad.name,
                "author": ad.author.username,
                "category": ad.category.name,
                "price": ad.price,
                "description": ad.description,
                "is_published": ad.is_published,
            },
            safe=False
        )


@method_decorator(csrf_exempt, name="dispatch")
class AdUpdateView(UpdateView):
    model = Ad
    fields = "__all__"

    def put(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        data = json.loads(request.body)

        self.object.author = get_object_or_404(User, username=data["username"])
        self.object.category = get_object_or_404(User, name=data["category"])
        self.object.name = data["name"]
        self.object.price = data["price"]
        self.object.description = data["description"]
        self.object.is_published = data["is_published"]

        return JsonResponse(
            {
                "id": self.object.id,
                "name": self.object.name,
                "author": self.object.author.username,
                "category": self.object.category.name,
                "price": self.object.price,
                "description": self.object.description,
                "is_published": self.object.is_published,
            },
            safe=False
        )

    @method_decorator(csrf_exempt, name="dispatch")
    class AdDeleteView(DeleteView):
        model = Ad
        success_url = "/"

        def delete(self, request, *args, **kwargs):
            ad = self.get_object()
            ad_id = ad.id
            super().delete(request, *args, **kwargs)
            return JsonResponse({"id": ad_id}, safe=False)
