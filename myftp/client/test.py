
import  time
size = 100
for i in range(100):
    res = str(i/size * 100)[:4]
    # \r 光标回到行首 不会换行  所以windows 换行 是 \r\n
    print("\r"+res,end="")

    time.sleep(0.1)





