from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from apps.habits.models import Habit
from .models import Plant
from .utils import create_plant_for_habit


class PlantHealthTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='tester',
            password='testpass123',
        )
        self.habit = Habit.objects.create(user=self.user, name='Exercise')
        self.plant = create_plant_for_habit(self.habit)

    def test_new_plant_starts_at_full_health(self):
        self.plant.update_health()
        self.assertEqual(self.plant.health, 100)

    def test_health_decays_by_20_per_day_missed(self):
        self.plant.last_watered = timezone.now() - timedelta(days=3)
        self.plant.save()
        self.plant.update_health()
        self.assertEqual(self.plant.health, 40)

    def test_health_floor_is_zero(self):
        self.plant.last_watered = timezone.now() - timedelta(days=30)
        self.plant.save()
        self.plant.update_health()
        self.assertEqual(self.plant.health, 0)

    def test_water_restores_health(self):
        self.plant.last_watered = timezone.now() - timedelta(days=3)
        self.plant.save()
        self.plant.update_health()
        self.assertEqual(self.plant.health, 40)
        self.plant.water()
        self.assertEqual(self.plant.health, 100)
        self.assertIsNotNone(self.plant.last_watered)
