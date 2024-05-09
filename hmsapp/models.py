from django.db import models

# Create your models here

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=100)
    user_name = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.user_name
    
class Homeowner(models.Model):
    homeowner_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='homeowner')

    def __str__(self):
        return f"Homeowner: {self.user_id.user_name}"

class Service(models.Model):
    service_id = models.AutoField(primary_key=True)
    service_name = models.CharField(max_length=20)

    def __str__(self):
        return self.service_name
    
class ServiceProvider(models.Model):
    service_provider_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profession = models.CharField(max_length=100)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20,default='Hour')
    availability=models.CharField(max_length=100,default='Available')
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)

    def __str__(self):
        return self.user.user_name + ' - ' + self.profession
    def calculate_average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            total_rating = sum(review.rating for review in reviews)
            return total_rating / len(reviews)
        return 0.0

class Booking(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
        ('Completed','Completed')
    ]
    booking_id = models.AutoField(primary_key=True)
    name = models.TextField()
    homeowner = models.ForeignKey(Homeowner, related_name='bookings', on_delete=models.CASCADE)
    service_provider = models.ForeignKey(ServiceProvider, related_name='bookings', on_delete=models.CASCADE)
    job = models.TextField()
    jobdescription = models.TextField(default='None')
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    bookingdate = models.DateField(auto_now_add=True)
    servicedate = models.DateField()
    servicetime = models.TimeField()
    location = models.CharField(max_length=255)
    landmark = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    isupdated=models.TextField(default='No')
    totalrate = models.DecimalField(max_digits=10, decimal_places=2,default=0)

    def __str__(self):
        return f"Booking {self.booking_id} - {self.homeowner.user.user_name} - {self.service_provider.user.user_name}"

class Reviews(models.Model):
    review_id = models.AutoField(primary_key=True)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='reviews')
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    rating = models.IntegerField()
    review = models.TextField()
    review_date = models.DateField(auto_now_add=True)

class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    homeowner = models.ForeignKey(Homeowner, on_delete=models.CASCADE, default=1)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, default=1) 
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    method = models.CharField(max_length=100)
    payment_status = models.CharField(max_length=100)

class Cancellation(models.Model):
    cancellation_id = models.AutoField(primary_key=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    homeowner = models.ForeignKey(Homeowner, on_delete=models.CASCADE, default=1)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, default=1) 
    cancellation_date = models.DateField(auto_now_add=True)
    reason = models.TextField()

    def __str__(self):
        return f"Cancellation for Booking {self.booking.booking_id}"

class Update(models.Model):
    update_id = models.AutoField(primary_key=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    homeowner = models.ForeignKey(Homeowner, on_delete=models.CASCADE, default=1)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, default=1)  
    updateto_date = models.DateField(auto_now_add=True)
    updateto_time = models.TimeField(auto_now_add=True)
    updatemade_date = models.DateField(auto_now_add=True)
    description = models.TextField()


class Billing(models.Model):
    bill_id = models.AutoField(primary_key=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    homeowner = models.ForeignKey(Homeowner, on_delete=models.CASCADE, default=1)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, default=1) 
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    payment_status = models.CharField(max_length=100)

