import random
from locust import HttpUser, task

from giantstar._locust import prepare_locust_tests


class TaskUser(HttpUser):
    # wait_time = between(0, 0)
    host = ""

    def on_start(self):
        self.locust_test = prepare_locust_tests()

    @task
    def test_cttest_case(self):
        cttest_case = self.weight_allocation(self.locust_test)
        try:
            cttest_case.run(locust_session=self.client)
        except Exception as ex:
            self.environment.events.request_failure.fire(
                request_type="Failed",
                name=cttest_case.title,
                response_time=0,
                response_length=0,
                exception=ex,
            )
            raise ex

    @staticmethod
    def weight_allocation(task: dict):
        weight_list = list(task.keys())
        weight_sum = sum(weight_list)
        chose = random.randint(1, weight_sum)
        key_sum = 0
        for i in weight_list:
            key_sum += i
            if key_sum >= chose:
                return random.choice(task.get(i))

