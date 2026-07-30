from django.test import TestCase


class DjangoConsumerAppTests(TestCase):
    def test_index_page_renders(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django example app")

    def test_example_form_page_renders(self):
        response = self.client.get("/forms/example/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Example form")

    def test_conditional_form_validation(self):
        response = self.client.post(
            "/forms/conditional/",
            {
                "contact_method": "email",
                "email": "",
                "phone": "",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enter an email address")

    def test_date_field_submission(self):
        response = self.client.post(
            "/forms/example/",
            {
                "username": "Jane",
                "contact_method": "email",
                "category": "news",
                "agreed": "on",
                "date_of_birth_day": "10",
                "date_of_birth_month": "2",
                "date_of_birth_year": "1999",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Form submitted successfully.")
