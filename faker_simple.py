from typing import List, Dict, Any, Optional
from faker import Faker
from faker.providers import BaseProvider, DynamicProvider
import random
import json

# Initialize Faker with a seed for reproducibility
fake = Faker("en_US")
Faker.seed(42)

# Custom provider for business units
class BusinessUnitProvider(BaseProvider):
    def business_unit(self):
        units = [
            "Sales", "Marketing", "Finance", "Operations", "IT", "Engineering",
            "Research", "Analytics", "HR", "Customer Support"
        ]
        return self.random_element(units)

city_provider = DynamicProvider(
    provider_name="city",
    elements=[
        "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Austin", "Miami",
        "Nashville", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose",
    ]
)


def generate_fake_employee(
    departments: Optional[List[str]] = None,
    titles: Optional[List[str]] = None,
    min_salary: int = 50000,
    max_salary: int = 200000,
    min_age: int = 21,
    max_age: int = 65,
    hire_start: str = '-30y',
    hire_end: str = 'today',
    locale: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate a single fake employee record with dynamic arguments.
    """
    generator = Faker(locale) if locale else fake
    # Add custom providers to the generator
    generator.add_provider(BusinessUnitProvider)
    generator.add_provider(city_provider)
    departments = departments or ["HR", "IT", "Sales", "Marketing", "Finance"]
    titles = titles or ["Manager", "Engineer", "Analyst", "Specialist"]
    department = random.choice(departments)
    title = random.choice(titles)
    salary = random.randint(min_salary, max_salary)
    employee = {
        "employee_id": generator.uuid4(),
        "name": generator.name(),
        "dob": generator.date_of_birth(minimum_age=min_age, maximum_age=max_age).isoformat(),
        "title": title,
        "department": department,
        "business_unit": generator.business_unit(),
        "city": generator.city(),
        "salary": salary,
        "email": generator.email(),
        "phone": generator.phone_number(),
        "hire_date": generator.date_between(start_date=hire_start, end_date=hire_end).isoformat(),
        "address": generator.address().replace("\n", ", "),
    }
    return employee

if __name__ == "__main__":
    # Generate employee records
    employees = [
        generate_fake_employee(
            departments=["Engineering", "Support", "Product"],
            titles=["Lead", "Developer", "QA", "IT Manager", "Project Manager", "Data Scientist"],
            # min_salary=60_000,
            # max_salary=225_000,
            # min_age=22,
            # max_age=55,
            hire_start='-10y',
            hire_end='today',
            locale="en_US"
        )
        for _ in range(5)
    ]
    print("Sample Employees:", json.dumps(employees, indent=2))
