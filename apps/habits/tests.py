from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.garden.models import Plant
from apps.garden.utils import create_plant_for_habit
from .models import Habit, HabitCompletion
from .utils import calculate_streak, get_best_streak, is_completed_in_period


class HabitModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='tester',
            password='testpass123',
        )
        self.daily_habit = Habit.objects.create(
            user=self.user,
            name='Drink water',
            frequency='daily',
        )
        self.weekly_habit = Habit.objects.create(
            user=self.user,
            name='Weekly review',
            frequency='weekly',
        )

    def complete_on(self, habit, days_ago):
        HabitCompletion.objects.create(
            habit=habit,
            date=date.today() - timedelta(days=days_ago),
        )

    def test_daily_streak_counts_consecutive_days(self):
        self.complete_on(self.daily_habit, 0)
        self.complete_on(self.daily_habit, 1)
        self.complete_on(self.daily_habit, 2)
        self.assertEqual(calculate_streak(self.daily_habit), 3)

    def test_daily_streak_starts_from_yesterday_if_today_not_done(self):
        self.complete_on(self.daily_habit, 1)
        self.complete_on(self.daily_habit, 2)
        self.complete_on(self.daily_habit, 3)
        self.assertEqual(calculate_streak(self.daily_habit), 3)

    def test_daily_streak_broken(self):
        self.complete_on(self.daily_habit, 0)
        self.complete_on(self.daily_habit, 2)
        self.assertEqual(calculate_streak(self.daily_habit), 1)

    def test_weekly_streak_counts_consecutive_weeks(self):
        self.complete_on(self.weekly_habit, 0)
        self.complete_on(self.weekly_habit, 7)
        self.complete_on(self.weekly_habit, 14)
        self.assertEqual(calculate_streak(self.weekly_habit), 3)

    def test_weekly_streak_starts_from_last_week_if_current_not_done(self):
        self.complete_on(self.weekly_habit, 7)
        self.complete_on(self.weekly_habit, 14)
        self.assertEqual(calculate_streak(self.weekly_habit), 2)

    def test_weekly_streak_broken(self):
        self.complete_on(self.weekly_habit, 7)
        self.complete_on(self.weekly_habit, 21)
        self.assertEqual(calculate_streak(self.weekly_habit), 1)

    def test_best_streak_daily(self):
        self.complete_on(self.daily_habit, 0)
        self.complete_on(self.daily_habit, 1)
        self.complete_on(self.daily_habit, 2)
        self.complete_on(self.daily_habit, 5)
        self.complete_on(self.daily_habit, 6)
        self.assertEqual(get_best_streak(self.daily_habit), 3)

    def test_best_streak_weekly(self):
        self.complete_on(self.weekly_habit, 0)
        self.complete_on(self.weekly_habit, 7)
        self.complete_on(self.weekly_habit, 14)
        self.complete_on(self.weekly_habit, 28)
        self.assertEqual(get_best_streak(self.weekly_habit), 3)

    def test_is_completed_in_period_daily(self):
        self.assertFalse(is_completed_in_period(self.daily_habit, date.today()))
        self.complete_on(self.daily_habit, 0)
        self.assertTrue(is_completed_in_period(self.daily_habit, date.today()))

    def test_is_completed_in_period_weekly(self):
        self.assertFalse(is_completed_in_period(self.weekly_habit, date.today()))
        self.complete_on(self.weekly_habit, 0)
        self.assertTrue(is_completed_in_period(self.weekly_habit, date.today()))


class ToggleCompleteTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='tester',
            password='testpass123',
        )
        self.client.login(username='tester', password='testpass123')
        self.habit = Habit.objects.create(
            user=self.user,
            name='Read books',
        )
        create_plant_for_habit(self.habit)

    def test_toggle_complete_requires_post(self):
        response = self.client.get(
            reverse('toggle_complete', kwargs={'pk': self.habit.pk})
        )
        self.assertEqual(response.status_code, 405)

    def test_toggle_complete_creates_completion(self):
        response = self.client.post(
            reverse('toggle_complete', kwargs={'pk': self.habit.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['completed'])
        self.assertTrue(
            HabitCompletion.objects.filter(habit=self.habit).exists()
        )

    def test_toggle_complete_removes_completion(self):
        self.client.post(reverse('toggle_complete', kwargs={'pk': self.habit.pk}))
        response = self.client.post(
            reverse('toggle_complete', kwargs={'pk': self.habit.pk})
        )
        self.assertFalse(response.json()['completed'])
        self.assertFalse(
            HabitCompletion.objects.filter(habit=self.habit).exists()
        )

    def test_toggle_complete_waters_plant(self):
        plant = self.habit.plant
        plant.health = 0
        plant.save()
        self.client.post(reverse('toggle_complete', kwargs={'pk': self.habit.pk}))
        plant.refresh_from_db()
        self.assertEqual(plant.health, 100)
        self.assertIsNotNone(plant.last_watered)

    def test_toggle_complete_only_for_own_habit(self):
        other_user = User.objects.create_user(
            username='other',
            password='testpass123',
        )
        other_habit = Habit.objects.create(user=other_user, name='Others habit')
        response = self.client.post(
            reverse('toggle_complete', kwargs={'pk': other_habit.pk})
        )
        self.assertEqual(response.status_code, 404)
