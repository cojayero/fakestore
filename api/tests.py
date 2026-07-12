from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Product


class ProductModelTest(TestCase):
    """Unit tests for the Product model."""

    def setUp(self):
        self.product = Product.objects.create(
            id=1,
            title="Fjallraven Backpack",
            price=109.95,
            description="Your perfect pack for everyday use.",
            category="men's clothing",
            image="https://fakestoreapi.com/img/81fAn.jpg",
        )

    def test_str_returns_title(self):
        self.assertEqual(str(self.product), "Fjallraven Backpack")

    def test_fields_stored_correctly(self):
        product = Product.objects.get(id=1)
        self.assertEqual(product.title, "Fjallraven Backpack")
        self.assertAlmostEqual(product.price, 109.95)
        self.assertEqual(product.category, "men's clothing")
        self.assertTrue(product.image.startswith("https://"))


class ProductListTest(APITestCase):
    """Tests for GET /products/ (list)."""

    def setUp(self):
        Product.objects.create(
            id=1, title="Product A", price=10.0,
            description="Desc A", category="cat1",
            image="https://example.com/a.jpg",
        )
        Product.objects.create(
            id=2, title="Product B", price=20.0,
            description="Desc B", category="cat2",
            image="https://example.com/b.jpg",
        )

    def test_list_returns_200(self):
        url = reverse("product-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_returns_all_products(self):
        url = reverse("product-list")
        response = self.client.get(url)
        # DRF pagination wraps results in a 'results' key
        results = response.data.get("results", response.data)
        self.assertEqual(len(results), 2)

    def test_list_contains_expected_fields(self):
        url = reverse("product-list")
        response = self.client.get(url)
        results = response.data.get("results", response.data)
        first = results[0]
        for field in ("id", "title", "price", "description", "category", "image"):
            self.assertIn(field, first)


class ProductDetailTest(APITestCase):
    """Tests for GET /products/{id}/ (retrieve)."""

    def setUp(self):
        self.product = Product.objects.create(
            id=1, title="Test Product", price=9.99,
            description="A test product.", category="electronics",
            image="https://example.com/test.jpg",
        )

    def test_retrieve_existing_product_returns_200(self):
        url = reverse("product-detail", kwargs={"pk": 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_returns_correct_data(self):
        url = reverse("product-detail", kwargs={"pk": 1})
        response = self.client.get(url)
        self.assertEqual(response.data["title"], "Test Product")
        self.assertAlmostEqual(float(response.data["price"]), 9.99)
        self.assertEqual(response.data["category"], "electronics")

    def test_retrieve_nonexistent_product_returns_404(self):
        url = reverse("product-detail", kwargs={"pk": 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ProductCreateTest(APITestCase):
    """Tests for POST /products/ (create)."""

    def _payload(self, **kwargs):
        base = {
            "id": 10,
            "title": "New Product",
            "price": 29.99,
            "description": "A brand new product.",
            "category": "jewelery",
            "image": "https://example.com/new.jpg",
        }
        base.update(kwargs)
        return base

    def test_create_product_returns_201(self):
        url = reverse("product-list")
        response = self.client.post(url, self._payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_product_persists_to_db(self):
        url = reverse("product-list")
        self.client.post(url, self._payload(), format="json")
        self.assertTrue(Product.objects.filter(id=10).exists())

    def test_create_product_returns_correct_data(self):
        url = reverse("product-list")
        response = self.client.post(url, self._payload(), format="json")
        self.assertEqual(response.data["title"], "New Product")
        self.assertAlmostEqual(float(response.data["price"]), 29.99)

    def test_create_product_missing_required_field_returns_400(self):
        url = reverse("product-list")
        payload = self._payload()
        del payload["title"]
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProductUpdateTest(APITestCase):
    """Tests for PUT /products/{id}/ (full update)."""

    def setUp(self):
        self.product = Product.objects.create(
            id=1, title="Old Title", price=5.0,
            description="Old desc.", category="old-cat",
            image="https://example.com/old.jpg",
        )

    def _payload(self):
        return {
            "id": 1,
            "title": "Updated Title",
            "price": 15.0,
            "description": "Updated description.",
            "category": "new-cat",
            "image": "https://example.com/updated.jpg",
        }

    def test_full_update_returns_200(self):
        url = reverse("product-detail", kwargs={"pk": 1})
        response = self.client.put(url, self._payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_full_update_changes_title(self):
        url = reverse("product-detail", kwargs={"pk": 1})
        self.client.put(url, self._payload(), format="json")
        self.product.refresh_from_db()
        self.assertEqual(self.product.title, "Updated Title")

    def test_partial_update_returns_200(self):
        url = reverse("product-detail", kwargs={"pk": 1})
        response = self.client.patch(url, {"price": 99.0}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partial_update_changes_price(self):
        url = reverse("product-detail", kwargs={"pk": 1})
        self.client.patch(url, {"price": 99.0}, format="json")
        self.product.refresh_from_db()
        self.assertAlmostEqual(self.product.price, 99.0)

    def test_update_nonexistent_product_returns_404(self):
        url = reverse("product-detail", kwargs={"pk": 999})
        response = self.client.put(url, self._payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ProductDeleteTest(APITestCase):
    """Tests for DELETE /products/{id}/ (destroy)."""

    def setUp(self):
        self.product = Product.objects.create(
            id=1, title="To Delete", price=1.0,
            description="Will be deleted.", category="misc",
            image="https://example.com/delete.jpg",
        )

    def test_delete_existing_product_returns_204(self):
        url = reverse("product-detail", kwargs={"pk": 1})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_removes_product_from_db(self):
        url = reverse("product-detail", kwargs={"pk": 1})
        self.client.delete(url)
        self.assertFalse(Product.objects.filter(id=1).exists())

    def test_delete_nonexistent_product_returns_404(self):
        url = reverse("product-detail", kwargs={"pk": 999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
