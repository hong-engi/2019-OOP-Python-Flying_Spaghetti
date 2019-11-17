class ERROR(BaseException):
    pass
def error_func():
    try:
        a=1/0
    except ZeroDivisionError:
        raise ERROR
try:
    error_func()
except ERROR:
    print("excepted")

print("{}".format('='*0+'asdf'))
list = ['asdf','s','qkrxasdfoals','asdff']
for i in range(len(list)):
    if len(list[i])>10:
        list[i] = list[i][0:9]
        print(i)
print("제목         사람수")
for i in list:
    print("{} - {}명".format(i+' '*(10-len(i)),6))