import uuid
import pytest

from django.utils import timezone
from django.contrib.auth.models import User

from rest_framework.authtoken.models import Token
from rest_framework import status

from .models import Company, Driver


@pytest.mark.django_db
def test_user_create():
    User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
    assert User.objects.count() == 1


@pytest.mark.django_db
def test_unauthorized(client):
    url = '/admin/'
    response = client.get(url)
    assert response.status_code == status.HTTP_302_FOUND


@pytest.mark.django_db
def test_superuser_view(admin_client):
    url = '/admin/'
    response = admin_client.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.fixture
def test_password():
    return 'strong-test-pass'


@pytest.fixture
def create_user(db, django_user_model, test_password):
    def make_user(**kwargs):
        kwargs['password'] = test_password
        if 'username' not in kwargs:
            kwargs['username'] = str(uuid.uuid4())
        return django_user_model.objects.create_user(**kwargs)
    return make_user


@pytest.mark.django_db
def test_driver_create(client, create_user):
    user = create_user(username='someone')
    driver = Driver.objects.create(user=user)
    driver.save()
    url = f'/drivers/{driver.id}/'
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert 'someone' in str(response.content)


@pytest.fixture
def auto_login_driver(db, client, create_user, test_password):
    def make_auto_login(user=None):
        if user is None:
            user = create_user()
        driver = Driver.objects.create(user=user)
        driver.save()
        client.login(username=user.username, password=test_password)
        token = Token.objects.get(user=user)
        headers = {'HTTP_AUTHORIZATION': f'Token {token}'}
        return client, driver, headers
    return make_auto_login


test_vehicle = {'car_manufacturer': 'fiat', 'model': 'punto',
                'year_of_production': 1998, 'license_plate': 'ZG2020A'}
test_company = {'name': 'kompanija',
                'address': 'zagrebacka ulica', 'wage_per_km': 100.0}
test_company2 = {'name': 'bolt',
                 'address': 'vukovarska ulica', 'wage_per_km': 90.0}
test_trip = {'lat': 65.1232, 'lng': 44.2132, 'timestamp': timezone.now()}


@pytest.mark.django_db
def test_driver_vehicle_create(auto_login_driver):
    client, _, headers = auto_login_driver()
    url = '/vehicles/'
    response = client.post(url, data=test_vehicle, **headers)
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_driver_vehicle_update(auto_login_driver):
    client, _, headers = auto_login_driver()
    url = '/vehicles/'
    response = client.post(url, data=test_vehicle, **headers)
    vehicle = response.json()
    url = f'/vehicles/{vehicle["id"]}/'
    test_vehicle['year_of_production'] = 1999
    response = client.put(url, data=test_vehicle,
                          content_type='application/json', **headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['year_of_production'] == 1999


@pytest.mark.django_db
def test_driver_choose_company(auto_login_driver):
    client, driver, headers = auto_login_driver()
    company = Company.objects.create(**test_company)
    company.save()
    url = f'/drivers/{driver.id}/'
    company_id = {'company_id': company.id}
    response = client.put(url, data=company_id,
                          content_type='application/json', **headers)
    driver = Driver.objects.get(id=driver.id)
    assert response.status_code == status.HTTP_200_OK
    assert driver.company == company


@pytest.mark.django_db
def test_driver_choose_company_again(auto_login_driver):
    client, driver, headers = auto_login_driver()

    company = Company.objects.create(**test_company)
    company.save()

    company2 = Company.objects.create(**test_company2)
    company2.save()

    url = f'/drivers/{driver.id}/'
    company_id = {'company_id': company.id}
    response = client.put(url, data=company_id,
                          content_type='application/json', **headers)

    company_id['company_id'] = company2.id
    response = client.put(url, data=company_id,
                          content_type='application/json', **headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_driver_create_trip(auto_login_driver):
    client, _, headers = auto_login_driver()
    url = '/trips/'
    response = client.post(url, data=test_trip, **headers)
    assert response.status_code == status.HTTP_201_CREATED
