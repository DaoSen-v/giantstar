import random
from locust import HttpUser, task, between

from gaintstar._locust import prepare_locust_tests


class TaskUser(HttpUser):
    # wait_time = between(0, 0)
    host = ""
    def on_start(self):
        self.locust_test = prepare_locust_tests()
    @task
    def test_cttest_case(self):
        cttest_case = random.choice(self.locust_test)
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
