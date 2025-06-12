import logging
import os
import sys
import traceback
from datetime import datetime
import json
from functools import wraps
import inspect

class Logger:
    """结构化日志系统
    
    提供统一的日志记录接口，支持不同级别的日志记录，
    包括DEBUG、INFO、WARNING、ERROR和CRITICAL。
    同时支持记录用户操作、系统事件和错误信息。
    """
    
    # 日志级别映射
    LEVELS = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }
    
    # 单例实例
    _instance = None
    
    @classmethod
    def get_instance(cls, log_level='info', log_dir=None):
        """获取Logger单例实例
        
        Args:
            log_level: 日志级别，可选值为debug、info、warning、error、critical
            log_dir: 日志文件目录，默认为项目根目录下的logs目录
            
        Returns:
            Logger: Logger实例
        """
        if cls._instance is None:
            cls._instance = cls(log_level, log_dir)
        return cls._instance
    
    def __init__(self, log_level='info', log_dir=None):
        """初始化Logger
        
        Args:
            log_level: 日志级别，可选值为debug、info、warning、error、critical
            log_dir: 日志文件目录，默认为项目根目录下的logs目录
        """
        # 获取项目根目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        
        # 设置日志目录
        if log_dir is None:
            log_dir = os.path.join(project_root, 'logs')
        
        # 确保日志目录存在
        os.makedirs(log_dir, exist_ok=True)
        
        # 设置日志级别
        self.log_level = self.LEVELS.get(log_level.lower(), logging.INFO)
        
        # 创建logger
        self.logger = logging.getLogger('imedilink')
        self.logger.setLevel(self.log_level)
        
        # 清除已有的处理器
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        
        # 创建文件处理器 - 按日期分割日志文件
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = os.path.join(log_dir, f'imedilink_{today}.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(self.log_level)
        
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 设置格式化器
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def _format_message(self, message, context=None):
        """格式化日志消息，添加上下文信息
        
        Args:
            message: 日志消息
            context: 上下文信息字典
            
        Returns:
            str: 格式化后的日志消息
        """
        if context is None:
            return message
        
        try:
            context_str = json.dumps(context, ensure_ascii=False)
            return f"{message} - Context: {context_str}"
        except Exception:
            return f"{message} - Context: {str(context)}"
    
    def debug(self, message, context=None):
        """记录DEBUG级别日志
        
        Args:
            message: 日志消息
            context: 上下文信息字典
        """
        self.logger.debug(self._format_message(message, context))
    
    def info(self, message, context=None):
        """记录INFO级别日志
        
        Args:
            message: 日志消息
            context: 上下文信息字典
        """
        self.logger.info(self._format_message(message, context))
    
    def warning(self, message, context=None):
        """记录WARNING级别日志
        
        Args:
            message: 日志消息
            context: 上下文信息字典
        """
        self.logger.warning(self._format_message(message, context))
    
    def error(self, message, context=None, exc_info=False):
        """记录ERROR级别日志
        
        Args:
            message: 日志消息
            context: 上下文信息字典
            exc_info: 是否记录异常信息
        """
        self.logger.error(self._format_message(message, context), exc_info=exc_info)
    
    def critical(self, message, context=None, exc_info=True):
        """记录CRITICAL级别日志
        
        Args:
            message: 日志消息
            context: 上下文信息字典
            exc_info: 是否记录异常信息
        """
        self.logger.critical(self._format_message(message, context), exc_info=exc_info)
    
    def exception(self, message, context=None):
        """记录异常日志，自动添加异常堆栈信息
        
        Args:
            message: 日志消息
            context: 上下文信息字典
        """
        exc_type, exc_value, exc_traceback = sys.exc_info()
        if exc_type is not None:
            if context is None:
                context = {}
            
            # 添加异常信息到上下文
            context.update({
                'exception_type': exc_type.__name__,
                'exception_message': str(exc_value),
                'traceback': traceback.format_exc()
            })
        
        self.logger.error(self._format_message(message, context))
    
    def user_action(self, user_id, action, details=None):
        """记录用户操作
        
        Args:
            user_id: 用户ID或标识
            action: 操作类型
            details: 操作详情
        """
        context = {
            'user_id': user_id,
            'action': action
        }
        
        if details:
            context['details'] = details
        
        self.info(f"User Action: {action}", context)
    
    def system_event(self, event_type, message, details=None):
        """记录系统事件
        
        Args:
            event_type: 事件类型
            message: 事件消息
            details: 事件详情
        """
        context = {
            'event_type': event_type
        }
        
        if details:
            context['details'] = details
        
        self.info(f"System Event: {message}", context)
    
    def api_request(self, api_name, request_data=None, response_data=None, error=None):
        """记录API请求
        
        Args:
            api_name: API名称
            request_data: 请求数据
            response_data: 响应数据
            error: 错误信息
        """
        context = {
            'api_name': api_name
        }
        
        if request_data:
            # 过滤敏感信息
            if isinstance(request_data, dict):
                filtered_data = request_data.copy()
                for key in ['password', 'api_key', 'secret', 'token']:
                    if key in filtered_data:
                        filtered_data[key] = '******'
                context['request_data'] = filtered_data
            else:
                context['request_data'] = str(request_data)
        
        if response_data:
            # 限制响应数据大小
            if isinstance(response_data, dict) or isinstance(response_data, list):
                try:
                    response_str = json.dumps(response_data)
                    if len(response_str) > 1000:
                        context['response_data'] = response_str[:1000] + '... (truncated)'
                    else:
                        context['response_data'] = response_data
                except:
                    context['response_data'] = str(response_data)[:1000] + '... (truncated)' if len(str(response_data)) > 1000 else str(response_data)
            else:
                context['response_data'] = str(response_data)[:1000] + '... (truncated)' if len(str(response_data)) > 1000 else str(response_data)
        
        if error:
            context['error'] = str(error)
            self.error(f"API Request Error: {api_name}", context)
        else:
            self.info(f"API Request: {api_name}", context)


def log_function_call(logger=None, level='info'):
    """函数调用日志装饰器
    
    记录函数的调用信息，包括参数和返回值
    
    Args:
        logger: Logger实例，如果为None则使用默认实例
        level: 日志级别
        
    Returns:
        function: 装饰后的函数
    """
    if logger is None:
        logger = Logger.get_instance()
    
    log_func = getattr(logger, level.lower())
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 获取函数信息
            func_name = func.__name__
            module_name = func.__module__
            
            # 获取调用者信息
            caller_frame = inspect.currentframe().f_back
            caller_info = inspect.getframeinfo(caller_frame) if caller_frame else None
            caller = f"{caller_info.filename}:{caller_info.lineno}" if caller_info else "unknown"
            
            # 过滤参数中的敏感信息
            filtered_args = []
            for arg in args:
                if isinstance(arg, str) and len(arg) > 100:
                    filtered_args.append(f"{arg[:100]}... (truncated)")
                else:
                    filtered_args.append(arg)
            
            filtered_kwargs = {}
            for key, value in kwargs.items():
                if key.lower() in ['password', 'api_key', 'secret', 'token']:
                    filtered_kwargs[key] = '******'
                elif isinstance(value, str) and len(value) > 100:
                    filtered_kwargs[key] = f"{value[:100]}... (truncated)"
                else:
                    filtered_kwargs[key] = value
            
            # 记录函数调用
            context = {
                'module': module_name,
                'function': func_name,
                'caller': caller,
                'args': str(filtered_args),
                'kwargs': str(filtered_kwargs)
            }
            
            log_func(f"Function Call: {module_name}.{func_name}", context)
            
            try:
                # 执行函数
                result = func(*args, **kwargs)
                
                # 记录返回值（可选）
                # 注意：对于大型返回值，可能需要截断或省略
                if level.lower() == 'debug':
                    result_str = str(result)
                    if len(result_str) > 200:
                        result_str = result_str[:200] + '... (truncated)'
                    
                    context['result'] = result_str
                    log_func(f"Function Return: {module_name}.{func_name}", context)
                
                return result
            except Exception as e:
                # 记录异常
                logger.exception(f"Function Exception: {module_name}.{func_name}", {
                    'module': module_name,
                    'function': func_name,
                    'caller': caller,
                    'exception': str(e)
                })
                raise
        
        return wrapper
    
    return decorator