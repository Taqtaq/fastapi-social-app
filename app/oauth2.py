# oauth2.py
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from . import schemas, database, models
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

def create_access_token(data: dict):
    # В функции create_access_token:
    try:
        to_encode = data.copy()
        
        now_utc_aware = datetime.now(timezone.utc) # Явно осведомленный о UTC объект
        expire_dt_utc_aware = now_utc_aware + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        exp_timestamp = int(expire_dt_utc_aware.timestamp()) # Получаем timestamp из осведомленного объекта
        to_encode.update({"exp": exp_timestamp})
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        # Отладочная информация
        print(f"\n[create_access_token] === ТОКЕН СОЗДАН ===")
        print(f"ЛОКАЛЬНОЕ ВРЕМЯ НА СЕРВЕРЕ ПРИ СОЗДАНИИ: {datetime.now().isoformat()}") # Просто для информации
        print(f"[create_access_token] Время вызова datetime.now(timezone.utc): {now_utc_aware.isoformat()}")
        print(f"[create_access_token] Расчетное время истечения (объект datetime UTC): {expire_dt_utc_aware.isoformat()}")
        print(f"[create_access_token] Timestamp истечения (payload.exp): {exp_timestamp}")
        print(f"[create_access_token] Полный Payload для кодирования: {to_encode}")
        # Добавим вывод самого токена здесь для удобства копирования
        print(f"[create_access_token] СГЕНЕРИРОВАННЫЙ ТОКЕН: {encoded_jwt}") 
        
        return encoded_jwt
    except Exception as e:
        print(f"[create_access_token] ОШИБКА: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка создания токена: {str(e)}"
        )

def verify_access_token(token: str, credentials_exception):
    print(f"\n[verify_access_token] ПОЛУЧЕННЫЙ ТОКЕН НА ПРОВЕРКУ: {token}") # <-- ВАЖНО!
    try:
        # Декодируем с проверкой подписи и срока
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        print(f"[verify_access_token] УСПЕШНО ДЕКОДИРОВАН PAYLOAD (с проверкой exp): {payload}")
        user_id = payload.get("user_id")
        
        if user_id is None:
            print(f"[verify_access_token] ОШИБКА: user_id отсутствует в payload.")
            raise credentials_exception
        
        # Эта дополнительная проверка времени может быть избыточной, если jwt.decode() отработал без ExpiredSignatureError
        # current_time_ts = int(datetime.now(timezone.utc).timestamp())
        # if payload["exp"] < current_time_ts:
        #     print(f"[verify_access_token] ДОП. ПРОВЕРКА: Токен просрочен. exp={payload['exp']}, current={current_time_ts}")
        #     raise jwt.ExpiredSignatureError # Искусственно вызываем, чтобы попасть в блок ниже
        
        return schemas.TokenData(id=user_id)
        
    except jwt.ExpiredSignatureError:
        print(f"[verify_access_token] ПЕРВИЧНАЯ ОШИВКА: jwt.ExpiredSignatureError (Токен просрочен по мнению библиотеки)")
        # Для просроченного токена получаем payload без проверки срока, чтобы увидеть детали
        try:
            payload_expired = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
           # print(f"[verify_access_token] ДЕКОДИРОВАННЫЙ PAYLOAD (БЕЗ ПРОВЕРКИ EXP): {payload_expired}") # <-- ВАЖНО!

            # Используем timezone.utc для fromtimestamp и для now, чтобы обеспечить согласованность
            expire_time_from_payload = datetime.fromtimestamp(payload_expired["exp"], tz=timezone.utc)
            current_time_utc = datetime.now(tz=timezone.utc) # Явно указываем tzinfo
            
            # print(f"\n[verify_access_token] === ДЕТАЛИ ПРОСРОЧЕННОГО ТОКЕНА ===")
            # print(f"[verify_access_token] Текущее время (datetime.now(timezone.utc)): {current_time_utc.isoformat()}")
            # print(f"[verify_access_token] Timestamp истечения из payload_expired.exp: {payload_expired['exp']}")
            # print(f"[verify_access_token] Время истечения из payload_expired.exp (datetime UTC): {expire_time_from_payload.isoformat()}")
            # print(f"[verify_access_token] Разница (текущее - истекшее): {current_time_utc - expire_time_from_payload}")
            
            detail = f"Token expired at {expire_time_from_payload.strftime('%Y-%m-%d %H:%M:%S UTC')}"
        except Exception as decode_error:
           # print(f"[verify_access_token] ОШИБКА при декодировании просроченного токена: {str(decode_error)}")
            detail = f"Token expired (decode error: {str(decode_error)})"
            
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    except JWTError as e:
   #     print(f"[verify_access_token] ОШИБКА JWTError (не ExpiredSignatureError): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e: # Общий обработчик на всякий случай
       # print(f"[verify_access_token] НЕОЖИДАННАЯ ОБЩАЯ ОШИБКА: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during token verification: {str(e)}"
        )


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail= "Не удалось проверить учетные данные", # "Could not validate credentials"
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    try:
       # print(f"\n[get_current_user] Вызов verify_access_token...")
        token_data = verify_access_token(token, credentials_exception)
       # print(f"[get_current_user] verify_access_token вернул: {token_data}")
        
        user = db.query(models.User).filter(models.User.id == token_data.id).first()
        
        if user is None:
           # print(f"[get_current_user] Пользователь с ID {token_data.id} не найден в БД")
            raise credentials_exception
        
        # print(f"[get_current_user] Пользователь найден: {user.email}")
        return user
        
    except HTTPException as http_exc:
        # Эта ошибка уже содержит детали, просто перевыбрасываем
        # print(f"[get_current_user] Перехвачена HTTPException: {http_exc.detail}") # Можно раскомментировать для доп. отладки
        raise
    except Exception as e:
      #  print(f"[get_current_user] Неожиданная ошибка: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка проверки пользователя: {str(e)}"
        )