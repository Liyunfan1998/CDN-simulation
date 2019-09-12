import multiprocessing
import time

def func(msg):
    print("msg:", msg)
    time.sleep(3)
    print("end")

if __name__ == "__main__":
    pool = multiprocessing.Pool(processes = 50)
    for i in range(3):
        msg = "hello %d" %(i)
        pool.apply_async(func, (msg, ))

    print("M~ M~ M~~~~~~~~~~~~~~~~~~~~~~")
    pool.close()
    pool.join()
    print("Sub-process(es) done.")