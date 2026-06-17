from faker import Faker

fake = Faker()


def create_personal_step(**overrides) -> dict[str, str]:
    data = {
        "name": fake.name(),
        "email": fake.email(),
        "dob": "1990-05-15",
        "country": "ca",
    }
    data.update(overrides)
    return data


def create_preferences_step(**overrides) -> dict[str, str]:
    data = {
        "framework": "playwright",
        "role": "qa",
        "experience": "5",
    }
    data.update(overrides)
    return data
