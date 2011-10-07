from models import Feed

def import_outline_element(o):
    for f in o:
        if hasattr(f,'xmlUrl'):
            new = Feed.objects.create(url = f.xmlUrl,
                                  #tags = self.cleaned_data['tags'],
                                  name = f.title,
                                  )
            new.save()
        else:
            import_outline_element(f)


