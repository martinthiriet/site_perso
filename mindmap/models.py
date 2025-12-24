from django.db import models
import os 
from django.contrib.auth.models import User
import unicodedata
from django.conf import settings
path=os.path.dirname(os.path.abspath(__file__))
path=path+"/"

class UserObject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

import os
import unicodedata
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

class Mapdata(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, default="Untitled")
    map_data = models.TextField(default=r"<#i>1<i#><#t>Start node<t#>")
    map_path = models.TextField(default=r"[None, '1', []]")
    map_link = models.TextField(default=r"None")
    share= models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Normalize the title to create a valid directory name
        new_title = self.title.replace(" ", "_")
        new_title = unicodedata.normalize('NFKD', new_title)
        new_title = new_title.encode('ASCII', 'ignore').decode('ASCII')

        # Check if the object is being updated
        if self.pk:
            # Get the old title
            old_instance = Mapdata.objects.get(pk=self.pk)
            old_title = old_instance.title.replace(" ", "_")
            old_title = unicodedata.normalize('NFKD', old_title)
            old_title = old_title.encode('ASCII', 'ignore').decode('ASCII')

            # Rename the directory if the title has changed
            if old_title != new_title:
                old_directory_path = os.path.join(settings.MEDIA_ROOT, 'compiled_data', old_title)
                new_directory_path = os.path.join(settings.MEDIA_ROOT, 'compiled_data', new_title)

                if os.path.exists(old_directory_path):
                    os.rename(old_directory_path, new_directory_path)

        # Update the title and save the object
        self.title = new_title
        super().save(*args, **kwargs)

        # Create the directory within the MEDIA_ROOT if it doesn't exist
        directory_path = os.path.join(settings.MEDIA_ROOT,'compiled_data', str(self.owner),self.title)
        os.makedirs(directory_path, exist_ok=True)

    def delete(self, *args, **kwargs):
        # Perform additional actions before deletion
        print(f"Deleting object with title: {self.title} and owner: {self.owner}")

        # Call the parent class's delete method to actually delete the object
        super().delete(*args, **kwargs)

        # Remove the directory if it exists
        directory_path = os.path.join(settings.MEDIA_ROOT, 'compiled_data',str(self.owner),self.title)
        if os.path.exists(directory_path):
            try:
                os.rmdir(directory_path)
            except OSError as e:
                print(f"Error deleting directory: {e}")

    def __str__(self):
        return f"{self.title} by {self.owner}"

