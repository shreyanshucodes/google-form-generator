import random
import unittest

from form import FormField
from generator import generate_row


class GeneratorTests(unittest.TestCase):
    def test_store_profile_fills_every_field(self):
        fields = [
            FormField("entry.1", "radio", "What is the geographical location of your store?", ["Kandivali", "Borivali", "Malad", "Andheri"]),
            FormField("entry.2", "radio", "How long your store been in business operation?", ["Less than 5 year", "5 to 15 years", "More than 15 years"]),
            FormField("entry.3", "radio", "What is the estimated physical floor space of your store", ["Micro", "Medium", "Large"]),
            FormField("entry.4", "radio", "how many total staff/employees currently work in your store?", ["1–2 employees", "3–4 employees", "5 or more employees"]),
            FormField("entry.5", "radio", "On average. how many home delivery orders does your store fulfil daily?", ["Less than 15 orders", "15 to 40 orders", "Above 40 orders"]),
        ]
        row = generate_row(fields, 1, random.Random(42))
        self.assertEqual(set(row), {field.name for field in fields})
        self.assertTrue(all(row.values()))

    def test_csr_profile_links_age_and_occupation(self):
        fields = [
            FormField("entry.1", "radio", "Your Age?", ["18 - 20", "21 - 23", "24 - 30", "31 - 40", "40 +"]),
            FormField("entry.2", "radio", "Occupation?", ["Student", "Salaried Employee", "Business Owner", "Professional", "Other"]),
            FormField("entry.3", "radio", "Have you heard of Reliance Industries Limited?", ["Yes", "No"]),
            FormField("entry.4", "textarea", "What improvement would you suggest for CSR communication by large companies?"),
        ]
        row = generate_row(fields, 1, random.Random(42))
        self.assertIn(row["entry.1"], fields[0].options)
        self.assertIn(row["entry.2"], fields[1].options)
        self.assertIn(row["entry.3"], fields[2].options)
        self.assertTrue(row["entry.4"])


if __name__ == "__main__":
    unittest.main()
