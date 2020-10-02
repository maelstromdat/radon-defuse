import json
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .models import Repositories
from .serializers import RepositorySerializer


class BaseViewTest(APITestCase):
    client = APIClient()

    @staticmethod
    def create_repository(id: str, owner: str, name: str, url: str, default_branch: str, description: str,
                          num_issues: int,
                          num_releases: int, num_stars: int, num_watchers: int, primary_language: str, created_at: str,
                          pushed_at: str):
        Repositories.objects.create(id=id, owner=owner, name=name, url=url, default_branch=default_branch,
                                    description=description, num_issues=num_issues, num_releases=num_releases,
                                    num_stars=num_stars, num_watchers=num_watchers, primary_language=primary_language,
                                    created_at=created_at, pushed_at=pushed_at)

    def setUp(self):
        # add test data
        self.create_repository(id='MDEwOlJlcG9zaXRvcnkxNTk0MTM0NQ==', owner='jnv',
                               name='ansible-role-unattended-upgrades',
                               url='https://github.com/jnv/ansible-role-unattended-upgrades', default_branch='master',
                               description='Setup unattended-upgrades on Debian-based systems',
                               num_issues=37, num_releases=15, num_stars=201, num_watchers=10, primary_language='shell',
                               created_at='2014-01-18T23:56:09Z', pushed_at='2020-08-18T12:28:29Z')

        self.create_repository(id='MDEwOlJlcG9zaXRvcnkxNjAzNjY0Ng==', owner='jnv',
                               name='ansible-role-debian-backports',
                               url='https://github.com/jnv/ansible-role-debian-backports', default_branch='master',
                               description='Setup backports repository for Debian and Ubuntu',
                               num_issues=5, num_releases=6, num_stars=7, num_watchers=1, primary_language='shell',
                               created_at='2014-01-15T16:46:51Z', pushed_at='2020-08-09T12:22:24Z')

    def _post_teardown(self):
        Repositories.objects.all().delete()


class RepositoriesTest(BaseViewTest):

    def test_get_all_repositories(self):
        """
        This test ensures that all repositories added in the setUp method exist when we make a GET request to the \
        repositories/ endpoint
        """
        # get API response
        response = self.client.get(reverse('repositories-list'))

        # get data from db
        repositories = Repositories.objects.all()
        serializer = RepositorySerializer(repositories, many=True)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_valid_single_repository(self):
        response = self.client.get(reverse('repositories-detail', kwargs={'pk': 'MDEwOlJlcG9zaXRvcnkxNTk0MTM0NQ=='}))
        repository = Repositories.objects.get(pk='MDEwOlJlcG9zaXRvcnkxNTk0MTM0NQ==')
        serializer = RepositorySerializer(repository)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_invalid_single_repository(self):
        response = self.client.get(reverse('repositories-detail', kwargs={'pk': 'WrOnGrEpOsItOrYsHa=='}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_valid_repository(self):
        valid_payload = {
            'id': 'MDEwOlJlcG9zaXRvcnkxNjE4MzAxNQ==',
            'owner': 'Juniper',
            'name': 'ansible-junos-stdlib',
            'url': 'https://github.com/Juniper/ansible-junos-stdlib'
        }

        response = self.client.post(
            reverse('repositories-list'),
            data=json.dumps(valid_payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_invalid_repository(self):
        invalid_payloads = [{
            # no id passed
            'owner': 'Juniper',
            'name': 'ansible-junos-stdlib',
            'url': 'https://github.com/Juniper/ansible-junos-stdlib',
        }, {
            'id': 'MDEwOlJlcG9zaXRvcnkxNjE4MzAxNQ==',
            # no owner passed
            'name': 'ansible-junos-stdlib',
            'url': 'https://github.com/Juniper/ansible-junos-stdlib',
        }, {
            'id': 'MDEwOlJlcG9zaXRvcnkxNjE4MzAxNQ==',
            'owner': 'Juniper',
            # no name passed
            'url': 'https://github.com/Juniper/ansible-junos-stdlib',
        }, {
            'id': 'MDEwOlJlcG9zaXRvcnkxNjE4MzAxNQ==',
            'owner': 'Juniper',
            'name': 'ansible-junos-stdlib'
            # no url passed
        }]

        for payload in invalid_payloads:
            response = self.client.post(
                reverse('repositories-list'),
                data=json.dumps(payload),
                content_type='application/json'
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_repository_conflict(self):
        payload = {
            'id': 'MDEwOlJlcG9zaXRvcnkxNjMwMDY5NQ==',
            'owner': 'angstwad',
            'name': 'docker.ubuntu',
            'url': 'https://github.com/angstwad/docker.ubuntu'
        }

        response = self.client.post(
            reverse('repositories-list'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # here the conflict
        response = self.client.post(
            reverse('repositories-list'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
