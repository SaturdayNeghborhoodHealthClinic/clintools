from pttrack import models
from datetime import date

p = models.Patient(first_name="James",
                   middle_name="R",
                   last_name="Brown",
                   address="5555 Five Ave.",
                   date_of_birth=date(year=1979,
                                      month=4,
                                      day=2),
                   phone="501-555-5555",
                   gender=models.Gender.objects.all()[0])
p.save()

p = models.Patient(first_name="J",
                   middle_name="K",
                   last_name="Rowling",
                   address="123 Hogwarts Ln. N",
                   date_of_birth=date(year=1967,
                                      month=7,
                                      day=2),
                   phone="321-321-3210",
                   gender=models.Gender.objects.all()[0])
p.save()

p = models.Patient(first_name="Steven",
                   middle_name="S",
                   last_name="Colbert",
                   address="111 HundredEleventh Rd. N",
                   date_of_birth=date(year=1957,
                                      month=1,
                                      day=1),
                   phone="321-321-3210",
                   gender=models.Gender.objects.all()[0])
p.save()
