Правила документування Apiary
=============================

Зміст
-----

* 1). Адміністративні
* 1.1). Система документації Apiary ESOZ використовує Apiary Blueprint, з джерелом в Github.
* 1.2). Apiary файл містить одразу інформацію для всіх середовищ.
* 1.3). Кожен працівник долучений до проєкту документації має змогу модифікувати джерельний файл на Github.
* 1.4). Для зміни потрібно мінімум одне погодження.
* 2). Структурні
* 2.1). Документація містить загальний Маніфест до опису HTTP протоколів і перелік всіх ендпойнтів.
* 2.2). Всі ендпойнти ЕСОЗ розділені на 4 групи: General, Personal, Medical, Administrative.
* 2.3). При використанні підписного контенту, payload інформація виноситься в фіктивні описи ендпойнтів, які використовуються для опису структур даних.
* 2.4). Кожен ендпойнт складається з наступного шаблону:
* 2.5). Необов'язкові параметри
* 3). Репрезентаційні
* 3.1). На асети використовуються прямі перманентні посилання.
* 3.2). Методи виведені з використання
* 3.3). Приватні методи
* 3.4). Нові версії методів без зміни назви
* 3.5). Нові версії методії (v2/v3)
* 3.6). Інформація про відмінності на середовищах
* 3.7). Особливості документування bulk методів по MIS токенах

## 1). Адміністративні

### 1.1. Система документації Apiary ESOZ використовує Oracle Apiary, з джерелом в Github.

### 1.2. Apiary файл містить одразу інформацію для всіх середовищ.

### 1.3. Кожен працівник долучений до проєкту документації має змогу модифікувати джерелльний файл на Github.

### 1.4. Для зміни потрібно мінімум одне погодження.

## 2). Структурні

### 2.1. Документація містить загальний Маніфест до опису HTTP протоколів і перелік всіх ендпойнтів.

### 2.2. Всі ендпойнти ЕСОЗ розділені на 4 групи: General, Personal, Medical, Administrative.

### 2.3. При використанні підписного контенту, payload інформація виноситься в фіктивні описи ендпойнтів, які використовуються для опису структур даних.

```
### Create Specimen [POST /api/patients/{patient_id}/specimens]

Key                | Value
-------------------|-----------
ESOZ API ID        | API-007-012-001-0493
Scope              | specimen:write
Auth               | yes
Link to Confluence | <a href="https://esoz.atlassian.net/wiki/spaces/ESOZ/pages/1/Create+Specimen">Create Specimen</a>

This endpoint allows to register Specimen by its own.

+ Parameters
    + patient_id: `7075e0e2-6b57-47fd-aff7-324806efa7e5` (string, required) - Unique patient identifier

+ Request (application/json)
    + Headers
        Authorization: Bearer mF_9.B5f-4.1JqM
        api-key: aFBLVTZ6Z2dON1V
        X-Custom-PSK: a2aa05c76f3f2d91870f923a53cc8aa8f23bbc01a8238d1c2c26d4299715a7e4
    + Attributes (object)
        + `signed_data`:`ew0KICAicGVyaW9kIjogew0KIC...` (string, required, fixed-type)

+ Response 202 (application/json)
    + Attributes (Response_OK)
        + meta (Response__Meta)
            + code: 202 (number)
        + data (`Job`)

### Dummy Create Specimen [POST /api/patients/{patient_id}/specimens/payload]

This chapter describes the structure of a single Specimen creation. This is not an actual web-service.

+ Request (application/json)
    + Headers
        api-key: aFBLVTZ6Z2dON1V
        Authorization: Bearer mF_9.B5f-4.1JqM
        X-Custom-PSK: a2aa05c76f3f2d91870f923a53cc8aa8f23bbc01a8238d1c2c26d4299715a7e4
    + Attributes (`Specimen_Request`)
```

### 2.4. Кожен ендпойнт складається з наступного шаблону:

```
### {Назва} [{Метод} {URL}]

Key                | Value
-------------------|-----------
ESOZ API ID        | {API}
Scope              | {Скоуп}
Auth               | {Авт}
Link to Confluence | <a href="{посилання на Confluence}">{Назва}</a>

{Текст}

{Реквізити}
```

Легенда:

* Назва --- назва ендпойнту, наприклад `Create Specimen`
* URL, --- посилання на метод API, наприклад `/api/patients/{patient_id}/specimens`
* Текст --- довільний текст, наприклад `See <a href="https://link.to/page/">link</a>.`
* Авт --- необхідність авторизації, наприклад `yes`
* Метод --- метод HTTP, наприклад `GET`
* API --- кодифікатор API, наприклад `API-007-012-001-0493`
* Скоуп --- необхідний права доступу, наприклад `specimen:read`
* Реквізити --- реквізитна частина, наприклад:

```
+ Parameters
    + patient_id: `7075e0e2-6b57-47fd-aff7-324806efa7e5` (string, required) - Unique patient identifier

+ Request (application/json)
    + Headers
        Authorization: Bearer mF_9.B5f-4.1JqM
        api-key: aFBLVTZ6Z2dON1V
        X-Custom-PSK: a2aa05c76f3f2d91870f923a53cc8aa8f23bbc01a8238d1c2c26d4299715a7e4
    + Attributes (object)
        + `signed_data`:`ew0KICAicGVyaW9kIjogew0KIC...` (string, required, fixed-type)

+ Response 202 (application/json)
    + Attributes (Response_OK)
        + meta (Response__Meta)
            + code: 202 (number)
        + data (`Job`)
```

### 2.5 Необов'язкові параметри

Параметри шаблону `Скоуп` і `Авт` є необов'язковими для розділу `User Authentication`.

## 3). Репрезентаційні

Правила, що впливают на верстку Apiary.

### 3.1. На асети використовуються прямі перманентні посилання

Перевіряйте, що ці посилання не потребують авторизації і підтримують хот лінкінг.

### 3.2. Методи виведені з використання

Методи виведені з використання позначаються і виділяються як `Deprecated`.

### 3.3. Приватні методи

Приватні методи позначаються і виділяються як `Private`.

### 3.4. Нові версії методії (v2/v3)

Версії методів які підтримуються паралельно позначаються маркуваннями `V2`, `V3`.

### 3.5. Нові версії методів без зміни назви

Нові версії методів без змін в назві, що потребують додаткого документування повинні
містити інформацію про застосування того чи іншого поля в певній версії, наприклад `8.5.5`, або `9.11`.

### 3.6. Інформація про відмінності на середовищах

Інформація про відмінності на середовищах надається в табличній формі з обов'язковою колонкою Environment
і супутніми колонками, що визначають відмінну функціональність.

Environmnet | Host
------------|-----
DEMO        | https://auth-demo.ehealth.gov.ua
PREPROD     | https://auth-preprod.ehealth.gov.ua
PROD        | https://auth.ehealth.gov.ua
