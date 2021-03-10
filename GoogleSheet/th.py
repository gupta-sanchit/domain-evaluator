import concurrent.futures
from GoogleSheet.script import CreateSheet


def foo(n):
    return n * n


l = [1, 2, 3, 4, 5, 6, 7, 8, 9]
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = []
    for url in l:
        futures.append(executor.submit(foo, n=url))
    for future in concurrent.futures.as_completed(futures):
        print(future.result())
