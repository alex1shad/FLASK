from hashlib import md5


def validate(request):
    json_data = request.json['password']
    if len(json_data) < 8:
        raise {'status': 'Пароль слишком короткий'}
    if json_data.isalpha():
        raise {'status': 'В пароле должны быть цифры'}
    if json_data.isdigit():
        raise {'status': 'В пароле должны быть буквы'}
    symbol_check = '!@#$%^&*()'
    for el in symbol_check:
        if el not in json_data:
            continue
        else:
            break
    else:
        raise {'status': 'В пароле должен быть один из символов: !@#$%^&*()'}
    hash_password = md5(json_data.encode()).hexdigest()
    return hash_password
