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

def error_logger(raise_error=True):
    """
    함수가 실패했을 때 발생한 에러 메시지를 출력하는 데코레이터
    입력값: raise_error (bool) - True면 에러를 다시 발생시킴, False면 에러를 무시하고 계속 진행
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            """
            이 데코레이터는 함수가 실패했을 때 발생한 에러 메시지를 출력합니다.
            """
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"================================\n⚠️ Function '{func.__name__}'\nℹ️ Error Message: {str(e)}\n================================")
                if raise_error:
                    raise  # 에러를 다시 발생시켜 호출자에게 전달합니다.
        return wrapper
    return decorator