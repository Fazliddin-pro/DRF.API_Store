from django.contrib.auth.models import User
from rest_framework import status
import pytest
from model_bakery import baker

from store.models import Collection, Product


@pytest.fixture
def create_collection(api_client):
    def do_create_collection(collection):
        return api_client.post("/store/collections/", collection)

    return do_create_collection


@pytest.mark.django_db
class TestCreateCollection:
    def test_if_user_is_anonymous_returns_401(self, create_collection):
        response = create_collection({"title": "My Collection"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, api_client, authenticate, create_collection):
        authenticate(is_staff=False)
        response = create_collection({"title": "My Collection"})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_returns_400(self, api_client, authenticate, create_collection):
        authenticate(is_staff=True)
        response = create_collection({"title": ""})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["title"] is not None

    def test_if_data_is_valid_returns_400(self, api_client, authenticate, create_collection):
        authenticate(is_staff=True)
        response = create_collection({"title": "My Collection"})

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["id"] > 0


@pytest.mark.django_db
class TestRetrieveCollection:
    def test_if_collection_exists_returns_200(self, api_client):
        collection = baker.make(Collection)

        response = api_client.get(f"/store/collections/{collection.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == collection.id
        assert response.data["title"] == collection.title

    def test_if_collection_does_not_exists_returns_404(self, api_client):
        response = api_client.get("/store/collections/1/")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_non_admin_user_is_restricted_to_get_only(self, api_client, authenticate):
        authenticate(is_staff=False)
        collection = baker.make(Collection)

        # Test GET method (allowed)
        response = api_client.get(f"/store/collections/{collection.id}/")
        assert response.status_code == status.HTTP_200_OK

        # Test POST method (forbidden)
        response = api_client.post("/store/collections/", {"title": "New Collection"})
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Test PUT method (forbidden)
        response = api_client.put(f"/store/collections/{collection.id}/", {"title": "Updated Collection"})
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Test DELETE method (forbidden)
        response = api_client.delete(f"/store/collections/{collection.id}/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_stuff(self, api_client, authenticate):
        authenticate(is_staff=True)
        collection = baker.make(Collection)

        # Test GET method (allowed)
        response = api_client.get(f"/store/collections/{collection.id}/")
        assert response.status_code == status.HTTP_200_OK

        # Test POST method (allowed)
        response = api_client.post("/store/collections/", {"title": "New Collection"})
        assert response.status_code == status.HTTP_201_CREATED

        # Test PUT method (allowed)
        response = api_client.put(f"/store/collections/{collection.id}/", {"title": "Updated Collection"})
        assert response.status_code == status.HTTP_200_OK

        # Test DELETE method (allowed)
        response = api_client.delete(f"/store/collections/{collection.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT


    def test_if_collection_has_products_returns_405(self, api_client, authenticate):
        authenticate(is_staff=True)
        collection = baker.make(Collection)
        baker.make(Product, collection=collection)

        response = api_client.delete(f"/store/collections/{collection.id}/")

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
class TestProductViewSet:
    def test_get_queryset(self, api_client):
        product = baker.make(Product)

        response = api_client.get(f"/store/products/{product.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == product.id
        assert response.data["title"] == product.title

    def test_if_user_is_not_admin_patchs_method(self, api_client, authenticate):
        authenticate(is_staff=False)
        product = baker.make(Product)

        response = api_client.patch(f"/store/products/{product.id}/", {"title": "Updated Product"})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_admin_patchs_method(self, api_client, authenticate):
        authenticate(is_staff=True)
        product = baker.make(Product)

        response = api_client.patch(f"/store/products/{product.id}/", {"title": "Updated Product"})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Updated Product"