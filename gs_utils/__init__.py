import time

def time_tracker(func):
    def wrapper(*args, **kwargs):
        """
        이 데코레이터는 함수의 실행 시간을 추적하고 콘솔에 출력합니다.

        Args:
            *args: 함수에 전달되는 가변 위치 인수.
            **kwargs: 함수에 전달되는 가변 키워드 인수.

        Returns:
            원본 함수의 실행 결과.

        """
        start_time = time.time()
        print(f"Function '{func.__name__}' started at: {time.ctime(start_time)}")
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Function '{func.__name__}' finished at: {time.ctime(end_time)}")
        print(f"Total execution time: {end_time - start_time:.4f} seconds")
        return result
    return wrapper