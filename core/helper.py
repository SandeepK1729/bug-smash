from django.forms.models import model_to_dict

from datetime import datetime

def getFormattedData(modelObjects, headers):
    """getFormattedData function

    Args:
        modelObjects (Model Object): Immutable list of model objects
        headers (list[str]): string list of headers
    """
    data = []
    for modelObject in modelObjects:
        row = model_to_dict(modelObject)
        data.append([
            row[header] for header in headers
        ])
    
    return data

def getDateObjectFromTime(datetime):
    date, time = datetime.split()
    re = [int(x) for x in date.split('-')]
    re.extend([int(x) for x in time.split(':')])
    
    
    return datetime(*re)