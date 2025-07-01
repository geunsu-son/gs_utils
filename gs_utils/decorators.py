import time

def time_tracker(func):
    def wrapper(*args, **kwargs):
        """
        이 데코레이터는 함수의 실행 시간을 추적하고 콘솔에 출력합니다.
        """
        start_time = time.time()
        print(f"⏳ Function '{func.__name__}' started at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"✅ Function '{func.__name__}' finished at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}")
        print(f"🕒 Total execution time: {end_time - start_time:.4f} seconds\n{'-'*50}")
        return result
    return wrapper
