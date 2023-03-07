from django.forms.models import model_to_dict


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