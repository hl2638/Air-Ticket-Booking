I'm using a conda venv.
The environment config is exported as environment.yml
To deploy, 
1) run """
conda env create -f environment.yml
"""
2) Manually CREATE A MYSQL DATABASE named "airticket_booking" and leave it empty.

3) 
To START THE SERVER run:
python manage.py runserver

The server will run at localhost:8000.

4)
MIGRATE ALL THE MODELS into mysql:
python manage.py makemigrations
python manage.py migrate

5)
CREATE A SUPERUSER by:
python manage.py createsuperuser

And then you can ACCESS THE ADMIN PAGE at
localhost:8000/admin
where you can manage data.

"""
On the admin page you will see customers/booking agents/airline staffs. They are highly decoupled with the "user" model, 
(i.e. they don't inherit from it) with only a foreign key field pointing to a user instance.
User is the base class used for authentication and session/requests. Customers/etc. are used for high-level functions. 
"""

6) LOG OUT THE ADMIN USER, since it doesn't do much with normal functionalities. 
Log in with other user identities with the pwds provided below, or register new ones.

7) You can ACCESS THE USER PORTAL once you are logged in, where there are functionalities exclusive to your user group.

==============================================

NOTES:
- Django provides a inspectdb method to import the sql database to Django python files. 
- Django doesn't support weak entities or combined primary keys. An alternative to do it is adding 'unique_together' constraints and not defining primary keys so django will automatically add an ID to the model.
- Django supports foreign keys, but not values of other columns of the model as the foreign key 
    e.g. if Flight's airline_name points to airplane, you can only get the airplane's pk (or another unique key) but not airplane's airline name. 
- Django's models are more object oriented than MySQL schemas. 
    For this reason and to maintain low coupling I'm using airplane (an object) instad of (airline_name, airplane_id) (a set of attributes representing the object) as a foreign key. 
    Similarly for other foreign keys.
- Django's models are basically encapsulated database relations. All the queries are done in Django styles: 
    Model.objects.get() for selecting one object, Model.objects.filter() for selecting multiple objects,
    QuerySet.values().annotate() for aggregates with group by.
- I decoupled the user identities with the user class. I wrote custom auth backends for different user types to login. 
    This took a lot of effort and consequently Django's built-in password reset doesn't work. I didn't bother writing my own.
- I followed part of Corey Schafer's tutorial on Django on Youtube.

==============================================

Usernames and Passwords (or create your own by registering)
"""
Airline Staff:
username: JBStaff1, etc. (see admin page for more)
pwd: AirlineStaff

Booking Agent:
username: booking@agent.com, etc.
pwd: pwd4agents

Customer:
username: customer@nyu.edu (this one only)
pwd: pwd4cust

username: one@nyu.edu, two@nyu.edu
pwd: pwd4customers
"""
