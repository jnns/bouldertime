from django.views.generic import FormView
from .forms import GymForm
from .models import Gym


class GymList(FormView):
    template_name = "core/gym_list.html"
    form_class = GymForm


class GymDetail(FormView):
    template_name = "core/gym_detail.html"
    form_class = GymForm

    def get_initial(self):
        return {"gym": self.kwargs.get("gym")}

    def get_context_data(self, **kwargs):
        gym = Gym.objects.get(slug=self.kwargs.get("gym"))
        return super().get_context_data(gym=gym, **kwargs)
