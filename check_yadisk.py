import yadisk

YANDEX_TOKEN = "y0__xDFvomZBxj2wTwgusy04xVUxtgL4E6rzYhwUYGX77JxfHIrUw"

y = yadisk.YaDisk(token=YANDEX_TOKEN)
print("check_token:", y.check_token())
print("disk_info name:", y.get_disk_info().user.login)