from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Allergy, DietaryRestriction, MedicalCondition, UserProfile

User = get_user_model()


class ReferenceModelListAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="testpassword123",
        )
        self.client.force_authenticate(user=self.user)

    def test_medical_conditions_list_authenticated(self):
        url = reverse("medical-conditions")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["status"])
        self.assertEqual(
            response.data["message"],
            "Medical condition list retrieved successfully.",
        )
        self.assertEqual(
            len(response.data["data"]),
            MedicalCondition.objects.count(),
        )
        # Verify ordering by name
        names = [item["name"] for item in response.data["data"]]
        self.assertEqual(names, sorted(names))

    def test_allergies_list_authenticated(self):
        url = reverse("allergies")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["status"])
        self.assertEqual(
            response.data["message"],
            "Allergy list retrieved successfully.",
        )
        self.assertEqual(
            len(response.data["data"]),
            Allergy.objects.count(),
        )
        # Verify ordering by name
        names = [item["name"] for item in response.data["data"]]
        self.assertEqual(names, sorted(names))

    def test_dietary_restrictions_list_authenticated(self):
        url = reverse("dietary-restrictions")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["status"])
        self.assertEqual(
            response.data["message"],
            "Dietary restriction list retrieved successfully.",
        )
        self.assertEqual(
            len(response.data["data"]),
            DietaryRestriction.objects.count(),
        )
        # Verify ordering by name
        names = [item["name"] for item in response.data["data"]]
        self.assertEqual(names, sorted(names))

    def test_endpoints_unauthenticated(self):
        self.client.force_authenticate(user=None)

        for endpoint_name in [
            "medical-conditions",
            "allergies",
            "dietary-restrictions",
        ]:
            url = reverse(endpoint_name)
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_endpoints_disallow_mutating_methods(self):
        for endpoint_name in [
            "medical-conditions",
            "allergies",
            "dietary-restrictions",
        ]:
            url = reverse(endpoint_name)
            post_resp = self.client.post(url, {"name": "Test"})
            self.assertEqual(
                post_resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
            )

            put_resp = self.client.put(url, {"name": "Test"})
            self.assertEqual(
                put_resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
            )

            patch_resp = self.client.patch(url, {"name": "Test"})
            self.assertEqual(
                patch_resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
            )

            delete_resp = self.client.delete(url)
            self.assertEqual(
                delete_resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
            )

    def test_user_profile_m2m_patch_and_get(self):
        profile = UserProfile.objects.create(
            user=self.user,
            age=25,
            gender="MALE",
            height_cm=175.0,
            weight_kg=70.0,
        )

        med_ids = list(
            MedicalCondition.objects.values_list("id", flat=True)[:2]
        )
        allergy_ids = list(Allergy.objects.values_list("id", flat=True)[:1])
        diet_ids = list(
            DietaryRestriction.objects.values_list("id", flat=True)[:2]
        )

        patch_url = reverse("user-profile")
        patch_resp = self.client.patch(
            patch_url,
            {
                "medical_conditions": med_ids,
                "allergies": allergy_ids,
                "dietary_restrictions": diet_ids,
            },
            format="json",
        )

        self.assertEqual(patch_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(patch_resp.data["data"]["medical_conditions"]), set(med_ids)
        )
        self.assertEqual(
            set(patch_resp.data["data"]["allergies"]), set(allergy_ids)
        )
        self.assertEqual(
            set(patch_resp.data["data"]["dietary_restrictions"]), set(diet_ids)
        )

        get_resp = self.client.get(patch_url)
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(get_resp.data["data"]["medical_conditions"]), set(med_ids)
        )
