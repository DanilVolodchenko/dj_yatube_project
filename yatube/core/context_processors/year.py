from datetime import datetime


def year(context):
    return {'year': datetime.today().year}
