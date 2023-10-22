def pluralize_word(word_if_one, word_if_two, word_if_five, count):
    """
    Склоняет слово в зависимости от числа count с учетом разных вариантов склонения.

    :param word_if_one: Слово, которое используется, если число оканчивается на 1 (кроме 11).
    :param word_if_two: Слово, которое используется, если число оканчивается на 2, 3 или 4 (кроме 12, 13, 14).
    :param word_if_five: Слово, которое используется в остальных случаях.
    :param count: Число, от которого зависит склонение.

    :return: Склоненное слово в соответствии с числом count.
    """
    if count % 10 == 1 and count % 100 != 11:
        return word_if_one
    elif count % 10 in [2, 3, 4] and count % 100 not in [12, 13, 14]:
        return word_if_two
    else:
        return word_if_five


class Messages:
    @staticmethod
    def hello():
        return f"LESC - Local English speaking club BOT\nВсем хай!"

    @staticmethod
    def price(price: str):
        return f"Стоимость - {price}"

    @staticmethod
    def meetings_dates():
        return f"На какие даты будет клуб:"

    @staticmethod
    def meeting_dates_after_cancel():
        return "Запись отменена, посмотри встречи на другую дату"

    @staticmethod
    def meeting_date_and_time(datetime_str):
        return f"Дата и время: {datetime_str}"

    @staticmethod
    def meeting_place(place_str):
        return f"Место встречи - {place_str}"

    @staticmethod
    def cnt_free_tickets(cnt_free_tickets):
        return f"Свободных мест - {cnt_free_tickets}"

    @staticmethod
    def no_free_tickets():
        return "Sorry, кажется, уже все места заняты, выбери другой день"

    @staticmethod
    def no_member_ticket():
        return "Вы еще не записались на эту встречу, вернитесь плис на меню со встречей и забронируйте снова"

    @staticmethod
    def no_meetings():
        return "Мы готовим ближайшие встречи и скоро вы сможете записаться на них"

    @staticmethod
    def no_meetings_after_cancel():
        return "Запись отменена, готовим ближайшие встречи и скоро вы сможете записаться на них"

    @staticmethod
    def booking_success():
        return "Вы записались на эту встречу!"

    @staticmethod
    def booking_success_pay_confirm():
        return "Мы проверяем оплату, если сейчас ночь, то мы подтвердим запись утром, не волнуйтесь, мы вас ждем"

    @staticmethod
    def subs_success_pay_confirm():
        return "Мы проверяем оплату, если сейчас ночь, то мы подтвердим покупку абонемента утром, не волнуйтесь, мы зафиксировали вашу покупку"

    @staticmethod
    def booking_success_pay_success():
        return "Мы подтвердили вашу оплату, спасибо, ждем вас на встрече!"

    @staticmethod
    def subs_success_pay_success():
        return "Мы подтвердили вашу оплату абонемент, спасибо, записывайтесь!"

    @staticmethod
    def booking_already():
        return "Вы уже записались на это занятие, подтвердите оплату и приходите!"

    @staticmethod
    def booking_unavailable():
        return "Запись на эту встречу пока что не доступна, мы откроем запись чуть позже"

    @staticmethod
    def payment_info():
        return "Оплатите запись по номеру +7 (800) 555-35-35 (Соня Батьковна А.) на Сбербанк / Тинькофф и подтвердите перевод по кнопке 'Подтвердить'"

    @staticmethod
    def subs_payment_info():
        return "Оплатите абонемент по номеру +7 (800) 555-35-35 (Соня Батьковна А.) на Сбербанк / Тинькофф и подтвердите перевод по кнопке 'Подтвердить'"

    @staticmethod
    def subs_info():
        return "Че за крутой абонемент стоит всего 2 тыщи покупай кайфанешь."

    @staticmethod
    def cancel_in_meeting_day():
        return "Вы отменяете запись в день встречи, по нашим правилам мы не можем вам вернуть деньги( Вы уверены, что хотите отменить бронирование?"

    @staticmethod
    def cancel_already(what: str):
        return f"Похоже, что то вы уже отменили {what}"

    @staticmethod
    def cancel_with_return_money():
        return "Запись отменена, сейчас вернем деньги, посмотри встречи на другую дату"

    @staticmethod
    def cancel_with_return_success():
        return "Мы отменили вашу запись и вернули деньги, увидимся на другой встрече, выберите для себя подходящую"

    @staticmethod
    def cancel_by_admin():
        return "Мы не подтвердили вашу запись, увидимся на другой встрече, если вы платили деньги, то мы их вам уже вернули"

    @staticmethod
    def cancel_with_return_no_money():
        return "Запись отменена, деньги не вернем, потому что вы отменили встречу в день встречи, посмотрите встречи на другую дату"

    @staticmethod
    def about_subscribe():
        return "че за крутой абонемент покупай у него куча плюшек"

    @staticmethod
    def subscribe_balance(balance: str):
        word = pluralize_word("запись", "записи", "записей", int(balance))
        return f"у вас уже есть абонемент все круто молодец ходити, у вас осталось {balance} {word}"
